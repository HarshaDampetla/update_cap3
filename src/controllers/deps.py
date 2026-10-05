import uuid
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.repositories.database import get_db
from src.repositories.user_repository import UserRepository
from src.repositories.stock_repository import StockRepository
from src.repositories.watchlist_repository import WatchlistRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.portfolio_repository import PortfolioRepository
from src.services.auth_service import AuthService
from src.services.stock_service import StockService
from src.services.watchlist_service import WatchlistService
from src.services.order_service import OrderService
from src.services.portfolio_service import PortfolioService
from src.services.analytics_service import AnalyticsService
from src.domain.entities.user import User, UserRole, UserStatus

security = HTTPBearer(auto_error=False)


# Service Dependency Providers
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db), PortfolioRepository(db))


def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    return StockService(StockRepository(db))


def get_watchlist_service(db: Session = Depends(get_db)) -> WatchlistService:
    return WatchlistService(WatchlistRepository(db), StockRepository(db))


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(OrderRepository(db), StockRepository(db), PortfolioRepository(db))


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    return PortfolioService(PortfolioRepository(db), StockRepository(db))


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(PortfolioRepository(db), StockRepository(db), OrderRepository(db))


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Authenticates Bearer token, checks active status."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Authentication token is required."}
        )

    payload = auth_service.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired authentication token."}
        )

    user_id = int(payload.get("sub", 0))
    user = auth_service.user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found."}
        )

    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_SUSPENDED", "message": "Account has been suspended."}
        )

    return user


def require_role(required_role: UserRole) -> Callable:
    """NFR-04: Role boundary partitioning dependency."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Operation requires {required_role.value} role. Current role: {current_user.role.value}."
                }
            )
        return current_user

    return role_checker
