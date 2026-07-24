import ast
from pathlib import Path

def get_imports(filepath):
    imports = set()
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    return imports

def test_api_layer_dependencies():
    banned_modules = {"sqlalchemy", "database", "infrastructure", "repositories"}
    api_dir = Path("api")
    
    if not api_dir.exists():
        return
        
    for py_file in api_dir.rglob("*.py"):
        file_imports = get_imports(py_file)
        
        for banned in banned_modules:
            assert banned not in file_imports, (
                f"CLEAN ARCHITECTURE VIOLATION: {py_file} imports '{banned}'. "
                "The API layer must not know about data access or ORM."
            )