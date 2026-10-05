import pytest
from decimal import Decimal
from src.services.analytics_service import AnalyticsService
from src.services.order_service import OrderService


@pytest.mark.ac("AC-10")
def test_analytics_service_daily_performance_and_sector_exposure(
    portfolio_repo, stock_repo, order_repo, seed_customer_user
):
    """Test full analytics service daily performance and sector exposure aggregation."""
    # Create stocks in different sectors with varying price movements
    s1 = stock_repo.create("AAPL", "Apple Inc.", "Technology", "NASDAQ", Decimal("150.0000"), Decimal("140.0000"))
    s2 = stock_repo.create("XOM", "Exxon Mobil", "Energy", "NYSE", Decimal("100.0000"), Decimal("110.0000"))
    
    portfolio_repo.init_cash(seed_customer_user.id, Decimal("50000.0000"))
    order_svc = OrderService(order_repo, stock_repo, portfolio_repo)
    analytics_svc = AnalyticsService(portfolio_repo, stock_repo, order_repo)

    # Buy AAPL and XOM
    order_svc.place_order(
        user_id=seed_customer_user.id,
        symbol="AAPL",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("10.0000"),
        auto_execute=True
    )
    order_svc.place_order(
        user_id=seed_customer_user.id,
        symbol="XOM",
        side_str="BUY",
        order_type_str="MARKET",
        quantity=Decimal("5.0000"),
        auto_execute=True
    )

    # 1. Daily performance
    perf = analytics_svc.get_daily_performance(seed_customer_user.id)
    assert perf["user_id"] == seed_customer_user.id
    assert len(perf["top_gainers"]) >= 1
    assert len(perf["top_losers"]) >= 1
    assert perf["top_gainers"][0]["symbol"] == "AAPL"
    assert perf["top_losers"][0]["symbol"] == "XOM"

    # 2. Sector exposure
    exposure = analytics_svc.get_sector_exposure(seed_customer_user.id)
    assert exposure["user_id"] == seed_customer_user.id
    assert Decimal(exposure["total_market_value"]) > Decimal("0")
    sectors = {s["sector"]: s for s in exposure["sectors"]}
    assert "Technology" in sectors
    assert "Energy" in sectors
