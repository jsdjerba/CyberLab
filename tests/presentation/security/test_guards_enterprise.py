import pytest
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base

# --- IMPORTS OBLIGATOIRES POUR LA CREATION DES TABLES SQLITE EN MEMOIRE ---
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.audit_model import AuditEventModel

from infrastructure.container import ApplicationContainer
from domain.value_objects.role import Role
from domain.value_objects.permission import Permission
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from presentation.security.guards import jwt_required, require_role, require_permission
from presentation.security.current_user import current_user
from presentation.error_handlers.api_exception_handler import register_api_error_handlers
from datetime import datetime, timezone

@pytest.fixture
def enterprise_app():
    app = Flask(__name__)
    engine = create_engine("sqlite:///:memory:")
    
    # La création des tables fonctionnera grâce aux imports des modèles ci-dessus
    Base.metadata.create_all(engine)
    
    session = sessionmaker(bind=engine)()
    app.container = ApplicationContainer(session=session)
    register_api_error_handlers(app)

    # Création d'utilisateurs de test
    repo = app.container._user_repository
    
    # Utilisation de User.create ou User.register selon votre implémentation
    teacher = User.create(UserId("u-prof"), Email("prof@lab.edu"), PasswordHash("hash"), Role.TEACHER, current_time=datetime.now(timezone.utc))
    student = User.create(UserId("u-stud"), Email("stud@lab.edu"), PasswordHash("hash"), Role.STUDENT, current_time=datetime.now(timezone.utc))
    deactivated = User.create(UserId("u-bad"), Email("bad@lab.edu"), PasswordHash("hash"), Role.STUDENT, current_time=datetime.now(timezone.utc))
    deactivated.deactivate()
    
    repo.save(teacher)
    repo.save(student)
    repo.save(deactivated)
    
    # --- COMMIT OBLIGATOIRE ---
    # Sauvegarde réellement les utilisateurs dans le SQLite en mémoire
    session.commit()

    @app.route("/api/secure", methods=["GET"])
    @jwt_required
    def secure_endpoint():
        return jsonify({"user": current_user.id, "perms": current_user.permissions}), 200

    @app.route("/api/admin-only", methods=["GET"])
    @jwt_required
    @require_role(Role.ADMIN)
    def admin_endpoint(): 
        return jsonify({"ok": True})

    @app.route("/api/create-lab", methods=["POST"])
    @jwt_required
    @require_permission(Permission.CREATE_LAB)
    def create_lab_endpoint(): 
        return jsonify({"ok": True})

    # Catch-all pour faciliter le debuggage au cas où une autre erreur 500 surviendrait
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

    with app.test_client() as client:
        yield client, app.container


def test_stateless_instant_revocation(enterprise_app):
    client, container = enterprise_app
    token = container._token_provider.create_token("u-bad", "STUDENT")
    
    # Le token est valide mathématiquement, mais l'utilisateur est inactif en BDD
    response = client.get("/api/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "révoqué" in response.get_json().get("message", "")

def test_permission_guard_allows_teacher_to_create_lab(enterprise_app):
    client, container = enterprise_app
    token = container._token_provider.create_token("u-prof", "TEACHER")
    
    response = client.post("/api/create-lab", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_permission_guard_denies_student_to_create_lab(enterprise_app):
    client, container = enterprise_app
    token = container._token_provider.create_token("u-stud", "STUDENT")
    
    response = client.post("/api/create-lab", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Permission refusée" in response.get_json().get("message", "")

def test_jwt_malformed_returns_401(enterprise_app):
    client, _ = enterprise_app
    response = client.get("/api/secure", headers={"Authorization": "TokenInvalidFormat"})
    assert response.status_code == 401
    assert "Format" in response.get_json().get("message", "")