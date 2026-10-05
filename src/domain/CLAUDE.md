# Domain Layer Instructions (`src/domain/`)

This directory houses the pure enterprise business rules, entities, value objects, and domain policies.

---

## 1. Cardinal Domain Rules
1. **Zero External Dependencies:**
   - No imports from `fastapi`, `starlette`, `sqlalchemy`, `requests`, or any database drivers.
   - Standard library (`decimal`, `datetime`, `enum`, `typing`, `dataclasses`) and `pydantic` only.
2. **Fixed-Point Arithmetic (NFR-01):**
   - Strictly prohibit Python `float`. Every price, quantity, valuation, and return percentage MUST use `decimal.Decimal`.
3. **Immutability of Executed Orders (NFR-02):**
   - Entities representing completed trades (`TradeExecution`, terminal `Order`) must be frozen / read-only.
4. **Mandatory Policy Files (BC-AINE-006 Rubric Section 7.2):**
   - At least 4 rule / policy / validator files must reside here:
     1. `src/domain/policies/order_validation_policy.py`: Enforces funds availability (`AC-08`), side, and order pricing.
     2. `src/domain/policies/order_lifecycle_policy.py`: Enforces finite state machine transitions (`AC-07`).
     3. `src/domain/policies/portfolio_pnl_policy.py`: Enforces fixed-point P&L formulas and zero-division handling (`AC-09`).
     4. `src/domain/policies/watchlist_limit_policy.py`: Enforces 10-watchlist limit and non-empty symbols (`AC-04`).
     5. `src/domain/policies/gainer_loser_policy.py`: Enforces gainer/loser sorting over active holdings (`AC-10`).
