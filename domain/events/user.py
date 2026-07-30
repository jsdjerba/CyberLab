"""
Aggregate Root représentant un utilisateur du système CyberLab.
"""
from typing import List
from datetime import datetime
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role
from domain.events.user_registered import UserRegistered
from domain.events.user_logged_in import UserLoggedIn
from domain.events.base import BaseDomainEvent
from domain.exceptions.auth_exceptions import AuthenticationError

class User:
    def __init__(self, user_id: UserId, email: Email, password_hash: PasswordHash, role: Role, is_active: bool = True):
        self._user_id = user_id
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._is_active = is_active
        self._domain_events: List[BaseDomainEvent] = []

    @property
    def user_id(self) -> UserId: return self._user_id

    @property
    def email(self) -> Email: return self._email

    @property
    def password_hash(self) -> PasswordHash: return self._password_hash

    @property
    def role(self) -> Role: return self._role

    @property
    def is_active(self) -> bool: return self._is_active

    def collect_events(self) -> tuple[BaseDomainEvent, ...]:
        """Retourne et vide la file des événements de domaine (Pattern UoW)."""
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    @classmethod
    def register(cls, user_id: UserId, email: Email, password_hash: PasswordHash, role: Role, current_time: datetime) -> 'User':
        """Constructeur métier avec injection du temps pour un déterminisme strict."""
        user = cls(user_id, email, password_hash, role)
        user._domain_events.append(UserRegistered(
            user_id=user_id.value,
            email=email.value,
            role=role.value,
            timestamp=current_time
        ))
        return user

    def login(self, current_time: datetime) -> None:
        """Processus métier de connexion."""
        if not self._is_active:
            raise AuthenticationError("Connexion refusée : Le compte utilisateur est désactivé.")
        
        self._domain_events.append(UserLoggedIn(
            user_id=self._user_id.value,
            timestamp=current_time
        ))

    def deactivate(self) -> None:
        self._is_active = False

    def activate(self) -> None:
        self._is_active = True