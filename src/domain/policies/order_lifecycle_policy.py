from src.domain.entities.order import OrderStatus
from src.domain.exceptions import InvalidOrderStateException


class OrderLifecyclePolicy:
    """Enforces order finite state machine transitions (AC-07, NFR-02)."""

    LEGAL_TRANSITIONS = {
        OrderStatus.PENDING: {
            OrderStatus.EXECUTED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
        },
        OrderStatus.EXECUTED: set(),  # Terminal (append-only)
        OrderStatus.CANCELLED: set(), # Terminal
        OrderStatus.REJECTED: set(),  # Terminal
    }

    @classmethod
    def can_transition(cls, current_status: OrderStatus, target_status: OrderStatus) -> bool:
        allowed = cls.LEGAL_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def validate_transition(cls, current_status: OrderStatus, target_status: OrderStatus, order_id: int) -> None:
        if not cls.can_transition(current_status, target_status):
            raise InvalidOrderStateException(
                current_status=current_status.value if hasattr(current_status, 'value') else str(current_status),
                attempted_status=target_status.value if hasattr(target_status, 'value') else str(target_status),
                order_id=order_id
            )
