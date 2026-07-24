import pytest
from pathlib import Path

def get_file_content(filepath: str) -> str:
    path = Path(__file__).parent.parent / filepath
    if not path.exists():
        pytest.fail(f"File {filepath} does not exist.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_api_health_is_clean():
    """Verify the API layer contains no database access logic."""
    content = get_file_content("api/health.py")
    assert "sqlalchemy" not in content, "api/health.py MUST NOT import sqlalchemy."
    assert "Session" not in content, "api/health.py MUST NOT import Session."
    assert "text(" not in content, "api/health.py MUST NOT use raw SQL text()."
    assert "execute(" not in content, "api/health.py MUST NOT execute DB queries directly."



def test_health_repository_encapsulation():
    """Verify the Repository is the sole owner of the SQL execution."""
    content = get_file_content("repositories/sqlalchemy/health_repository.py")
    assert "text" in content, "HealthRepository MUST encapsulate the raw text() SQL execution."