import pytest
from src.scripts.seed_data import seed_database
from src.repositories.database import SessionLocal
from src.repositories.models import UserModel, StockModel, WatchlistModel, HoldingModel


def test_seed_database_execution():
    """Verify that seed_database initializes all required seed records without error."""
    seed_database()
    db = SessionLocal()
    try:
        users = db.query(UserModel).all()
        assert len(users) >= 3
        stocks = db.query(StockModel).all()
        assert len(stocks) >= 10
        watchlists = db.query(WatchlistModel).all()
        assert len(watchlists) >= 1
        holdings = db.query(HoldingModel).all()
        assert len(holdings) >= 1
    finally:
        db.close()
