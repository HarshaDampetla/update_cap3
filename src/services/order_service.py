from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List
from src.domain.entities.order import Order, OrderSide, OrderType, OrderStatus, TradeExecution
from src.domain.policies.order_validation_policy import OrderValidationPolicy
from src.domain.exceptions import (
    StockNotFoundException,
    InsufficientFundsException,
    InvalidOrderStateException,
    InvalidOrderInputException
)
from src.repositories.order_repository import OrderRepository
from src.repositories.stock_repository import StockRepository
from src.repositories.portfolio_repository import PortfolioRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        stock_repo: StockRepository,
        portfolio_repo: PortfolioRepository
    ):
        self.order_repo = order_repo
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo

    def place_order(
        self,
        user_id: int,
        symbol: str,
        side_str: str,
        order_type_str: str,
        quantity: Decimal,
        limit_price: Optional[Decimal] = None,
        auto_execute: bool = True
    ) -> Order:
        """
        Places order with pre-trade checks (AC-08), enters PENDING with server timestamp (AC-06),
        and optionally coordinates with execution stub (AC-07, NFR-02).
        """
        sym = symbol.upper().strip()
        stock = self.stock_repo.get_by_symbol(sym, include_delisted=False)
        if not stock:
            raise StockNotFoundException(sym)

        try:
            side = OrderSide(side_str.upper())
            order_type = OrderType(order_type_str.upper())
        except ValueError as e:
            raise InvalidOrderInputException(f"Invalid side or order type: {e}")

        qty = Decimal(str(quantity)).quantize(Decimal("0.0001"))
        if qty <= Decimal("0.0000"):
            raise InvalidOrderInputException("Quantity must be greater than zero.")

        # Determine quote price
        quote_p = stock.current_price
        if order_type == OrderType.LIMIT:
            if limit_price is None or Decimal(str(limit_price)) <= Decimal("0.0000"):
                raise InvalidOrderInputException("Limit order requires positive limit_price.")
            limit_p = Decimal(str(limit_price)).quantize(Decimal("0.0001"))
        else:
            limit_p = None

        effective_price = limit_p if (order_type == OrderType.LIMIT and limit_p is not None) else quote_p

        # AC-08: Pre-trade cash verification for BUY orders
        if side == OrderSide.BUY:
            available_cash = self.portfolio_repo.get_cash(user_id)
            # Will raise InsufficientFundsException if required funds > available_cash
            OrderValidationPolicy.validate_buy_funds(
                available_cash=available_cash,
                quote_price=effective_price,
                quantity=qty
            )
        elif side == OrderSide.SELL:
            # Check customer has sufficient shares
            holding = self.portfolio_repo.get_holding(user_id, sym)
            if not holding or holding.shares_held < qty:
                available_shares = holding.shares_held if holding else Decimal("0.0000")
                raise InsufficientFundsException(
                    available_cash=available_shares,
                    required_funds=qty
                )

        # AC-06: Create order with status PENDING and server-side UTC timestamp
        order = self.order_repo.create_order(
            user_id=user_id,
            symbol=sym,
            side=side,
            order_type=order_type,
            quantity=qty,
            quote_price=quote_p,
            limit_price=limit_p
        )

        # AC-07 & NFR-02: Stub execution matching
        if auto_execute:
            order = self.execute_order(order.id, fill_price=effective_price)

        return order

    def execute_order(self, order_id: int, fill_price: Optional[Decimal] = None) -> Order:
        """AC-07: Transition PENDING -> EXECUTED and record append-only trade execution."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found.")

        price = fill_price if fill_price is not None else order.quote_price
        price = Decimal(str(price)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        cost = (order.quantity * price).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # Deduct or credit cash & update holdings
        if order.side == OrderSide.BUY:
            self.portfolio_repo.deduct_cash(order.user_id, cost)
            self.portfolio_repo.add_shares(order.user_id, order.symbol, order.quantity, price)
        else:
            self.portfolio_repo.reduce_shares(order.user_id, order.symbol, order.quantity)
            self.portfolio_repo.credit_cash(order.user_id, cost)

        # Transition order to EXECUTED
        executed_order = self.order_repo.update_status(order_id, OrderStatus.EXECUTED)

        # NFR-02: Record immutable trade execution
        self.order_repo.record_execution(
            order_id=order_id,
            executed_price=price,
            quantity=order.quantity
        )

        return executed_order

    def cancel_order(self, order_id: int, user_id: int) -> Order:
        """AC-07: Transition PENDING -> CANCELLED. Rejects if in terminal state."""
        order = self.order_repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise ValueError(f"Order {order_id} not found for user {user_id}.")

        return self.order_repo.update_status(order_id, OrderStatus.CANCELLED)

    def list_orders(self, user_id: int) -> List[Order]:
        return self.order_repo.list_by_user(user_id)
