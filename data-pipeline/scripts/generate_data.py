#!/usr/bin/env python3
"""
Marketing Data Generation Script
Run this in Google Colab to generate realistic marketing data

Usage:
    python generate_data.py --days 90 --users 500000
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root and data-pipeline to path
project_root = Path(__file__).parent.parent.parent
data_pipeline_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(data_pipeline_root))

from flask import Flask
from shared.data_layer.models import db
from shared.data_layer.config import AppConfig
from generators.complete_data_generator import CompleteDataGenerator


def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    # Ensure instance directory exists
    AppConfig.init_db_directory()
    
    # Initialize database
    db.init_app(app)
    
    return app


def main():
    parser = argparse.ArgumentParser(description='Generate marketing data')
    parser.add_argument('--days', type=int, default=90, help='Days of historical data')
    parser.add_argument('--users', type=int, default=500000, help='Number of users to generate')
    parser.add_argument('--campaigns', type=int, default=15, help='Campaigns per channel')
    args = parser.parse_args()
    
    print("="*70)
    print("OLIVE MARKETING INTELLIGENCE - DATA GENERATOR")
    print("="*70)
    print(f"Configuration:")
    print(f"  Days: {args.days}")
    print(f"  Users: {args.users:,}")
    print(f"  Campaigns per channel: {args.campaigns}")
    print(f"  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Create Flask app
    app = create_app()
    
    # Print config
    AppConfig.print_config()
    
    # Generate data
    print("\nInitializing generator...")
    generator = CompleteDataGenerator(
        days=args.days,
        users_target=args.users,
        campaigns_per_channel=args.campaigns
    )
    
    generator.generate_all(app)
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE!")
    print("="*70)
    print(f"Database location: {AppConfig.DB_PATH}")
    print(f"Database size: {Path(AppConfig.DB_PATH).stat().st_size / (1024*1024):.1f} MB")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext steps:")
    print("  1. Train ML models: python ml-models/scripts/train_all.py --use-gpu")
    print("  2. Package for local: python package_for_local.py")
    print("="*70)


if __name__ == '__main__':
    main()
