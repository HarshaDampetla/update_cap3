# Agent Directory & Table of Contents

This document serves as the master Table of Contents for all autonomous Claude Code agents operating within the MarketScope engineering harness.

---

## 1. Harness Foundation Agents

Base agents shipped with the Claude Harness Engine foundation:

| Agent Identifier | Definition File | Primary Responsibility |
| :--- | :--- | :--- |
| **planner** | [.claude/agents/planner.md](file:///.claude/agents/planner.md) | Architectural planning, specification refinement, dependency graph sequencing. |
| **generator** | [.claude/agents/generator.md](file:///.claude/agents/generator.md) | TDD production code generation, refactoring, and agent team coordination. |
| **evaluator** | [.claude/agents/evaluator.md](file:///.claude/agents/evaluator.md) | Multi-gate verification, contract ratcheting, Playwright MCP test execution. |
| **security-reviewer** | [.claude/agents/security-reviewer.md](file:///.claude/agents/security-reviewer.md) | OWASP vulnerability scans, role boundary audits, credential leak detection. |
| **test-engineer** | [.claude/agents/test-engineer.md](file:///.claude/agents/test-engineer.md) | Test plan authoring, red-phase test generation, coverage reporting. |
| **design-critic** | [.claude/agents/design-critic.md](file:///.claude/agents/design-critic.md) | GAN-based heuristic scoring of UI design, layout, and visual fidelity. |
| **ui-designer** | [.claude/agents/ui-designer.md](file:///.claude/agents/ui-designer.md) | Responsive frontend components, Tailwind/CSS styling, view templates. |

---

## 2. Project-Specific Domain & Technical Agents

Specialized agents authored specifically for the MarketScope trading and portfolio analytics platform:

| Agent Identifier | Definition File | Specialized Domain / Technical Capability |
| :--- | :--- | :--- |
| **order-lifecycle-agent** | [.claude/agents/order-lifecycle-agent.md](file:///.claude/agents/order-lifecycle-agent.md) | Order finite state machine, pre-trade funds validation (`AC-08`), stub execution, append-only trade ledger. |
| **portfolio-stats-agent** | [.claude/agents/portfolio-stats-agent.md](file:///.claude/agents/portfolio-stats-agent.md) | Fixed-point Decimal portfolio valuations (`AC-09`), gainer/loser sorting algorithms (`AC-10`), sector allocation. |
| **crud-scaffolder-agent** | [.claude/agents/crud-scaffolder-agent.md](file:///.claude/agents/crud-scaffolder-agent.md) | Scaffolds layered Controller-Service-Repository-Domain architectures with automated role boundaries (`NFR-04`). |
| **archtest-author-agent** | [.claude/agents/archtest-author-agent.md](file:///.claude/agents/archtest-author-agent.md) | Generates structural tests enforcing unidirectional layer dependencies and invariant constraints (`NFR-08`). |
