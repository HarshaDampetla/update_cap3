import pytest
from decimal import Decimal
from src.services.watchlist_service import WatchlistService
from src.domain.exceptions import WatchlistUpdateException


@pytest.mark.ac("AC-05")
def test_watchlist_update_atomic_rollback_on_single_invalid_symbol(watchlist_repo, stock_repo, seed_customer_user):
    """AC-05: If any symbol in a batch is invalid, the operation rolls back and raises WatchlistUpdateException."""
    stock_repo.create("IBM", "IBM Corp.", "Technology", "NYSE", Decimal("180.0000"))
    stock_repo.create("ORCL", "Oracle Corp.", "Technology", "NYSE", Decimal("130.0000"))

    service = WatchlistService(watchlist_repo, stock_repo)
    wl = service.create_watchlist(
        user_id=seed_customer_user.id,
        name="Legacy Tech",
        symbols=["IBM"]
    )
    assert wl.symbols == ["IBM"]

    # Attempt batch add containing valid "ORCL" and invalid "NONEXISTENT_TICKER"
    with pytest.raises(WatchlistUpdateException) as exc_info:
        service.add_symbols_atomic(
            watchlist_id=wl.id,
            user_id=seed_customer_user.id,
            symbols=["ORCL", "NONEXISTENT_TICKER"]
        )

    assert exc_info.value.code == "WATCHLIST_UPDATE_FAILED"
    assert exc_info.value.ac_id == "AC-05"

    # Verify atomic rollback: ORCL was NOT persisted
    reloaded_wl = watchlist_repo.get_by_id_and_user(wl.id, seed_customer_user.id)
    assert reloaded_wl.symbols == ["IBM"]
    assert "ORCL" not in reloaded_wl.symbols
