import pytest
from src.domain.entities.order import OrderStatus
from src.domain.exceptions import InvalidOrderStateException
from src.domain.policies.order_lifecycle_policy import OrderLifecyclePolicy


@pytest.mark.ac("AC-07")
def test_legal_order_state_transitions():
    """AC-07: PENDING can legally transition to EXECUTED, CANCELLED, or REJECTED."""
    assert OrderLifecyclePolicy.can_transition(OrderStatus.PENDING, OrderStatus.EXECUTED) is True
    assert OrderLifecyclePolicy.can_transition(OrderStatus.PENDING, OrderStatus.CANCELLED) is True
    assert OrderLifecyclePolicy.can_transition(OrderStatus.PENDING, OrderStatus.REJECTED) is True

    # Validate method executes without error
    OrderLifecyclePolicy.validate_transition(OrderStatus.PENDING, OrderStatus.EXECUTED, order_id=101)
    OrderLifecyclePolicy.validate_transition(OrderStatus.PENDING, OrderStatus.CANCELLED, order_id=102)
    OrderLifecyclePolicy.validate_transition(OrderStatus.PENDING, OrderStatus.REJECTED, order_id=103)


@pytest.mark.ac("AC-07")
def test_terminal_state_transitions_raise_exception():
    """AC-07: Transitions from terminal states raise InvalidOrderStateException."""
    terminal_states = [OrderStatus.EXECUTED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
    target_states = [OrderStatus.PENDING, OrderStatus.EXECUTED, OrderStatus.CANCELLED, OrderStatus.REJECTED]

    for terminal in terminal_states:
        for target in target_states:
            with pytest.raises(InvalidOrderStateException) as exc_info:
                OrderLifecyclePolicy.validate_transition(terminal, target, order_id=999)

            assert exc_info.value.code == "INVALID_ORDER_STATE"
            assert exc_info.value.ac_id == "AC-07"
            assert exc_info.value.order_id == 999
            assert exc_info.value.current_status == terminal.value
            assert exc_info.value.attempted_status == target.value
