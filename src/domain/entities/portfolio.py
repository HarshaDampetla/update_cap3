from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel


class Holding(BaseModel):
    id: int
    user_id: int
    symbol: str
    shares_held: Decimal
    average_buy_price: Decimal
    updated_at: datetime


class PortfolioCash(BaseModel):
    user_id: int
    available_cash: Decimal
    updated_at: datetime
