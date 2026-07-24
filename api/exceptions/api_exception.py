class APIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(APIException):
    def __init__(self, message: str = "Ressource introuvable"):
        super().__init__("NOT_FOUND", message, 404)

class UnauthorizedException(APIException):
    def __init__(self, message: str = "Accès non autorisé"):
        super().__init__("UNAUTHORIZED", message, 401)

class ValidationException(APIException):
    def __init__(self, message: str = "Données invalides"):
        super().__init__("VALIDATION_ERROR", message, 400)