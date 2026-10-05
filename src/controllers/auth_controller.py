from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from src.services.auth_service import AuthService
from src.controllers.deps import get_auth_service, get_current_user
from src.domain.entities.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    """AC-01: Customer registration."""
    user = auth_service.register(req.email, req.password)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value,
        "created_at": user.created_at.isoformat()
    }


@router.post("/login")
def login(req: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """User authentication returning JWT access token."""
    res = auth_service.login(req.email, req.password)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}
        )
    return res


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns current authenticated user details."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "status": current_user.status.value
    }
