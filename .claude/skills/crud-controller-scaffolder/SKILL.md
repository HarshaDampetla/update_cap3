---
name: crud-controller-scaffolder
description: Patterns for scaffolding FastAPI routers with role-based auth guards, Pydantic DTOs, correlation IDs, and domain error mapping.
---

# CRUD Controller Scaffolder Skill

This skill provides templates and conventions for generating robust, role-partitioned controllers.

---

## 1. Controller Template (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
import uuid
from src.controllers.auth_guards import get_current_user, require_role
from src.domain.entities.user import User, UserRole

router = APIRouter(prefix="/api/admin/stocks", tags=["Admin Stocks"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_stock(
    payload: CreateStockDTO,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    x_correlation_id: Optional[str] = Header(None),
    service: StockService = Depends()
):
    correlation_id = x_correlation_id or str(uuid.uuid4())
    logger.info("Stock creation initiated", extra={"correlation_id": correlation_id, "actor": current_admin.id})
    return await service.create_stock(payload, actor_id=current_admin.id)
```

---

## 2. Invariants Checklist
- [ ] Explicit prefix matching `/api/admin/*` or `/api/customer/*`.
- [ ] Dependencies enforce `require_role(UserRole.ADMIN)` on administrative operations.
- [ ] No direct repository imports or raw SQL executions.
- [ ] Exceptions caught and translated into structured JSON responses.
