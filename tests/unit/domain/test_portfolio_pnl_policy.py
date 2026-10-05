import pytest
from decimal import Decimal
from src.domain.policies.portfolio_pnl_policy import PortfolioPnLPolicy


@pytest.mark.ac("AC-09")
@pytest.mark.nfr("NFR-01")
def test_portfolio_pnl_calculation_exact_decimals():
    """AC-09 & NFR-01: Verifies exact fixed-point P&L calculation matching spec baseline."""
    holdings = [
        {
            "symbol": "AAPL",
            "shares_held": Decimal("10.0000"),
            "average_buy_price": Decimal("170.0000"),
            "current_price": Decimal("180.2500")
        },
        {
            "symbol": "NVDA",
            "shares_held": Decimal("20.0000"),
            "average_buy_price": Decimal("110.0000"),
            "current_price": Decimal("120.5000")
        },
        {
            "symbol": "MSFT",
            "shares_held": Decimal("5.0000"),
            "average_buy_price": Decimal("400.0000"),
            "current_price": Decimal("420.0000")
        }
    ]

    summary = PortfolioPnLPolicy.calculate_summary(holdings)

    assert summary["total_invested"] == Decimal("5900.0000")
    assert summary["current_value"] == Decimal("6312.5000")
    assert summary["absolute_pnl"] == Decimal("412.5000")
    assert summary["percent_pnl"] == Decimal("6.9915")


@pytest.mark.ac("AC-09")
def test_position_pnl_calculation():
    """AC-09: Single position P&L calculation."""
    res = PortfolioPnLPolicy.calculate_position_pnl(
        shares_held=Decimal("10.0000"),
        avg_price=Decimal("170.0000"),
        current_price=Decimal("180.2500")
    )
    assert res["total_invested"] == Decimal("1700.0000")
    assert res["current_value"] == Decimal("1802.5000")
    assert res["absolute_pnl"] == Decimal("102.5000")
    assert res["percent_pnl"] == Decimal("6.0294")
