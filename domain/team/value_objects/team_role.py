from enum import Enum

class TeamRole(Enum):
    """Value Object (Enum) définissant les rôles opérationnels au sein de l'équipe."""
    CAPTAIN = "CAPTAIN"
    ATTACKER = "ATTACKER"
    DEFENDER = "DEFENDER"
    ANALYST = "ANALYST"