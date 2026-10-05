import ast
from pathlib import Path
import pytest

DOMAIN_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "domain"


@pytest.mark.nfr("NFR-01")
def test_no_float_operations_in_domain_policies():
    """NFR-01: Prices, quantities, and P&L must be Decimal; Python float is strictly banned."""
    policy_dir = DOMAIN_DIR / "policies"

    for py_file in policy_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            # Check for float() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "float":
                    pytest.fail(f"NFR-01 violation: float() call found in {py_file.name}:{node.lineno}")
            # Check for float literal numbers
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                pytest.fail(f"NFR-01 violation: float literal '{node.value}' found in {py_file.name}:{node.lineno}")
