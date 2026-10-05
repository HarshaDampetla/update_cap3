import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from decimal import Decimal
import jwt
import bcrypt
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.exceptions import (
    EmailAlreadyExistsException,
    InvalidRoleException,
    UnauthorizedRoleModificationException,
)
from src.repositories.user_repository import UserRepository
from src.repositories.portfolio_repository import PortfolioRepository

SECRET_KEY = os.environ.get("JWT_SECRET", "marketscope-capstone-jwt-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class AuthService:
    def __init__(self, user_repo: UserRepository, portfolio_repo: Optional[PortfolioRepository] = None):
        self.user_repo = user_repo
        self.portfolio_repo = portfolio_repo

    @staticmethod
    def hash_password(password: str) -> str:
        """NFR-03: Strong bcrypt KDF with rounds >= 12."""
        # bcrypt has 72-byte max length limitation
        pw_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """NFR-03: Verify bcrypt hash safely."""
        try:
            pw_bytes = plain_password.encode("utf-8")[:72]
            h_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pw_bytes, h_bytes)
        except Exception:
            return False

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Min 8 chars, 1 uppercase, 1 digit, 1 special char."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[@$!%*?&#^()_\-+=\[\]{};:'\",.<>]", password):
            return False
        return True

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": now})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    def register(self, email: str, password: str) -> User:
        """AC-01: Customer registration with ACTIVE status, CUSTOMER role, and $100,000 initial cash."""
        clean_email = email.lower().strip()
        existing = self.user_repo.get_by_email(clean_email)
        if existing:
            raise EmailAlreadyExistsException(clean_email)

        # Hash password securely (NFR-03)
        hashed_password = self.hash_password(password)

        user = self.user_repo.create(
            email=clean_email,
            password_hash=hashed_password,
            role=UserRole.CUSTOMER.value,
            status=UserStatus.ACTIVE.value
        )

        # Initialize default cash balance of $100,000.00 (AC-01)
        if self.portfolio_repo:
            self.portfolio_repo.init_cash(user.id, Decimal("100000.0000"))

        return user

    def login(self, email: str, password: str) -> Dict[str, Any]:
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            return None

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        token = self.create_access_token(token_data)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value
            }
        }

    def update_user_role(self, target_user_id: int, new_role_str: str, actor_admin: User) -> Dict[str, Any]:
        """AC-02: Admin role modification with immutable audit log."""
        if actor_admin.role != UserRole.ADMIN:
            raise UnauthorizedRoleModificationException("Only administrators may modify user roles.")

        try:
            new_role = UserRole(new_role_str)
        except ValueError:
            raise InvalidRoleException(new_role_str)

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise ValueError(f"Target user with ID {target_user_id} not found.")

        prev_role = target_user.role.value
        updated_user = self.user_repo.update_role(
            target_user_id=target_user_id,
            new_role=new_role.value,
            actor_admin_id=actor_admin.id
        )

        return {
            "user_id": updated_user.id,
            "previous_role": prev_role,
            "new_role": updated_user.role.value,
            "updated_by": actor_admin.id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
