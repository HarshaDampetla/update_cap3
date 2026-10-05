from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    SUSPENDED = "SUSPENDED"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class User(BaseModel):
    id: int
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.CUSTOMER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    def __repr__(self) -> str:
        # NFR-03: Never include password hash in string representations
        return f"<User id={self.id} email='{self.email}' role='{self.role}' status='{self.status}'>"

    def __str__(self) -> str:
        return self.__repr__()
