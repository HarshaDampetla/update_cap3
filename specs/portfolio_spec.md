# Feature Specification: Portfolio Holdings & P&L Valuation

**Feature ID:** SPEC-PORT-001  
**Target Module:** Portfolio & Holdings Engine  
**Primary ACs:** `AC-09`  
**Primary NFRs:** `NFR-01`  

---

## 1. Feature Overview

The Portfolio module aggregates a customer's active equity holdings and computes summary valuation metrics including invested capital, market value, absolute profit and loss (P&L), and percentage return. Every valuation is strictly calculated using deterministic fixed-point decimal arithmetic.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-09: Customer Portfolio Valuation Endpoint
- **Given** an authenticated customer holding $K$ equity positions ($K \ge 0$).
- **When** the customer sends a request to `GET /api/portfolio/statistics`.
- **Then** the endpoint calculates and returns:
  1. `total_invested`:
     $$\text{total\_invested} = \sum_{i=1}^K \left(\text{shares\_held}_i \times \text{average\_buy\_price}_i\right)$$
  2. `current_value`:
     $$\text{current\_value} = \sum_{i=1}^K \left(\text{shares\_held}_i \times \text{current\_price}_i\right)$$
  3. `absolute_pnl`:
     $$\text{absolute\_pnl} = \text{current\_value} - \text{total\_invested}$$
  4. `percent_pnl`:
     $$\text{percent\_pnl} = \begin{cases} \left(\frac{\text{absolute\_pnl}}{\text{total\_invested}}\right) \times 100, & \text{if } \text{total\_invested} > 0 \\ 0.0000, & \text{if } \text{total\_invested} = 0 \end{cases}$$
- **And** all metrics are computed in fixed-point decimal (`NFR-01`); floating-point types (`float`, `double`) are banned.
- **And** values are rounded deterministically to 4 decimal places (`ROUND_HALF_UP`).
- **And** the customer can only access their own portfolio statistics; requesting another customer's portfolio returns `403 Forbidden`.

### Portfolio Holdings Details (Customer Journey)
- **Given** an authenticated customer.
- **When** calling `GET /api/portfolio/holdings`.
- **Then** return an itemized list of all active holdings with:
  - `symbol`, `shares_held`, `average_buy_price`, `current_price`, `total_cost`, `market_value`, `unrealized_pnl`, `unrealized_pnl_percent`.

---

## 3. API Contracts & Data Transfer Objects

### 3.1 GET /api/portfolio/statistics
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Response: 200 OK**
  ```json
  {
    "user_id": 101,
    "total_invested": "5900.0000",
    "current_value": "6312.5000",
    "absolute_pnl": "412.5000",
    "percent_pnl": "6.9915",
    "currency": "USD",
    "calculated_at": "2026-10-04T12:40:00Z"
  }
  ```

### 3.2 GET /api/portfolio/holdings
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Response: 200 OK**
  ```json
  [
    {
      "symbol": "AAPL",
      "shares_held": "10.0000",
      "average_buy_price": "170.0000",
      "current_price": "180.2500",
      "total_invested": "1700.0000",
      "current_value": "1802.5000",
      "absolute_pnl": "102.5000",
      "percent_pnl": "6.0294"
    },
    {
      "symbol": "NVDA",
      "shares_held": "20.0000",
      "average_buy_price": "110.0000",
      "current_price": "120.5000",
      "total_invested": "2200.0000",
      "current_value": "2410.0000",
      "absolute_pnl": "210.0000",
      "percent_pnl": "9.5455"
    },
    {
      "symbol": "MSFT",
      "shares_held": "5.0000",
      "average_buy_price": "400.0000",
      "current_price": "420.0000",
      "total_invested": "2000.0000",
      "current_value": "2100.0000",
      "absolute_pnl": "100.0000",
      "percent_pnl": "5.0000"
    }
  ]
  ```

---

## 4. Domain Models & Mathematics Policy

```python
# src/domain/policies/portfolio_pnl_policy.py
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict

class PortfolioPnLPolicy:
    """Enforces mathematical precision and zero floating-point error (NFR-01)."""
    
    PRECISION = Decimal("0.0001")

    @classmethod
    def calculate_summary(cls, holdings: List[Dict[str, Decimal]]) -> Dict[str, Decimal]:
        total_invested = Decimal("0.0000")
        current_value = Decimal("0.0000")

        for h in holdings:
            shares = Decimal(str(h["shares_held"]))
            avg_price = Decimal(str(h["average_buy_price"]))
            curr_price = Decimal(str(h["current_price"]))

            total_invested += (shares * avg_price)
            current_value += (shares * curr_price)

        total_invested = total_invested.quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        current_value = current_value.quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        
        absolute_pnl = (current_value - total_invested).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)

        if total_invested > Decimal("0.0000"):
            percent_pnl = ((absolute_pnl / total_invested) * Decimal("100")).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        else:
            percent_pnl = Decimal("0.0000")

        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "absolute_pnl": absolute_pnl,
            "percent_pnl": percent_pnl
        }
```

---

## 5. Test Matrix & Traceability

1. `tests/unit/domain/test_portfolio_pnl_policy.py` $\rightarrow$ Validates `AC-09` & `NFR-01`: Exact decimal P&L results on standard holdings.
2. `tests/unit/domain/test_portfolio_empty_holdings.py` $\rightarrow$ Validates `AC-09`: Zero holdings return `$0.0000` without ZeroDivisionError.
3. `tests/unit/services/test_portfolio_service.py` $\rightarrow$ Validates `AC-09`: Aggregates customer holdings, fetches latest mock quotes, and formats DTOs.
4. `tests/architecture/test_decimal_pnl_enforcement.py` $\rightarrow$ Validates `NFR-01`: Scans PnL calculator functions to guarantee no Python `float` operations exist.
