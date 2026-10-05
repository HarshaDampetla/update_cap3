import pytest
from decimal import Decimal
from src.services.watchlist_service import WatchlistService


@pytest.mark.ac("AC-05")
def test_watchlist_rename_and_remove_symbol(watchlist_repo, stock_repo, seed_customer_user):
    """AC-05: Rename watchlist and remove individual symbols."""
    stock_repo.create("UBER", "Uber Technologies", "Technology", "NYSE", Decimal("70.0000"))
    stock_repo.create("LYFT", "Lyft Inc.", "Technology", "NASDAQ", Decimal("15.0000"))

    service = WatchlistService(watchlist_repo, stock_repo)
    wl = service.create_watchlist(
        user_id=seed_customer_user.id,
        name="Rideshare",
        symbols=["UBER", "LYFT"]
    )

    # Rename
    renamed = service.rename_watchlist(wl.id, seed_customer_user.id, "Mobility Services")
    assert renamed.name == "Mobility Services"

    # Remove symbol
    modified = service.remove_symbol(wl.id, seed_customer_user.id, "LYFT")
    assert "LYFT" not in modified.symbols
    assert "UBER" in modified.symbols

    # Delete watchlist
    deleted = service.delete_watchlist(wl.id, seed_customer_user.id)
    assert deleted is True
    assert watchlist_repo.get_by_id_and_user(wl.id, seed_customer_user.id) is None
