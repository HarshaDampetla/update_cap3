# MarketScope — Stock Trading & Portfolio Analytics Platform

[![AI-Native Engineering](https://img.shields.io/badge/AI--Native-Harness%20v1-blue.svg)](AGENTS.md)
[![Compliance](https://img.shields.io/badge/Business%20Case-BC--AINE--006-green.svg)](docs/business-case.md)
[![Zero Hand Coding](https://img.shields.io/badge/Code%20Generation-Claude%20Code%20Only-orange.svg)](CLAUDE.md)
[![Coverage](https://img.shields.io/badge/Coverage-%E2%89%A585%25-brightgreen.svg)](coverage.xml)

MarketScope is an enterprise self-serve retail brokerage and portfolio analytics platform developed under the **AI-Native Engineering Capstone (BC-AINE-006)**. The entire engineering substrate is built upon the **Claude Harness Engine**, combining Karpathy ratcheting, Generator–Evaluator adversarial loops, agent teams, and layered verification.

---

## 1. Quick-Start Guide (Single-Command Bootstrap)

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend and Playwright)
- Git

### 1.1 Backend Setup & Seed Data
```bash
# 1. Install dependencies
pip install -r requirements.txt || pip install fastapi uvicorn pydantic sqlalchemy pytest pytest-cov passlib bcrypt

# 2. Seed database with baseline users, stocks, and portfolios
python -m src.scripts.seed_data

# 3. Start Backend API Server (Swagger UI at http://localhost:8000/docs)
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 1.2 Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

---

## 2. Seed Credentials & Baseline Data

| Role | Email | Password | Initial Balance | Initial Assets |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin@marketscope.com` | `AdminPass123!` | N/A | Full stock catalog CRUD |
| **Customer 1** | `trader1@marketscope.com` | `TraderPass123!` | `$100,000.00` | AAPL (10), MSFT (5), NVDA (20) |
| **Customer 2** | `trader2@marketscope.com` | `TraderPass123!` | `$25,000.00` | Cash only |

---

## 3. Running Test Suites & Quality Verification

```bash
# 1. Run all functional Acceptance Criteria tests (AC-01 through AC-10)
pytest tests/ -v -m "ac" --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml

# 2. Run structural architecture tests (NFR-08)
pytest tests/architecture/ -v

# 3. Run Playwright end-to-end browser tests
npx playwright test

# 4. Run programmatic Claude Agent SDK cycle
python scripts/run_agent_cycle.py sprint-1
```

---

## 4. Documentation & Substrate Index

- **Business Case:** [docs/business-case.md](file:///docs/business-case.md)
- **Architecture & Mermaid Diagrams:** [docs/architecture.md](file:///docs/architecture.md)
- **TDD Guidelines & Worked Examples:** [docs/tdd.md](file:///docs/tdd.md)
- **Knowledge Deposits:** [docs/knowledge-deposits.md](file:///docs/knowledge-deposits.md)
- **Fix Loop Evidence:** [docs/fix-loops/role-boundary-leak-fix.md](file:///docs/fix-loops/role-boundary-leak-fix.md)
- **Master Specification:** [specs/app_spec.md](file:///specs/app_spec.md)
- **Agent Directory:** [AGENTS.md](file:///AGENTS.md)
- **Sprint Contracts:** [sprint-contracts/](sprint-contracts/)
- **Evaluator Reports:** [Sprint 1](specs/reviews/sprint-1-evaluator-report.md) · [Sprint 2](specs/reviews/sprint-2-evaluator-report.md) · [Sprint 3](specs/reviews/sprint-3-evaluator-report.md)
- **Substrate Manifest:** [plugin.json](plugin.json)

