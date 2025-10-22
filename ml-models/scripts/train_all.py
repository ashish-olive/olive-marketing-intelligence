#!/usr/bin/env python3
"""
Master Training Script
Train all ML models on GPU in Google Colab
"""
import sys
from pathlib import Path
import torch
import json
from datetime import datetime
import argparse

# Add project root and ml-models to path
project_root = Path(__file__).parent.parent.parent
ml_models_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ml_models_root))

from trainers.ltv_predictor import train_ltv_model
from trainers.campaign_forecaster import train_campaign_model
from trainers.churn_predictor import train_churn_model


def main():
    parser = argparse.ArgumentParser(description='Train all ML models')
    parser.add_argument('--db-path', type=str, default='instance/marketing.db',
                       help='Path to database')
    parser.add_argument('--use-gpu', action='store_true',
                       help='Use GPU if available')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--models-dir', type=str, default='ml-models/trained_models',
                       help='Directory to save trained models')
    args = parser.parse_args()
    
    # Setup device
    if args.use_gpu and torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"\n{'='*70}")
        print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        print(f"{'='*70}\n")
    else:
        device = torch.device('cpu')
        print(f"\n{'='*70}")
        print("💻 Using CPU")
        print(f"{'='*70}\n")
    
    # Create models directory
    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check database
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("   Please run data generation first:")
        print("   python data-pipeline/scripts/generate_data.py --days 90 --users 500000")
        sys.exit(1)
    
    db_size = db_path.stat().st_size / (1024 * 1024)
    print(f"✓ Database found: {db_path} ({db_size:.1f} MB)\n")
    
    # Training results
    results = {
        'train_date': datetime.now().isoformat(),
        'device': str(device),
        'epochs': args.epochs,
        'database': str(db_path),
        'models': {}
    }
    
    # Train models
    print("\n" + "="*70)
    print("STARTING MODEL TRAINING")
    print("="*70)
    print(f"Training 3 models with {args.epochs} epochs each")
    print(f"Estimated time: 15-20 minutes on T4 GPU")
    print("="*70 + "\n")
    
    try:
        # 1. LTV Predictor
        print("\n[1/3] Training LTV Predictor...")
        ltv_metrics = train_ltv_model(
            db_path=str(db_path),
            device=device,
            epochs=args.epochs,
            save_path=str(models_dir / 'ltv_predictor.pth')
        )
        results['models']['ltv_predictor'] = ltv_metrics
        print("✓ LTV Predictor complete\n")
        
        # 2. Campaign Forecaster
        print("\n[2/3] Training Campaign Forecaster...")
        campaign_metrics = train_campaign_model(
            db_path=str(db_path),
            device=device,
            epochs=args.epochs,
            save_path=str(models_dir / 'campaign_forecaster.pth')
        )
        results['models']['campaign_forecaster'] = campaign_metrics
        print("✓ Campaign Forecaster complete\n")
        
        # 3. Churn Predictor
        print("\n[3/3] Training Churn Predictor...")
        churn_metrics = train_churn_model(
            db_path=str(db_path),
            device=device,
            epochs=args.epochs,
            save_path=str(models_dir / 'churn_predictor.pth')
        )
        results['models']['churn_predictor'] = churn_metrics
        print("✓ Churn Predictor complete\n")
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save metadata
    metadata_path = models_dir / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("🎉 ALL MODELS TRAINED SUCCESSFULLY!")
    print("="*70)
    print(f"\nModels saved to: {models_dir}/")
    print("\nModel Performance:")
    print("-" * 70)
    
    if 'ltv_predictor' in results['models']:
        ltv = results['models']['ltv_predictor']
        print(f"LTV Predictor:")
        print(f"  - Test RMSE: ${ltv['test_rmse']:.2f}")
        print(f"  - Test MAE: ${ltv['test_mae']:.2f}")
        print(f"  - Epochs: {ltv['epochs_trained']}")
    
    if 'campaign_forecaster' in results['models']:
        camp = results['models']['campaign_forecaster']
        print(f"\nCampaign Forecaster:")
        print(f"  - Test RMSE: ${camp['test_rmse']:.2f}")
        print(f"  - Test MAPE: {camp['test_mape']:.2f}%")
        print(f"  - Epochs: {camp['epochs_trained']}")
    
    if 'churn_predictor' in results['models']:
        churn = results['models']['churn_predictor']
        print(f"\nChurn Predictor:")
        print(f"  - AUC-ROC: {churn['test_auc_roc']:.4f}")
        print(f"  - F1-Score: {churn['f1_score']:.4f}")
        print(f"  - Epochs: {churn['epochs_trained']}")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Package for local deployment:")
    print("   python package_for_local.py")
    print("\n2. Download the package:")
    print("   from google.colab import files")
    print("   files.download('deployment_package.zip')")
    print("\n3. Extract locally and run the app!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
