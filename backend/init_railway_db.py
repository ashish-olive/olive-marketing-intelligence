#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
Generates the full 1.5GB database during Docker build
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'data-pipeline'))

from flask import Flask
from shared.data_layer.models import db
from shared.data_layer.config import AppConfig
from data_pipeline.generators.complete_data_generator import CompleteDataGenerator


def init_railway_database():
    """Initialize database with full dataset for Railway"""
    print("="*70)
    print("GENERATING FULL DATABASE FOR RAILWAY DEPLOYMENT")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    # Ensure instance directory exists
    AppConfig.init_db_directory()
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
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
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)


if __name__ == '__main__':
    init_railway_database()
