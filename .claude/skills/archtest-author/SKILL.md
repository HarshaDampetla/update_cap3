---
name: archtest-author
description: Patterns for authoring and running automated architectural constraint tests enforcing Clean Architecture layering and role isolation.
---

# Architecture Test Authoring Skill

This skill guides the creation of automated structural tests (`tests/architecture/`) that enforce Clean Architecture layering rules and security boundaries (`NFR-08`).

---

## 1. Structural Layering Rules

```
src/controllers/  --> May import src/services, src/domain
src/services/     --> May import src/repositories, src/domain
src/repositories/ --> May import src/domain, src/database
src/domain/       --> Must NOT import from controllers, services, repositories, or external frameworks
```

### Automated AST Import Verification (Python)
```python
import ast
import os
import pytest

@pytest.mark.nfr("NFR-08")
def test_domain_layer_has_no_framework_dependencies():
    domain_dir = "src/domain"
    forbidden_modules = {"fastapi", "starlette", "sqlalchemy", "requests", "src.controllers", "src.services", "src.repositories"}

    for root, _, files in os.walk(domain_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            assert alias.name not in forbidden_modules, f"Forbidden import {alias.name} in {path}"
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            assert not any(node.module.startswith(m) for m in forbidden_modules), f"Forbidden import {node.module} in {path}"
```

---

## 2. Role Boundary Verification (NFR-04)

Verify that every endpoint under `/api/admin/*` rejects non-admin users with HTTP 403 Forbidden:
```python
@pytest.mark.nfr("NFR-04")
def test_all_admin_endpoints_reject_customer(test_client, customer_token):
    admin_routes = ["/api/admin/stocks", "/api/admin/users/1/role", "/api/admin/statistics/orders"]
    headers = {"Authorization": f"Bearer {customer_token}"}
    
    for route in admin_routes:
        response = test_client.get(route, headers=headers)
        assert response.status_code == 403, f"Route {route} did not enforce role boundary for CUSTOMER"
```
