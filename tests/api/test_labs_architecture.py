import ast
from pathlib import Path

def test_labs_api_architecture():
    filepath = Path("api/v1/labs_api.py")
    banned = ["sqlalchemy", "repository", "database", "models", "infrastructure"]
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for n in (node.names if isinstance(node, ast.Import) else [node.module]):
                name = n.name if hasattr(n, 'name') else n
                assert not any(b in name for b in banned), f"Violation in {name}"