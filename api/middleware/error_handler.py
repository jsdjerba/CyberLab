from api.middleware.response_builder import ResponseBuilder
from api.exceptions.api_exception import APIException

def register_error_handlers(app):
    # 1. Erreurs métier API (Priorité haute)
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        return ResponseBuilder.error(e.code, e.message, e.status_code)

    # 2. Erreurs de validation standard
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return ResponseBuilder.error("INVALID_INPUT", str(e), 400)

    # 3. Exception globale (Sécurité : ne jamais exposer le traceback)
    @app.errorhandler(Exception)
    def handle_global_exception(e):
        return ResponseBuilder.error("INTERNAL_SERVER_ERROR", "Une erreur inattendue est survenue", 500)