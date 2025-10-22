"""
LTV Predictor Training Script
Train neural network to predict 180-day LTV from early user behavior
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
import pickle

# Add project root and ml-models to path
project_root = Path(__file__).parent.parent.parent
ml_models_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ml_models_root))

from shared.data_layer.models import db, UserInstall
from shared.data_layer.config import AppConfig
from models.architectures import LTVPredictor
from flask import Flask


class LTVDataset(Dataset):
    """Dataset for LTV prediction"""
    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]


def prepare_data(db_path):
    """Load and prepare data from database"""
    print("Loading data from database...")
    
    # Convert to absolute path
    from pathlib import Path
    db_path = Path(db_path).resolve()
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        # Load users
        users = UserInstall.query.filter(
            UserInstall.ltv_180d.isnot(None)
        ).all()
        
        print(f"Loaded {len(users)} users")
        
        # Extract features
        features = []
        targets = []
        
        for user in users:
            # Feature engineering
            feature_vector = [
                # Retention features
                float(user.retention_d1 or 0),
                float(user.retention_d7 or 0),
                float(user.retention_d30 or 0),
                float(user.d1_active or 0),
                float(user.d7_active or 0),
                float(user.d30_active or 0),
                
                # Engagement features
                float(user.session_count_7d or 0),
                float(user.session_count_30d or 0),
                float(user.avg_session_duration or 0),
                float(user.total_playtime_minutes or 0),
                
                # Monetization features
                float(user.is_payer or 0),
                float(user.first_purchase_day or 999),
                float(user.total_revenue or 0),
                float(user.ltv_7d or 0),
                float(user.ltv_30d or 0),
                
                # Device features (one-hot)
                1.0 if user.device_type == 'iOS' else 0.0,
                1.0 if user.device_type == 'Android' else 0.0,
                
                # Geo features (one-hot for top countries)
                1.0 if user.country == 'US' else 0.0,
                1.0 if user.country == 'UK' else 0.0,
                1.0 if user.country == 'CA' else 0.0,
                1.0 if user.country == 'AU' else 0.0,
                
                # User segment (one-hot)
                1.0 if user.user_segment == 'power_user' else 0.0,
                1.0 if user.user_segment == 'regular' else 0.0,
                1.0 if user.user_segment == 'casual' else 0.0,
                
                # Channel features (one-hot)
                1.0 if user.channel_id == 1 else 0.0,  # Meta
                1.0 if user.channel_id == 2 else 0.0,  # Google
                1.0 if user.channel_id == 3 else 0.0,  # TikTok
                1.0 if user.channel_id == 4 else 0.0,  # Programmatic
                
                # Install source
                1.0 if user.install_source == 'paid' else 0.0,
            ]
            
            features.append(feature_vector)
            targets.append(float(user.ltv_180d))
        
        features = np.array(features)
        targets = np.array(targets).reshape(-1, 1)
        
        print(f"Features shape: {features.shape}")
        print(f"Targets shape: {targets.shape}")
        
        return features, targets


def train_ltv_model(db_path, device, epochs=100, batch_size=256, save_path=None):
    """Train LTV prediction model"""
    print("\n" + "="*70)
    print("TRAINING LTV PREDICTOR")
    print("="*70 + "\n")
    
    # Prepare data
    features, targets = prepare_data(db_path)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        features, targets, test_size=0.2, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    print(f"Train set: {len(X_train)}")
    print(f"Val set: {len(X_val)}")
    print(f"Test set: {len(X_test)}\n")
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    
    # Create datasets
    train_dataset = LTVDataset(X_train, y_train)
    val_dataset = LTVDataset(X_val, y_val)
    test_dataset = LTVDataset(X_test, y_test)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Create model
    model = LTVPredictor(input_size=features.shape[1]).to(device)
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Training on: {device}\n")
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    # Training loop
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        for features_batch, targets_batch in train_loader:
            features_batch = features_batch.to(device)
            targets_batch = targets_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(features_batch)
            loss = criterion(outputs, targets_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for features_batch, targets_batch in val_loader:
                features_batch = features_batch.to(device)
                targets_batch = targets_batch.to(device)
                
                outputs = model(features_batch)
                loss = criterion(outputs, targets_batch)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        # Print progress
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best model
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
    
    # Test evaluation
    model.eval()
    test_loss = 0.0
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        for features_batch, targets_batch in test_loader:
            features_batch = features_batch.to(device)
            targets_batch = targets_batch.to(device)
            
            outputs = model(features_batch)
            loss = criterion(outputs, targets_batch)
            test_loss += loss.item()
            
            all_predictions.extend(outputs.cpu().numpy())
            all_targets.extend(targets_batch.cpu().numpy())
    
    test_loss /= len(test_loader)
    rmse = np.sqrt(test_loss)
    
    # Calculate metrics
    all_predictions = np.array(all_predictions)
    all_targets = np.array(all_targets)
    mae = np.mean(np.abs(all_predictions - all_targets))
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Best Val Loss: {best_val_loss:.4f}")
    print(f"Test RMSE: ${rmse:.2f}")
    print(f"Test MAE: ${mae:.2f}")
    print(f"Model saved to: {save_path}")
    
    return {
        'test_rmse': float(rmse),
        'test_mae': float(mae),
        'best_val_loss': float(best_val_loss),
        'epochs_trained': epoch + 1
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=str, default='instance/marketing.db')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=256)
    parser.add_argument('--use-gpu', action='store_true')
    args = parser.parse_args()
    
    device = torch.device('cuda' if args.use_gpu and torch.cuda.is_available() else 'cpu')
    
    train_ltv_model(
        db_path=args.db_path,
        device=device,
        epochs=args.epochs,
        batch_size=args.batch_size,
        save_path='ml-models/trained_models/ltv_predictor.pth'
    )
