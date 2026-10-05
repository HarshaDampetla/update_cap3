from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, event
)
from sqlalchemy.orm import relationship
from src.repositories.database import Base
from src.domain.exceptions import HardDeleteProhibitedException


def utc_now():
    return datetime.now(timezone.utc)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="CUSTOMER", nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    watchlists = relationship("WatchlistModel", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="user")
    holdings = relationship("HoldingModel", back_populates="user")
    cash = relationship("PortfolioCashModel", back_populates="user", uselist=False)


class UserRoleAuditLogModel(Base):
    __tablename__ = "user_role_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    previous_role = Column(String(50), nullable=False)
    new_role = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)


class StockModel(Base):
    __tablename__ = "stocks"

    symbol = Column(String(10), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    current_price = Column(Numeric(18, 4), nullable=False)
    open_price = Column(Numeric(18, 4), nullable=False)
    high_price = Column(Numeric(18, 4), nullable=False)
    low_price = Column(Numeric(18, 4), nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class WatchlistModel(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="watchlists")
    items = relationship("WatchlistItemModel", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItemModel(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False, index=True)
    symbol = Column(String(10), ForeignKey("stocks.symbol"), nullable=False)
    added_at = Column(DateTime, default=utc_now, nullable=False)

    watchlist = relationship("WatchlistModel", back_populates="items")
    stock = relationship("StockModel")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_symbol"),
    )


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(10), ForeignKey("stocks.symbol"), nullable=False)
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    quote_price = Column(Numeric(18, 4), nullable=False)
    limit_price = Column(Numeric(18, 4), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False, index=True)
    server_timestamp = Column(DateTime, default=utc_now, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    user = relationship("UserModel", back_populates="orders")
    stock = relationship("StockModel")
    execution = relationship("TradeExecutionModel", back_populates="order", uselist=False)


class TradeExecutionModel(Base):
    """NFR-02: Executed trades are append-only. No updates or deletes permitted."""
    __tablename__ = "trade_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False, index=True)
    executed_price = Column(Numeric(18, 4), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    total_value = Column(Numeric(18, 4), nullable=False)
    execution_timestamp = Column(DateTime, default=utc_now, nullable=False)

    order = relationship("OrderModel", back_populates="execution")


# NFR-02: Append-only guardrails for TradeExecutionModel
@event.listens_for(TradeExecutionModel, "before_update")
def block_trade_execution_update(mapper, connection, target):
    raise HardDeleteProhibitedException("TradeExecution", str(target.id))


@event.listens_for(TradeExecutionModel, "before_delete")
def block_trade_execution_delete(mapper, connection, target):
    raise HardDeleteProhibitedException("TradeExecution", str(target.id))


class HoldingModel(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(10), ForeignKey("stocks.symbol"), nullable=False)
    shares_held = Column(Numeric(18, 4), nullable=False)
    average_buy_price = Column(Numeric(18, 4), nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="holdings")
    stock = relationship("StockModel")

    __table_args__ = (
        UniqueConstraint("user_id", "symbol", name="uq_user_holding_symbol"),
    )


class PortfolioCashModel(Base):
    __tablename__ = "portfolio_cash"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    available_cash = Column(Numeric(18, 4), default=0, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="cash")
