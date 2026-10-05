import pytest
from src.domain.exceptions import WatchlistLimitExceededException, WatchlistUpdateException
from src.domain.policies.watchlist_limit_policy import WatchlistLimitPolicy


@pytest.mark.ac("AC-04")
def test_watchlist_creation_allowed_below_ten():
    """AC-04: Customer with < 10 watchlists can create a new watchlist."""
    WatchlistLimitPolicy.validate_creation(
        current_watchlist_count=9,
        name="Crypto Proxies",
        symbols=["COIN", "MSTR"]
    )


@pytest.mark.ac("AC-04")
def test_watchlist_creation_rejected_at_ten():
    """AC-04: Customer already holding 10 watchlists is rejected."""
    with pytest.raises(WatchlistLimitExceededException) as exc_info:
        WatchlistLimitPolicy.validate_creation(
            current_watchlist_count=10,
            name="Eleventh Watchlist",
            symbols=["AAPL"]
        )

    assert exc_info.value.code == "WATCHLIST_LIMIT_EXCEEDED"
    assert exc_info.value.ac_id == "AC-04"
    assert exc_info.value.current_count == 10
    assert exc_info.value.max_limit == 10


@pytest.mark.ac("AC-04")
def test_watchlist_creation_requires_name_and_symbols():
    """AC-04: Empty name or empty symbol list is rejected."""
    with pytest.raises(WatchlistUpdateException) as exc_info:
        WatchlistLimitPolicy.validate_creation(
            current_watchlist_count=2,
            name="",
            symbols=["AAPL"]
        )
    assert "name cannot be empty" in str(exc_info.value).lower()

    with pytest.raises(WatchlistUpdateException) as exc_info:
        WatchlistLimitPolicy.validate_creation(
            current_watchlist_count=2,
            name="Valid Name",
            symbols=[]
        )
    assert "at least one symbol" in str(exc_info.value).lower()
