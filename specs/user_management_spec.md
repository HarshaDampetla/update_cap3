# Feature Specification: User Onboarding, Authentication & Role Administration

**Feature ID:** SPEC-USER-001  
**Target Module:** User Management & Identity  
**Primary ACs:** `AC-01`, `AC-02`  
**Primary NFRs:** `NFR-03`, `NFR-04`  

---

## 1. Feature Overview

The User Management module provides self-service registration and authentication for retail customers, alongside role governance and audit logging for administrators. Security boundaries partition retail investor operations from supervisory administrative endpoints.

---

## 2. Acceptance Criteria (Testable Specifications)

### AC-01: Customer Registration & Baseline State
- **Given** an unregistered email address `user@example.com` and a password meeting security criteria (min 8 chars, 1 uppercase, 1 digit, 1 special char).
- **When** a `POST` request is submitted to `/api/auth/register`.
- **Then** a new user account is created in the database.
- **And** the account state is initialized to `ACTIVE`.
- **And** the account role is initialized to `CUSTOMER`.
- **And** the password is saved strictly as a `bcrypt` hash (`NFR-03`); plaintext password is never stored or logged.
- **And** a default portfolio cash balance of `$100,000.00` is initialized for self-serve paper trading.
- **And** response status is `201 Created` with a sanitized user DTO.

### AC-02: Admin Role Modification & Audit Trail
- **Given** an authenticated user with role `ADMIN`.
- **When** the admin submits a `PATCH /api/admin/users/{user_id}/role` request specifying a valid target role (`CUSTOMER`, `ADMIN`, `SUSPENDED`).
- **Then** the target user's role is updated in the database.
- **And** an immutable audit record is created in `user_role_audit_logs` containing:
  - `target_user_id`: ID of the affected user.
  - `actor_admin_id`: ID of the admin making the change.
  - `previous_role`: Prior role string.
  - `new_role`: Updated role string.
  - `timestamp`: UTC timestamp of the action.
- **And** if an authenticated `CUSTOMER` attempts to call this endpoint, the request is rejected with `403 Forbidden` (`NFR-04`).

---

## 3. API Contracts & Data Transfer Objects

### 3.1 POST /api/auth/register
- **Request Body:**
  ```json
  {
    "email": "investor@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response: 201 Created**
  ```json
  {
    "id": 101,
    "email": "investor@example.com",
    "role": "CUSTOMER",
    "status": "ACTIVE",
    "created_at": "2026-10-04T12:00:00Z"
  }
  ```

### 3.2 POST /api/auth/login
- **Request Body:**
  ```json
  {
    "email": "investor@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response: 200 OK**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 101,
      "email": "investor@example.com",
      "role": "CUSTOMER"
    }
  }
  ```

### 3.3 PATCH /api/admin/users/{user_id}/role
- **Headers:** `Authorization: Bearer <ADMIN_JWT>`
- **Request Body:**
  ```json
  {
    "role": "SUSPENDED"
  }
  ```
- **Response: 200 OK**
  ```json
  {
    "user_id": 101,
    "previous_role": "CUSTOMER",
    "new_role": "SUSPENDED",
    "updated_by": 1,
    "updated_at": "2026-10-04T12:05:00Z"
  }
  ```

---

## 4. Domain Models & Exceptions

```python
# src/domain/entities/user.py
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
```

### Domain Exceptions:
- `EmailAlreadyExistsException` (409 Conflict)
- `InvalidRoleException` (400 Bad Request)
- `UnauthorizedRoleModificationException` (403 Forbidden)

---

## 5. Test Matrix & Traceability

1. `tests/unit/domain/test_user_registration.py` $\rightarrow$ Validates `AC-01`: Account created in `ACTIVE` state with `CUSTOMER` role.
2. `tests/unit/domain/test_password_hashing.py` $\rightarrow$ Validates `NFR-03`: Bcrypt verification, plaintext password rejection in logs.
3. `tests/unit/services/test_admin_role_audit.py` $\rightarrow$ Validates `AC-02`: Role update persists audit log with actor ID and timestamp.
4. `tests/architecture/test_role_boundaries.py` $\rightarrow$ Validates `NFR-04`: Non-admin requests to `/api/admin/*` return 403.
