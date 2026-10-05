from fastapi import APIRouter, Depends
from src.services.analytics_service import AnalyticsService
from src.controllers.deps import get_analytics_service, get_current_user
from src.domain.entities.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/daily-performance")
def get_daily_performance(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """AC-10: Top 5 gainers and losers from customer's current holdings."""
    return analytics_service.get_daily_performance(current_user.id)


@router.get("/sector-exposure")
def get_sector_exposure(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Sector distribution and exposure breakdown."""
    return analytics_service.get_sector_exposure(current_user.id)
