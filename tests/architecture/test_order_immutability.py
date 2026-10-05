import pytest
from decimal import Decimal
from src.domain.entities.order import OrderSide, OrderType
from src.domain.exceptions import HardDeleteProhibitedException
from src.repositories.models import TradeExecutionModel


@pytest.mark.nfr("NFR-02")
def test_trade_execution_cannot_be_updated(order_repo, db_session):
    """NFR-02: Executed trades cannot be updated."""
    order = order_repo.create_order(
        user_id=1,
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("10.0000"),
        quote_price=Decimal("180.0000")
    )

    trade = order_repo.record_execution(
        order_id=order.id,
        executed_price=Decimal("180.0000"),
        quantity=Decimal("10.0000")
    )
    assert trade.id is not None

    raw_model = db_session.query(TradeExecutionModel).filter(TradeExecutionModel.id == trade.id).first()
    assert raw_model is not None

    with pytest.raises(HardDeleteProhibitedException):
        raw_model.executed_price = Decimal("200.0000")
        db_session.flush()


@pytest.mark.nfr("NFR-02")
def test_trade_execution_cannot_be_deleted(order_repo, db_session):
    """NFR-02: Executed trades cannot be deleted."""
    order = order_repo.create_order(
        user_id=1,
        symbol="MSFT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("5.0000"),
        quote_price=Decimal("400.0000")
    )

    trade = order_repo.record_execution(
        order_id=order.id,
        executed_price=Decimal("400.0000"),
        quantity=Decimal("5.0000")
    )
    assert trade.id is not None

    raw_model = db_session.query(TradeExecutionModel).filter(TradeExecutionModel.id == trade.id).first()
    assert raw_model is not None

    with pytest.raises(HardDeleteProhibitedException):
        db_session.delete(raw_model)
        db_session.flush()
