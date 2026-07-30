"""Énumération des rôles du système et de leurs permissions (Enterprise RBAC)."""
from enum import Enum
from domain.value_objects.permission import Permission

class Role(Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

    @property
    def permissions(self) -> list[Permission]:
        """Mapping strict des rôles vers leurs permissions autorisées."""
        mapping = {
            Role.ADMIN: list(Permission), # L'Admin possède toutes les permissions
            Role.TEACHER: [
                Permission.CREATE_CLASSROOM, 
                Permission.DELETE_CLASSROOM,
                Permission.CREATE_TEAM, 
                Permission.DELETE_TEAM,
                Permission.CREATE_LAB, 
                Permission.START_LAB, 
                Permission.STOP_LAB,
                Permission.VIEW_REPORTS, 
                Permission.SUBMIT_FLAG
            ],
            Role.STUDENT: [
                Permission.START_LAB, 
                Permission.STOP_LAB, 
                Permission.SUBMIT_FLAG
            ]
        }
        return mapping.get(self, [])