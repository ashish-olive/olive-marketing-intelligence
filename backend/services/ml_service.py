"""
ML Model Service
Loads and uses trained ML models for predictions
Falls back to rule-based predictions if models not available
"""
import sys
from pathlib import Path
import torch
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.data_layer.config import AppConfig


class MLService:
    """Service for ML model inference"""
    
    def __init__(self):
        self.device = torch.device('cpu')  # Always CPU for local inference
        self.models = {}
        self.scalers = {}
        self.models_loaded = False
        
        # Try to load models
        if AppConfig.USE_ML_MODELS:
            self.load_models()
    
    def load_models(self):
        """Load pre-trained models from disk"""
        models_dir = AppConfig.MODELS_DIR
        
        if not models_dir.exists():
            print("⚠️  Models directory not found. Using fallback predictions.")
            return
        
        try:
            # Load LTV predictor
            ltv_path = models_dir / 'ltv_predictor.pth'
            if ltv_path.exists():
                checkpoint = torch.load(ltv_path, map_location=self.device)
                
                # Import model architecture
                sys.path.insert(0, str(models_dir.parent))
                from models.architectures import LTVPredictor
                
                model = LTVPredictor(input_size=checkpoint['input_size'])
                model.load_state_dict(checkpoint['model_state_dict'])
                model.eval()
                
                self.models['ltv'] = model
                self.scalers['ltv'] = checkpoint['scaler']
                print("✓ LTV Predictor loaded")
            
            # Load campaign forecaster
            campaign_path = models_dir / 'campaign_forecaster.pth'
            if campaign_path.exists():
                checkpoint = torch.load(campaign_path, map_location=self.device)
                
                from models.architectures import CampaignForecaster
                
                model = CampaignForecaster(input_size=checkpoint['input_size'])
                model.load_state_dict(checkpoint['model_state_dict'])
                model.eval()
                
                self.models['campaign'] = model
                self.scalers['campaign'] = checkpoint['scaler']
                print("✓ Campaign Forecaster loaded")
            
            # Load churn predictor
            churn_path = models_dir / 'churn_predictor.pth'
            if churn_path.exists():
                checkpoint = torch.load(churn_path, map_location=self.device)
                
                from ml_models.models.architectures import ChurnPredictor
                
                model = ChurnPredictor(input_size=checkpoint['input_size'])
                model.load_state_dict(checkpoint['model_state_dict'])
                model.eval()
                
                self.models['churn'] = model
                self.scalers['churn'] = checkpoint['scaler']
                print("✓ Churn Predictor loaded")
            
            self.models_loaded = len(self.models) > 0
            
            if self.models_loaded:
                print(f"✓ Loaded {len(self.models)} ML models")
            else:
                print("⚠️  No models found. Using fallback predictions.")
                
        except Exception as e:
            print(f"⚠️  Error loading models: {e}")
            print("   Using fallback rule-based predictions")
            self.models_loaded = False
    
    def predict_ltv(self, user_features):
        """
        Predict user LTV
        
        Args:
            user_features: dict with user attributes
        
        Returns:
            Predicted LTV (float)
        """
        if self.models_loaded and 'ltv' in self.models:
            # ML prediction
            try:
                # Extract features in correct order
                features = self._extract_ltv_features(user_features)
                features_scaled = self.scalers['ltv'].transform([features])
                
                with torch.no_grad():
                    input_tensor = torch.FloatTensor(features_scaled)
                    prediction = self.models['ltv'](input_tensor)
                    return float(prediction.item())
            except Exception as e:
                print(f"ML prediction failed: {e}, using fallback")
                return self._fallback_ltv_prediction(user_features)
        else:
            # Fallback: rule-based
            return self._fallback_ltv_prediction(user_features)
    
    def predict_campaign_performance(self, historical_data):
        """
        Predict next 7 days of campaign performance
        
        Args:
            historical_data: List of daily performance dicts
        
        Returns:
            List of predicted CPIs for next 7 days
        """
        if self.models_loaded and 'campaign' in self.models:
            try:
                # Prepare sequence
                sequence = self._prepare_campaign_sequence(historical_data)
                sequence_scaled = self.scalers['campaign'].transform(
                    sequence.reshape(-1, sequence.shape[-1])
                ).reshape(sequence.shape)
                
                with torch.no_grad():
                    input_tensor = torch.FloatTensor(sequence_scaled).unsqueeze(0)
                    predictions = self.models['campaign'](input_tensor)
                    return predictions.squeeze().cpu().numpy().tolist()
            except Exception as e:
                print(f"ML prediction failed: {e}, using fallback")
                return self._fallback_campaign_prediction(historical_data)
        else:
            return self._fallback_campaign_prediction(historical_data)
    
    def predict_churn(self, user_features):
        """
        Predict churn probability
        
        Args:
            user_features: dict with user attributes
        
        Returns:
            Churn probability (0-1)
        """
        if self.models_loaded and 'churn' in self.models:
            try:
                features = self._extract_churn_features(user_features)
                features_scaled = self.scalers['churn'].transform([features])
                
                with torch.no_grad():
                    input_tensor = torch.FloatTensor(features_scaled)
                    prediction = self.models['churn'](input_tensor)
                    return float(prediction.item())
            except Exception as e:
                print(f"ML prediction failed: {e}, using fallback")
                return self._fallback_churn_prediction(user_features)
        else:
            return self._fallback_churn_prediction(user_features)
    
    def _extract_ltv_features(self, user_features):
        """Extract features for LTV prediction"""
        # Match the feature order from training
        return [
            user_features.get('retention_d1', 0),
            user_features.get('retention_d7', 0),
            user_features.get('retention_d30', 0),
            # ... add all 30 features in correct order
        ]
    
    def _extract_churn_features(self, user_features):
        """Extract features for churn prediction"""
        return [
            user_features.get('session_count_7d', 0),
            user_features.get('session_count_30d', 0),
            # ... add all features
        ]
    
    def _prepare_campaign_sequence(self, historical_data):
        """Prepare sequence for campaign forecasting"""
        sequence = []
        for day in historical_data[-14:]:  # Last 14 days
            sequence.append([
                day.get('spend', 0),
                day.get('installs', 0),
                day.get('cpi', 0),
                # ... add all features
            ])
        return np.array(sequence)
    
    def _fallback_ltv_prediction(self, user_features):
        """Simple rule-based LTV prediction"""
        base_ltv = 15.0
        retention_mult = user_features.get('retention_d7', 0.5) / 0.5
        payer_mult = 2.0 if user_features.get('is_payer', False) else 1.0
        return base_ltv * retention_mult * payer_mult
    
    def _fallback_campaign_prediction(self, historical_data):
        """Simple rule-based campaign prediction"""
        if not historical_data:
            return [2.5] * 7
        
        recent_cpi = np.mean([d.get('cpi', 2.5) for d in historical_data[-7:]])
        # Add slight trend
        return [recent_cpi * (1 + i * 0.01) for i in range(7)]
    
    def _fallback_churn_prediction(self, user_features):
        """Simple rule-based churn prediction"""
        session_count = user_features.get('session_count_7d', 0)
        retention = user_features.get('retention_d7', 0)
        
        # Simple heuristic
        if session_count == 0:
            return 0.9
        elif retention < 0.3:
            return 0.7
        elif retention < 0.5:
            return 0.4
        else:
            return 0.2


# Global instance
ml_service = MLService()
