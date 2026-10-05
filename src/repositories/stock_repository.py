from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.repositories.models import StockModel
from src.domain.entities.stock import Stock, StockStatus
from src.domain.exceptions import HardDeleteProhibitedException


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: StockModel) -> Stock:
        return Stock(
            symbol=model.symbol,
            name=model.name,
            sector=model.sector,
            exchange=model.exchange,
            current_price=Decimal(str(model.current_price)),
            open_price=Decimal(str(model.open_price)),
            high_price=Decimal(str(model.high_price)),
            low_price=Decimal(str(model.low_price)),
            status=StockStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def get_by_symbol(self, symbol: str, include_delisted: bool = False) -> Optional[Stock]:
        sym = symbol.upper().strip()
        q = self.db.query(StockModel).filter(StockModel.symbol == sym)
        if not include_delisted:
            q = q.filter(StockModel.status == StockStatus.ACTIVE.value)
        model = q.first()
        return self._to_entity(model) if model else None

    def get_model_by_symbol(self, symbol: str) -> Optional[StockModel]:
        return self.db.query(StockModel).filter(StockModel.symbol == symbol.upper().strip()).first()

    def create(
        self,
        symbol: str,
        name: str,
        sector: str,
        exchange: str,
        initial_price: Decimal,
        open_price: Optional[Decimal] = None
    ) -> Stock:
        price = Decimal(str(initial_price))
        open_p = Decimal(str(open_price)) if open_price is not None else price
        model = StockModel(
            symbol=symbol.upper().strip(),
            name=name.strip(),
            sector=sector.strip(),
            exchange=exchange.strip(),
            current_price=price,
            open_price=open_p,
            high_price=price,
            low_price=price,
            status=StockStatus.ACTIVE.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(
        self,
        symbol: str,
        name: Optional[str] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        status: Optional[StockStatus] = None
    ) -> Optional[Stock]:
        model = self.get_model_by_symbol(symbol)
        if not model:
            return None
        if name is not None:
            model.name = name.strip()
        if sector is not None:
            model.sector = sector.strip()
        if exchange is not None:
            model.exchange = exchange.strip()
        if status is not None:
            model.status = status.value if hasattr(status, 'value') else str(status)
        model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def soft_delete(self, symbol: str) -> Optional[Stock]:
        """AC-03: Soft-delete stock: symbol transitions to DELETED, never hard-deleted."""
        model = self.get_model_by_symbol(symbol)
        if not model:
            return None
        model.status = StockStatus.DELETED.value
        model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def hard_delete_prohibited(self, symbol: str):
        """Guard method against hard deletions."""
        raise HardDeleteProhibitedException("Stock", symbol)

    def search(
        self,
        query: Optional[str] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        include_delisted: bool = False
    ) -> List[Stock]:
        q = self.db.query(StockModel)
        if not include_delisted:
            q = q.filter(StockModel.status == StockStatus.ACTIVE.value)
        else:
            q = q.filter(StockModel.status != StockStatus.DELETED.value)

        if query:
            pattern = f"%{query.strip()}%"
            q = q.filter(or_(StockModel.symbol.ilike(pattern), StockModel.name.ilike(pattern)))

        if sector:
            q = q.filter(StockModel.sector.ilike(f"%{sector.strip()}%"))

        if exchange:
            q = q.filter(StockModel.exchange.ilike(f"%{exchange.strip()}%"))

        models = q.order_by(StockModel.symbol.asc()).all()
        return [self._to_entity(m) for m in models]

    def update_price(
        self,
        symbol: str,
        current_price: Decimal,
        high_price: Optional[Decimal] = None,
        low_price: Optional[Decimal] = None
    ) -> Optional[Stock]:
        model = self.get_model_by_symbol(symbol)
        if not model:
            return None
        price = Decimal(str(current_price))
        model.current_price = price
        if high_price is not None:
            model.high_price = max(model.high_price, Decimal(str(high_price)))
        else:
            model.high_price = max(model.high_price, price)
        if low_price is not None:
            model.low_price = min(model.low_price, Decimal(str(low_price)))
        else:
            model.low_price = min(model.low_price, price)
        model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
