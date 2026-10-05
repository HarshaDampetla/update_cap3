# Test-Driven Development (TDD) Discipline & Standards

**Document ID:** TDD-AINE-006  
**System:** MarketScope Stock Trading & Portfolio Analytics Platform  
**Compliance Standard:** AI-Native Engineering Rubric (BC-AINE-006)  

---

## 1. The TDD Mandate for AI-Native Engineering

In MarketScope, **no production code is written without a prior failing test**. Claude Code agents strictly adhere to the Red-Green-Refactor loop. This ensures:
1. **Spec-Is-Truth:** Every test is derived directly from an Acceptance Criterion (`AC-01` through `AC-10`) or Non-Functional Requirement (`NFR-01` through `NFR-08`).
2. **Zero Dead Code:** Agents write only the minimum code necessary to make the failing test pass.
3. **Regression Prevention:** The automated test harness runs after every mutation.

---

## 2. Red-Green-Refactor Workflow

```
   [1. RED PHASE]
Write test specifying expected behavior.
Run test suite -> verify failure with expected error.
             |
             v
  [2. GREEN PHASE]
Generate minimal implementation satisfying the test.
Run test suite -> verify 100% pass.
             |
             v
 [3. REFACTOR PHASE]
Clean up structure, extract value objects, ensure
fixed-point Decimal compliance, run lint & archtests.
```

### Commit History Strategy for Red-Green Verification
To provide an incontrovertible audit trail for the Virtusa reviewer plugin:
1. **Commit 1 (RED):** `test(order): add failing test for AC-08 insufficient funds validation`
2. **Commit 2 (GREEN):** `feat(order): implement OrderValidationPolicy to pass AC-08`
3. **Commit 3 (REFACTOR):** `refactor(order): enforce Decimal fixed-point calculation in AC-08 balance checks`

Across development, at least 10 discrete test files must showcase this progression.

---

## 3. Worked Example: AC-08 Insufficient Funds Path

### 3.1 Requirement Definition
> **AC-08:** BUY order fails with `InsufficientFundsException` when `quote_price * quantity` exceeds the customer's `available_cash`.

### Step 1: The RED Phase
The test engineer agent authors the test asserting the exact exception and message before any order placement logic exists.

```python
# File: tests/unit/domain/test_order_validation_policy.py
import pytest
from decimal import Decimal
from src.domain.exceptions import InsufficientFundsException
from src.domain.policies.order_validation_policy import OrderValidationPolicy

@pytest.mark.ac("AC-08")
def test_buy_order_fails_with_insufficient_funds_exception():
    """
    AC-08: BUY order must fail with InsufficientFundsException
    when quote_price * quantity exceeds available_cash.
    """
    # Arrange: Customer has 1,000.00 cash; Order requires 150.00 * 10 = 1,500.00
    available_cash = Decimal("1000.00")
    quote_price = Decimal("150.00")
    quantity = Decimal("10")
    
    policy = OrderValidationPolicy()

    # Act & Assert: Expect InsufficientFundsException
    with pytest.raises(InsufficientFundsException) as exc_info:
        policy.validate_buy_funds(
            available_cash=available_cash,
            quote_price=quote_price,
            quantity=quantity
        )
    
    # Assert deterministic error payload and message
    assert "insufficient funds" in str(exc_info.value).lower()
    assert exc_info.value.available_cash == available_cash
    assert exc_info.value.required_funds == Decimal("1500.00")
```

**Test Execution Output (RED):**
```
FAILED tests/unit/domain/test_order_validation_policy.py::test_buy_order_fails_with_insufficient_funds_exception - ModuleNotFoundError: No module named 'src.domain.policies.order_validation_policy'
```

---

### Step 2: The GREEN Phase
The generator agent produces the minimal domain policy and exception definition to satisfy the test.

```python
# File: src/domain/exceptions.py
from decimal import Decimal

class InsufficientFundsException(Exception):
    def __init__(self, available_cash: Decimal, required_funds: Decimal):
        super().__init__(
            f"Insufficient funds: Available cash {available_cash} is less than required {required_funds}."
        )
        self.available_cash = available_cash
        self.required_funds = required_funds
        self.ac_id = "AC-08"
```

```python
# File: src/domain/policies/order_validation_policy.py
from decimal import Decimal
from src.domain.exceptions import InsufficientFundsException

class OrderValidationPolicy:
    @staticmethod
    def validate_buy_funds(available_cash: Decimal, quote_price: Decimal, quantity: Decimal) -> None:
        required_funds = quote_price * quantity
        if required_funds > available_cash:
            raise InsufficientFundsException(
                available_cash=available_cash,
                required_funds=required_funds
            )
```

**Test Execution Output (GREEN):**
```
tests/unit/domain/test_order_validation_policy.py::test_buy_order_fails_with_insufficient_funds_exception PASSED [100%]
```

---

### Step 3: The REFACTOR Phase
The refactoring step hardens the types, enforces fixed-point validation, and guards against negative inputs.

```python
# File: src/domain/policies/order_validation_policy.py
from decimal import Decimal
from src.domain.exceptions import InsufficientFundsException, InvalidOrderInputException

class OrderValidationPolicy:
    """Enforces pre-trade risk and fund availability invariants."""

    @classmethod
    def calculate_order_cost(cls, quote_price: Decimal, quantity: Decimal) -> Decimal:
        if not isinstance(quote_price, Decimal) or not isinstance(quantity, Decimal):
            raise TypeError("Financial computations strictly require Decimal types (NFR-01)")
        if quote_price <= Decimal("0.00") or quantity <= Decimal("0"):
            raise InvalidOrderInputException("Quote price and quantity must be strictly positive")
        return (quote_price * quantity).quantize(Decimal("0.0001"))

    @classmethod
    def validate_buy_funds(cls, available_cash: Decimal, quote_price: Decimal, quantity: Decimal) -> Decimal:
        if not isinstance(available_cash, Decimal):
            raise TypeError("available_cash must be Decimal (NFR-01)")
        
        required_funds = cls.calculate_order_cost(quote_price, quantity)
        if required_funds > available_cash:
            raise InsufficientFundsException(
                available_cash=available_cash,
                required_funds=required_funds
            )
        return required_funds
```

**Re-run All Tests:**
```
pytest tests/ -v
1 passed in 0.04s (100% green, 0 floating point errors)
```

---

## 4. Test Suite Taxonomy & Tagging Rules

Every test in the repository must be categorised and tagged with its corresponding `AC-NN` or `NFR-NN` identifier:

| Test Layer | Directory | Mandatory Tag / Marker | Purpose |
| :--- | :--- | :--- | :--- |
| **Domain Unit Tests** | `tests/unit/domain/` | `@pytest.mark.ac("AC-NN")` | Pure business logic, invariants, Decimal calculations |
| **Service Integration**| `tests/unit/services/` | `@pytest.mark.ac("AC-NN")` | Use-case orchestration, atomic transactions, mock stubs |
| **Controller Tests** | `tests/unit/controllers/`| `@pytest.mark.nfr("NFR-04")` | Role boundary checks (403 vs 200), HTTP DTO mapping |
| **Architecture Tests**| `tests/architecture/` | `@pytest.mark.nfr("NFR-08")` | Structural tests enforcing clean layering boundaries |
| **Playwright UI Tests**| `tests/e2e/` | `@pytest.mark.e2e` | End-to-end user journeys (login, watchlist, trade, dashboard) |

### Minimum Acceptance Floor
- Total Unit Tests: $\ge 20$
- Code Coverage: $\ge 80\%$ required, target $100\%$ on `src/domain/`
- All 10 ACs must have direct test representation.
