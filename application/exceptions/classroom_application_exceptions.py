"""Exceptions spécifiques à la couche Application Classroom."""

class ClassroomApplicationException(Exception):
    """Exception de base pour la couche Application."""
    pass

class ClassroomNotFoundApplicationException(ClassroomApplicationException):
    """Levée lorsqu'une salle de classe demandée est introuvable."""
    def __init__(self, classroom_id: str):
        super().__init__(f"La salle de classe avec l'ID '{classroom_id}' est introuvable.")
        self.classroom_id = classroom_id

class DatabaseLockedException(ClassroomApplicationException):
    """Exception technique transitoire pour simuler le verrouillage SQLite."""
    pass