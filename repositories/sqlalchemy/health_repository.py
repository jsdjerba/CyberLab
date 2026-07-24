from sqlalchemy import text
from sqlalchemy.orm import Session

class HealthRepository:
    def __init__(self, session: Session):
        self.session = session

    def ping(self) -> bool:
        try:
            # Executes a lightweight query to verify DB responsiveness
            self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False