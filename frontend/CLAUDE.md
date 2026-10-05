# Frontend Module Instructions (React / Vite)

This document directs all user interface development within the `frontend/` directory.

---

## 1. Visual & Architectural Standards
- **Framework:** React 18+ with Vite and TailwindCSS.
- **Responsiveness:** Mobile-first responsive layout (support for mobile $< 640\text{px}$, tablet $768\text{px}$, desktop $\ge 1024\text{px}$).
- **Financial Number Formatting:**
  - Currencies displayed with exact 2 or 4 decimal digits (e.g., `$1,802.50` or `$120.5000`).
  - Gains displayed in emerald green (`text-emerald-400`), losses in rose red (`text-rose-400`), neutral in slate (`text-slate-400`).
- **Design Aesthetic:** Premium dark-mode palette (`bg-slate-900`, `bg-slate-800` cards, subtle borders `border-slate-700/60`).

---

## 2. Core User Journey Views
1. **Authentication:** Login and Register forms with validation and token storage.
2. **Stock Catalog & Search:** Live search bar with sector dropdown, exchange filters, and stock detail modals.
3. **Watchlist Manager:** Tabbed interface supporting up to 10 watchlists, inline renaming, and atomic symbol addition/removal.
4. **Order Entry Widget:** Side-by-side BUY/SELL order form with real-time purchasing power calculation and immediate warning on insufficient cash.
5. **Portfolio & Holdings Table:** Total invested, current value, absolute P&L, percent return cards, and sortable holdings table.
6. **Analytics Dashboard:** Top 5 gainers / top 5 losers side-by-side cards with percentage badges, and sector allocation chart.
7. **Admin Console:** User account management (role switcher, suspend toggle) and soft-delete catalog manager.

---

## 3. UI Verification & Playwright Attributes
- All interactive elements must contain distinct `data-testid` attributes (e.g., `data-testid="buy-order-btn"`, `data-testid="portfolio-total-pnl"`).
- Playwright snapshot tests must validate responsiveness across mobile and desktop viewport profiles.
