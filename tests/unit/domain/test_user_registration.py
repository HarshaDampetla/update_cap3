import pytest
from datetime import datetime, timezone
from src.domain.entities.user import User, UserRole, UserStatus


@pytest.mark.ac("AC-01")
def test_user_entity_default_state_and_role():
    """AC-01: User initialized in ACTIVE state with CUSTOMER role."""
    now = datetime.now(timezone.utc)
    user = User(
        id=1,
        email="customer@example.com",
        password_hash="$2b$12$fakehashedpasswordstringforunittest",
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now
    )

    assert user.role == UserRole.CUSTOMER
    assert user.status == UserStatus.ACTIVE
    assert user.email == "customer@example.com"


@pytest.mark.nfr("NFR-03")
def test_user_representation_omits_password_hash():
    """NFR-03: Password hash must never appear in string or repr representation."""
    now = datetime.now(timezone.utc)
    secret_hash = "$2b$12$verysecretpasswordhash"
    user = User(
        id=1,
        email="customer@example.com",
        password_hash=secret_hash,
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now
    )

    assert secret_hash not in str(user)
    assert secret_hash not in repr(user)
