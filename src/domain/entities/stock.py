from decimal import Decimal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class StockStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DELISTED = "DELISTED"
    DELETED = "DELETED"


class Stock(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str
    sector: str
    exchange: str
    current_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    status: StockStatus = StockStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    def __init__(self, **data):
        if "symbol" in data and isinstance(data["symbol"], str):
            data["symbol"] = data["symbol"].upper()
        super().__init__(**data)
