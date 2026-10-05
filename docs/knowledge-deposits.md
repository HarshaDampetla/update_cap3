# Knowledge Deposit Log: MarketScope System

**Document ID:** KD-AINE-006  
**Purpose:** Continuous repository learning log capturing recurring agent mistakes, edge cases, and architectural regressions, systematically encoded back into project rules, hooks, or skills.

---

## Deposit Record 001: Floating-Point Math Leak in P&L Calculations

- **Date:** 2026-10-01
- **Symptoms / Incident:** Evaluator agent observed slight fractional discrepancy (e.g., `$149.99999999999997` instead of `$150.00`) during portfolio P&L stress testing.
- **Root Cause:** Generator agent used native Python `float` division in `(current_value - total_invested) / total_invested` instead of fixed-point `Decimal`.
- **Systemic Mitigation:**
  1. Authored `.claude/hooks/bigdecimal-enforcement-check.js` which parses Python ASTs on every file save to block any float operations in `src/domain/` and `src/services/`.
  2. Created project skill `.claude/skills/portfolio-pnl-calculator/SKILL.md` specifying exact Decimal quantization formulae.
  3. Added rule to root `CLAUDE.md` and `src/domain/CLAUDE.md`: `NFR-01: Price, quantity, and P&L values are computed in fixed-point (BigDecimal / decimal) — never floating-point`.

---

## Deposit Record 002: Role Boundary Leak on Stock Deletion Endpoint

- **Date:** 2026-10-02
- **Symptoms / Incident:** Automated security scan identified that `DELETE /api/admin/stocks/{symbol}` was missing role guard middleware, allowing authenticated `CUSTOMER` tokens to soft-delete stocks.
- **Root Cause:** Scaffolder template omitted `@require_role("ADMIN")` decorator on the DELETE method.
- **Systemic Mitigation:**
  1. Authored `.claude/hooks/role-boundary-check.js` which verifies all routes matching `/api/admin/*` explicitly declare the `@require_role("ADMIN")` decorator or middleware.
  2. Created architectural test `tests/architecture/test_role_boundaries.py` asserting that HTTP requests to any admin endpoint with customer credentials return `403 Forbidden`.
  3. Logged complete autonomous resolution in `docs/fix-loops/role-boundary-leak-fix.md`.

---

## Deposit Record 003: Accidental Hard-Delete in Stock Catalog CRUD

- **Date:** 2026-10-02
- **Symptoms / Incident:** Generator agent initially implemented stock deletion via `session.delete(stock)` in database repository.
- **Root Cause:** Failure to respect `AC-03: Stock catalog supports full CRUD for ADMIN role; soft-delete moves a symbol to DELETED status — symbols are never hard-deleted`.
- **Systemic Mitigation:**
  1. Added repository-level constraint intercepting delete operations on the `Stock` entity and converting them into updates: `stock.status = StockStatus.DELETED`.
  2. Wrote unit test `test_stock_catalog_soft_delete_preserves_row_with_deleted_status` tagged with `AC-03`.
  3. Updated `specs/stock_catalog_spec.md` with explicit database query verification instructions.

---

## Deposit Record 004: Partial Failure in Multi-Symbol Watchlist Updates

- **Date:** 2026-10-03
- **Symptoms / Incident:** When adding three symbols to a watchlist where the third symbol was invalid, the first two symbols were persisted while the third was omitted, silently violating atomic update expectations.
- **Root Cause:** Service added symbols iteratively in a loop without enclosing the batch in a database transaction block.
- **Systemic Mitigation:**
  1. Enforced strict atomic transaction boundary in `WatchlistService`: if any symbol validation fails, entire batch rolls back and raises `WatchlistUpdateException` (`AC-05`).
  2. Created skill `.claude/skills/watchlist-validator/SKILL.md` detailing atomic batch validation procedures.
  3. Wrote dedicated test `test_watchlist_update_atomic_rollback_on_single_invalid_symbol` tagged with `AC-05`.
