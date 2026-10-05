import pytest
from decimal import Decimal
from src.services.stock_service import StockService


@pytest.mark.ac("AC-03")
def test_stock_search_filtering(stock_repo):
    """AC-03: Filter stocks by query, sector, and exchange."""
    service = StockService(stock_repo)
    service.create_stock("CRM", "Salesforce Inc.", "Technology", "NYSE", Decimal("300.0000"))
    service.create_stock("ADBE", "Adobe Inc.", "Technology", "NASDAQ", Decimal("500.0000"))
    service.create_stock("PFE", "Pfizer Inc.", "Healthcare", "NYSE", Decimal("28.0000"))

    # Filter by query
    res = service.search_stocks(query="CRM")
    assert len(res) == 1
    assert res[0]["symbol"] == "CRM"

    # Filter by sector
    tech_stocks = service.search_stocks(sector="Technology")
    assert len(tech_stocks) >= 2
    for s in tech_stocks:
        assert s["sector"] == "Technology"

    # Filter by exchange
    nasdaq_stocks = service.search_stocks(exchange="NASDAQ")
    for s in nasdaq_stocks:
        assert s["exchange"] == "NASDAQ"
