"""
PyTorch Model Architectures
Neural network definitions for marketing intelligence
"""
import torch
import torch.nn as nn


class LTVPredictor(nn.Module):
    """
    Predict 180-day LTV from early user behavior
    Input: 30 features (retention, sessions, geo, device, etc.)
    Output: Predicted LTV (single value)
    """
    def __init__(self, input_size=30, hidden_sizes=[256, 128, 64]):
        super(LTVPredictor, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(prev_size, 1))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class CampaignForecaster(nn.Module):
    """
    Forecast campaign performance for next 7 days
    Input: Historical performance (14 days x features)
    Output: Next 7 days predictions
    """
    def __init__(self, input_size=10, hidden_size=128, num_layers=2, output_days=7):
        super(CampaignForecaster, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, output_days)
        )
    
    def forward(self, x):
        # x shape: (batch, sequence_length, input_size)
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Predict next 7 days
        predictions = self.fc(last_output)
        
        return predictions


class ChurnPredictor(nn.Module):
    """
    Predict if user will churn in next 7 days
    Input: User behavioral features
    Output: Churn probability (0-1)
    """
    def __init__(self, input_size=25, hidden_sizes=[128, 64, 32]):
        super(ChurnPredictor, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(0.3)
            ])
            prev_size = hidden_size
        
        # Output layer with sigmoid for probability
        layers.extend([
            nn.Linear(prev_size, 1),
            nn.Sigmoid()
        ])
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class BudgetOptimizer(nn.Module):
    """
    Deep Q-Network for budget optimization
    Input: State (channel performance, budget, day)
    Output: Q-values for each action (budget allocation)
    """
    def __init__(self, state_size=20, action_size=10, hidden_sizes=[256, 128]):
        super(BudgetOptimizer, self).__init__()
        
        layers = []
        prev_size = state_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        # Output Q-values for each action
        layers.append(nn.Linear(prev_size, action_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


def get_model(model_name, **kwargs):
    """
    Factory function to get model by name
    
    Args:
        model_name: 'ltv', 'campaign', 'churn', or 'budget'
        **kwargs: Model-specific parameters
    
    Returns:
        Model instance
    """
    models = {
        'ltv': LTVPredictor,
        'campaign': CampaignForecaster,
        'churn': ChurnPredictor,
        'budget': BudgetOptimizer
    }
    
    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}. Choose from {list(models.keys())}")
    
    return models[model_name](**kwargs)


def count_parameters(model):
    """Count trainable parameters in model"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == '__main__':
    # Test model creation
    print("Testing model architectures...\n")
    
    # LTV Predictor
    ltv_model = LTVPredictor()
    print(f"LTV Predictor: {count_parameters(ltv_model):,} parameters")
    test_input = torch.randn(32, 30)
    output = ltv_model(test_input)
    print(f"  Input: {test_input.shape}, Output: {output.shape}\n")
    
    # Campaign Forecaster
    campaign_model = CampaignForecaster()
    print(f"Campaign Forecaster: {count_parameters(campaign_model):,} parameters")
    test_input = torch.randn(32, 14, 10)
    output = campaign_model(test_input)
    print(f"  Input: {test_input.shape}, Output: {output.shape}\n")
    
    # Churn Predictor
    churn_model = ChurnPredictor()
    print(f"Churn Predictor: {count_parameters(churn_model):,} parameters")
    test_input = torch.randn(32, 25)
    output = churn_model(test_input)
    print(f"  Input: {test_input.shape}, Output: {output.shape}\n")
    
    # Budget Optimizer
    budget_model = BudgetOptimizer()
    print(f"Budget Optimizer: {count_parameters(budget_model):,} parameters")
    test_input = torch.randn(32, 20)
    output = budget_model(test_input)
    print(f"  Input: {test_input.shape}, Output: {output.shape}\n")
    
    print("✓ All models created successfully!")
