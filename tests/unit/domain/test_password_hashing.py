import pytest
from src.services.auth_service import AuthService


@pytest.mark.nfr("NFR-03")
def test_bcrypt_password_hashing_and_verification():
    """NFR-03: Passwords stored using bcrypt with work factor >= 12."""
    plain = "SuperSecurePassword123!"
    hashed = AuthService.hash_password(plain)

    # Verify bcrypt signature $2b$ or $2a$
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    # Verify work factor is 12
    cost = hashed.split("$")[2]
    assert int(cost) >= 12

    # Verification checks
    assert AuthService.verify_password(plain, hashed) is True
    assert AuthService.verify_password("WrongPassword123!", hashed) is False


@pytest.mark.nfr("NFR-03")
def test_password_strength_validation():
    """NFR-03: Password validation policy."""
    assert AuthService.validate_password_strength("StrongPass1!") is True
    assert AuthService.validate_password_strength("short1!") is False
    assert AuthService.validate_password_strength("nouppercase1!") is False
    assert AuthService.validate_password_strength("NoDigitsHere!") is False
    assert AuthService.validate_password_strength("NoSpecialChar1") is False
