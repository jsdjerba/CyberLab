import inspect
import pathlib
import ast
import repositories.sqlalchemy as impl
from repositories.base_repository import BaseRepository

def test_no_commit_rollback_in_repos():
    for _, obj in inspect.getmembers(impl):
        if inspect.isclass(obj) and issubclass(obj, BaseRepository):
            source = inspect.getsource(obj)
            assert ".commit(" not in source, f"Violation: {obj.__name__} utilise commit()"
            assert ".rollback(" not in source, f"Violation: {obj.__name__} utilise rollback()"

def test_interfaces_isolation():
    for path in pathlib.Path("repositories/interfaces/").glob("*.py"):
        if path.name == "__init__.py": continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "sqlalchemy" not in node.module, f"Violation: {path.name} importe SQLAlchemy"
                assert "database.models" not in node.module, f"Violation: {path.name} importe models"