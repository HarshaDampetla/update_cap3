import pytest
from decimal import Decimal
from src.domain.policies.portfolio_pnl_policy import PortfolioPnLPolicy


@pytest.mark.ac("AC-09")
def test_portfolio_empty_holdings_zero_division_guard():
    """AC-09: Customer with zero holdings returns $0.0000 without ZeroDivisionError."""
    summary = PortfolioPnLPolicy.calculate_summary([])

    assert summary["total_invested"] == Decimal("0.0000")
    assert summary["current_value"] == Decimal("0.0000")
    assert summary["absolute_pnl"] == Decimal("0.0000")
    assert summary["percent_pnl"] == Decimal("0.0000")
