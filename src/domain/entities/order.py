from decimal import Decimal
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class Order(BaseModel):
    id: int
    user_id: int
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    quote_price: Decimal
    limit_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    server_timestamp: datetime
    executed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class TradeExecution(BaseModel):
    """NFR-02: Trade executions are append-only and frozen/immutable."""
    model_config = ConfigDict(frozen=True)

    id: int
    order_id: int
    executed_price: Decimal
    quantity: Decimal
    total_value: Decimal
    execution_timestamp: datetime
