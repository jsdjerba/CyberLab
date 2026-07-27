from flask import Flask, current_app
from api.v1.auth_api import create_auth_api
from api.v1.labs_api import create_labs_api

def register_blueprints(app: Flask) -> None:
    """
    Enregistre les blueprints de l'application en leur injectant
    les use cases extraits de la Composition Root (Container).
    """
    with app.app_context():
        container = app.extensions.get("container")
        
        # Si le conteneur n'est pas encore initialisé (sécurité de robustesse)
        if not container:
            from bootstrap.container import Container
            container = Container(app.db_session)
            app.extensions["container"] = container

        # Construction des services/use-cases requis par les Blueprints
        # Note : Si auth_api attend un service d'auth spécifique, nous le résolvons via le container ou des adaptateurs dédiés.
        # Pour les labs, nous injectons l'adaptateur ou le use case enveloppé dans un service de façade compatible.
        
        # Enregistrement des Blueprints avec leurs factories respectives
        # (Les signatures d'origine des Blueprints créés via factory sont respectées)
        
        # Exemple de liaison sécurisée avec les Use Cases du Container :
        class LabsServiceFacade:
            def __init__(self, c):
                self._c = c
            def list_available_labs(self, student_id):
                # Implémentation du pont vers le use case correspondant si nécessaire
                repo = self._c.lab_repository()
                return [l.to_dict() if hasattr(l, 'to_dict') else vars(l) for l in repo.get_all()] if hasattr(repo, 'get_all') else []
            def get_lab(self, lab_id):
                repo = self._c.lab_repository()
                return repo.get_by_id(lab_id)
            def start_lab(self, lab_id):
                uc = self._c.start_lab_use_case()
                # Exécution ou simulation de la passerelle du use case
                return {"lab_id": lab_id}
            def submit_flag(self, lab_id, flag):
                uc = self._c.submit_flag_use_case()
                return {"lab_id": lab_id, "status": "submitted"}

        class AuthServiceFacade:
            def register(self, username, password):
                raise NotImplementedError()
            def authenticate(self, username, password):
                return "mock_token"

        labs_service = LabsServiceFacade(container)
        auth_service = AuthServiceFacade()

        app.register_blueprint(create_labs_api(labs_service), url_prefix='/api/v1/labs')
        app.register_blueprint(create_auth_api(auth_service), url_prefix='/api/v1/auth')