# Business Case: MarketScope — Stock Trading & Portfolio Analytics Platform

**Document ID:** BC-AINE-006  
**Domain:** FinTech — Capital Markets / Retail Brokerage  
**Project:** MarketScope Self-Serve Trading Platform  
**Target Audience:** Virtusa Reviewer Plugin, Lead System Architects, Autonomous Claude Code Agents  

---

## 1. Executive Summary & Problem Definition

### 1.1 The Problem
In modern retail capital markets, retail investors demand an intuitive, transparent, and responsive self-serve brokerage platform that delivers instant market execution, auditable order handling, and real-time portfolio analytics. Legacy retail brokerage platforms suffer from fragmented user onboarding, brittle order-state management, opaque error responses, and batch-delayed portfolio calculations that rely on floating-point arithmetic prone to rounding errors.

MarketScope addresses these challenges by delivering an enterprise-grade, self-serve trading and portfolio analytics engine designed from first principles with:
1. Strict deterministic financial computing (zero floating-point tolerance via fixed-point decimal arithmetic).
2. Explicit, non-bypassable state machines governing the complete trade order lifecycle.
3. Partitioned role-based access control protecting administrative stock catalog administration from retail accounts.
4. Guaranteed atomic operations on user watchlists.
5. Append-only, immutable audit journals for all executed trades and administrative role modifications.

### 1.2 The AI-Native Mandate
MarketScope is engineered under a zero-hand-coding constraint. Every line of application code, persistence schema, unit test, architectural constraint check, and end-to-end user verification is generated and maintained exclusively by Claude Code autonomous agents operating under strict specifications and harness guardrails.

---

## 2. Target User Personas

| Persona | Role Identifier | Needs & Key Workflows | Security & Operational Boundaries |
| :--- | :--- | :--- | :--- |
| **Retail Investor** | `CUSTOMER` | • Self-onboard with email and strong credentials.<br>• Search stocks by ticker, sector, or exchange.<br>• Create and curate up to 10 atomic watchlists.<br>• Place and cancel BUY/SELL market and limit orders.<br>• Review real-time portfolio P&L, holdings, and top daily movers. | Strictly restricted from administrative endpoints; cannot manipulate executed orders, alter stock catalog listings, or exceed available cash. |
| **Brokerage Administrator** | `ADMIN` | • Manage global stock catalog (create, update, soft-delete symbols).<br>• Supervise user account states (ACTIVE, SUSPENDED).<br>• Audit order queues, settlement buffers, and platform-wide volume. | Subject to mandatory actor-and-timestamp audit logging on all state-altering operations; cannot delete executed trades. |
| **Suspended Account** | `SUSPENDED` | • Read-only access to historical tax and trade statements (if permitted).<br>• Blocked from placing new orders, modifying watchlists, or executing trades. | Handled deterministically at authentication and controller boundary layers. |

---

## 3. Core Value Proposition

MarketScope provides a high-reliability, self-serve trading experience characterized by:
- **Financial Determinism:** Eliminates rounding anomalies and balance discrepancies through mandatory `Decimal` (fixed-point) mathematics across all valuations, commissions, and P&L calculations.
- **Auditable Integrity:** Complete immutability of historical trade logs and administrative privilege escalations.
- **Resilient Concurrency:** Atomic watchlist mutation semantics that guarantee no partial state leaks during multi-symbol updates.
- **Instant Decision Intelligence:** Automated computation of customer-specific daily top 5 gainers and losers alongside aggregate portfolio P&L metrics.
- **Production-Ready AI Harness:** Engineered with formal specifications acting as the single source of truth (`Spec-Is-Truth`), backed by pre-commit verification gates and automated evaluators.

---

## 4. Key Success Metrics & KPIs

| Metric Category | Target KPI | Measurement Mechanism |
| :--- | :--- | :--- |
| **Financial Accuracy** | 100% fixed-point precision; 0 floating-point leaks | Static analysis and custom pre-commit AST scanner (`bigdecimal-enforcement-check`) |
| **Order Safety** | 0 illegal order state transitions; 100% rejection of unfunded BUYs | State machine enforcement unit and architectural tests |
| **Role Boundary Isolation**| 0 unauthorized accesses from `CUSTOMER` to `ADMIN` routes | Architecture test suite (`test_role_boundaries`) verifying 403 Forbidden |
| **Atomic Operations** | 100% rollback on partial watchlist symbol failures | Transactional boundary tests raising `WatchlistUpdateException` |
| **System Responsiveness** | Health check response < 1.0s at startup (`NFR-07`) | Continuous HTTP probe during boot cycle |
| **Test Quality** | >= 20 unit tests, 100% AC-NN test traceability, >= 80% code coverage | CI pipeline coverage report (`coverage.xml` / `lcov.info`) |

---

## 5. Domain Rules & Invariant Constraints

1. **Role State & Transition Invariants:**
   - Registration creates accounts in `ACTIVE` state with `role = CUSTOMER` (`AC-01`).
   - Only users with `ADMIN` role can alter user roles or account states (`AC-02`).
   - All role modifications generate immutable audit entries capturing `target_user_id`, `actor_admin_id`, `previous_role`, `new_role`, and `timestamp`.
2. **Catalog Invariants:**
   - Stock symbols are unique, uppercase strings (e.g., `AAPL`, `MSFT`, `GOOGL`).
   - Soft-delete only (`AC-03`): Deleting a stock marks status as `DELETED` / `DELISTED`. Hard deletes (`DELETE FROM stocks`) are forbidden.
3. **Watchlist Constraints:**
   - Maximum 10 watchlists per customer (`AC-04`).
   - A watchlist must contain a non-empty name and at least one stock symbol upon creation.
   - All mutations (rename, adding symbols, removing symbols) are all-or-nothing transactions; invalid symbols abort the entire transaction and raise `WatchlistUpdateException` (`AC-05`).
4. **Order Execution & Balance Invariants:**
   - BUY orders validate `available_cash >= quote_price * quantity`. If insufficient, immediately raise `InsufficientFundsException` (`AC-08`).
   - Orders begin in `PENDING` state with server-generated UTC timestamps (`AC-06`).
   - Transitions strictly follow the directed graph: `PENDING` -> `EXECUTED` | `CANCELLED` | `REJECTED`. Any other transition or mutation on terminal states raises `InvalidOrderStateException` (`AC-07`).
   - Executed orders and trade records are append-only (`NFR-02`).
5. **Portfolio & Analytics Rules:**
   - `total_invested = sum(shares_held * average_buy_price)`.
   - `current_value = sum(shares_held * current_market_price)`.
   - `absolute_pnl = current_value - total_invested`.
   - `percent_pnl = (absolute_pnl / total_invested) * 100` (or `0.00` if `total_invested == 0`).
   - Top 5 gainers and losers are evaluated strictly over the requesting customer's current active holdings based on daily price movement (`AC-10`).
