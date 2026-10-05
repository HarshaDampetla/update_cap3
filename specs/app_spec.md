# Master System Specification: MarketScope Platform

**Document ID:** SPEC-ROOT-001  
**Project:** MarketScope — Stock Trading & Portfolio Analytics Platform  
**Business Case ID:** BC-AINE-006  
**Domain:** FinTech — Capital Markets / Brokerage  
**Status:** Approved / Authoritative Single Source of Truth (`Spec-Is-Truth`)  

---

## 1. System Vision & Scope

MarketScope is a high-reliability, self-serve retail brokerage and portfolio analytics platform. The platform empowers retail investors to manage watchlists, place market/limit orders, and analyze portfolio performance in real time with absolute mathematical precision, while providing brokerage administrators with tools to govern stock listings, audit trade queues, and control user roles.

### 1.1 In-Scope Features
1. **User Onboarding & Identity Management:** Self-service registration, credential hashing with bcrypt, role management (`CUSTOMER`, `ADMIN`, `SUSPENDED`), and immutable administrative action auditing.
2. **Stock Catalog Administration & Search:** Full CRUD for administrators with soft-delete via `DELISTED` / `DELETED` state, and multi-attribute stock search by symbol, sector, or exchange.
3. **Atomic Watchlist Management:** Creation and customization of up to 10 watchlists per customer with atomic transactional mutations.
4. **Order Placement & Execution State Machine:** Market and limit orders (BUY / SELL), server-side timestamping, available cash verification, stub execution, and immutable post-execution trade records.
5. **Portfolio Holdings & Analytics:** Real-time valuation, average buy price, invested capital, absolute and percentage P&L computed using fixed-point Decimal arithmetic.
6. **Statistics & Performance Dashboard:** Customer-specific daily top 5 gainers and top 5 losers from current holdings, sector exposure, and system-wide order audit metrics.

### 1.2 Out-of-Scope (Strict Boundaries)
- Direct physical exchange connectivity (NYSE/NASDAQ FIX protocol) or live order matching book.
- Clearinghouse settlement infrastructure (T+1 clearing, DTCC).
- Real-time WebSocket market streaming (polled REST stub is specified).
- Margin trading, short selling, leverage, options, derivatives, futures.
- Multi-currency accounts or FX conversion.
- Third-party KYC/AML integrations (stubbed verification flag).
- Complex capital gains tax computing beyond basic realized/unrealized P&L.

---

## 2. Non-Functional Requirements & System Invariants

The platform enforces 8 architectural non-negotiables:

| ID | Invariant Requirement | Enforcement Mechanism |
| :--- | :--- | :--- |
| **NFR-01** | Price, quantity, and P&L values are computed in fixed-point (`Decimal` / `BigDecimal`) — never floating-point. | AST Pre-commit Hook (`bigdecimal-enforcement-check`) & Unit Tests |
| **NFR-02** | Trade records and executed orders are append-only — no edits or deletes post-execution. | Database triggers, repository immutability assertions |
| **NFR-03** | Passwords stored using strong KDF (`bcrypt`, work factor $\ge 12$). Plaintext credentials never logged or returned. | Controller DTO sanitizer & Auth Guard Hook (`password-hash-check`) |
| **NFR-04** | Authentication enforced at controller layer; `ADMIN` and `CUSTOMER` endpoints partitioned by role. | HTTP Middleware & Architecture Tests (`test_role_boundaries`) |
| **NFR-05** | Database migrations are append-only. Existing migration files are never mutated. | Migration versioning scanner in CI |
| **NFR-06** | Structured JSON logs with request correlation IDs (`x-correlation-id`). | FastAPI logging middleware |
| **NFR-07** | Health endpoint (`GET /health`) returns HTTP 200 within 1 second of successful startup. | Health probe check in test runner and evaluator |
| **NFR-08** | Architecture rules enforced as automated tests (e.g., ADMIN endpoints unreachable by CUSTOMER; executed orders cannot be mutated). | ArchUnit / Pytest Architecture suite |

---

## 3. Functional Acceptance Criteria Master Matrix

Every functional requirement is mapped to a unique identifier:

| ID | Title | Summary Specification | Feature Spec Link |
| :--- | :--- | :--- | :--- |
| **AC-01** | Customer Registration | Customer can register with email and password; new account created in `ACTIVE` state with `role = CUSTOMER`. | [user_management_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/user_management_spec.md) |
| **AC-02** | Admin Role Auditing | Admin can update a user's role (`CUSTOMER` / `ADMIN` / `SUSPENDED`); action audited with actor and timestamp. | [user_management_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/user_management_spec.md) |
| **AC-03** | Stock Catalog Soft-Delete | Stock catalog supports full CRUD for ADMIN; soft-delete moves symbol to `DELETED` / `DELISTED` — never hard-deleted. | [stock_catalog_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/stock_catalog_spec.md) |
| **AC-04** | Watchlist Creation Limit | Customer can create a watchlist with a name and $\ge 1$ symbol; maximum of 10 watchlists per customer. | [watchlist_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/watchlist_spec.md) |
| **AC-05** | Atomic Watchlist Ops | Watchlist operations (rename, add/remove symbols, delete) execute atomically; partial updates rejected with `WatchlistUpdateException`. | [watchlist_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/watchlist_spec.md) |
| **AC-06** | Order Placement Pending | Customer can place market or limit order (BUY/SELL); order enters `PENDING` state with server-side timestamp. | [order_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/order_spec.md) |
| **AC-07** | Order State Lifecycle | Lifecycle `PENDING` $\rightarrow$ `EXECUTED` / `CANCELLED` / `REJECTED` enforced; invalid transitions raise `InvalidOrderStateException`. | [order_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/order_spec.md) |
| **AC-08** | Cash Balance Verification | BUY order fails with `InsufficientFundsException` when `quote_price * quantity` exceeds customer's `available_cash`. | [order_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/order_spec.md) |
| **AC-09** | Portfolio Statistics | Portfolio endpoint returns `total_invested`, `current_value`, `absolute_pnl`, and `percent_pnl` for requesting customer. | [portfolio_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/portfolio_spec.md) |
| **AC-10** | Daily Top Gainers/Losers | Daily statistics endpoint returns top 5 gainers and top 5 losers from requesting customer's current holdings. | [analytics_spec.md](file:///c:/Users/harsh/Downloads/claude_harness_eng_v1-main/specs/analytics_spec.md) |

---

## 4. Market Data Feed (Stub Specification)

To provide dynamic price movements without requiring third-party API keys or external subscriptions:
1. **Initial Baseline:** Initial prices are loaded from seed data.
2. **Random-Walk Generator:**
   - Evaluated periodically on a configurable tick timer (default: 5 seconds) or triggered on-demand via REST endpoint `POST /api/market/tick`.
   - Formula:
     $$P_{t+1} = \max\left(0.01, P_t \times \left(1 + \Delta\right)\right)$$
     where $\Delta \in [-0.03, +0.03]$ (Gaussian or bounded uniform random walk).
   - High, Low, and Current prices are updated with exact 4-decimal precision (`ROUND_HALF_UP`).
3. **Deterministic Testing Mode:** When testing, the random seed or explicit mock prices can be injected to guarantee reproducible assertions.

---

## 5. Seed Data Baseline

A bootstrap seeder must populate the database on initial startup:
- **Admin Account:** `admin@marketscope.com` / `AdminPass123!` (Role: `ADMIN`)
- **Sample Customer 1:** `trader1@marketscope.com` / `TraderPass123!` (Role: `CUSTOMER`, Cash: `$100,000.00`)
- **Sample Customer 2:** `trader2@marketscope.com` / `TraderPass123!` (Role: `CUSTOMER`, Cash: `$25,000.00`)
- **Initial Stocks:**
  - `AAPL` (Apple Inc., Technology, NASDAQ, `$180.00`)
  - `MSFT` (Microsoft Corp., Technology, NASDAQ, `$420.00`)
  - `GOOGL` (Alphabet Inc., Technology, NASDAQ, `$175.00`)
  - `AMZN` (Amazon.com Inc., Consumer Discretionary, NASDAQ, `$185.00`)
  - `NVDA` (Nvidia Corp., Technology, NASDAQ, `$120.00`)
  - `JPM` (JPMorgan Chase, Financials, NYSE, `$200.00`)
  - `XOM` (Exxon Mobil, Energy, NYSE, `$115.00`)
  - `JNJ` (Johnson & Johnson, Healthcare, NYSE, `$155.00`)
  - `TSLA` (Tesla Inc., Consumer Discretionary, NASDAQ, `$240.00`)
  - `BRK.B` (Berkshire Hathaway, Financials, NYSE, `$440.00`)
- **Initial Seed Watchlists:** "Tech Giants" (AAPL, MSFT, NVDA) for `trader1`.
- **Initial Seed Holdings:**
  - `trader1`: 10 shares of `AAPL` @ `$170.00`, 5 shares of `MSFT` @ `$400.00`, 20 shares of `NVDA` @ `$110.00`.
