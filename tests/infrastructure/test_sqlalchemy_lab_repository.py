import pytest
from domain.labs.value_objects.lab_id import LabId
from domain.labs.entities.lab import Lab
from infrastructure.repositories.sqlalchemy_lab_repository import SqlAlchemyLabRepository
from database.models.lab import Lab as LabModel

class FakeQuery:
    def __init__(self, result=None):
        self._result = result
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self._result

class FakeSession:
    def __init__(self, lab_model=None):
        self._lab_model = lab_model
    def query(self, model):
        return FakeQuery(self._lab_model)

def test_sqlalchemy_lab_repository_get_by_id_found():
    # Arrange : Création d'un modèle ORM avec les champs exacts confirmés
    orm_lab = LabModel(
        id=1,
        lab_id="L1",
        title="Cyber Security 101",
        category="Security",
        difficulty="Easy",
        version="1.0",
        is_active=True
    )
    session = FakeSession(orm_lab)
    repo = SqlAlchemyLabRepository(session)

    # Act
    domain_lab = repo.get_by_id(LabId("L1"))

    # Assert
    assert domain_lab is not None
    assert isinstance(domain_lab, Lab)
    assert domain_lab.id.value == "L1"
    assert domain_lab.title == "Cyber Security 101"

def test_sqlalchemy_lab_repository_get_by_id_not_found():
    session = FakeSession(None)
    repo = SqlAlchemyLabRepository(session)

    domain_lab = repo.get_by_id(LabId("UNKNOWN"))

    assert domain_lab is None