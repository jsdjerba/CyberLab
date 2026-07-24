import os
from flask import Flask
from database.session import get_engine, initialize_session

DB_DIR = os.path.join(os.getcwd(), 'database_files')

def register_extensions(app: Flask) -> None:
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = get_engine(database_uri)
    
    # Stockage sur l'app pour accès global propre
    app.db_session = initialize_session(engine)
    app.db_engine = engine

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        app.db_session.remove()