import pytest
from decimal import Decimal
from src.domain.entities.stock import StockStatus
from src.domain.exceptions import HardDeleteProhibitedException
from src.repositories.models import StockModel


@pytest.mark.ac("AC-03")
def test_stock_soft_delete_preserves_row_with_deleted_status(stock_repo, db_session):
    """AC-03: Deleting a stock moves it to DELETED status; row persists in database."""
    # 1. Create stock
    stock = stock_repo.create(
        symbol="ORCL",
        name="Oracle Corp.",
        sector="Technology",
        exchange="NYSE",
        initial_price=Decimal("125.0000")
    )
    assert stock.status == StockStatus.ACTIVE

    # 2. Soft-delete
    deleted_stock = stock_repo.soft_delete("ORCL")
    assert deleted_stock.status == StockStatus.DELETED

    # 3. Assert database row still physically exists
    raw_model = db_session.query(StockModel).filter(StockModel.symbol == "ORCL").first()
    assert raw_model is not None
    assert raw_model.status == "DELETED"

    # 4. Standard search omits soft-deleted stock
    active_search = stock_repo.search(query="ORCL", include_delisted=False)
    assert len(active_search) == 0

    # 5. Guard against hard delete
    with pytest.raises(HardDeleteProhibitedException):
        stock_repo.hard_delete_prohibited("ORCL")
