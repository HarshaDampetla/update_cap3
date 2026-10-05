from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import WatchlistModel, WatchlistItemModel, StockModel
from src.domain.entities.watchlist import Watchlist
from src.domain.entities.stock import StockStatus
from src.domain.exceptions import WatchlistUpdateException


class WatchlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: WatchlistModel) -> Watchlist:
        symbols = [item.symbol for item in model.items]
        return Watchlist(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            symbols=symbols,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def count_by_user_id(self, user_id: int) -> int:
        return self.db.query(WatchlistModel).filter(WatchlistModel.user_id == user_id).count()

    def get_by_id_and_user(self, watchlist_id: int, user_id: int) -> Optional[Watchlist]:
        model = self.db.query(WatchlistModel).filter(
            WatchlistModel.id == watchlist_id,
            WatchlistModel.user_id == user_id
        ).first()
        return self._to_entity(model) if model else None

    def get_model(self, watchlist_id: int, user_id: int) -> Optional[WatchlistModel]:
        return self.db.query(WatchlistModel).filter(
            WatchlistModel.id == watchlist_id,
            WatchlistModel.user_id == user_id
        ).first()

    def list_by_user(self, user_id: int) -> List[Watchlist]:
        models = self.db.query(WatchlistModel).filter(
            WatchlistModel.user_id == user_id
        ).order_by(WatchlistModel.id.asc()).all()
        return [self._to_entity(m) for m in models]

    def create(self, user_id: int, name: str, symbols: List[str]) -> Watchlist:
        """AC-04 & AC-05: Atomically create watchlist with valid symbols."""
        # Validate symbols exist and are active
        cleaned_symbols = [s.upper().strip() for s in symbols]
        invalid_symbols = []
        for sym in cleaned_symbols:
            stock = self.db.query(StockModel).filter(
                StockModel.symbol == sym,
                StockModel.status == StockStatus.ACTIVE.value
            ).first()
            if not stock:
                invalid_symbols.append(sym)

        if invalid_symbols:
            raise WatchlistUpdateException(
                f"Atomic creation aborted: Symbol(s) {invalid_symbols} do not exist or are not active in catalog.",
                invalid_symbols=invalid_symbols
            )

        try:
            wl = WatchlistModel(
                user_id=user_id,
                name=name.strip(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(wl)
            self.db.flush()

            for sym in set(cleaned_symbols):
                item = WatchlistItemModel(
                    watchlist_id=wl.id,
                    symbol=sym,
                    added_at=datetime.now(timezone.utc)
                )
                self.db.add(item)

            self.db.commit()
            self.db.refresh(wl)
            return self._to_entity(wl)
        except Exception:
            self.db.rollback()
            raise

    def rename(self, watchlist_id: int, user_id: int, new_name: str) -> Watchlist:
        wl = self.get_model(watchlist_id, user_id)
        if not wl:
            raise WatchlistUpdateException(f"Watchlist with ID {watchlist_id} not found.")
        if not new_name or not new_name.strip():
            raise WatchlistUpdateException("Watchlist name cannot be empty.")
        wl.name = new_name.strip()
        wl.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(wl)
        return self._to_entity(wl)

    def add_symbols_atomic(self, watchlist_id: int, user_id: int, symbols: List[str]) -> Watchlist:
        """AC-05: Atomic batch add of symbols. If any symbol is invalid, rolls back completely."""
        wl = self.get_model(watchlist_id, user_id)
        if not wl:
            raise WatchlistUpdateException(f"Watchlist with ID {watchlist_id} not found.")

        cleaned = [s.upper().strip() for s in symbols]
        invalid_symbols = []
        for sym in cleaned:
            stock = self.db.query(StockModel).filter(
                StockModel.symbol == sym,
                StockModel.status == StockStatus.ACTIVE.value
            ).first()
            if not stock:
                invalid_symbols.append(sym)

        if invalid_symbols:
            raise WatchlistUpdateException(
                f"Atomic update aborted: Symbol '{invalid_symbols[0]}' does not exist in catalog.",
                invalid_symbols=invalid_symbols
            )

        try:
            existing = {item.symbol for item in wl.items}
            for sym in cleaned:
                if sym not in existing:
                    item = WatchlistItemModel(
                        watchlist_id=wl.id,
                        symbol=sym,
                        added_at=datetime.now(timezone.utc)
                    )
                    self.db.add(item)
                    existing.add(sym)

            wl.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(wl)
            return self._to_entity(wl)
        except Exception:
            self.db.rollback()
            raise

    def remove_symbol(self, watchlist_id: int, user_id: int, symbol: str) -> Watchlist:
        wl = self.get_model(watchlist_id, user_id)
        if not wl:
            raise WatchlistUpdateException(f"Watchlist with ID {watchlist_id} not found.")
        sym = symbol.upper().strip()
        item = self.db.query(WatchlistItemModel).filter(
            WatchlistItemModel.watchlist_id == watchlist_id,
            WatchlistItemModel.symbol == sym
        ).first()
        if item:
            self.db.delete(item)
            wl.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(wl)
        return self._to_entity(wl)

    def delete_watchlist(self, watchlist_id: int, user_id: int) -> bool:
        wl = self.get_model(watchlist_id, user_id)
        if not wl:
            return False
        self.db.delete(wl)
        self.db.commit()
        return True
