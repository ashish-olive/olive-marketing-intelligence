"""
Campaign Forecaster Training Script
Train LSTM to forecast campaign performance for next 7 days
"""
import sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.data_layer.models import db, Campaign, DailyCampaignPerformance
from ml_models.models.architectures import CampaignForecaster
from flask import Flask


class CampaignDataset(Dataset):
    """Dataset for campaign forecasting"""
    def __init__(self, sequences, targets):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]


def prepare_sequences(db_path, lookback=14, forecast=7):
    """Prepare time series sequences from campaign data"""
    print("Loading campaign data...")
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        campaigns = Campaign.query.all()
        
        sequences = []
        targets = []
        
        for campaign in campaigns:
            # Get daily performance sorted by date
            daily_perf = DailyCampaignPerformance.query.filter_by(
                campaign_id=campaign.id
            ).order_by(DailyCampaignPerformance.date).all()
            
            if len(daily_perf) < lookback + forecast:
                continue
            
            # Create sequences
            for i in range(len(daily_perf) - lookback - forecast + 1):
                # Input: 14 days of history
                sequence = []
                for j in range(i, i + lookback):
                    day = daily_perf[j]
                    sequence.append([
                        float(day.spend),
                        float(day.installs),
                        float(day.cpi),
                        float(day.ctr),
                        float(day.cvr),
                        float(day.retention_d1 or 0),
                        float(day.retention_d7 or 0),
                        float(day.roas_7d or 0),
                        float(day.date.weekday()),  # Day of week
                        float((day.date - campaign.start_date).days)  # Campaign age
                    ])
                
                # Target: next 7 days CPI
                target = []
                for j in range(i + lookback, i + lookback + forecast):
                    target.append(float(daily_perf[j].cpi))
                
                sequences.append(sequence)
                targets.append(target)
        
        sequences = np.array(sequences)
        targets = np.array(targets)
        
        print(f"Created {len(sequences)} sequences")
        print(f"Sequence shape: {sequences.shape}")
        print(f"Target shape: {targets.shape}")
        
        return sequences, targets


def train_campaign_model(db_path, device, epochs=100, batch_size=32, save_path=None):
    """Train campaign forecasting model"""
    print("\n" + "="*70)
    print("TRAINING CAMPAIGN FORECASTER")
    print("="*70 + "\n")
    
    # Prepare data
    sequences, targets = prepare_sequences(db_path)
    
    # Split data
    train_size = int(0.8 * len(sequences))
    val_size = int(0.1 * len(sequences))
    
    X_train = sequences[:train_size]
    y_train = targets[:train_size]
    X_val = sequences[train_size:train_size+val_size]
    y_val = targets[train_size:train_size+val_size]
    X_test = sequences[train_size+val_size:]
    y_test = targets[train_size+val_size:]
    
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}\n")
    
    # Scale features
    scaler = StandardScaler()
    X_train_reshaped = X_train.reshape(-1, X_train.shape[-1])
    scaler.fit(X_train_reshaped)
    
    X_train = scaler.transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
    X_val = scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
    X_test = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
    
    # Create datasets
    train_dataset = CampaignDataset(X_train, y_train)
    val_dataset = CampaignDataset(X_val, y_val)
    test_dataset = CampaignDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Create model
    model = CampaignForecaster(input_size=10, hidden_size=128, num_layers=2).to(device)
    print(f"Model: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Device: {device}\n")
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        for seq_batch, target_batch in train_loader:
            seq_batch = seq_batch.to(device)
            target_batch = target_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(seq_batch)
            loss = criterion(outputs, target_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for seq_batch, target_batch in val_loader:
                seq_batch = seq_batch.to(device)
                target_batch = target_batch.to(device)
                
                outputs = model(seq_batch)
                loss = criterion(outputs, target_batch)
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
                    'input_size': 10
                }, save_path)
        else:
            patience_counter += 1
            if patience_counter >= 10:
                print(f"\nEarly stopping at epoch {epoch+1}")
                break
    
    # Test
    model.eval()
    test_loss = 0.0
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for seq_batch, target_batch in test_loader:
            seq_batch = seq_batch.to(device)
            target_batch = target_batch.to(device)
            
            outputs = model(seq_batch)
            loss = criterion(outputs, target_batch)
            test_loss += loss.item()
            
            all_preds.extend(outputs.cpu().numpy())
            all_targets.extend(target_batch.cpu().numpy())
    
    test_loss /= len(test_loader)
    rmse = np.sqrt(test_loss)
    
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    mape = np.mean(np.abs((all_targets - all_preds) / (all_targets + 1e-8))) * 100
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Test RMSE: ${rmse:.2f}")
    print(f"Test MAPE: {mape:.2f}%")
    print(f"Model saved to: {save_path}")
    
    return {
        'test_rmse': float(rmse),
        'test_mape': float(mape),
        'best_val_loss': float(best_val_loss),
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
    
    train_campaign_model(
        db_path=args.db_path,
        device=device,
        epochs=args.epochs,
        save_path='ml-models/trained_models/campaign_forecaster.pth'
    )
