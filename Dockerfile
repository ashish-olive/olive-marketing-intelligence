# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary files for database generation
COPY backend/ .
COPY shared/ ./shared/
COPY data-pipeline/ ./data-pipeline/
COPY ml-models/ ./ml-models/

# Create instance directory for database
RUN mkdir -p instance

# Generate the full database during build
RUN cd backend && python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').absolute()))
sys.path.insert(0, str(Path('../data-pipeline').absolute()))

from flask import Flask
from shared.data_layer.models import db
from shared.data_layer.config import AppConfig
from data_pipeline.generators.complete_data_generator import CompleteDataGenerator

# Create Flask app
app = Flask(__name__)
app.config.from_object(AppConfig)

# Ensure instance directory exists
AppConfig.init_db_directory()

# Initialize database
db.init_app(app)

with app.app_context():
    print('='*70)
    print('GENERATING FULL DATABASE FOR RAILWAY DEPLOYMENT')
    print('='*70)
    
    # Create tables
    db.create_all()
    print('✓ Database tables created')
    
    # Generate full dataset
    generator = CompleteDataGenerator(
        days=90,  # Full 90 days
        users_target=500000,  # Full 500k users
        campaigns_per_channel=15  # Full 15 campaigns per channel
    )
    
    generator.generate_all(app)
    
    print('='*70)
    print('DATABASE GENERATION COMPLETE!')
    print('='*70)
"

# Expose the port that Railway will use
EXPOSE $PORT

# Set the start command
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
