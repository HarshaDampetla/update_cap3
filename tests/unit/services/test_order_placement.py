import pytest
from decimal import Decimal
from src.services.order_service import OrderService
from src.domain.entities.order import OrderStatus, OrderSide, OrderType
from src.domain.exceptions import InsufficientFundsException, InvalidOrderStateException


@pytest.mark.ac("AC-06")
def test_order_placement_enters_pending_with_server_timestamp(
    order_repo, stock_repo, portfolio_repo, seed_customer_user
):
    """AC-06: Order enters PENDING state with server-side UTC timestamp."""
    stock_repo.create("AMD", "AMD Corp.", "Technology", "NASDAQ", Decimal("150.0000"))
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("50000.0000"))

    service = OrderService(order_repo, stock_repo, portfolio_repo)
    order = service.place_order(
        user_id=seed_customer_user.id,
        symbol="AMD",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("10.0000"),
        auto_execute=False  # Keep in PENDING state to verify AC-06
    )

    assert order.id is not None
    assert order.status == OrderStatus.PENDING
    assert order.server_timestamp is not None
    assert order.symbol == "AMD"
    assert order.quantity == Decimal("10.0000")


@pytest.mark.ac("AC-08")
def test_buy_order_insufficient_funds_rejection_leaves_cash_intact(
    order_repo, stock_repo, portfolio_repo, seed_customer_user
):
    """AC-08: BUY order fails with InsufficientFundsException when funds deficient; cash balance untouched."""
    stock_repo.create("EQIX", "Equinix Inc.", "Technology", "NASDAQ", Decimal("800.0000"))
    # Customer only has $1,000 cash; 2 shares require $1,600
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("1000.0000"))

    service = OrderService(order_repo, stock_repo, portfolio_repo)

    with pytest.raises(InsufficientFundsException) as exc_info:
        service.place_order(
            user_id=seed_customer_user.id,
            symbol="EQIX",
            side_str="BUY",
            order_type_str="MARKET",
            quantity=Decimal("2.0000")
        )

    assert exc_info.value.code == "INSUFFICIENT_FUNDS"
    assert exc_info.value.ac_id == "AC-08"

    # Verify customer cash remains untouched
    assert portfolio_repo.get_cash(seed_customer_user.id) == Decimal("1000.0000")


@pytest.mark.ac("AC-07")
@pytest.mark.nfr("NFR-02")
def test_order_execution_and_append_only_record(
    order_repo, stock_repo, portfolio_repo, seed_customer_user
):
    """AC-07 & NFR-02: Executed order transitions to EXECUTED and produces trade record."""
    stock_repo.create("INTC", "Intel Corp.", "Technology", "NASDAQ", Decimal("30.0000"))
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("1000.0000"))

    service = OrderService(order_repo, stock_repo, portfolio_repo)
    executed_order = service.place_order(
        user_id=seed_customer_user.id,
        symbol="INTC",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("10.0000"),
        auto_execute=True
    )

    assert executed_order.status == OrderStatus.EXECUTED
    assert executed_order.executed_at is not None

    # Cash deducted: 1000 - (30 * 10) = 700
    assert portfolio_repo.get_cash(seed_customer_user.id) == Decimal("700.0000")

    # Holding created
    holding = portfolio_repo.get_holding(seed_customer_user.id, "INTC")
    assert holding.shares_held == Decimal("10.0000")
    assert holding.average_buy_price == Decimal("30.0000")

    # Append-only trade record exists
    execution = order_repo.get_execution(executed_order.id)
    assert execution is not None
    assert execution.executed_price == Decimal("30.0000")
    assert execution.total_value == Decimal("300.0000")


@pytest.mark.ac("AC-07")
def test_order_cancellation_and_terminal_state_rejection(
    order_repo, stock_repo, portfolio_repo, seed_customer_user
):
    """AC-07: Cancelling pending order transitions to CANCELLED; cannot transition once executed."""
    stock_repo.create("QCOM", "Qualcomm Inc.", "Technology", "NASDAQ", Decimal("160.0000"))
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("10000.0000"))

    service = OrderService(order_repo, stock_repo, portfolio_repo)

    # 1. Place order without auto_execute
    pending_order = service.place_order(
        user_id=seed_customer_user.id,
        symbol="QCOM",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("5.0000"),
        auto_execute=False
    )
    assert pending_order.status == OrderStatus.PENDING

    # 2. Cancel order
    cancelled_order = service.cancel_order(pending_order.id, seed_customer_user.id)
    assert cancelled_order.status == OrderStatus.CANCELLED

    # 3. Attempting to cancel already CANCELLED order raises InvalidOrderStateException
    with pytest.raises(InvalidOrderStateException) as exc_info:
        service.cancel_order(pending_order.id, seed_customer_user.id)
    assert exc_info.value.code == "INVALID_ORDER_STATE"
    assert exc_info.value.ac_id == "AC-07"
