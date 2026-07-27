import pytest
from flask import Flask
from core.app_factory import create_app
from bootstrap.container import Container

def test_create_app_registers_container():
    app = create_app('testing')
    assert "container" in app.extensions
    assert isinstance(app.extensions["container"], Container)

def test_container_uses_application_session():
    app = create_app('testing')
    container = app.extensions["container"]
    assert container._session is app.db_session

def test_no_domain_import_from_flask():
    import domain
    import sys
    # Vérifie qu'aucun module du domaine n'a importé 'flask' dans ses références globales
    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("domain") and mod is not None:
            # S'assure que 'flask' n'est pas lié dans l'espace de noms du domaine
            assert "flask" not in vars(mod), f"Le module domaine {mod_name} ne doit pas importer Flask !"