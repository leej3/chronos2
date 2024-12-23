from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.api.dto.auth import LoginForm, UserLoginResponse
from src.features.auth.auth_service import AuthService

router = APIRouter(tags=["Auth"], prefix="/auth")
auth_service = AuthService()


@router.post("/login")
def init_user(data: LoginForm) -> UserLoginResponse:
    tokens = auth_service.login(
        email=data.email,
        password=data.password,
    )
    return UserLoginResponse(tokens=tokens)
