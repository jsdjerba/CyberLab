from typing import List
from application.interfaces.user_repository import IUserRepository

class GamificationService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def award_xp(self, student_id: str, amount: int) -> int:
        user = self.user_repo.get_by_domain_id(student_id)
        if not user:
            raise ValueError("Student not found")
            
        user.add_xp(amount)
        # La vérification des badges se fait dans le domaine
        user.check_achievements()
        
        self.user_repo.save(user)
        return user.xp