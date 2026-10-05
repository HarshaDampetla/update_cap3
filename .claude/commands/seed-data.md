---
name: seed-data
description: Populate the MarketScope database with default admin, customer users, stock catalog, and sample portfolio positions.
---

# /seed-data — Populate MarketScope Baseline Data

When executed, initialize and populate the database with deterministic seed data specified in [specs/app_spec.md](file:///specs/app_spec.md):

```bash
python -m src.scripts.seed_data
```

## Seeded Baseline Entities:
1. **Admin User:** `admin@marketscope.com` / `AdminPass123!` (role: `ADMIN`, status: `ACTIVE`).
2. **Customer 1:** `trader1@marketscope.com` / `TraderPass123!` (role: `CUSTOMER`, cash: `$100,000.00`).
3. **Customer 2:** `trader2@marketscope.com` / `TraderPass123!` (role: `CUSTOMER`, cash: `$25,000.00`).
4. **10 Active Stock Equities:** `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `JPM`, `XOM`, `JNJ`, `TSLA`, `BRK.B`.
5. **Default Watchlists:** "Tech Giants" (AAPL, MSFT, NVDA).
6. **Initial Holdings:** `trader1` holding positions in AAPL, MSFT, and NVDA.
