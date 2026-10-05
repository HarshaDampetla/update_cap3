import pytest
from decimal import Decimal
from src.services.stock_service import StockService
from src.domain.entities.stock import StockStatus
from src.domain.exceptions import StockAlreadyExistsException, StockNotFoundException


@pytest.mark.ac("AC-03")
def test_stock_creation_and_update(stock_repo):
    """AC-03: Stock catalog CRUD operations."""
    service = StockService(stock_repo)

    stock = service.create_stock(
        symbol="NFLX",
        name="Netflix Inc.",
        sector="Communication Services",
        exchange="NASDAQ",
        initial_price=Decimal("600.0000"),
        open_price=Decimal("595.0000")
    )
    assert stock.symbol == "NFLX"
    assert stock.current_price == Decimal("600.0000")
    assert stock.status == StockStatus.ACTIVE

    # Update metadata
    updated = service.update_stock(
        symbol="NFLX",
        name="Netflix Entertainment Inc.",
        sector="Technology"
    )
    assert updated.name == "Netflix Entertainment Inc."
    assert updated.sector == "Technology"


@pytest.mark.ac("AC-03")
def test_duplicate_stock_creation_rejected(stock_repo):
    """AC-03: Duplicate symbol raises StockAlreadyExistsException."""
    service = StockService(stock_repo)
    service.create_stock("DIS", "Walt Disney Co.", "Entertainment", "NYSE", Decimal("110.0000"))

    with pytest.raises(StockAlreadyExistsException):
        service.create_stock("DIS", "Disney Inc.", "Entertainment", "NYSE", Decimal("112.0000"))


@pytest.mark.ac("AC-03")
def test_nonexistent_stock_update_raises_not_found(stock_repo):
    """AC-03: Updating non-existent stock raises StockNotFoundException."""
    service = StockService(stock_repo)
    with pytest.raises(StockNotFoundException):
        service.update_stock("UNKNOWN_SYM", name="New Name")
