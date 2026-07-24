from flask import current_app
from core.app_factory import create_app
# 1. Importe tes modèles (ajuste le chemin selon ton projet)
from database.models import Base 


print("Metadata tables:", list(Base.metadata.tables.keys()))
print("Metadata object:", Base.metadata)


def test_models_hardening():
    print("\nStarting Phase 2.2.1 Database Hardening Test...")
    app = create_app('testing')

    with app.app_context():

        print("=== DEBUG METADATA AVANT CREATE_ALL ===")
        print(list(Base.metadata.tables.keys()))
        print("======================================")

        engine = current_app.db_engine

        Base.metadata.create_all(engine)

        from sqlalchemy import inspect
        inspector = inspect(engine)

        print("=== TABLES SQLite ===")
        print(inspector.get_table_names())
        print("=====================")

        assert "lab_progress" in inspector.get_table_names()