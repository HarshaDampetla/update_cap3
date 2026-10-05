import random
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any
from src.domain.entities.stock import Stock, StockStatus
from src.domain.exceptions import StockAlreadyExistsException, StockNotFoundException
from src.repositories.stock_repository import StockRepository


class StockService:
    def __init__(self, stock_repo: StockRepository):
        self.stock_repo = stock_repo

    def create_stock(
        self,
        symbol: str,
        name: str,
        sector: str,
        exchange: str,
        initial_price: Decimal,
        open_price: Optional[Decimal] = None
    ) -> Stock:
        """AC-03: Create a new stock in the catalog."""
        sym = symbol.upper().strip()
        existing = self.stock_repo.get_by_symbol(sym, include_delisted=True)
        if existing:
            raise StockAlreadyExistsException(sym)

        price = Decimal(str(initial_price)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        open_p = Decimal(str(open_price)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if open_price is not None else price

        return self.stock_repo.create(
            symbol=sym,
            name=name,
            sector=sector,
            exchange=exchange,
            initial_price=price,
            open_price=open_p
        )

    def update_stock(
        self,
        symbol: str,
        name: Optional[str] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        status: Optional[StockStatus] = None
    ) -> Stock:
        """AC-03: Update stock metadata."""
        sym = symbol.upper().strip()
        stock = self.stock_repo.get_by_symbol(sym, include_delisted=True)
        if not stock:
            raise StockNotFoundException(sym)

        return self.stock_repo.update(
            symbol=sym,
            name=name,
            sector=sector,
            exchange=exchange,
            status=status
        )

    def soft_delete_stock(self, symbol: str) -> Stock:
        """AC-03: Soft-delete stock into DELETED status. Never hard-deleted."""
        sym = symbol.upper().strip()
        stock = self.stock_repo.get_by_symbol(sym, include_delisted=True)
        if not stock:
            raise StockNotFoundException(sym)

        return self.stock_repo.soft_delete(sym)

    def get_stock(self, symbol: str, include_delisted: bool = False) -> Stock:
        sym = symbol.upper().strip()
        stock = self.stock_repo.get_by_symbol(sym, include_delisted=include_delisted)
        if not stock:
            raise StockNotFoundException(sym)
        return stock

    def search_stocks(
        self,
        query: Optional[str] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        include_delisted: bool = False
    ) -> List[Dict[str, Any]]:
        stocks = self.stock_repo.search(
            query=query,
            sector=sector,
            exchange=exchange,
            include_delisted=include_delisted
        )
        results = []
        for s in stocks:
            diff = s.current_price - s.open_price
            if s.open_price > Decimal("0.0000"):
                pct = ((diff / s.open_price) * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                pct_str = f"{'+' if pct >= 0 else ''}{pct}%"
            else:
                pct_str = "0.00%"

            results.append({
                "symbol": s.symbol,
                "name": s.name,
                "sector": s.sector,
                "exchange": s.exchange,
                "current_price": str(s.current_price),
                "open_price": str(s.open_price),
                "high_price": str(s.high_price),
                "low_price": str(s.low_price),
                "change_percent": pct_str,
                "status": s.status.value
            })
        return results

    def trigger_market_tick(self, delta_map: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Simulates price ticks using random walk: P(t+1) = max(0.01, P(t) * (1 + delta))."""
        stocks = self.stock_repo.search(include_delisted=False)
        updated_stocks = []
        for s in stocks:
            if delta_map and s.symbol in delta_map:
                delta = Decimal(str(delta_map[s.symbol]))
            else:
                # Bounded uniform random walk in [-0.03, +0.03]
                val = random.uniform(-0.03, 0.03)
                delta = Decimal(str(round(val, 4)))

            new_price = (s.current_price * (Decimal("1") + delta)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if new_price < Decimal("0.0100"):
                new_price = Decimal("0.0100")

            updated = self.stock_repo.update_price(
                symbol=s.symbol,
                current_price=new_price,
                high_price=max(s.high_price, new_price),
                low_price=min(s.low_price, new_price)
            )
            updated_stocks.append({
                "symbol": updated.symbol,
                "old_price": str(s.current_price),
                "new_price": str(updated.current_price),
                "high": str(updated.high_price),
                "low": str(updated.low_price)
            })
        return updated_stocks
