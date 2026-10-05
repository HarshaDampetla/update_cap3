# Sprint Contract 03: Portfolio Holdings & Analytics Dashboard

**Sprint ID:** SPRINT-03  
**Target Capabilities:** Portfolio Valuation, Top Gainers/Losers, Admin Order Telemetry  
**Participating Agents:** `planner`, `generator`, `evaluator`, `portfolio-stats-agent`, `test-engineer`  
**Target Invariants:** `AC-09`, `AC-10`, `NFR-01`, `NFR-04`  
**Status:** NEGOTIATED & LOCKED  

---

## 1. Scope & Deliverables

1. **Portfolio Valuation:**
   - Summary endpoint returning `total_invested`, `current_value`, `absolute_pnl`, and `percent_pnl` (`AC-09`).
   - Strict fixed-point Decimal calculation with 4 decimal places (`NFR-01`).
   - Holdings breakdown endpoint with per-position unrealized P&L.
2. **Analytics & Performance:**
   - Daily performance endpoint calculating top 5 gainers and top 5 losers from current holdings (`AC-10`).
   - Sector allocation breakdown.
   - Admin order statistics endpoint for status volume and most-traded stocks.
3. **End-to-End UI Verification:**
   - Playwright browser interaction test validating responsive dashboard layout.

---

## 2. Negotiated Acceptance Gates (Generator <-> Evaluator)

| Gate ID | Condition to Pass | Verification Method |
| :--- | :--- | :--- |
| **GATE-1: Precision Math** | P&L math reproduces exact cent-level values with 0 floating point errors. | Pytest test suite (`AC-09`, `NFR-01`) |
| **GATE-2: Ranking Order** | Gainer/loser arrays properly sorted and bounded by customer's active holdings. | Sorting test (`AC-10`) |
| **GATE-3: Zero Holdings** | Customer with empty portfolio receives `$0.0000` stats with no division-by-zero error. | Edge case test (`AC-09`) |
| **GATE-4: Playwright E2E** | Automated browser execution navigates portfolio page, captures screenshot. | Playwright runner |
| **GATE-5: Coverage Final**| Total repository test coverage $\ge 85\%$. | `coverage.xml` validation |

---

## 3. Ratchet Sign-Off

- **Generator Agent Signature:** Approved
- **Evaluator Agent Signature:** Approved
