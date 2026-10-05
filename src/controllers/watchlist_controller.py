from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from src.services.watchlist_service import WatchlistService
from src.controllers.deps import get_watchlist_service, get_current_user
from src.domain.entities.user import User

router = APIRouter(prefix="/api/watchlists", tags=["Watchlists"])


class CreateWatchlistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbols: List[str]


class RenameWatchlistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class AddSymbolsRequest(BaseModel):
    symbols: List[str]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_watchlist(
    req: CreateWatchlistRequest,
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """AC-04: Create watchlist with max 10 limit and non-empty symbols."""
    wl = watchlist_service.create_watchlist(
        user_id=current_user.id,
        name=req.name,
        symbols=req.symbols
    )
    return {
        "id": wl.id,
        "user_id": wl.user_id,
        "name": wl.name,
        "symbols": wl.symbols,
        "created_at": wl.created_at.isoformat()
    }


@router.get("")
def list_watchlists(
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """List customer watchlists with realtime symbol prices."""
    return watchlist_service.list_watchlists_with_items(current_user.id)


@router.patch("/{watchlist_id}/name")
def rename_watchlist(
    watchlist_id: int,
    req: RenameWatchlistRequest,
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """AC-05: Atomic rename."""
    wl = watchlist_service.rename_watchlist(watchlist_id, current_user.id, req.name)
    return {
        "id": wl.id,
        "name": wl.name,
        "symbols": wl.symbols,
        "updated_at": wl.updated_at.isoformat()
    }


@router.post("/{watchlist_id}/symbols")
def add_symbols(
    watchlist_id: int,
    req: AddSymbolsRequest,
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """AC-05: Atomic multi-symbol addition. Rejects and rolls back if any symbol invalid."""
    wl = watchlist_service.add_symbols_atomic(watchlist_id, current_user.id, req.symbols)
    return {
        "id": wl.id,
        "name": wl.name,
        "symbols": wl.symbols,
        "updated_at": wl.updated_at.isoformat()
    }


@router.delete("/{watchlist_id}/symbols/{symbol}")
def remove_symbol(
    watchlist_id: int,
    symbol: str,
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """AC-05: Remove symbol from watchlist."""
    wl = watchlist_service.remove_symbol(watchlist_id, current_user.id, symbol)
    return {
        "id": wl.id,
        "name": wl.name,
        "symbols": wl.symbols,
        "updated_at": wl.updated_at.isoformat()
    }


@router.delete("/{watchlist_id}")
def delete_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """AC-05: Atomic delete watchlist."""
    success = watchlist_service.delete_watchlist(watchlist_id, current_user.id)
    return {
        "id": watchlist_id,
        "deleted": success
    }
