from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.repositories.models import OrderModel, TradeExecutionModel, StockModel
from src.domain.entities.order import Order, OrderSide, OrderType, OrderStatus, TradeExecution
from src.domain.policies.order_lifecycle_policy import OrderLifecyclePolicy


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            symbol=model.symbol,
            side=OrderSide(model.side),
            order_type=OrderType(model.order_type),
            quantity=Decimal(str(model.quantity)),
            quote_price=Decimal(str(model.quote_price)),
            limit_price=Decimal(str(model.limit_price)) if model.limit_price is not None else None,
            status=OrderStatus(model.status),
            server_timestamp=model.server_timestamp,
            executed_at=model.executed_at,
            cancelled_at=model.cancelled_at
        )

    def _execution_to_entity(self, model: TradeExecutionModel) -> TradeExecution:
        return TradeExecution(
            id=model.id,
            order_id=model.order_id,
            executed_price=Decimal(str(model.executed_price)),
            quantity=Decimal(str(model.quantity)),
            total_value=Decimal(str(model.total_value)),
            execution_timestamp=model.execution_timestamp
        )

    def create_order(
        self,
        user_id: int,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        quote_price: Decimal,
        limit_price: Optional[Decimal] = None
    ) -> Order:
        """AC-06: Order enters PENDING state with server-side UTC timestamp."""
        now = datetime.now(timezone.utc)
        model = OrderModel(
            user_id=user_id,
            symbol=symbol.upper().strip(),
            side=side.value,
            order_type=order_type.value,
            quantity=Decimal(str(quantity)),
            quote_price=Decimal(str(quote_price)),
            limit_price=Decimal(str(limit_price)) if limit_price is not None else None,
            status=OrderStatus.PENDING.value,
            server_timestamp=now
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, order_id: int) -> Optional[Order]:
        model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        return self._to_entity(model) if model else None

    def get_model_by_id(self, order_id: int) -> Optional[OrderModel]:
        return self.db.query(OrderModel).filter(OrderModel.id == order_id).first()

    def list_by_user(self, user_id: int) -> List[Order]:
        models = self.db.query(OrderModel).filter(
            OrderModel.user_id == user_id
        ).order_by(OrderModel.server_timestamp.desc()).all()
        return [self._to_entity(m) for m in models]

    def update_status(self, order_id: int, target_status: OrderStatus) -> Order:
        """AC-07: Transition order status according to finite state machine."""
        model = self.get_model_by_id(order_id)
        if not model:
            raise ValueError(f"Order {order_id} not found.")

        current = OrderStatus(model.status)
        OrderLifecyclePolicy.validate_transition(current, target_status, order_id)

        model.status = target_status.value
        now = datetime.now(timezone.utc)
        if target_status == OrderStatus.EXECUTED:
            model.executed_at = now
        elif target_status == OrderStatus.CANCELLED:
            model.cancelled_at = now

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def record_execution(
        self,
        order_id: int,
        executed_price: Decimal,
        quantity: Decimal
    ) -> TradeExecution:
        """NFR-02: Record append-only trade execution."""
        total_val = (Decimal(str(executed_price)) * Decimal(str(quantity))).quantize(Decimal("0.0001"))
        exec_model = TradeExecutionModel(
            order_id=order_id,
            executed_price=Decimal(str(executed_price)),
            quantity=Decimal(str(quantity)),
            total_value=total_val,
            execution_timestamp=datetime.now(timezone.utc)
        )
        self.db.add(exec_model)
        self.db.commit()
        self.db.refresh(exec_model)
        return self._execution_to_entity(exec_model)

    def get_execution(self, order_id: int) -> Optional[TradeExecution]:
        model = self.db.query(TradeExecutionModel).filter(TradeExecutionModel.order_id == order_id).first()
        return self._execution_to_entity(model) if model else None

    def get_admin_order_statistics(self) -> Dict:
        """Admin telemetry for order statuses and volumes."""
        counts = dict(
            self.db.query(OrderModel.status, func.count(OrderModel.id))
            .group_by(OrderModel.status)
            .all()
        )
        vol_by_status = {
            "PENDING": counts.get(OrderStatus.PENDING.value, 0),
            "EXECUTED": counts.get(OrderStatus.EXECUTED.value, 0),
            "CANCELLED": counts.get(OrderStatus.CANCELLED.value, 0),
            "REJECTED": counts.get(OrderStatus.REJECTED.value, 0),
        }
        settlement_queue = vol_by_status["PENDING"]

        # Most traded symbols
        top_syms = (
            self.db.query(
                OrderModel.symbol,
                func.count(OrderModel.id).label("trade_count"),
                func.sum(OrderModel.quantity).label("total_shares")
            )
            .filter(OrderModel.status == OrderStatus.EXECUTED.value)
            .group_by(OrderModel.symbol)
            .order_by(func.count(OrderModel.id).desc())
            .limit(5)
            .all()
        )

        most_traded = [
            {
                "symbol": row[0],
                "trade_count": int(row[1]),
                "total_shares": float(row[2]) if row[2] else 0
            }
            for row in top_syms
        ]

        return {
            "daily_volume_by_status": vol_by_status,
            "settlement_queue_count": settlement_queue,
            "most_traded_symbols": most_traded
        }
