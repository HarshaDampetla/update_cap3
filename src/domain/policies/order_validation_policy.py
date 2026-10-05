from decimal import Decimal
from src.domain.exceptions import InsufficientFundsException, InvalidOrderInputException


class OrderValidationPolicy:
    """Enforces pre-trade risk, decimal math, and fund availability invariants (AC-08, NFR-01)."""

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
