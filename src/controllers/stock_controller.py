from typing import Optional, Dict
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from src.services.stock_service import StockService
from src.controllers.deps import get_stock_service

router = APIRouter(prefix="/api", tags=["Stocks & Market"])


class TickRequest(BaseModel):
    delta_map: Optional[Dict[str, float]] = None


@router.get("/stocks")
def get_stocks(
    query: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    exchange: Optional[str] = Query(None),
    include_delisted: bool = Query(False),
    stock_service: StockService = Depends(get_stock_service)
):
    """Customer & public catalog browsing and search with 4-decimal prices."""
    items = stock_service.search_stocks(
        query=query,
        sector=sector,
        exchange=exchange,
        include_delisted=include_delisted
    )
    return {
        "items": items,
        "total": len(items)
    }


@router.get("/stocks/{symbol}")
def get_stock_detail(
    symbol: str,
    stock_service: StockService = Depends(get_stock_service)
):
    stock = stock_service.get_stock(symbol, include_delisted=True)
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "exchange": stock.exchange,
        "current_price": str(stock.current_price),
        "open_price": str(stock.open_price),
        "high_price": str(stock.high_price),
        "low_price": str(stock.low_price),
        "status": stock.status.value,
        "created_at": stock.created_at.isoformat(),
        "updated_at": stock.updated_at.isoformat()
    }


@router.post("/market/tick")
def trigger_market_tick(
    req: Optional[TickRequest] = None,
    stock_service: StockService = Depends(get_stock_service)
):
    """Triggers simulated random-walk market tick."""
    delta_map = req.delta_map if req else None
    updated = stock_service.trigger_market_tick(delta_map=delta_map)
    return {
        "status": "success",
        "ticks_generated": len(updated),
        "stocks": updated
    }
