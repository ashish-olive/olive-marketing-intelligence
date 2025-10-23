"""
Database configuration for Olive Marketing Intelligence
Supports both data generation (Colab) and local environments
"""
import os
from pathlib import Path


class AppConfig:
    """Application configuration"""
    
    # Get the base directory (project root)
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Database configuration
    DB_PATH = str(BASE_DIR.absolute() / 'instance' / 'marketing.db')
    _default_uri = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', _default_uri)
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    
    # API configuration
    API_PORT = int(os.getenv('API_PORT', 5000))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # ML Models configuration
    MODELS_DIR = BASE_DIR / 'ml-models' / 'trained_models'
    USE_ML_MODELS = os.getenv('USE_ML_MODELS', '1') == '1'
    
    @classmethod
    def init_db_directory(cls):
        """Ensure instance directory exists"""
        instance_dir = cls.BASE_DIR / 'instance'
        instance_dir.mkdir(exist_ok=True)
        return instance_dir
    
    @classmethod
    def print_config(cls):
        """Print configuration for debugging"""
        print(f"[CONFIG] BASE_DIR: {cls.BASE_DIR}")
        print(f"[CONFIG] DB_PATH: {cls.DB_PATH}")
        print(f"[CONFIG] DATABASE_URI: {cls.SQLALCHEMY_DATABASE_URI}")
        print(f"[CONFIG] MODELS_DIR: {cls.MODELS_DIR}")
        print(f"[CONFIG] USE_ML_MODELS: {cls.USE_ML_MODELS}")
