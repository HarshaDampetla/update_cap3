from fastapi import APIRouter, Depends
from src.services.portfolio_service import PortfolioService
from src.controllers.deps import get_portfolio_service, get_current_user
from src.domain.entities.user import User

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("/statistics")
def get_portfolio_statistics(
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """AC-09: Fixed-point decimal portfolio statistics."""
    return portfolio_service.get_statistics(current_user.id)


@router.get("/holdings")
def get_portfolio_holdings(
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Itemized holdings with unrealized P&L."""
    return portfolio_service.get_holdings_breakdown(current_user.id)


@router.get("/cash")
def get_portfolio_cash(
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """Available cash balance for purchasing power."""
    return portfolio_service.get_cash_balance(current_user.id)
