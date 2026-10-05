# Testing Suite Instructions (`tests/`)

This directory houses the comprehensive verification substrate for MarketScope.

---

## 1. Test Directory Structure
```
tests/
├── architecture/          # Structural tests enforcing clean layering & role boundaries (NFR-08)
│   ├── test_layer_dependencies.py
│   ├── test_role_boundaries.py
│   └── test_order_immutability.py
├── unit/
│   ├── domain/            # Pure unit tests for entities, policies & Decimal math
│   │   ├── test_order_validation_policy.py    (AC-08)
│   │   ├── test_order_lifecycle.py            (AC-07)
│   │   ├── test_portfolio_pnl_policy.py       (AC-09)
│   │   ├── test_gainer_loser_policy.py        (AC-10)
│   │   └── test_watchlist_limit_policy.py     (AC-04)
│   ├── services/          # Business use cases, transaction rollback & mocks
│   │   ├── test_watchlist_atomicity.py        (AC-05)
│   │   ├── test_stock_catalog_service.py      (AC-03)
│   │   └── test_user_service.py               (AC-01, AC-02)
│   └── controllers/       # HTTP status codes & authentication guards
└── e2e/                   # Playwright UI browser interaction tests
    ├── test_customer_trade_flow.spec.ts
    └── snapshots/         # Responsive visual regression snapshots
```

---

## 2. Test Rules & Traceability
1. **Mandatory AC Tagging:**
   - Every single test file must include `@pytest.mark.ac("AC-NN")` corresponding to the Acceptance Criteria it exercises.
   - All 10 ACs (`AC-01` through `AC-10`) must have at least one dedicated test.
2. **Red-Green-Refactor Pattern:**
   - Commit history must demonstrate the test being committed first (RED), followed by the minimal passing implementation (GREEN), followed by cleanup (REFACTOR).
3. **Coverage Artifact:**
   - Always run with `--cov=src --cov-report=xml:coverage.xml --cov-report=term-missing`.
   - Maintain minimum 80% coverage across the codebase, with 100% on domain policies.
