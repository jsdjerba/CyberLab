from application.exceptions.application_exceptions import ApplicationException

class TeamNotFoundApplicationException(ApplicationException):
    """Levée lorsque l'équipe ciblée par une commande n'existe pas en base."""
    pass