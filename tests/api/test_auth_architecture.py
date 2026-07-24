import ast
from pathlib import Path

def test_auth_api_architecture():
    filepath = Path("api/v1/auth_api.py")
    if not filepath.exists():
        return
        
    banned_keywords = ["sqlalchemy", "repository", "database", "models", "infrastructure"]
    
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(filepath))
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for banned in banned_keywords:
                    assert banned not in alias.name, f"CLEAN ARCHITECTURE VIOLATION: '{banned}' found in imports."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for banned in banned_keywords:
                    assert banned not in node.module, f"CLEAN ARCHITECTURE VIOLATION: '{banned}' found in from imports."