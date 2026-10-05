# Architecture Specification: MarketScope Platform

**Document ID:** ARCH-AINE-006  
**System:** MarketScope Stock Trading & Portfolio Analytics Platform  
**Compliance Standard:** AI-Native Engineering Rubric (BC-AINE-006)  

---

## 1. Architectural Philosophy & Layered Structure

MarketScope is engineered using a strict Clean Architecture / Layered Architecture pattern. Dependencies flow inward unidirectionally:

$$\text{Controllers} \longrightarrow \text{Services} \longrightarrow \text{Repositories} \longrightarrow \text{Domain Model}$$

```
+--------------------------------------------------------------------------+
|                        API / Controller Layer                            |
|  - Role-based Auth Guards (ADMIN / CUSTOMER / SUSPENDED)                |
|  - HTTP Request Validation (Pydantic / DTOs)                            |
|  - Structured Logging & Correlation ID Injection (NFR-04, NFR-06)        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                          Application Services                            |
|  - Use-Case Orchestration (UserService, OrderService, PortfolioService) |
|  - Atomic Database Transaction Management (AC-05)                        |
|  - Domain Policy Invocation & External Stub Coordination                 |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                         Persistence / Repositories                       |
|  - CRUD Scaffolding & Query Interfaces                                   |
|  - Soft-Delete Filtering (AC-03: symbols never hard-deleted)             |
|  - Append-Only Trade Record Invariant (NFR-02)                           |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                          Core Domain Layer                               |
|  - Pure Business Entities (User, Stock, Watchlist, Order, Holding)       |
|  - Value Objects (Price, Quantity, CashBalance, Ticker)                  |
|  - Fixed-Point Decimal Calculation Engine (NFR-01)                       |
|  - Domain Invariants & Policies (OrderValidationPolicy, PnLPolicy)       |
+--------------------------------------------------------------------------+
```

### Architectural Layer Invariants (Enforced via Automated ArchTests)
1. **Controllers** must never access Repositories or the Database directly; all calls must route through Services.
2. **Domain Models and Policies** must have zero external framework, HTTP, or database dependencies.
3. **Services** encapsulate transactional boundaries (`AC-05`).
4. **Repositories** enforce append-only invariants on executed orders and audit tables (`NFR-02`).

---

## 2. C4 Context Diagram

```mermaid
C4Context
    title System Context Diagram - MarketScope Platform

    Person(customer, "Retail Customer", "Executes trades, tracks portfolio, manages watchlists.")
    Person(admin, "Brokerage Admin", "Manages stock catalog, audits orders, updates user roles.")

    System(marketscope, "MarketScope Brokerage Platform", "Provides self-serve trade execution, catalog management, and real-time portfolio analytics.")
    
    System_Ext(market_stub, "Market Data Feed (Stub)", "Simulates scheduled ticks with configurable random-walk price updates.")
    System_Ext(auth_kdf, "KDF Engine (Bcrypt)", "Provides secure password hashing and verification.")

    Rel(customer, marketscope, "Manages portfolio, places orders, configures watchlists", "HTTPS / JSON")
    Rel(admin, marketscope, "Administers stocks, modifies user roles, audits trades", "HTTPS / JSON")
    Rel(marketscope, market_stub, "Polls / receives current market price ticks", "Internal In-Memory / REST")
    Rel(marketscope, auth_kdf, "Hashes credentials securely", "Native CPU")
```

---

## 3. Order Placement & Execution Sequence Flow

The following sequence diagram illustrates the lifecycle of a BUY order, detailing validation against available cash (`AC-08`), transition to `PENDING` (`AC-06`), stub execution (`AC-07`), balance deduction, and append-only trade journaling (`NFR-02`).

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Retail Customer
    participant Ctrl as OrderController
    participant Auth as RoleAuthGuard
    participant Svc as OrderService
    participant Policy as OrderValidationPolicy
    participant Wallet as PortfolioRepository
    participant OrderRepo as OrderRepository
    participant Stub as MarketDataFeedStub
    participant Audit as TradeAuditJournal

    Customer->>Ctrl: POST /api/orders (symbol: "AAPL", qty: 10, type: "BUY", order_type: "MARKET")
    Ctrl->>Auth: Verify Token & Role == CUSTOMER
    Auth-->>Ctrl: Authenticated (UserID: 42)
    
    Ctrl->>Svc: placeOrder(userId=42, symbol="AAPL", qty=10, side="BUY")
    Svc->>Stub: getQuote("AAPL")
    Stub-->>Svc: quote_price = 150.00
    
    Svc->>Wallet: getAvailableCash(userId=42)
    Wallet-->>Svc: available_cash = 1000.00
    
    Note over Svc, Policy: Required Cost = 150.00 * 10 = 1500.00 Decimal
    Svc->>Policy: validatePurchase(cash=1000.00, required=1500.00)
    
    alt available_cash < required_funds (AC-08)
        Policy-->>Svc: InsufficientFundsException("Required 1500.00 exceeds available 1000.00")
        Svc-->>Ctrl: Raise 400 Bad Request
        Ctrl-->>Customer: Error JSON: {"code": "INSUFFICIENT_FUNDS", "ac": "AC-08"}
    else available_cash >= required_funds (Happy Path)
        Policy-->>Svc: Validated
        Svc->>OrderRepo: createOrder(status=PENDING, server_timestamp=UTC_NOW) (AC-06)
        OrderRepo-->>Svc: order_id = 901, status = PENDING
        
        Note over Svc, Stub: Synchronous / Asynchronous Stub Execution Engine
        Svc->>Stub: executeOrderStub(order_id=901)
        Stub-->>Svc: execution_status = EXECUTED, fill_price = 150.00
        
        Svc->>Svc: transitionState(order=901, from=PENDING, to=EXECUTED) (AC-07)
        Svc->>Wallet: deductCash(userId=42, amount=1500.00)
        Svc->>Wallet: addHoldings(userId=42, symbol="AAPL", qty=10, price=150.00)
        Svc->>Audit: appendTradeRecord(order_id=901, execution_data) (NFR-02)
        Svc-->>Ctrl: OrderPlacedDTO(id=901, status="EXECUTED")
        Ctrl-->>Customer: 201 Created JSON
    end
```

---

## 4. Order State Machine Model

Order lifecycle enforcement (`AC-07`) strictly complies with the following finite state machine:

```mermaid
stateDiagram-v2
    [*] --> PENDING: Order Placed (Server Timestamp)
    
    PENDING --> EXECUTED: Stub Matching Success
    PENDING --> CANCELLED: Customer Cancellation Request
    PENDING --> REJECTED: Execution / Risk Check Failure
    
    EXECUTED --> [*]: Append-Only (Immutable)
    CANCELLED --> [*]: Terminal State
    REJECTED --> [*]: Terminal State

    note right of EXECUTED
        NFR-02: Executed orders are append-only.
        Zero edits or deletes permitted.
    end note
```

Any attempt to transition an order from `EXECUTED`, `CANCELLED`, or `REJECTED` to another state raises `InvalidOrderStateException` (`AC-07`).

---

## 5. Domain Invariants & Precision Rules

### 5.1 Fixed-Point Arithmetic (`NFR-01`)
All financial quantities ($P\&L$, prices, cash balances, quantities) are computed using exact decimal representations:
- **Python:** `decimal.Decimal` with rounding `ROUND_HALF_UP`.
- **Database:** `NUMERIC(18, 4)` for currency amounts; `NUMERIC(18, 6)` for fractional shares if applicable.
- **Rule:** Floating-point data types (`float`, `double`) are banned across domain logic, controllers, and persistence layers.

### 5.2 Append-Only Audit Integrity (`NFR-02`)
The persistence schema guarantees:
- Every execution produces a permanent row in `trade_executions`.
- Update and delete operations on `trade_executions` are blocked via database triggers or repository assertions.

### 5.3 Password Cryptography & Credentials (`NFR-03`)
- All user passwords are encrypted using `bcrypt` (work factor $\ge 12$).
- Plaintext passwords or decoded credentials are never logged, formatted into error messages, or returned in API responses.

### 5.4 Role Boundary Partitioning (`NFR-04`)
- Controllers use strict role decorators or middleware guards:
  - `/api/admin/*` $\rightarrow$ requires role `ADMIN`. Access by `CUSTOMER` or `SUSPENDED` results in `403 Forbidden`.
  - `/api/customer/*` $\rightarrow$ requires authenticated `CUSTOMER` or `ADMIN`.
- User suspension blocks all trading mutations.

### 5.5 Atomic Watchlist Engine (`AC-05`)
Watchlist mutations run inside atomic transactions. If any symbol in a bulk addition is invalid or delisted, the transaction rolls back completely and returns `WatchlistUpdateException`.

---

## 6. Database Entity-Relationship Architecture

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : generates
    USERS ||--o{ WATCHLISTS : owns
    USERS ||--o{ ORDERS : places
    USERS ||--o{ HOLDINGS : possesses
    USERS ||--o{ PORTFOLIO_CASH : maintains

    STOCKS ||--o{ WATCHLIST_ITEMS : referenced_in
    STOCKS ||--o{ ORDERS : target_symbol
    STOCKS ||--o{ HOLDINGS : asset_type

    WATCHLISTS ||--o{ WATCHLIST_ITEMS : contains
    ORDERS ||--o| TRADE_EXECUTIONS : records

    USERS {
        int id PK
        string email UK
        string password_hash
        string role "CUSTOMER | ADMIN | SUSPENDED"
        string status "ACTIVE | SUSPENDED"
        datetime created_at
        datetime updated_at
    }

    STOCKS {
        string symbol PK
        string name
        string sector
        string exchange
        decimal current_price
        decimal open_price
        decimal high_price
        decimal low_price
        string status "ACTIVE | DELISTED | DELETED"
        datetime created_at
    }

    WATCHLISTS {
        int id PK
        int user_id FK
        string name
        datetime created_at
        datetime updated_at
    }

    WATCHLIST_ITEMS {
        int id PK
        int watchlist_id FK
        string symbol FK
        datetime added_at
    }

    ORDERS {
        int id PK
        int user_id FK
        string symbol FK
        string side "BUY | SELL"
        string order_type "MARKET | LIMIT"
        decimal quantity
        decimal quote_price
        decimal limit_price
        string status "PENDING | EXECUTED | CANCELLED | REJECTED"
        datetime server_timestamp
        datetime executed_at
    }

    TRADE_EXECUTIONS {
        int id PK
        int order_id FK "UK (Append-Only)"
        decimal executed_price
        decimal quantity
        decimal total_value
        datetime execution_timestamp
    }

    HOLDINGS {
        int id PK
        int user_id FK
        string symbol FK
        decimal shares_held
        decimal average_buy_price
        datetime updated_at
    }

    PORTFOLIO_CASH {
        int user_id PK, FK
        decimal available_cash
        datetime updated_at
    }
```
