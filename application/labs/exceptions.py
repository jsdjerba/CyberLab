class LabApplicationError(Exception):
    """Exception de base pour les erreurs applicatives des labs."""
    pass

class LabNotFoundError(LabApplicationError):
    """Levée lorsqu'un laboratoire n'est pas trouvé dans le repository."""
    pass


class LabInstanceNotFoundError(LabApplicationError):
    """Levée lorsqu'aucune progression n'est trouvée pour l'étudiant et le lab."""
    pass