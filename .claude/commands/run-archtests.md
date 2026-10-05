---
name: run-archtests
description: Run automated structural architecture tests enforcing unidirectional layers, role boundary isolation, and immutability.
---

# /run-archtests — Architecture Constraint Suite

Executes all structural architecture tests (`NFR-08`):

```bash
pytest tests/architecture/ -v
```

## Enforced Invariants:
1. **Layer Dependency Rules:** Controllers $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ Domain.
2. **Domain Isolation:** Zero web framework or database imports in `src/domain/`.
3. **Role Partitioning:** All `/api/admin/*` endpoints reject non-admin users with 403 (`NFR-04`).
4. **Execution Immutability:** Trade records and executed orders have no update or delete paths (`NFR-02`).
5. **Decimal Precision Guard:** Rejects code with floating-point calculations in financial paths (`NFR-01`).
