---
name: verify-ac
description: Run the automated test suite filtered by Acceptance Criteria tags (AC-01 through AC-10) and generate a compliance report.
---

# /verify-ac — Verify All Acceptance Criteria

Executes all automated tests mapped to Acceptance Criteria (`AC-01` through `AC-10`):

```bash
pytest tests/ -v -m "ac" --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml
```

## Traceability Check
- `AC-01`: Registration and default `ACTIVE` status (`tests/unit/domain/test_user_registration.py`)
- `AC-02`: Admin role update and audit log (`tests/unit/services/test_admin_role_audit.py`)
- `AC-03`: Stock CRUD and soft-delete verification (`tests/unit/services/test_stock_catalog_crud.py`)
- `AC-04`: Watchlist creation and 10-watchlist quota (`tests/unit/services/test_watchlist_limit.py`)
- `AC-05`: Atomic watchlist operations (`tests/unit/services/test_watchlist_atomicity.py`)
- `AC-06`: Order placement and `PENDING` timestamp (`tests/unit/services/test_order_placement.py`)
- `AC-07`: State machine lifecycle transitions (`tests/unit/domain/test_order_lifecycle.py`)
- `AC-08`: Insufficient funds rejection on BUY (`tests/unit/domain/test_order_validation_policy.py`)
- `AC-09`: Portfolio valuation & P&L statistics (`tests/unit/domain/test_portfolio_pnl_policy.py`)
- `AC-10`: Daily top 5 gainers and losers (`tests/unit/domain/test_gainer_loser_policy.py`)
