import pytest
from decimal import Decimal
from src.domain.policies.gainer_loser_policy import GainerLoserPolicy


@pytest.mark.ac("AC-10")
def test_gainer_loser_fewer_than_five_holdings():
    """AC-10: Handles customer portfolios with fewer than 5 holdings gracefully."""
    holdings = [
        {"symbol": "NVDA", "shares_held": Decimal("20"), "current_price": Decimal("120.50"), "open_price": Decimal("115.00")},
        {"symbol": "AAPL", "shares_held": Decimal("10"), "current_price": Decimal("180.25"), "open_price": Decimal("178.50")}
    ]

    movers = GainerLoserPolicy.rank_movers(holdings)

    assert len(movers["top_gainers"]) == 2
    assert len(movers["top_losers"]) == 2
    assert movers["top_gainers"][0]["symbol"] == "NVDA"
    assert movers["top_gainers"][1]["symbol"] == "AAPL"


@pytest.mark.ac("AC-10")
def test_gainer_loser_zero_holdings():
    """AC-10: Handles 0 holdings with empty arrays."""
    movers = GainerLoserPolicy.rank_movers([])
    assert movers["top_gainers"] == []
    assert movers["top_losers"] == []
