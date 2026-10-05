# Sprint Contract 01: Core Identity, Security & Stock Catalog

**Sprint ID:** SPRINT-01  
**Target Capabilities:** User Onboarding, RBAC Security, Stock Catalog Scaffolding  
**Participating Agents:** `planner`, `generator`, `evaluator`, `security-reviewer`, `test-engineer`  
**Target Invariants:** `AC-01`, `AC-02`, `AC-03`, `NFR-03`, `NFR-04`, `NFR-07`  
**Status:** NEGOTIATED & LOCKED  

---

## 1. Scope & Deliverables

1. **User Identity & Roles:**
   - Registration endpoint (`POST /api/auth/register`) creating `ACTIVE` user with `role = CUSTOMER` (`AC-01`).
   - Bcrypt credential hashing (`NFR-03`) with zero plaintext credential logging.
   - Admin role transition endpoint (`PATCH /api/admin/users/{id}/role`) with immutable audit logging (`AC-02`).
   - JWT authentication and controller-layer role partitioning (`NFR-04`).
2. **Stock Catalog CRUD:**
   - Admin stock management endpoints (`POST`, `PUT`, `DELETE /api/admin/stocks`) (`AC-03`).
   - Repository-enforced soft-delete invariant: symbol transitions to `DELETED` state and is never hard-deleted (`AC-03`).
   - Public stock discovery search (`GET /api/stocks`) filtered by symbol, sector, and exchange.
3. **Infrastructure & Diagnostics:**
   - Health check endpoint (`GET /health`) responding HTTP 200 within 1 second (`NFR-07`).
   - Database migrations for `users`, `user_role_audit_logs`, and `stocks`.

---

## 2. Negotiated Acceptance Gates (Generator <-> Evaluator)

| Gate ID | Condition to Pass | Verification Method |
| :--- | :--- | :--- |
| **GATE-1: TDD Unit** | Minimum 12 unit tests passing; all tests tagged with `AC-01`, `AC-02`, or `AC-03`. | `pytest tests/unit/ -v` |
| **GATE-2: Security** | Passwords hashed with bcrypt; role boundary test verifies `CUSTOMER` receives 403 on `/api/admin/*`. | Security reviewer agent audit |
| **GATE-3: Immutability**| Database test verifies soft-deleted stock remains in database table with status `DELETED`. | `pytest tests/unit/repositories/test_stock_soft_delete.py` |
| **GATE-4: Health Check**| Health check returns 200 in $< 500\text{ms}$. | HTTP probe |
| **GATE-5: Coverage** | Backend code coverage $\ge 85\%$. | `pytest --cov=src --cov-report=xml` |

---

## 3. Ratchet Sign-Off

- **Generator Agent Signature:** Approved (Implementation Plan Locked)
- **Evaluator Agent Signature:** Approved (Verification Criteria Strict & Testable)
