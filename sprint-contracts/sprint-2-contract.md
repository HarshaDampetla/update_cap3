# Sprint Contract 02: Watchlists & Order Lifecycle Management

**Sprint ID:** SPRINT-02  
**Target Capabilities:** Watchlist Management, Order Placement Engine, Pre-Trade Risk  
**Participating Agents:** `planner`, `generator`, `evaluator`, `order-lifecycle-agent`, `test-engineer`  
**Target Invariants:** `AC-04`, `AC-05`, `AC-06`, `AC-07`, `AC-08`, `NFR-01`, `NFR-02`  
**Status:** NEGOTIATED & LOCKED  

---

## 1. Scope & Deliverables

1. **Watchlist Operations:**
   - Watchlist creation with name and $\ge 1$ symbol; maximum limit of 10 watchlists per customer (`AC-04`).
   - Atomic multi-symbol mutations: all-or-nothing transactional guarantees raising `WatchlistUpdateException` on partial failure (`AC-05`).
2. **Order Placement & State Machine:**
   - Market and limit order placement (BUY/SELL) entering `PENDING` state with server-side UTC timestamp (`AC-06`).
   - Finite state machine: `PENDING` $\rightarrow$ `EXECUTED` / `CANCELLED` / `REJECTED`; invalid transitions raise `InvalidOrderStateException` (`AC-07`).
   - Pre-trade purchasing power check: BUY orders raise `InsufficientFundsException` when `quote_price * quantity > available_cash` (`AC-08`).
   - Append-only invariant on executed orders and trade records (`NFR-02`).
   - Fixed-point Decimal math across all valuations (`NFR-01`).

---

## 2. Negotiated Acceptance Gates (Generator <-> Evaluator)

| Gate ID | Condition to Pass | Verification Method |
| :--- | :--- | :--- |
| **GATE-1: Watchlist Limit** | Rejection of 11th watchlist creation with `WatchlistLimitExceededException`. | Pytest unit test (`AC-04`) |
| **GATE-2: Atomicity** | Single invalid symbol in bulk update triggers rollback and `WatchlistUpdateException`. | Transaction rollback test (`AC-05`) |
| **GATE-3: Pre-Trade Check** | Unfunded BUY order raises `InsufficientFundsException` with zero cash deduction. | Pre-trade risk test (`AC-08`) |
| **GATE-4: State Machine** | Orders in terminal states cannot be mutated or cancelled; raises `InvalidOrderStateException`. | State transition test (`AC-07`) |
| **GATE-5: Append-Only** | Attempted UPDATE/DELETE on executed trades raises database error. | Architecture test (`NFR-02`) |

---

## 3. Ratchet Sign-Off

- **Generator Agent Signature:** Approved
- **Evaluator Agent Signature:** Approved
