"""
Modèle SQLAlchemy (ORM) de la table utilisateurs.
Strictement confiné à l'infrastructure.
"""
from sqlalchemy import Column, String, Boolean
from infrastructure.database import Base # Supposant que votre Base déclarative s'y trouve

class UserModel(Base):
    __tablename__ = "auth_users"
    
    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)