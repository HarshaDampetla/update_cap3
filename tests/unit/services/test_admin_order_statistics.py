import pytest
from decimal import Decimal
from src.services.analytics_service import AnalyticsService
from src.services.order_service import OrderService


@pytest.mark.ac("AC-10")
def test_admin_order_statistics_telemetry(
    portfolio_repo, stock_repo, order_repo, seed_customer_user
):
    """AC-10: Admin order telemetry groups volume by status and tracks settlement queue."""
    stock_repo.create("NVDA", "Nvidia Corp.", "Technology", "NASDAQ", Decimal("120.0000"))
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("50000.0000"))

    order_svc = OrderService(order_repo, stock_repo, portfolio_repo)
    analytics_svc = AnalyticsService(portfolio_repo, stock_repo, order_repo)

    # 1. Place 1 executed order
    order_svc.place_order(
        user_id=seed_customer_user.id,
        symbol="NVDA",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("10.0000"),
        auto_execute=True
    )

    # 2. Place 1 pending order
    order_svc.place_order(
        user_id=seed_customer_user.id,
        symbol="NVDA",
        side_str="BUY",
        order_type_str="LIMIT",
        quantity=Decimal("5.0000"),
        limit_price=Decimal("110.0000"),
        auto_execute=False
    )

    stats = analytics_svc.get_admin_order_statistics()

    assert stats["daily_volume_by_status"]["EXECUTED"] >= 1
    assert stats["daily_volume_by_status"]["PENDING"] >= 1
    assert stats["settlement_queue_count"] >= 1
    assert len(stats["most_traded_symbols"]) >= 1
    assert stats["most_traded_symbols"][0]["symbol"] == "NVDA"
