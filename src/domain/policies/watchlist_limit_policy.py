from typing import List
from src.domain.exceptions import WatchlistLimitExceededException, WatchlistUpdateException


class WatchlistLimitPolicy:
    """Enforces watchlist count limit and symbol requirements (AC-04)."""

    MAX_WATCHLISTS_PER_CUSTOMER = 10

    @classmethod
    def validate_creation(cls, current_watchlist_count: int, name: str, symbols: List[str]) -> None:
        if current_watchlist_count >= cls.MAX_WATCHLISTS_PER_CUSTOMER:
            raise WatchlistLimitExceededException(
                current_count=current_watchlist_count,
                max_limit=cls.MAX_WATCHLISTS_PER_CUSTOMER
            )

        if not name or not name.strip():
            raise WatchlistUpdateException("Watchlist name cannot be empty.")

        if not symbols or len(symbols) == 0:
            raise WatchlistUpdateException("Watchlist must contain at least one symbol.")
