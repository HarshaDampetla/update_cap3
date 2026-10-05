import ast
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"


@pytest.mark.nfr("NFR-08")
def test_domain_layer_has_zero_forbidden_imports():
    """NFR-08: Domain layer must not import from framework, db, or higher layers."""
    domain_dir = SRC_DIR / "domain"
    forbidden_modules = {"fastapi", "starlette", "sqlalchemy", "requests", "src.repositories", "src.services", "src.controllers"}

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_modules:
                        assert not alias.name.startswith(forbidden), (
                            f"Domain layer violation in {py_file.name}: imports '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_modules:
                        assert not node.module.startswith(forbidden), (
                            f"Domain layer violation in {py_file.name}: imports from '{node.module}'"
                        )


@pytest.mark.nfr("NFR-08")
def test_controllers_do_not_import_repositories_directly():
    """NFR-08: Controllers must never import repositories directly (route through services only)."""
    controllers_dir = SRC_DIR / "controllers"

    for py_file in controllers_dir.glob("*.py"):
        if py_file.name == "deps.py":
            continue  # deps.py acts as composition root/dependency injection provider
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "src.repositories" not in alias.name, (
                        f"Controller layer violation in {py_file.name}: imports '{alias.name}' directly"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "src.repositories" not in node.module, (
                        f"Controller layer violation in {py_file.name}: imports from '{node.module}' directly"
                    )
