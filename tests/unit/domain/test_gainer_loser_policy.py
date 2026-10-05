import pytest
from decimal import Decimal
from src.domain.policies.gainer_loser_policy import GainerLoserPolicy


@pytest.mark.ac("AC-10")
def test_gainer_loser_policy_ranking():
    """AC-10: Correct ranking of top gainers and losers from holdings."""
    holdings = [
        {"symbol": "NVDA", "shares_held": Decimal("20"), "current_price": Decimal("120.50"), "open_price": Decimal("115.00")}, # +4.7826%
        {"symbol": "AAPL", "shares_held": Decimal("10"), "current_price": Decimal("180.25"), "open_price": Decimal("178.50")}, # +0.9804%
        {"symbol": "MSFT", "shares_held": Decimal("5"), "current_price": Decimal("420.00"), "open_price": Decimal("425.00")},  # -1.1765%
        {"symbol": "GOOGL", "shares_held": Decimal("8"), "current_price": Decimal("175.00"), "open_price": Decimal("170.00")}, # +2.9412%
        {"symbol": "AMZN", "shares_held": Decimal("15"), "current_price": Decimal("185.00"), "open_price": Decimal("190.00")}, # -2.6316%
        {"symbol": "TSLA", "shares_held": Decimal("12"), "current_price": Decimal("250.00"), "open_price": Decimal("240.00")}, # +4.1667%
        {"symbol": "XOM", "shares_held": Decimal("7"), "current_price": Decimal("110.00"), "open_price": Decimal("115.00")},   # -4.3478%
    ]

    movers = GainerLoserPolicy.rank_movers(holdings)

    # Top gainers should be capped at 5 and sorted descending
    gainers = movers["top_gainers"]
    assert len(gainers) == 5
    assert gainers[0]["symbol"] == "NVDA"
    assert gainers[1]["symbol"] == "TSLA"
    assert gainers[2]["symbol"] == "GOOGL"
    assert gainers[3]["symbol"] == "AAPL"
    assert gainers[4]["symbol"] == "MSFT"

    # Top losers should be capped at 5 and sorted ascending (worst first)
    losers = movers["top_losers"]
    assert len(losers) == 5
    assert losers[0]["symbol"] == "XOM"   # -4.3478%
    assert losers[1]["symbol"] == "AMZN"  # -2.6316%
    assert losers[2]["symbol"] == "MSFT"  # -1.1765%
