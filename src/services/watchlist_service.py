from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from src.domain.entities.watchlist import Watchlist
from src.domain.policies.watchlist_limit_policy import WatchlistLimitPolicy
from src.domain.exceptions import WatchlistUpdateException
from src.repositories.watchlist_repository import WatchlistRepository
from src.repositories.stock_repository import StockRepository


class WatchlistService:
    def __init__(self, watchlist_repo: WatchlistRepository, stock_repo: StockRepository):
        self.watchlist_repo = watchlist_repo
        self.stock_repo = stock_repo

    def create_watchlist(self, user_id: int, name: str, symbols: List[str]) -> Watchlist:
        """AC-04 & AC-05: Enforce count <= 10, valid symbols, and atomic creation."""
        current_count = self.watchlist_repo.count_by_user_id(user_id)
        WatchlistLimitPolicy.validate_creation(current_count, name, symbols)

        return self.watchlist_repo.create(user_id=user_id, name=name, symbols=symbols)

    def list_watchlists_with_items(self, user_id: int) -> List[Dict[str, Any]]:
        watchlists = self.watchlist_repo.list_by_user(user_id)
        results = []
        for wl in watchlists:
            items = []
            for sym in wl.symbols:
                stock = self.stock_repo.get_by_symbol(sym, include_delisted=True)
                if stock:
                    diff = stock.current_price - stock.open_price
                    if stock.open_price > Decimal("0.0000"):
                        pct = ((diff / stock.open_price) * Decimal("100")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                        pct_str = f"{'+' if pct >= 0 else ''}{pct}%"
                    else:
                        pct_str = "0.00%"
                    items.append({
                        "symbol": stock.symbol,
                        "name": stock.name,
                        "current_price": str(stock.current_price),
                        "change_percent": pct_str
                    })
                else:
                    items.append({
                        "symbol": sym,
                        "name": sym,
                        "current_price": "0.0000",
                        "change_percent": "0.00%"
                    })
            results.append({
                "id": wl.id,
                "name": wl.name,
                "symbols": wl.symbols,
                "items": items,
                "created_at": wl.created_at.isoformat()
            })
        return results

    def rename_watchlist(self, watchlist_id: int, user_id: int, new_name: str) -> Watchlist:
        return self.watchlist_repo.rename(watchlist_id, user_id, new_name)

    def add_symbols_atomic(self, watchlist_id: int, user_id: int, symbols: List[str]) -> Watchlist:
        """AC-05: Atomic batch symbol addition."""
        return self.watchlist_repo.add_symbols_atomic(watchlist_id, user_id, symbols)

    def remove_symbol(self, watchlist_id: int, user_id: int, symbol: str) -> Watchlist:
        return self.watchlist_repo.remove_symbol(watchlist_id, user_id, symbol)

    def delete_watchlist(self, watchlist_id: int, user_id: int) -> bool:
        return self.watchlist_repo.delete_watchlist(watchlist_id, user_id)
