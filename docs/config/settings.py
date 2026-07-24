import os
import logging

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'cyberlab.db')

class BaseConfig:
    """Base configuration containing settings common to all environments."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'cyberlab-offline-super-secret-key-v1')
    DEBUG = False
    TESTING = False
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'cyberlab.log')
    LOG_LEVEL = logging.INFO
    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Development environment specific configuration."""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class TestingConfig(BaseConfig):
    """Testing environment specific configuration."""
    TESTING = True
    LOG_LEVEL = logging.DEBUG
    # Use memory database for standard testing, but fallback to file if explicitly tested
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# Configuration dictionary to allow dynamic loading
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': BaseConfig
}