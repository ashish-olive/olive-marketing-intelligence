#!/usr/bin/env python3
"""
Railway startup script with database generation
Generates the full 1.5GB database at runtime (after deployment)
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'data-pipeline'))

from flask import Flask
from shared.data_layer.models import db
from shared.data_layer.config import AppConfig
from generators.complete_data_generator import CompleteDataGenerator


def generate_database():
    """Generate the full database at runtime"""
    print("="*70)
    print("GENERATING FULL DATABASE AT RUNTIME")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will take 15-20 minutes...")
    print("="*70)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    # Ensure instance directory exists
    AppConfig.init_db_directory()
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Check if database already exists
        db_path = Path(AppConfig.DB_PATH)
        if db_path.exists() and db_path.stat().st_size > 1000000:  # > 1MB
            print("Database already exists, skipping generation")
            return
        
        # Create tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        # Generate full dataset
        print("Generating full dataset...")
        generator = CompleteDataGenerator(
            days=90,  # Full 90 days
            users_target=500000,  # Full 500k users
            campaigns_per_channel=15  # Full 15 campaigns per channel
        )
        
        generator.generate_all(app)
        
        print("="*70)
        print("DATABASE GENERATION COMPLETE!")
        print("="*70)
        print(f"Database location: {AppConfig.DB_PATH}")
        print(f"Database size: {db_path.stat().st_size / (1024*1024):.1f} MB")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)


if __name__ == '__main__':
    generate_database()
