class RepositoryException(Exception):
    """Classe de base pour toutes les exceptions liées à la couche de persistance (Repositories)."""
    pass

class DuplicateEnrollmentException(RepositoryException):
    """Levée lorsqu'un utilisateur tente de rejoindre une classe dans laquelle il est déjà inscrit."""
    pass

class DuplicateLabProgressException(RepositoryException):
    """Levée lors d'une tentative de création d'un suivi de progression en double pour un même Lab."""
    pass

class DuplicateAchievementException(RepositoryException):
    """Levée lors de l'attribution d'un badge (Achievement) qu'un utilisateur possède déjà."""
    pass

class DatabaseException(RepositoryException):
    """Levée pour les erreurs générales de base de données (ex: OperationalError de SQLAlchemy)."""
    pass