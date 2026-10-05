import pytest
from decimal import Decimal
from src.domain.entities.user import UserRole, UserStatus
from src.domain.exceptions import EmailAlreadyExistsException


@pytest.mark.ac("AC-01")
def test_user_registration_initializes_account_and_balance(auth_service, portfolio_repo):
    """AC-01: Customer registration creates ACTIVE account with CUSTOMER role and $100,000 balance."""
    email = "new_investor@example.com"
    password = "SecurePassword123!"

    user = auth_service.register(email, password)

    assert user.id is not None
    assert user.email == email
    assert user.role == UserRole.CUSTOMER
    assert user.status == UserStatus.ACTIVE

    # Verify initial cash balance
    cash = portfolio_repo.get_cash(user.id)
    assert cash == Decimal("100000.0000")


@pytest.mark.ac("AC-01")
def test_duplicate_email_registration_rejected(auth_service):
    """AC-01: Duplicate email raises EmailAlreadyExistsException."""
    auth_service.register("unique@example.com", "Password123!")

    with pytest.raises(EmailAlreadyExistsException):
        auth_service.register("unique@example.com", "DifferentPass123!")
