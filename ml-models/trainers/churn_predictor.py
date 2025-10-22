"""
Churn Predictor Training Script
Train model to predict user churn in next 7 days
"""
import sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support

# Add project root and ml-models to path
project_root = Path(__file__).parent.parent.parent
ml_models_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ml_models_root))

from shared.data_layer.models import db, UserInstall
from models.architectures import ChurnPredictor
from flask import Flask


class ChurnDataset(Dataset):
    """Dataset for churn prediction"""
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


def prepare_churn_data(db_path):
    """Prepare churn prediction data"""
    print("Loading user data...")
    
    # Convert to absolute path
    from pathlib import Path
    db_path = Path(db_path).resolve()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        users = UserInstall.query.all()
        
        features = []
        labels = []
        
        for user in users:
            # Feature engineering for churn
            feature_vector = [
                # Engagement metrics
                float(user.session_count_7d or 0),
                float(user.session_count_30d or 0),
                float(user.avg_session_duration or 0),
                float(user.total_playtime_minutes or 0),
                
                # Retention
                float(user.retention_d1 or 0),
                float(user.retention_d7 or 0),
                float(user.retention_d30 or 0),
                float(user.d1_active or 0),
                float(user.d7_active or 0),
                float(user.d30_active or 0),
                
                # Monetization
                float(user.is_payer or 0),
                float(user.total_revenue or 0),
                float(user.ltv_7d or 0),
                float(user.ltv_30d or 0),
                
                # Recency (days since install)
                float(user.days_to_churn or 0) if user.is_churned else 999,
                
                # Device
                1.0 if user.device_type == 'iOS' else 0.0,
                1.0 if user.device_type == 'Android' else 0.0,
                
                # Geo
                1.0 if user.country == 'US' else 0.0,
                1.0 if user.country == 'UK' else 0.0,
                1.0 if user.country == 'CA' else 0.0,
                
                # User segment
                1.0 if user.user_segment == 'power_user' else 0.0,
                1.0 if user.user_segment == 'regular' else 0.0,
                1.0 if user.user_segment == 'casual' else 0.0,
                
                # Channel
                1.0 if user.channel_id == 1 else 0.0,
                1.0 if user.channel_id == 2 else 0.0,
            ]
            
            features.append(feature_vector)
            labels.append(float(user.is_churned or 0))
        
        features = np.array(features)
        labels = np.array(labels).reshape(-1, 1)
        
        print(f"Total users: {len(features)}")
        print(f"Churned: {int(labels.sum())} ({labels.mean()*100:.1f}%)")
        print(f"Features shape: {features.shape}")
        
        return features, labels


def train_churn_model(db_path, device, epochs=100, batch_size=256, save_path=None):
    """Train churn prediction model"""
    print("\n" + "="*70)
    print("TRAINING CHURN PREDICTOR")
    print("="*70 + "\n")
    
    # Prepare data
    features, labels = prepare_churn_data(db_path)
    
    # Split
    X_train, X_temp, y_train, y_temp = train_test_split(
        features, labels, test_size=0.2, random_state=42, stratify=labels
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}\n")
    
    # Scale
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    
    # Datasets
    train_dataset = ChurnDataset(X_train, y_train)
    val_dataset = ChurnDataset(X_val, y_val)
    test_dataset = ChurnDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Model
    model = ChurnPredictor(input_size=features.shape[1]).to(device)
    print(f"Model: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Device: {device}\n")
    
    # Loss with class weights (handle imbalance)
    pos_weight = torch.tensor([len(labels) / labels.sum() - 1]).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        for feat_batch, label_batch in train_loader:
            feat_batch = feat_batch.to(device)
            label_batch = label_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(feat_batch)
            loss = criterion(outputs, label_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for feat_batch, label_batch in val_loader:
                feat_batch = feat_batch.to(device)
                label_batch = label_batch.to(device)
                
                outputs = model(feat_batch)
                loss = criterion(outputs, label_batch)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] - Train: {train_loss:.4f}, Val: {val_loss:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            if save_path:
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'scaler': scaler,
                    'input_size': features.shape[1]
                }, save_path)
        else:
            patience_counter += 1
            if patience_counter >= 10:
                print(f"\nEarly stopping at epoch {epoch+1}")
                break
    
    # Test
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for feat_batch, label_batch in test_loader:
            feat_batch = feat_batch.to(device)
            outputs = model(feat_batch)
            all_preds.extend(outputs.cpu().numpy())
            all_labels.extend(label_batch.numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    # Metrics
    auc_roc = roc_auc_score(all_labels, all_preds)
    pred_binary = (all_preds > 0.5).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, pred_binary, average='binary'
    )
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Test AUC-ROC: {auc_roc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"Model saved to: {save_path}")
    
    return {
        'test_auc_roc': float(auc_roc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'epochs_trained': epoch + 1
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=str, default='instance/marketing.db')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--use-gpu', action='store_true')
    args = parser.parse_args()
    
    device = torch.device('cuda' if args.use_gpu and torch.cuda.is_available() else 'cpu')
    
    train_churn_model(
        db_path=args.db_path,
        device=device,
        epochs=args.epochs,
        save_path='ml-models/trained_models/churn_predictor.pth'
    )
