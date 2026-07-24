class EventBusError(Exception):
    """Exception de base pour le système d'événements."""
    pass

class HandlerNotFound(EventBusError):
    """Levée uniquement en mode strict si aucun handler n'est trouvé."""
    pass

class EventProcessingError(EventBusError):
    """
    Levée lorsqu'un handler échoue lors du traitement d'un événement.
    Masque les erreurs techniques de l'infrastructure.
    """
    def __init__(self, event_type: str, handler_name: str, cause: Exception):
        # Message neutre pour éviter de fuiter les internes (ex: SQLite errors)
        super().__init__("A technical error occurred while processing the event.")
        self.event_type = event_type
        self.handler_name = handler_name
        self.cause = cause