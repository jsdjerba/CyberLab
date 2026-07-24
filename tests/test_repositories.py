import pytest
from database.models.progress import Progress as ProgressDB
from database.models.user import User as UserModel
from database.models.lab import Lab as LabModel
from domain.progress.entities.progress import Progress as DomainProgress
from repositories.sqlalchemy.progress_repository import ProgressRepository

def test_save_progress_resolves_tech_ids(session):
    # Setup infrastructure entities
    user = UserModel(domain_id="user-uuid-1", username="testuser", password_hash="x", role="STUDENT")
    lab = LabModel(lab_id="HTTP_01", title="L", category="C", difficulty="D", version="V")
    session.add_all([user, lab])
    session.flush() # Assure IDs exist

    repo = ProgressRepository(session)
    # Domain entity uses domain_id
    progress_entity = DomainProgress.start(student_id="user-uuid-1", lab_id="HTTP_01")
    repo.save(progress_entity)
    session.flush()

    db_progress = session.query(ProgressDB).filter_by(domain_id=progress_entity.progress_id).first()
    assert db_progress is not None
    assert db_progress.user_id == user.id