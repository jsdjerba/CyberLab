import pytest
from sqlalchemy import inspect
from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.models import Base, TeamModel, TeamMemberModel

@pytest.fixture
def inspector(tmp_path):
    # Utilisation d'un vrai fichier temporaire au lieu de :memory: pour contrer l'amnésie du NullPool
    db_path = tmp_path / "test_schema.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    
    # Crée les tables (ferme la connexion, mais le fichier persiste sur disque)
    Base.metadata.create_all(engine)
    
    # Inspecte le fichier existant
    return inspect(engine)

def test_team_table_exists(inspector):
    tables = inspector.get_table_names()
    assert "teams" in tables

def test_team_members_table_exists(inspector):
    tables = inspector.get_table_names()
    assert "team_members" in tables

def test_team_score_has_default_zero(inspector):
    columns = inspector.get_columns("teams")
    score_col = next(col for col in columns if col["name"] == "score")
    
    # SQLite renvoie souvent les valeurs par défaut sous forme de littéraux SQL (avec ou sans guillemets)
    assert score_col["default"] in ("0", "'0'"), "Le score doit avoir une valeur par défaut de 0 en base"

def test_foreign_key_cascade_is_defined(inspector):
    fks = inspector.get_foreign_keys("team_members")
    assert len(fks) >= 1
    
    team_fk = next(fk for fk in fks if fk["referred_table"] == "teams")
    assert "options" in team_fk
    assert team_fk["options"].get("ondelete") == "CASCADE"

def test_team_member_unique_constraint_exists(inspector):
    uniques = inspector.get_unique_constraints("team_members")
    has_composite_unique = any(
        "team_id" in u["column_names"] and "student_id" in u["column_names"] 
        for u in uniques
    )
    assert has_composite_unique is True