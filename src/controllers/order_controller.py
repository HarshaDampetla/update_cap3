from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from src.services.order_service import OrderService
from src.controllers.deps import get_order_service, get_current_user
from src.domain.entities.user import User

router = APIRouter(prefix="/api/orders", tags=["Orders"])


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: str
    limit_price: Optional[str] = None
    auto_execute: Optional[bool] = True


@router.post("", status_code=status.HTTP_201_CREATED)
def place_order(
    req: PlaceOrderRequest,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    AC-06: Order enters PENDING with server-side UTC timestamp.
    AC-08: Pre-trade cash verification (fails if insufficient funds).
    AC-07 & NFR-02: Stub execution to EXECUTED.
    """
    qty = Decimal(req.quantity)
    lim_p = Decimal(req.limit_price) if req.limit_price else None

    order = order_service.place_order(
        user_id=current_user.id,
        symbol=req.symbol,
        side_str=req.side,
        order_type_str=req.order_type,
        quantity=qty,
        limit_price=lim_p,
        auto_execute=req.auto_execute if req.auto_execute is not None else True
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "symbol": order.symbol,
        "side": order.side.value,
        "order_type": order.order_type.value,
        "quantity": str(order.quantity),
        "quote_price": str(order.quote_price),
        "limit_price": str(order.limit_price) if order.limit_price else None,
        "status": order.status.value,
        "server_timestamp": order.server_timestamp.isoformat(),
        "executed_at": order.executed_at.isoformat() if order.executed_at else None
    }


@router.get("")
def list_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """List customer orders."""
    orders = order_service.list_orders(current_user.id)
    return [
        {
            "id": o.id,
            "symbol": o.symbol,
            "side": o.side.value,
            "order_type": o.order_type.value,
            "quantity": str(o.quantity),
            "quote_price": str(o.quote_price),
            "limit_price": str(o.limit_price) if o.limit_price else None,
            "status": o.status.value,
            "server_timestamp": o.server_timestamp.isoformat(),
            "executed_at": o.executed_at.isoformat() if o.executed_at else None,
            "cancelled_at": o.cancelled_at.isoformat() if o.cancelled_at else None
        }
        for o in orders
    ]


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """AC-07: Cancel order. Rejects if order is already in a terminal state."""
    order = order_service.cancel_order(order_id, current_user.id)
    return {
        "id": order.id,
        "status": order.status.value,
        "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None
    }
