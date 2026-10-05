# Controller Layer Instructions (`src/controllers/`)

This directory contains the API routing endpoints, request/response validation, and authorization guards.

---

## 1. Architectural Rules
1. **Unidirectional Calls:**
   - Controllers call **Services only**. Controllers must never import Repositories or execute SQL/ORM statements.
2. **Role-Based Access Control Partitioning (NFR-04):**
   - Every route under `/api/admin/*` must include the `@require_role(UserRole.ADMIN)` dependency guard.
   - Every route under `/api/customer/*` or customer-specific endpoints must verify token identity (`current_user.id`).
   - If an unauthorized user attempts an operation, return `403 Forbidden` with standardized error JSON.
3. **Structured Request Logging (NFR-06):**
   - Read the incoming `x-correlation-id` header or generate a new UUID4.
   - Attach correlation ID to log output and return it in response headers.
4. **Exception Mapping:**
   - Catch domain exceptions (`InsufficientFundsException`, `WatchlistUpdateException`, `InvalidOrderStateException`) in global FastAPI exception handlers to yield deterministic status codes.
