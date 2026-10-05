from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import PortfolioCashModel, HoldingModel
from src.domain.entities.portfolio import Holding, PortfolioCash


class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cash(self, user_id: int) -> Decimal:
        cash_model = self.db.query(PortfolioCashModel).filter(PortfolioCashModel.user_id == user_id).first()
        if not cash_model:
            return Decimal("0.0000")
        return Decimal(str(cash_model.available_cash)).quantize(Decimal("0.0001"))

    def init_cash(self, user_id: int, initial_amount: Decimal = Decimal("100000.0000")) -> PortfolioCash:
        amount = Decimal(str(initial_amount)).quantize(Decimal("0.0001"))
        cash_model = self.db.query(PortfolioCashModel).filter(PortfolioCashModel.user_id == user_id).first()
        if not cash_model:
            cash_model = PortfolioCashModel(
                user_id=user_id,
                available_cash=amount,
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(cash_model)
        else:
            cash_model.available_cash = amount
            cash_model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(cash_model)
        return PortfolioCash(
            user_id=cash_model.user_id,
            available_cash=Decimal(str(cash_model.available_cash)),
            updated_at=cash_model.updated_at
        )

    def deduct_cash(self, user_id: int, amount: Decimal) -> Decimal:
        cash_model = self.db.query(PortfolioCashModel).filter(PortfolioCashModel.user_id == user_id).first()
        if not cash_model:
            raise ValueError(f"No cash account found for user {user_id}")
        deduct_amt = Decimal(str(amount))
        current = Decimal(str(cash_model.available_cash))
        if current < deduct_amt:
            raise ValueError("Insufficient funds to deduct.")
        new_balance = (current - deduct_amt).quantize(Decimal("0.0001"))
        cash_model.available_cash = new_balance
        cash_model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(cash_model)
        return new_balance

    def credit_cash(self, user_id: int, amount: Decimal) -> Decimal:
        cash_model = self.db.query(PortfolioCashModel).filter(PortfolioCashModel.user_id == user_id).first()
        credit_amt = Decimal(str(amount))
        if not cash_model:
            cash_model = PortfolioCashModel(
                user_id=user_id,
                available_cash=credit_amt.quantize(Decimal("0.0001")),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(cash_model)
        else:
            current = Decimal(str(cash_model.available_cash))
            cash_model.available_cash = (current + credit_amt).quantize(Decimal("0.0001"))
            cash_model.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(cash_model)
        return Decimal(str(cash_model.available_cash))

    def get_holdings(self, user_id: int) -> List[Holding]:
        models = self.db.query(HoldingModel).filter(
            HoldingModel.user_id == user_id,
            HoldingModel.shares_held > 0
        ).all()
        return [
            Holding(
                id=m.id,
                user_id=m.user_id,
                symbol=m.symbol,
                shares_held=Decimal(str(m.shares_held)).quantize(Decimal("0.0001")),
                average_buy_price=Decimal(str(m.average_buy_price)).quantize(Decimal("0.0001")),
                updated_at=m.updated_at
            )
            for m in models
        ]

    def get_holding(self, user_id: int, symbol: str) -> Optional[Holding]:
        m = self.db.query(HoldingModel).filter(
            HoldingModel.user_id == user_id,
            HoldingModel.symbol == symbol.upper().strip()
        ).first()
        if not m or m.shares_held <= 0:
            return None
        return Holding(
            id=m.id,
            user_id=m.user_id,
            symbol=m.symbol,
            shares_held=Decimal(str(m.shares_held)).quantize(Decimal("0.0001")),
            average_buy_price=Decimal(str(m.average_buy_price)).quantize(Decimal("0.0001")),
            updated_at=m.updated_at
        )

    def add_shares(self, user_id: int, symbol: str, shares: Decimal, price: Decimal) -> Holding:
        sym = symbol.upper().strip()
        add_s = Decimal(str(shares))
        p = Decimal(str(price))
        m = self.db.query(HoldingModel).filter(
            HoldingModel.user_id == user_id,
            HoldingModel.symbol == sym
        ).first()

        now = datetime.now(timezone.utc)
        if not m:
            m = HoldingModel(
                user_id=user_id,
                symbol=sym,
                shares_held=add_s.quantize(Decimal("0.0001")),
                average_buy_price=p.quantize(Decimal("0.0001")),
                updated_at=now
            )
            self.db.add(m)
        else:
            old_shares = Decimal(str(m.shares_held))
            old_avg = Decimal(str(m.average_buy_price))
            new_shares = old_shares + add_s
            # Weighted average price
            total_cost = (old_shares * old_avg) + (add_s * p)
            new_avg = (total_cost / new_shares).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            m.shares_held = new_shares.quantize(Decimal("0.0001"))
            m.average_buy_price = new_avg
            m.updated_at = now

        self.db.commit()
        self.db.refresh(m)
        return Holding(
            id=m.id,
            user_id=m.user_id,
            symbol=m.symbol,
            shares_held=Decimal(str(m.shares_held)),
            average_buy_price=Decimal(str(m.average_buy_price)),
            updated_at=m.updated_at
        )

    def reduce_shares(self, user_id: int, symbol: str, shares: Decimal) -> Optional[Holding]:
        sym = symbol.upper().strip()
        rem_s = Decimal(str(shares))
        m = self.db.query(HoldingModel).filter(
            HoldingModel.user_id == user_id,
            HoldingModel.symbol == sym
        ).first()
        if not m or Decimal(str(m.shares_held)) < rem_s:
            raise ValueError(f"Insufficient shares of {sym} to sell.")

        current_s = Decimal(str(m.shares_held))
        new_shares = (current_s - rem_s).quantize(Decimal("0.0001"))
        now = datetime.now(timezone.utc)
        m.shares_held = new_shares
        m.updated_at = now
        self.db.commit()
        self.db.refresh(m)
        return Holding(
            id=m.id,
            user_id=m.user_id,
            symbol=m.symbol,
            shares_held=Decimal(str(m.shares_held)),
            average_buy_price=Decimal(str(m.average_buy_price)),
            updated_at=m.updated_at
        )
