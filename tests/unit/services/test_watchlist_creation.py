import pytest
from decimal import Decimal
from src.services.watchlist_service import WatchlistService
from src.domain.exceptions import WatchlistUpdateException


@pytest.mark.ac("AC-04")
def test_watchlist_creation_with_valid_symbols(watchlist_repo, stock_repo, seed_customer_user):
    """AC-04: Watchlist creation with name and >= 1 valid symbol."""
    stock_repo.create("AMD", "Advanced Micro Devices", "Technology", "NASDAQ", Decimal("150.0000"))
    stock_repo.create("INTC", "Intel Corp.", "Technology", "NASDAQ", Decimal("30.0000"))

    service = WatchlistService(watchlist_repo, stock_repo)
    wl = service.create_watchlist(
        user_id=seed_customer_user.id,
        name="Chipmakers",
        symbols=["AMD", "INTC"]
    )

    assert wl.id is not None
    assert wl.name == "Chipmakers"
    assert "AMD" in wl.symbols
    assert "INTC" in wl.symbols


@pytest.mark.ac("AC-04")
def test_watchlist_creation_with_empty_symbols_rejected(watchlist_repo, stock_repo, seed_customer_user):
    """AC-04: Creating watchlist with empty symbols raises WatchlistUpdateException."""
    service = WatchlistService(watchlist_repo, stock_repo)

    with pytest.raises(WatchlistUpdateException):
        service.create_watchlist(
            user_id=seed_customer_user.id,
            name="Empty List",
            symbols=[]
        )
