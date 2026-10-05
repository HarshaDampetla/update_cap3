# Backend Module Instructions (FastAPI / Python)

This document governs all backend code generation under `backend/` and `src/`.

---

## 1. Architectural Guardrails
- **Dependency Flow:** Controllers $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ Domain.
- Controllers MUST NEVER import database models or access SQLite sessions directly.
- Repositories MUST encapsulate all SQLAlchemy queries and handle soft-deletion filters (`status != 'DELETED'`).
- Domain logic must remain framework-agnostic.

---

## 2. Mandatory Coding Conventions
- **Fixed-Point Arithmetic (NFR-01):**
  - Always use `from decimal import Decimal, ROUND_HALF_UP`.
  - All currency and P&L fields must serialize to string representation in JSON responses to avoid browser IEEE 754 precision loss.
  - Ban Python `float` for prices, quantities, cash balances, and valuations.
- **Password Security (NFR-03):**
  - Use `passlib.context.CryptContext(schemes=["bcrypt"])`.
  - Never include raw or hashed passwords in string representations (`__repr__`, `__str__`).
- **Error Handling:**
  - Map domain exceptions to standard HTTP error DTOs:
    - `InsufficientFundsException` $\rightarrow$ `400 Bad Request` (`code: INSUFFICIENT_FUNDS`, `ac_id: AC-08`).
    - `InvalidOrderStateException` $\rightarrow$ `400 Bad Request` (`code: INVALID_ORDER_STATE`, `ac_id: AC-07`).
    - `WatchlistUpdateException` $\rightarrow$ `400 Bad Request` (`code: WATCHLIST_UPDATE_FAILED`, `ac_id: AC-05`).
- **Structured Logging (NFR-06):**
  - Every log entry must include `timestamp`, `level`, `correlation_id`, `message`, and context parameters.

---

## 3. Verification Commands
```bash
# Type check
mypy src/ --strict

# Lint
ruff check src/

# Run backend unit tests
pytest tests/unit/ -v
```
