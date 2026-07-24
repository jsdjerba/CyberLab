import os

# Définition des chemins de base
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# AJOUT : Définition de DB_DIR requise par core/extensions.py
DB_DIR = BASE_DIR 
DB_PATH = os.path.join(DB_DIR, 'cyberlab_dev.db')

class BaseConfig:
    """Configuration de base pour l'application Flask."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'cyberlab-super-secret-key-default')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

class TestingConfig(BaseConfig):
    """Configuration pour l'environnement de test (Base de données en mémoire volatile)."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionnaire de mapping utilisé par core.app_factory
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}