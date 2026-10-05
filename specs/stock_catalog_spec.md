# Feature Specification: Stock Catalog Administration & Discovery

**Feature ID:** SPEC-STOCK-001  
**Target Module:** Stock Catalog & Market Discovery  
**Primary ACs:** `AC-03`  
**Primary NFRs:** `NFR-01`, `NFR-04`  

---

## 1. Feature Overview

The Stock Catalog module provides administrative catalog maintenance (CRUD) and retail investor discovery (search and filter by symbol, sector, or exchange). It integrates with a simulated market data feed to provide realistic price fluctuations.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-03: Stock Catalog Full CRUD & Soft-Delete Invariant
- **Given** an authenticated user with role `ADMIN`.
- **When** the admin submits:
  - `POST /api/admin/stocks`: Creates a new stock with symbol, company name, sector, exchange, and initial price.
  - `PUT /api/admin/stocks/{symbol}`: Updates stock metadata (name, sector, exchange).
  - `DELETE /api/admin/stocks/{symbol}`: Performs a **soft-delete**.
- **Then** the stock's status transitions to `DELETED` (or `DELISTED`).
- **And** the database record is **never hard-deleted** (`DELETE FROM stocks` is prohibited).
- **And** soft-deleted stocks are omitted from customer search results, but remain referenced in historical trade records.
- **And** any attempt by a `CUSTOMER` role to invoke CRUD endpoints returns `403 Forbidden` (`NFR-04`).

### Stock Catalog Browsing & Search (Customer Journey)
- **Given** an active customer or anonymous user.
- **When** querying `GET /api/stocks?query=AAP&sector=Technology&exchange=NASDAQ`.
- **Then** return matching active stocks with current price, day high, day low, and 24h change.
- **And** price values are returned as fixed-point decimal strings (`NFR-01`).

---

## 3. API Contracts & Data Transfer Objects

### 3.1 POST /api/admin/stocks (Create Stock)
- **Headers:** `Authorization: Bearer <ADMIN_JWT>`
- **Request Body:**
  ```json
  {
    "symbol": "TSLA",
    "name": "Tesla Inc.",
    "sector": "Consumer Discretionary",
    "exchange": "NASDAQ",
    "initial_price": "240.50"
  }
  ```
- **Response: 201 Created**
  ```json
  {
    "symbol": "TSLA",
    "name": "Tesla Inc.",
    "sector": "Consumer Discretionary",
    "exchange": "NASDAQ",
    "current_price": "240.5000",
    "status": "ACTIVE",
    "created_at": "2026-10-04T12:10:00Z"
  }
  ```

### 3.2 DELETE /api/admin/stocks/{symbol} (Soft Delete)
- **Headers:** `Authorization: Bearer <ADMIN_JWT>`
- **Response: 200 OK**
  ```json
  {
    "symbol": "TSLA",
    "status": "DELETED",
    "message": "Stock TSLA successfully moved to DELETED status.",
    "updated_at": "2026-10-04T12:15:00Z"
  }
  ```

### 3.3 GET /api/stocks (Customer Catalog Search)
- **Query Params:** `query` (optional), `sector` (optional), `exchange` (optional), `include_delisted` (default: false)
- **Response: 200 OK**
  ```json
  {
    "items": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "current_price": "180.2500",
        "open_price": "178.5000",
        "high_price": "181.0000",
        "low_price": "178.0000",
        "change_percent": "+0.98%",
        "status": "ACTIVE"
      }
    ],
    "total": 1
  }
  ```

---

## 4. Domain Models & Exceptions

```python
# src/domain/entities/stock.py
from decimal import Decimal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, constr

class StockStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DELISTED = "DELISTED"
    DELETED = "DELETED"

class Stock(BaseModel):
    symbol: constr(to_upper=True, min_length=1, max_length=10)
    name: str
    sector: str
    exchange: str
    current_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    status: StockStatus = StockStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
```

### Domain Exceptions:
- `StockAlreadyExistsException` (409 Conflict)
- `StockNotFoundException` (404 Not Found)
- `HardDeleteProhibitedException` (400 Bad Request)

---

## 5. Test Matrix & Traceability

1. `tests/unit/services/test_stock_catalog_crud.py` $\rightarrow$ Validates `AC-03`: Full CRUD execution under `ADMIN` role.
2. `tests/unit/repositories/test_stock_soft_delete.py` $\rightarrow$ Validates `AC-03`: Deleting stock alters status to `DELETED` and verifies row persists in database.
3. `tests/unit/services/test_stock_search.py` $\rightarrow$ Validates filtering by symbol, sector, and exchange.
4. `tests/architecture/test_stock_decimal_precision.py` $\rightarrow$ Validates `NFR-01`: Prices are strictly `Decimal` with 4 decimal places.
