"""
Module de base pour les exceptions du domaine CyberLab.
"""

class BaseDomainException(Exception):
    """
    Exception racine pour l'ensemble du domaine CyberLab.
    Toute erreur métier doit hériter de cette classe.
    """
    pass