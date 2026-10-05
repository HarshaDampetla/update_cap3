import pytest
from decimal import Decimal
from src.domain.exceptions import InsufficientFundsException, InvalidOrderInputException
from src.domain.policies.order_validation_policy import OrderValidationPolicy


@pytest.mark.ac("AC-08")
def test_buy_order_fails_with_insufficient_funds_exception():
    """AC-08: BUY order fails with InsufficientFundsException when quote_price * quantity exceeds available_cash."""
    available_cash = Decimal("1000.00")
    quote_price = Decimal("150.00")
    quantity = Decimal("10")

    with pytest.raises(InsufficientFundsException) as exc_info:
        OrderValidationPolicy.validate_buy_funds(
            available_cash=available_cash,
            quote_price=quote_price,
            quantity=quantity
        )

    assert "fails" in str(exc_info.value).lower()
    assert exc_info.value.available_cash == available_cash
    assert exc_info.value.required_funds == Decimal("1500.0000")
    assert exc_info.value.code == "INSUFFICIENT_FUNDS"
    assert exc_info.value.ac_id == "AC-08"


@pytest.mark.ac("AC-08")
def test_buy_order_succeeds_when_funds_sufficient():
    """AC-08: BUY order validates and returns required funds when cash is sufficient."""
    available_cash = Decimal("2000.00")
    quote_price = Decimal("150.00")
    quantity = Decimal("10")

    required = OrderValidationPolicy.validate_buy_funds(
        available_cash=available_cash,
        quote_price=quote_price,
        quantity=quantity
    )
    assert required == Decimal("1500.0000")


@pytest.mark.nfr("NFR-01")
def test_order_validation_rejects_non_decimal_types():
    """NFR-01: Financial computations strictly require Decimal types."""
    with pytest.raises(TypeError):
        OrderValidationPolicy.validate_buy_funds(
            available_cash=1000.0,  # float banned
            quote_price=Decimal("150.00"),
            quantity=Decimal("10")
        )

    with pytest.raises(TypeError):
        OrderValidationPolicy.calculate_order_cost(
            quote_price=150.0,  # float banned
            quantity=Decimal("10")
        )


@pytest.mark.ac("AC-06")
def test_order_validation_rejects_negative_or_zero_values():
    """AC-06: Non-positive price or quantity is rejected."""
    with pytest.raises(InvalidOrderInputException):
        OrderValidationPolicy.calculate_order_cost(
            quote_price=Decimal("0.00"),
            quantity=Decimal("10")
        )

    with pytest.raises(InvalidOrderInputException):
        OrderValidationPolicy.calculate_order_cost(
            quote_price=Decimal("100.00"),
            quantity=Decimal("-1")
        )
