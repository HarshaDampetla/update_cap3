# Feature Specification: Statistics & Performance Dashboard

**Feature ID:** SPEC-STAT-001  
**Target Module:** Analytics & Audit Reporting  
**Primary ACs:** `AC-10`  
**Primary NFRs:** `NFR-01`, `NFR-04`  

---

## 1. Feature Overview

The Analytics module computes real-time performance insights for investors and operational telemetry for administrators. For customers, it ranks daily gainers and losers strictly from their active holdings and generates sector diversification metrics. For administrators, it aggregates platform-wide order flow, settlement queues, and symbol volume.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-10: Customer Daily Statistics (Top 5 Gainers & Losers)
- **Given** an authenticated customer with active equity holdings.
- **When** calling `GET /api/analytics/daily-performance`.
- **Then** the endpoint:
  1. Retrieves all active holdings belonging to the requesting customer.
  2. For each holding, computes the 24-hour daily price movement using fixed-point Decimal arithmetic:
     $$\text{day\_change\_percent} = \left(\frac{\text{current\_price} - \text{open\_price}}{\text{open\_price}}\right) \times 100$$
  3. Sorts holdings descending by `day_change_percent` to extract the **Top 5 Gainers** (or all if count $< 5$).
  4. Sorts holdings ascending by `day_change_percent` to extract the **Top 5 Losers** (or all if count $< 5$).
- **And** returns a structured JSON payload partitioned into `top_gainers` and `top_losers`.
- **And** holdings with zero price movement are correctly ordered.
- **And** if the customer has 0 holdings, both arrays return empty `[]`.

### Sector Exposure & Allocation (Customer Analytics)
- **Given** an active customer.
- **When** calling `GET /api/analytics/sector-exposure`.
- **Then** aggregates total market value by stock sector (e.g., Technology, Healthcare, Energy) and computes percentage weight of the total portfolio.

### Order Audit & System Statistics (Internal & Admin Scope)
- **Given** an authenticated user with role `ADMIN`.
- **When** calling `GET /api/admin/statistics/orders`.
- **Then** returns:
  - Daily order volume grouped by status (`PENDING`, `EXECUTED`, `CANCELLED`, `REJECTED`).
  - Total settlement queue count (orders pending execution).
  - Top 5 most-traded symbols across the entire platform.

---

## 3. API Contracts & Data Transfer Objects

### 3.1 GET /api/analytics/daily-performance (Customer Daily Stats)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Response: 200 OK**
  ```json
  {
    "user_id": 101,
    "top_gainers": [
      {
        "symbol": "NVDA",
        "name": "Nvidia Corp.",
        "shares_held": "20.0000",
        "current_price": "120.5000",
        "open_price": "115.0000",
        "change_amount": "5.5000",
        "change_percent": "+4.7826%"
      },
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "shares_held": "10.0000",
        "current_price": "180.2500",
        "open_price": "178.5000",
        "change_amount": "1.7500",
        "change_percent": "+0.9804%"
      }
    ],
    "top_losers": [
      {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "shares_held": "5.0000",
        "current_price": "420.0000",
        "open_price": "425.0000",
        "change_amount": "-5.0000",
        "change_percent": "-1.1765%"
      }
    ],
    "calculated_at": "2026-10-04T12:45:00Z"
  }
  ```

### 3.2 GET /api/admin/statistics/orders (Admin Audit Stats)
- **Headers:** `Authorization: Bearer <ADMIN_JWT>`
- **Response: 200 OK**
  ```json
  {
    "daily_volume_by_status": {
      "PENDING": 4,
      "EXECUTED": 142,
      "CANCELLED": 12,
      "REJECTED": 3
    },
    "settlement_queue_count": 4,
    "most_traded_symbols": [
      { "symbol": "NVDA", "trade_count": 58, "total_shares": 1420 },
      { "symbol": "AAPL", "trade_count": 41, "total_shares": 850 },
      { "symbol": "TSLA", "trade_count": 33, "total_shares": 620 }
    ]
  }
  ```

---

## 4. Domain Models & Sorting Policy

```python
# src/domain/policies/gainer_loser_policy.py
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict

class GainerLoserPolicy:
    """Ranks top gainers and losers from holdings using fixed-point math."""

    @classmethod
    def rank_movers(cls, holdings_data: List[Dict]) -> Dict[str, List[Dict]]:
        calculated = []
        for item in holdings_data:
            curr = Decimal(str(item["current_price"]))
            open_p = Decimal(str(item["open_price"]))
            diff = curr - open_p
            pct = ((diff / open_p) * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            
            calculated.append({
                **item,
                "change_amount": diff.quantize(Decimal("0.0001")),
                "change_percent": pct
            })

        # Sort for gainers (highest positive first)
        gainers = sorted(calculated, key=lambda x: x["change_percent"], reverse=True)[:5]
        
        # Sort for losers (lowest / most negative first)
        losers = sorted(calculated, key=lambda x: x["change_percent"])[:5]

        return {
            "top_gainers": gainers,
            "top_losers": losers
        }
```

---

## 5. Test Matrix & Traceability

1. `tests/unit/domain/test_gainer_loser_policy.py` $\rightarrow$ Validates `AC-10`: Correct ranking of top 5 gainers and losers.
2. `tests/unit/domain/test_analytics_fewer_than_five_holdings.py` $\rightarrow$ Validates `AC-10`: Handles customer portfolios with 1, 2, or 3 holdings gracefully.
3. `tests/unit/services/test_admin_order_statistics.py` $\rightarrow$ Validates platform-wide audit counts and volume grouping.
4. `tests/architecture/test_analytics_role_protection.py` $\rightarrow$ Validates `NFR-04`: Prohibits retail customers from accessing admin order statistics.
