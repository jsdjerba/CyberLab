# database/repository.py

from database.models import User

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_username(self, username: str):
        return self.session.query(User).filter_by(username=username).first()

    def create(self, user: User):
        self.session.add(user)