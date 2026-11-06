import os
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file if present
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Base configuration class with default settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-college-placement-secret-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Admin credentials for authentication
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # Path to saved Machine Learning model
    MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'saved_model', 'placement_model.joblib')
    MODEL_METRICS_PATH = os.path.join(BASE_DIR, 'ml', 'saved_model', 'model_metrics.json')

    # Path to sample data
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample_placement_data.csv')

    # Spark output directory
    SPARK_OUTPUT_DIR = os.path.join(BASE_DIR, 'spark', 'output')

    # Database configuration
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'college_placement_db')

    # Use SQLite if specified or fallback
    USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')
    SQLITE_DB_NAME = os.getenv('SQLITE_DB_NAME', 'placement_system.db')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # Allow direct DATABASE_URL override if present
        env_url = os.getenv('DATABASE_URL')
        if env_url:
            return env_url
        if self.USE_SQLITE:
            return f"sqlite:///{os.path.join(BASE_DIR, self.SQLITE_DB_NAME)}"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration using SQLite in-memory."""
    DEBUG = False
    TESTING = True
    USE_SQLITE = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


# Configuration mapping dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

