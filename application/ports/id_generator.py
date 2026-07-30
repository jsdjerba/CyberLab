"""
Port applicatif pour la génération d'identifiants uniques (Clean Architecture).
Abreuve les Use Cases en identifiants sans imposer de couplage à un UUID natif ou à la DB.
"""
from typing import Protocol


class IdGenerator(Protocol):
    def generate(self) -> str:
        ...