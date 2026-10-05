from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from src.services.auth_service import AuthService
from src.services.stock_service import StockService
from src.services.analytics_service import AnalyticsService
from src.controllers.deps import (
    get_auth_service,
    get_stock_service,
    get_analytics_service,
    require_role
)
from src.domain.entities.user import User, UserRole
from src.domain.entities.stock import StockStatus

router = APIRouter(prefix="/api/admin", tags=["Administration"])


class RoleUpdateRequest(BaseModel):
    role: str


class CreateStockRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str
    sector: str
    exchange: str
    initial_price: str
    open_price: Optional[str] = None


class UpdateStockRequest(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None
    status: Optional[str] = None


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    req: RoleUpdateRequest,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service)
):
    """AC-02: Admin role update with immutable audit logging."""
    return auth_service.update_user_role(
        target_user_id=user_id,
        new_role_str=req.role,
        actor_admin=current_admin
    )


@router.get("/users")
def list_users(
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service)
):
    users = auth_service.user_repo.list_all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role.value,
            "status": u.status.value,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]


@router.get("/users/{user_id}/audit-logs")
def get_user_audit_logs(
    user_id: int,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.user_repo.get_audit_logs(target_user_id=user_id)


@router.post("/stocks", status_code=status.HTTP_201_CREATED)
def create_stock(
    req: CreateStockRequest,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    stock_service: StockService = Depends(get_stock_service)
):
    """AC-03: Create stock in catalog."""
    price = Decimal(req.initial_price)
    open_p = Decimal(req.open_price) if req.open_price else price
    stock = stock_service.create_stock(
        symbol=req.symbol,
        name=req.name,
        sector=req.sector,
        exchange=req.exchange,
        initial_price=price,
        open_price=open_p
    )
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "exchange": stock.exchange,
        "current_price": str(stock.current_price),
        "status": stock.status.value,
        "created_at": stock.created_at.isoformat()
    }


@router.put("/stocks/{symbol}")
def update_stock(
    symbol: str,
    req: UpdateStockRequest,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    stock_service: StockService = Depends(get_stock_service)
):
    """AC-03: Update stock metadata."""
    st_val = StockStatus(req.status) if req.status else None
    stock = stock_service.update_stock(
        symbol=symbol,
        name=req.name,
        sector=req.sector,
        exchange=req.exchange,
        status=st_val
    )
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "exchange": stock.exchange,
        "current_price": str(stock.current_price),
        "status": stock.status.value,
        "updated_at": stock.updated_at.isoformat()
    }


@router.delete("/stocks/{symbol}")
def soft_delete_stock(
    symbol: str,
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    stock_service: StockService = Depends(get_stock_service)
):
    """AC-03: Soft-delete stock symbol to DELETED state. Never hard-deleted."""
    stock = stock_service.soft_delete_stock(symbol)
    return {
        "symbol": stock.symbol,
        "status": stock.status.value,
        "message": f"Stock {stock.symbol} successfully moved to DELETED status.",
        "updated_at": stock.updated_at.isoformat()
    }


@router.get("/statistics/orders")
def get_admin_order_statistics(
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Admin telemetry for order volume, settlement queue, and top symbols."""
    return analytics_service.get_admin_order_statistics()
