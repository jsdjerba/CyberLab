class ApplicationError(Exception):
    """Classe de base pour toutes les erreurs de la couche application."""
    pass

class LabNotFoundError(ApplicationError):
    """Levée lorsqu'un laboratoire est introuvable."""
    def __init__(self, lab_id: str):
        super().__init__(f"Le laboratoire avec l'identifiant '{lab_id}' est introuvable.")

class LabInstanceNotFoundError(ApplicationError):
    """Levée lorsqu'une instance de laboratoire est introuvable."""
    def __init__(self, instance_id: str):
        super().__init__(f"L'instance de laboratoire '{instance_id}' est introuvable.")

class StudentNotFoundError(ApplicationError):
    """Levée lorsqu'un étudiant est introuvable."""
    def __init__(self, student_id: str):
        super().__init__(f"L'étudiant avec l'identifiant '{student_id}' est introuvable.")