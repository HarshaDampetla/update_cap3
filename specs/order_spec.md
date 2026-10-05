# Feature Specification: Order Placement, State Lifecycle & Execution

**Feature ID:** SPEC-ORDER-001  
**Target Module:** Trade Order Engine  
**Primary ACs:** `AC-06`, `AC-07`, `AC-08`  
**Primary NFRs:** `NFR-01`, `NFR-02`  

---

## 1. Feature Overview

The Order Placement module processes market and limit orders for equities. The platform validates pre-trade purchasing power, transitions orders through an auditable finite state machine, coordinates with an execution stub, and records immutable, append-only trade records upon completion.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-06: Order Placement & Server-Side Timestamping
- **Given** an authenticated customer with sufficient trading permissions.
- **When** the customer submits `POST /api/orders` specifying:
  - `symbol`: Valid active stock symbol (e.g., `"AAPL"`).
  - `side`: `"BUY"` or `"SELL"`.
  - `order_type`: `"MARKET"` or `"LIMIT"`.
  - `quantity`: Positive integer or fixed-point decimal.
  - `limit_price`: Required if `order_type == "LIMIT"`.
- **Then** the order record is created in the database with status `PENDING`.
- **And** the order is tagged with a server-side generated UTC timestamp (`server_timestamp`).
- **And** response status is `201 Created` with full order details.

### AC-07: Finite State Machine Lifecycle Enforcement
- **Given** an order existing in the database.
- **When** an event requests a state transition:
  - Legal: `PENDING` $\rightarrow$ `EXECUTED` (upon stub matching fill).
  - Legal: `PENDING` $\rightarrow$ `CANCELLED` (customer cancellation before execution).
  - Legal: `PENDING` $\rightarrow$ `REJECTED` (validation failure or market feed rejection).
- **Then** the state transition succeeds and updates `status` and `executed_at` / `cancelled_at`.
- **And** if an order is already in a terminal state (`EXECUTED`, `CANCELLED`, `REJECTED`):
  - Any subsequent mutation, cancellation, or transition attempt raises `InvalidOrderStateException`.
  - HTTP response is `400 Bad Request`.
- **And** post-execution orders and generated trade execution records are **append-only** (`NFR-02`); direct SQL updates or deletes are blocked.

### AC-08: Pre-Trade Purchasing Power & InsufficientFundsException
- **Given** a customer attempting to place a `"BUY"` order.
- **When** the required funds, calculated as:
  $$\text{Required Funds} = \text{quote\_price} \times \text{quantity}$$
  exceeds the customer's `available_cash` balance.
- **Then** the order is immediately rejected before entering `PENDING` state.
- **And** the system raises `InsufficientFundsException`.
- **And** response status is `400 Bad Request` with structured error details containing `available_cash` and `required_funds`.
- **And** the customer's cash balance remains completely untouched.

---

## 3. API Contracts & Data Transfer Objects

### 3.1 POST /api/orders (Place Order)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Request Body (Market Order):**
  ```json
  {
    "symbol": "AAPL",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": "10"
  }
  ```
- **Response: 201 Created**
  ```json
  {
    "id": 901,
    "user_id": 101,
    "symbol": "AAPL",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": "10.0000",
    "quote_price": "180.0000",
    "status": "PENDING",
    "server_timestamp": "2026-10-04T12:30:00.123456Z"
  }
  ```

### 3.2 Error Response: AC-08 Insufficient Funds
- **Response: 400 Bad Request**
  ```json
  {
    "error": "InsufficientFundsException",
    "message": "BUY order fails: required funds 1800.0000 exceeds available cash 500.0000",
    "code": "INSUFFICIENT_FUNDS",
    "available_cash": "500.0000",
    "required_funds": "1800.0000",
    "ac_id": "AC-08"
  }
  ```

### 3.3 POST /api/orders/{id}/cancel (Cancel Pending Order)
- **Headers:** `Authorization: Bearer <CUSTOMER_JWT>`
- **Response: 200 OK**
  ```json
  {
    "id": 901,
    "status": "CANCELLED",
    "cancelled_at": "2026-10-04T12:31:00Z"
  }
  ```

### 3.4 Error Response: AC-07 Invalid Order State
- **Response: 400 Bad Request**
  ```json
  {
    "error": "InvalidOrderStateException",
    "message": "Cannot transition order 901 from EXECUTED to CANCELLED.",
    "code": "INVALID_ORDER_STATE",
    "current_status": "EXECUTED",
    "attempted_status": "CANCELLED",
    "ac_id": "AC-07"
  }
  ```

---

## 4. Domain Models & Exceptions

```python
# src/domain/entities/order.py
from decimal import Decimal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Order(BaseModel):
    id: int
    user_id: int
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    quote_price: Decimal
    limit_price: Decimal = None
    status: OrderStatus = OrderStatus.PENDING
    server_timestamp: datetime
    executed_at: datetime = None
```

```python
# src/domain/exceptions.py
from decimal import Decimal

class InsufficientFundsException(Exception):
    def __init__(self, available_cash: Decimal, required_funds: Decimal):
        super().__init__(f"BUY order fails: required funds {required_funds} exceeds available cash {available_cash}")
        self.available_cash = str(available_cash)
        self.required_funds = str(required_funds)
        self.code = "INSUFFICIENT_FUNDS"
        self.ac_id = "AC-08"

class InvalidOrderStateException(Exception):
    def __init__(self, current_status: str, attempted_status: str, order_id: int):
        super().__init__(f"Cannot transition order {order_id} from {current_status} to {attempted_status}.")
        self.current_status = current_status
        self.attempted_status = attempted_status
        self.order_id = order_id
        self.code = "INVALID_ORDER_STATE"
        self.ac_id = "AC-07"
```

---

## 5. Test Matrix & Traceability

1. `tests/unit/services/test_order_placement.py` $\rightarrow$ Validates `AC-06`: Order enters `PENDING` state with server-generated UTC timestamp.
2. `tests/unit/domain/test_order_lifecycle.py` $\rightarrow$ Validates `AC-07`: `PENDING` $\rightarrow$ `EXECUTED`, `CANCELLED`, `REJECTED`; blocks transitions from terminal states.
3. `tests/unit/domain/test_order_validation_policy.py` $\rightarrow$ Validates `AC-08`: `InsufficientFundsException` raised on deficient cash balance.
4. `tests/architecture/test_order_immutability.py` $\rightarrow$ Validates `NFR-02`: Prohibits updates or deletions on executed orders.
