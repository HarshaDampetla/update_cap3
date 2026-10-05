import pytest
from decimal import Decimal
from src.services.portfolio_service import PortfolioService


@pytest.mark.ac("AC-09")
@pytest.mark.nfr("NFR-01")
def test_portfolio_service_statistics_calculation(
    portfolio_repo, stock_repo, seed_customer_user
):
    """AC-09: Portfolio statistics computation across multiple customer holdings."""
    stock_repo.create("AAPL", "Apple Inc.", "Technology", "NASDAQ", Decimal("180.2500"))
    stock_repo.create("NVDA", "Nvidia Corp.", "Technology", "NASDAQ", Decimal("120.5000"))

    # Add holdings for customer:
    # 10 AAPL @ 170.00
    # 20 NVDA @ 110.00
    portfolio_repo.add_shares(seed_customer_user.id, "AAPL", Decimal("10.0000"), Decimal("170.0000"))
    portfolio_repo.add_shares(seed_customer_user.id, "NVDA", Decimal("20.0000"), Decimal("110.0000"))

    service = PortfolioService(portfolio_repo, stock_repo)
    stats = service.get_statistics(seed_customer_user.id)

    # Invested: (10*170) + (20*110) = 1700 + 2200 = 3900.0000
    # Current Value: (10*180.25) + (20*120.50) = 1802.50 + 2410.00 = 4212.5000
    # Absolute P&L: 4212.50 - 3900 = 312.5000
    # Percent P&L: (312.50 / 3900) * 100 = 8.0128%
    assert stats["user_id"] == seed_customer_user.id
    assert stats["total_invested"] == "3900.0000"
    assert stats["current_value"] == "4212.5000"
    assert stats["absolute_pnl"] == "312.5000"
    assert stats["percent_pnl"] == "8.0128"


@pytest.mark.ac("AC-09")
def test_portfolio_service_holdings_breakdown(
    portfolio_repo, stock_repo, seed_customer_user
):
    """AC-09: Itemized holdings breakdown."""
    stock_repo.create("MSFT", "Microsoft Corp.", "Technology", "NASDAQ", Decimal("420.0000"))
    portfolio_repo.add_shares(seed_customer_user.id, "MSFT", Decimal("5.0000"), Decimal("400.0000"))

    service = PortfolioService(portfolio_repo, stock_repo)
    breakdown = service.get_holdings_breakdown(seed_customer_user.id)

    assert len(breakdown) == 1
    item = breakdown[0]
    assert item["symbol"] == "MSFT"
    assert item["shares_held"] == "5.0000"
    assert item["total_invested"] == "2000.0000"
    assert item["current_value"] == "2100.0000"
    assert item["absolute_pnl"] == "100.0000"
    assert item["percent_pnl"] == "5.0000"
