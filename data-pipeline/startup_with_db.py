#!/usr/bin/env python3
"""
Database generation for Fly.io deployment
This module provides the generate_database function for runtime database creation
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root and data-pipeline to path
project_root = Path(__file__).parent.parent
data_pipeline_root = Path(__file__).parent
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
    db.init_app(app)
    return app


def generate_database():
    """Generate the marketing database at runtime"""
    print("="*70)
    print("GENERATING FULL DATABASE AT RUNTIME")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will take 15-20 minutes...")
    print("="*70)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        # Generate data
        print("Initializing generator...")
        generator = CompleteDataGenerator(
            days=90,
            users_target=500000,
            campaigns_per_channel=15
        )
        
        print("Generating data...")
        generator.generate_all_data()
        
        print("Database generation completed successfully!")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    generate_database()
