# MarketScope — AI-Native Engineering Directive

> **Stock Trading & Portfolio Analytics Platform (BC-AINE-006)**  
> Domain: FinTech — Capital Markets / Retail Brokerage  
> Evaluation Standard: AI-Native Engineering Rubric (Virtusa Capstone)  

---

## 1. Non-Negotiable Operational Rules

1. **No-Hand-Coding Rule:** All production code, database migrations, and automated tests must be generated exclusively by Claude Code agents. Human edits are strictly restricted to specs, `CLAUDE.md`, agent definitions, hooks, skills, and substrate documentation.
2. **Spec-Is-Truth Rule:** The specifications in `specs/` are the absolute source of truth. If code and specification disagree, the spec wins. Never modify a test or code to match flawed implementation; update the spec deliberately, then regenerate the code.
3. **PR-Only Merge Rule:** Direct pushes or commits to `main` are strictly forbidden. All features, bug fixes, and refactors must flow through pull requests with `--no-ff` merge commits to preserve an auditable agent evidence trail.
4. **Synthetic-Data Rule:** Use strictly generated dummy data. Real credentials, proprietary data, or live exchange secrets must never be placed in the codebase.

---

## 2. Core Architectural & Domain Invariants

- **NFR-01 (Fixed-Point Math):** Prices, quantities, and P&L must be computed using `Decimal` / `BigDecimal` with 4 decimal places (`ROUND_HALF_UP`). Floating-point types (`float`, `double`) are banned.
- **NFR-02 (Append-Only Trades):** Executed orders and trade execution logs are immutable. No `UPDATE` or `DELETE` statements are permitted on execution records.
- **NFR-03 (Secure KDF):** Passwords must be hashed using `bcrypt` (work factor $\ge 12$). Plaintext credentials are never logged or returned.
- **NFR-04 (Role Partitioning):** Authentication and role checks are enforced at the controller layer. Endpoints under `/api/admin/*` require `ADMIN` role; requests from `CUSTOMER` or `SUSPENDED` return `403 Forbidden`.
- **NFR-05 (Append-Only Migrations):** Database migration files are strictly append-only.
- **NFR-06 (Structured Logs):** All HTTP requests log structured JSON containing a unique `x-correlation-id`.
- **NFR-07 (Fast Startup):** Health endpoint (`GET /health`) must return HTTP 200 in under 1 second.
- **NFR-08 (Architecture Guardrails):** Clean Architecture boundaries (Controllers $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ Domain) are enforced by automated architecture tests.

---

## 3. Technology Stack & Execution Commands

- **Backend:** Python 3.11+ / FastAPI / SQLAlchemy / SQLite / Pydantic
- **Frontend:** React 18+ / Vite / TailwindCSS / Lucide Icons
- **Testing:** Pytest / Pytest-Cov (Backend), Playwright (E2E), ArchUnit / AST Linter (Architecture)

### Commands Quick Reference
```bash
# Run Backend Locally (Single command bootstrap)
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run Frontend Locally
cd frontend && npm run dev

# Run Seed Data Bootstrap
python -m src.scripts.seed_data

# Run All Unit & Integration Tests with Coverage
pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing

# Run Specific Acceptance Criterion Test
pytest -m "ac('AC-08')" -v

# Run Structural & Architecture Tests
pytest tests/architecture/ -v

# Run End-to-End Playwright Tests
npx playwright test
```

---

## 4. Karpathy Coding Guidelines

1. **Think Before Coding:** State assumptions explicitly. If requirements are ambiguous, clarify before touching code.
2. **Simplicity First:** Write the minimum code that satisfies the failing test. No speculative abstractions.
3. **Surgical Changes:** Edit only what the sprint contract or issue requires. Do not reformat adjacent unrelated code.
4. **Goal-Driven Execution:** Transform vague tasks into explicit, verifiable criteria (Red test $\rightarrow$ Green code $\rightarrow$ Refactor).

---

## 5. Substrate Navigation

- **Master Specification:** [specs/app_spec.md](file:///specs/app_spec.md)
- **Business Case:** [docs/business-case.md](file:///docs/business-case.md)
- **Architecture & Diagrams:** [docs/architecture.md](file:///docs/architecture.md)
- **TDD Guidelines:** [docs/tdd.md](file:///docs/tdd.md)
- **Knowledge Deposits:** [docs/knowledge-deposits.md](file:///docs/knowledge-deposits.md)
- **Agents Index:** [AGENTS.md](file:///AGENTS.md)
