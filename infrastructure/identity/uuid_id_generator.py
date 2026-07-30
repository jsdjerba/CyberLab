"""
Adaptateur d'infrastructure pour la génération d'ID.
"""
import uuid
from application.ports.id_generator import IdGenerator

class UuidIdGenerator(IdGenerator):
    """Implémente la génération d'identifiants uniques via UUIDv4."""
    
    def generate(self) -> str:
        return f"u-{uuid.uuid4().hex[:12]}"