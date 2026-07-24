
"""
Architecture Fitness Function.
Uses AST parsing to statically forbid forbidden imports inside domain/ and services/.
Enforces Clean Architecture dependency rule: Domain has zero knowledge of infrastructure.
"""
import ast
import os
import pytest

FORBIDDEN_MODULES = (
    "flask",
    "sqlalchemy",
    "database.models",
    "repositories",
    "infrastructure",
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROTECTED_DIRS = (
    os.path.join(PROJECT_ROOT, "domain"),
    os.path.join(PROJECT_ROOT, "services"),
)


def _iter_python_files(directory: str):
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


def _imported_modules(filepath: str) -> set[str]:
    with open(filepath, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=filepath)

    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
    return modules


def _violates(module_name: str) -> str | None:
    for forbidden in FORBIDDEN_MODULES:
        if module_name == forbidden or module_name.startswith(forbidden + "."):
            return forbidden
    return None


def _collect_violations(directory: str) -> list[tuple[str, str, str]]:
    violations = []
    for filepath in _iter_python_files(directory):
        for module in _imported_modules(filepath):
            hit = _violates(module)
            if hit:
                violations.append((filepath, module, hit))
    return violations


@pytest.mark.parametrize("protected_dir", PROTECTED_DIRS)
def test_no_forbidden_imports_in_protected_layers(protected_dir):
    violations = _collect_violations(protected_dir)
    assert violations == [], (
        f"Clean Architecture violation(s) detected: {violations}. "
        f"domain/ and services/ must never import Flask, SQLAlchemy, "
        f"database.models, repositories implementations or infrastructure."
    )


def test_services_interfaces_are_protocols_not_implementations():
    interfaces_dir = os.path.join(PROJECT_ROOT, "services", "interfaces")
    for filepath in _iter_python_files(interfaces_dir):
        modules = _imported_modules(filepath)
        assert "sqlalchemy" not in modules
        assert "flask" not in modules
