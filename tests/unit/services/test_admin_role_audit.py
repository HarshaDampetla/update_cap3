import pytest
from src.domain.entities.user import UserRole
from src.domain.exceptions import UnauthorizedRoleModificationException, InvalidRoleException


@pytest.mark.ac("AC-02")
def test_admin_role_update_persists_audit_log(auth_service, seed_admin_user, seed_customer_user):
    """AC-02: Role update creates immutable audit record with actor ID and timestamp."""
    res = auth_service.update_user_role(
        target_user_id=seed_customer_user.id,
        new_role_str="SUSPENDED",
        actor_admin=seed_admin_user
    )

    assert res["user_id"] == seed_customer_user.id
    assert res["previous_role"] == "CUSTOMER"
    assert res["new_role"] == "SUSPENDED"
    assert res["updated_by"] == seed_admin_user.id

    # Verify audit log in database
    logs = auth_service.user_repo.get_audit_logs(target_user_id=seed_customer_user.id)
    assert len(logs) >= 1
    latest = logs[0]
    assert latest["actor_admin_id"] == seed_admin_user.id
    assert latest["previous_role"] == "CUSTOMER"
    assert latest["new_role"] == "SUSPENDED"


@pytest.mark.ac("AC-02")
def test_customer_cannot_update_role(auth_service, seed_customer_user):
    """AC-02: Customer calling role update raises UnauthorizedRoleModificationException."""
    with pytest.raises(UnauthorizedRoleModificationException):
        auth_service.update_user_role(
            target_user_id=seed_customer_user.id,
            new_role_str="ADMIN",
            actor_admin=seed_customer_user  # Customer attempting role update
        )


@pytest.mark.ac("AC-02")
def test_invalid_role_string_rejected(auth_service, seed_admin_user, seed_customer_user):
    """AC-02: Invalid role raises InvalidRoleException."""
    with pytest.raises(InvalidRoleException):
        auth_service.update_user_role(
            target_user_id=seed_customer_user.id,
            new_role_str="SUPERUSER",  # Invalid role
            actor_admin=seed_admin_user
        )
