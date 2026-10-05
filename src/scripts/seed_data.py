from decimal import Decimal
from datetime import datetime, timezone
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import (
    UserModel,
    StockModel,
    WatchlistModel,
    WatchlistItemModel,
    HoldingModel,
    PortfolioCashModel
)
from src.services.auth_service import AuthService


def seed_database():
    print("=== [MarketScope] Starting Database Bootstrap Seeder ===")
    init_db()
    db = SessionLocal()

    try:
        # 1. Seed Users (Admin, Trader1, Trader2)
        users_data = [
            {
                "email": "admin@marketscope.com",
                "password": "AdminPass123!",
                "role": "ADMIN",
                "status": "ACTIVE",
                "cash": Decimal("0.0000")
            },
            {
                "email": "trader1@marketscope.com",
                "password": "TraderPass123!",
                "role": "CUSTOMER",
                "status": "ACTIVE",
                "cash": Decimal("100000.0000")
            },
            {
                "email": "trader2@marketscope.com",
                "password": "TraderPass123!",
                "role": "CUSTOMER",
                "status": "ACTIVE",
                "cash": Decimal("25000.0000")
            }
        ]

        user_map = {}
        for u in users_data:
            existing = db.query(UserModel).filter(UserModel.email == u["email"]).first()
            if not existing:
                hashed = AuthService.hash_password(u["password"])
                now = datetime.now(timezone.utc)
                user_obj = UserModel(
                    email=u["email"],
                    password_hash=hashed,
                    role=u["role"],
                    status=u["status"],
                    created_at=now,
                    updated_at=now
                )
                db.add(user_obj)
                db.flush()
                user_map[u["email"]] = user_obj

                # Initialize portfolio cash
                cash_obj = PortfolioCashModel(
                    user_id=user_obj.id,
                    available_cash=u["cash"],
                    updated_at=now
                )
                db.add(cash_obj)
                print(f"Created user: {u['email']} ({u['role']}) with cash ${u['cash']}")
            else:
                user_map[u["email"]] = existing
                print(f"User {u['email']} already exists.")

        # 2. Seed Baseline Stocks
        stocks_data = [
            ("AAPL", "Apple Inc.", "Technology", "NASDAQ", Decimal("180.0000"), Decimal("178.5000")),
            ("MSFT", "Microsoft Corp.", "Technology", "NASDAQ", Decimal("420.0000"), Decimal("425.0000")),
            ("GOOGL", "Alphabet Inc.", "Technology", "NASDAQ", Decimal("175.0000"), Decimal("174.0000")),
            ("AMZN", "Amazon.com Inc.", "Consumer Discretionary", "NASDAQ", Decimal("185.0000"), Decimal("182.0000")),
            ("NVDA", "Nvidia Corp.", "Technology", "NASDAQ", Decimal("120.0000"), Decimal("115.0000")),
            ("JPM", "JPMorgan Chase", "Financials", "NYSE", Decimal("200.0000"), Decimal("198.5000")),
            ("XOM", "Exxon Mobil", "Energy", "NYSE", Decimal("115.0000"), Decimal("116.0000")),
            ("JNJ", "Johnson & Johnson", "Healthcare", "NYSE", Decimal("155.0000"), Decimal("154.5000")),
            ("TSLA", "Tesla Inc.", "Consumer Discretionary", "NASDAQ", Decimal("240.0000"), Decimal("235.0000")),
            ("BRK.B", "Berkshire Hathaway", "Financials", "NYSE", Decimal("440.0000"), Decimal("438.0000")),
        ]

        for sym, name, sector, exchange, curr_price, open_price in stocks_data:
            existing_stock = db.query(StockModel).filter(StockModel.symbol == sym).first()
            if not existing_stock:
                now = datetime.now(timezone.utc)
                stock_obj = StockModel(
                    symbol=sym,
                    name=name,
                    sector=sector,
                    exchange=exchange,
                    current_price=curr_price,
                    open_price=open_price,
                    high_price=max(curr_price, open_price),
                    low_price=min(curr_price, open_price),
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now
                )
                db.add(stock_obj)
                print(f"Created stock: {sym} (${curr_price})")
            else:
                print(f"Stock {sym} already exists.")

        db.commit()

        # 3. Seed Watchlist for trader1: "Tech Giants" (AAPL, MSFT, NVDA)
        trader1 = user_map.get("trader1@marketscope.com")
        if trader1:
            wl = db.query(WatchlistModel).filter(
                WatchlistModel.user_id == trader1.id,
                WatchlistModel.name == "Tech Giants"
            ).first()
            if not wl:
                now = datetime.now(timezone.utc)
                wl = WatchlistModel(
                    user_id=trader1.id,
                    name="Tech Giants",
                    created_at=now,
                    updated_at=now
                )
                db.add(wl)
                db.flush()

                for s in ["AAPL", "MSFT", "NVDA"]:
                    item = WatchlistItemModel(
                        watchlist_id=wl.id,
                        symbol=s,
                        added_at=now
                    )
                    db.add(item)
                print("Created seed watchlist 'Tech Giants' for trader1.")

            # 4. Seed Initial Holdings for trader1:
            # 10 shares of AAPL @ $170.00, 5 shares of MSFT @ $400.00, 20 shares of NVDA @ $110.00
            holdings_seed = [
                ("AAPL", Decimal("10.0000"), Decimal("170.0000")),
                ("MSFT", Decimal("5.0000"), Decimal("400.0000")),
                ("NVDA", Decimal("20.0000"), Decimal("110.0000")),
            ]
            for s, qty, avg_price in holdings_seed:
                holding = db.query(HoldingModel).filter(
                    HoldingModel.user_id == trader1.id,
                    HoldingModel.symbol == s
                ).first()
                if not holding:
                    now = datetime.now(timezone.utc)
                    holding = HoldingModel(
                        user_id=trader1.id,
                        symbol=s,
                        shares_held=qty,
                        average_buy_price=avg_price,
                        updated_at=now
                    )
                    db.add(holding)
                    print(f"Created holding for trader1: {qty} {s} @ ${avg_price}")

            db.commit()

        print("=== [MarketScope] Database Seed Completed Successfully ===")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
