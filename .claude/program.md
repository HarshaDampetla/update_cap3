# Program

## Instructions

### Project: MarketScope — Stock Trading & Portfolio Analytics Platform (BC-AINE-006)
- **Problem Statement:** Self-serve retail trading and portfolio analytics platform with strict zero-hand-coding, fixed-point math, and auditable order state machine.
- **Specifications:** `specs/app_spec.md`, `specs/user_management_spec.md`, `specs/stock_catalog_spec.md`, `specs/watchlist_spec.md`, `specs/order_spec.md`, `specs/portfolio_spec.md`, `specs/analytics_spec.md`.
- **Domain Policies:** `src/domain/policies/` (`order_validation_policy.py`, `order_lifecycle_policy.py`, `portfolio_pnl_policy.py`, `watchlist_limit_policy.py`, `gainer_loser_policy.py`).
- **Acceptance Criteria:**
  - AC-01: Customer registration (ACTIVE, role=CUSTOMER).
  - AC-02: Admin user role updates with immutable audit log.
  - AC-03: Stock catalog CRUD with soft-delete (status=DELETED); never hard-delete.
  - AC-04: Watchlist creation with name & >= 1 symbol; max 10 watchlists per customer.
  - AC-05: Atomic watchlist operations; partial failures raise WatchlistUpdateException.
  - AC-06: Order placement (BUY/SELL, MARKET/LIMIT) enters PENDING with server-side UTC timestamp.
  - AC-07: Order lifecycle PENDING -> EXECUTED / CANCELLED / REJECTED; invalid transitions raise InvalidOrderStateException.
  - AC-08: BUY orders fail with InsufficientFundsException when quote_price * quantity > available_cash.
  - AC-09: Portfolio statistics returns total_invested, current_value, absolute_pnl, percent_pnl in Decimal.
  - AC-10: Daily statistics returns top 5 gainers and top 5 losers from current holdings.
- **Specialized Agents:** `order-lifecycle-agent`, `portfolio-stats-agent`, `crud-scaffolder-agent`, `archtest-author-agent`.


## Constraints

- **Layered architecture:** All code must respect the layer hierarchy defined in `architecture.md`. No cross-layer imports in forbidden directions.
- **Review gate:** Every sprint/iteration must pass the review gate before advancing to the next phase.
- **Max retries:** No more than 3 consecutive auto-fix attempts per error category before escalating to a human.
- **No new dependencies without noting:** Any new package or library added must be logged in the current iteration's status block.
- **Self-heal before revert:** Always attempt automated self-healing (see Self-Healing Policy) before reverting to a prior commit.
- **Never delete learned rules:** Rules discovered during a session (error patterns, project-specific fixes) must be preserved in memory and never removed.
- **TDD mandatory:** Write failing tests FIRST, then implement code to make them pass. Never write implementation before tests. Tests define the contract; code fulfills it.
- **100% meaningful coverage:** Every line of generated code must be covered by tests. Coverage is not about bug prevention — it's about guaranteeing the agent has double-checked the behavior of every line it wrote (ref: "AI is forcing us to write good code" by Steve Krenzel). At 100%, any uncovered line is an immediate, unambiguous signal of missing verification.
- **Coverage floor: 80%.** The ratchet gate BLOCKS any commit that drops coverage below 80%. Target is 100% — 80% is the absolute minimum, not the goal.
- **Model tiering:** Use Opus for orchestration/evaluation (judgment tasks), Sonnet for implementation teammates (execution tasks). Configure via project-manifest.json.

## Stopping Criteria

The autonomous `/auto` loop terminates when any of the following conditions are met:

| Condition | Description |
|-----------|-------------|
| All features pass | Every story in the current sprint has passing tests and a green review gate |
| 3 consecutive failures | The same error category fails 3 times in a row without progress |
| Architecture violation | A layer dependency violation is detected and cannot be auto-fixed |
| Coverage below threshold | Test coverage drops below the project baseline and cannot be recovered in one iteration |
| Max iterations | The configured maximum iteration count is reached (default: 50, configured in project-manifest.json) |

## Self-Healing Policy

When an automated check fails, apply the fix strategy from the table below before re-running. If the fix strategy fails after the max retry count, stop and report.

| Category | Signal | Auto-fix |
|----------|--------|----------|
| Lint/format | ruff/eslint fails | `ruff check --fix && ruff format` |
| Type error | mypy/tsc reports type errors | Fix annotation or cast at the error site |
| Test failure | pytest/vitest fails | Fix code under test; never modify the test to make it pass |
| Import error | `ImportError` / `ModuleNotFoundError` at runtime | Fix layer placement or missing `__init__` |
| Coverage drop | Coverage falls below baseline | Add targeted tests for uncovered lines |
| API check fail | Evaluator returns 500/404 or wrong response schema | Read error message, fix service logic or router handler |
| Playwright fail | Element not found / wrong state in browser test | Read selector, fix component rendering or interaction |
| Design score low | Critic scores UI below threshold | Apply critique feedback, regenerate affected component |
| Docker fail | Container fails to start or health check fails | Read container logs, fix config or dependency issue |
| Architecture drift | Response shape does not match declared schema | Read schema definition, fix response serialization |

## Pipeline Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| 1 | BRD | pending | Business requirements not yet loaded |
| 2 | Spec | pending | |
| 3 | Design | pending | |
| 4 | Implement | pending | |
| 5 | Review | pending | |
| 6 | Test | pending | |
| 7 | Deploy | pending | |
| 8 | Commit | pending | |

## Current Focus

```
iteration : 0
status    : idle
story     : (none)
phase     : (none)
coverage  : (none)
```
