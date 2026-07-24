# database/unit_of_work.py

from database.repository import UserRepository

class UnitOfWork:
    def __init__(self, session):
        self.session = session
        self.users = UserRepository(session) # Initialisation du repo

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()