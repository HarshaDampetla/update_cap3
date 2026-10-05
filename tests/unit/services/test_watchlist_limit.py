import pytest
from decimal import Decimal
from src.services.watchlist_service import WatchlistService
from src.domain.exceptions import WatchlistLimitExceededException


@pytest.mark.ac("AC-04")
def test_watchlist_ten_limit_enforced(watchlist_repo, stock_repo, seed_customer_user):
    """AC-04: Customer can create up to 10 watchlists; 11th is rejected with WatchlistLimitExceededException."""
    stock_repo.create("CSCO", "Cisco Systems", "Technology", "NASDAQ", Decimal("50.0000"))
    service = WatchlistService(watchlist_repo, stock_repo)

    # Create 10 watchlists
    for i in range(1, 11):
        service.create_watchlist(
            user_id=seed_customer_user.id,
            name=f"Watchlist {i}",
            symbols=["CSCO"]
        )

    assert watchlist_repo.count_by_user_id(seed_customer_user.id) == 10

    # Attempt 11th creation
    with pytest.raises(WatchlistLimitExceededException) as exc_info:
        service.create_watchlist(
            user_id=seed_customer_user.id,
            name="Watchlist 11",
            symbols=["CSCO"]
        )

    assert exc_info.value.code == "WATCHLIST_LIMIT_EXCEEDED"
    assert exc_info.value.ac_id == "AC-04"
