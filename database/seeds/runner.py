from core.security.password_hasher import PasswordHasher
from database.models import User
from domain.enums.user_role import UserRole

def run_seeds(session):
    admin_password = PasswordHasher.hash_password("admin_default_pass")
    admin = User(
        username="admin",
        password_hash=admin_password,
        role=UserRole.ADMIN.value
    )
    session.add(admin)
    session.commit()