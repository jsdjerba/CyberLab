from database.models import User

class UserMapper:
    @staticmethod
    def to_model(username, password_hash, role):
        # Vérifie si role est une instance d'Enum ou une chaîne, 
        # puis normalise en majuscules pour correspondre à UserRole
        role_value = role.value if hasattr(role, 'value') else str(role).upper()
        return User(username=username, password_hash=password_hash, role=role_value)

    @staticmethod
    def to_dto(user_model):
        from domain.dto.user_dto import UserDTO
        return UserDTO(
            id=user_model.id,
            username=user_model.username,
            role=user_model.role,
            xp=getattr(user_model, 'xp', 0)
        )