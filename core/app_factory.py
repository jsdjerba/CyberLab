import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from config.settings import config_by_name, BaseConfig
from core.extensions import register_extensions
from core.blueprint_loader import register_blueprints
from api.error_handlers import register_error_handlers
from bootstrap.container import Container  # Ajout de l'import du Container

def configure_logging(app: Flask) -> None:
    if app.logger.handlers:
        return
        
    log_file = app.config.get('LOG_FILE', 'logs/cyberlab.log')
    log_dir = os.path.dirname(log_file)
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    file_handler = RotatingFileHandler(log_file, maxBytes=1024000, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config.get('LOG_LEVEL', logging.INFO))
    app.logger.info('CyberLab Core Engine initialization started.')

def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    
    config_class = config_by_name.get(config_name, BaseConfig)
    app.config.from_object(config_class)
    
    configure_logging(app)
    
    register_extensions(app)
    
    # Séquence obligatoire validée de la Composition Root
    container = Container(app.db_session)
    app.extensions["container"] = container
    
    register_blueprints(app)
    register_error_handlers(app)
    
    app.logger.info('CyberLab Core Engine successfully loaded.')
    return app