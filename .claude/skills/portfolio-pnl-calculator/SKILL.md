---
name: portfolio-pnl-calculator
description: Procedures and formulas for computing exact fixed-point portfolio P&L, weighted average price, and gainer/loser rankings without floating-point error.
---

# Portfolio P&L Calculator Skill

This skill guides the implementation of deterministic, financial-grade calculations for portfolio valuations, percentage returns, and gainer/loser rankings.

---

## 1. Cardinal Math Rule (NFR-01)

**Never use `float` or `double` for currency, share quantities, or returns.**
Always use:
```python
from decimal import Decimal, ROUND_HALF_UP

PRECISION = Decimal("0.0001")
CURRENCY_PRECISION = Decimal("0.01")
```

---

## 2. Core Valuation Formulas (AC-09)

### Total Invested Capital
$$\text{total\_invested} = \sum_{i=1}^n (\text{shares}_i \times \text{average\_buy\_price}_i)$$

### Current Market Value
$$\text{current\_value} = \sum_{i=1}^n (\text{shares}_i \times \text{current\_market\_price}_i)$$

### Absolute Profit & Loss
$$\text{absolute\_pnl} = \text{current\_value} - \text{total\_invested}$$

### Percentage Profit & Loss
$$\text{percent\_pnl} = \begin{cases} \left(\frac{\text{absolute\_pnl}}{\text{total\_invested}}\right) \times 100, & \text{if } \text{total\_invested} > 0 \\ 0.0000, & \text{if } \text{total\_invested} = 0 \end{cases}$$

---

## 3. Daily Gainer & Loser Ranking Algorithm (AC-10)

For each active holding in the customer's portfolio:
```python
def calculate_day_change(current_price: Decimal, open_price: Decimal) -> Decimal:
    if open_price <= Decimal("0"):
        return Decimal("0.0000")
    diff = current_price - open_price
    return ((diff / open_price) * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
```

1. Sort all active holdings by `change_percent` descending $\rightarrow$ take first 5 for `top_gainers`.
2. Sort all active holdings by `change_percent` ascending $\rightarrow$ take first 5 for `top_losers`.
3. If portfolio contains fewer than 5 holdings, return all active holdings sorted without padding synthetic data.

---

## 4. Verification Check
- Assert `percent_pnl` with zero positions produces `Decimal("0.0000")`.
- Assert division by zero never occurs.
- Assert all outputs serialize to JSON string representations (e.g. `"180.2500"`).
