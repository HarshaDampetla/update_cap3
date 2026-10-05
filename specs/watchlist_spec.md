# Feature Specification: Customer Watchlist Management

**Feature ID:** SPEC-WATCH-001  
**Target Module:** Watchlist Management  
**Primary ACs:** `AC-04`, `AC-05`  
**Primary NFRs:** `NFR-04`  

---

## 1. Feature Overview

The Watchlist module allows retail investors to track curated sets of equities. The system guarantees transactional atomicity across all watchlist mutations, strictly limits watchlist counts to 10 per customer, and requires at least one symbol upon creation.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-04: Watchlist Creation & 10-Watchlist Limit
- **Given** an authenticated customer holding $N$ watchlists.
- **When** the customer submits `POST /api/watchlists` with a non-empty name and a list containing at least one valid stock symbol.
- **Then** if $N < 10$:
  - A new watchlist is created and linked to the customer.
  - The specified symbols are associated with the watchlist.
  - Response status is `201 Created`.
- **And** if $N \ge 10$:
  - The creation request is rejected with `400 Bad Request`.
  - Error code is `WATCHLIST_LIMIT_EXCEEDED` ("Customer cannot hold more than 10 watchlists").
- **And** if the symbol list is empty:
  - The request is rejected with `400 Bad Request` ("Watchlist must contain at least one symbol").

### AC-05: Atomic Watchlist Mutations & WatchlistUpdateException
- **Given** an existing customer watchlist.
- **When** the customer initiates an update operation:
  - Renaming the watchlist (`PATCH /api/watchlists/{id}/name`).
  - Adding symbols in bulk (`POST /api/watchlists/{id}/symbols`).
  - Removing symbols (`DELETE /api/watchlists/{id}/symbols/{symbol}`).
  - Deleting the watchlist (`DELETE /api/watchlists/{id}`).
- **Then** the operation executes inside an **atomic database transaction**.
- **And** if any symbol in a batch is invalid, non-existent, or soft-deleted:
  - The entire operation rolls back immediately.
  - No partial changes are persisted.
  - The system raises `WatchlistUpdateException` returning `400 Bad Request` with error details.

---

## 3. API Contracts & Data Transfer Objects

### 3.1 POST /api/watchlists (Create Watchlist)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Request Body:**
  ```json
  {
    "name": "Semiconductors",
    "symbols": ["NVDA", "TSM", "INTC"]
  }
  ```
- **Response: 201 Created**
  ```json
  {
    "id": 12,
    "user_id": 101,
    "name": "Semiconductors",
    "symbols": ["NVDA", "TSM", "INTC"],
    "created_at": "2026-10-04T12:20:00Z"
  }
  ```

### 3.2 POST /api/watchlists/{id}/symbols (Batch Add Symbols)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Request Body:**
  ```json
  {
    "symbols": ["AMD", "INVALID_SYM"]
  }
  ```
- **Response: 400 Bad Request (Atomic Rollback)**
  ```json
  {
    "error": "WatchlistUpdateException",
    "message": "Atomic update aborted: Symbol 'INVALID_SYM' does not exist in catalog.",
    "code": "WATCHLIST_UPDATE_FAILED",
    "ac_id": "AC-05"
  }
  ```

### 3.3 GET /api/watchlists (List Customer Watchlists)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Response: 200 OK**
  ```json
  [
    {
      "id": 12,
      "name": "Semiconductors",
      "items": [
        {
          "symbol": "NVDA",
          "name": "Nvidia Corp.",
          "current_price": "120.5000",
          "change_percent": "+2.10%"
        }
      ]
    }
  ]
  ```

---

## 4. Domain Models & Exceptions

```python
# src/domain/entities/watchlist.py
from datetime import datetime
from typing import List
from pydantic import BaseModel, constr

class Watchlist(BaseModel):
    id: int
    user_id: int
    name: constr(min_length=1, max_length=50)
    symbols: List[str]
    created_at: datetime
    updated_at: datetime
```

```python
# src/domain/exceptions.py
class WatchlistUpdateException(Exception):
    def __init__(self, message: str, invalid_symbols: list = None):
        super().__init__(message)
        self.invalid_symbols = invalid_symbols or []
        self.code = "WATCHLIST_UPDATE_FAILED"
        self.ac_id = "AC-05"

class WatchlistLimitExceededException(Exception):
    def __init__(self, current_count: int, max_limit: int = 10):
        super().__init__(f"Limit reached: Customer already holds {current_count}/{max_limit} watchlists.")
        self.code = "WATCHLIST_LIMIT_EXCEEDED"
        self.ac_id = "AC-04"
```

---

## 5. Test Matrix & Traceability

1. `tests/unit/services/test_watchlist_creation.py` $\rightarrow$ Validates `AC-04`: Watchlist created with $\ge 1$ symbol; rejects empty symbols.
2. `tests/unit/services/test_watchlist_limit.py` $\rightarrow$ Validates `AC-04`: 11th watchlist creation fails with `WatchlistLimitExceededException`.
3. `tests/unit/services/test_watchlist_atomicity.py` $\rightarrow$ Validates `AC-05`: Partial symbol failure aborts transaction and raises `WatchlistUpdateException`.
4. `tests/unit/services/test_watchlist_mutation.py` $\rightarrow$ Validates `AC-05`: Atomic rename, add, remove, and delete operations.
