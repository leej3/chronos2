from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from src.api.dto.auth import LoginForm, UserLoginResponse
from src.features.auth.auth_service import AuthService, Tokens

router = APIRouter(tags=["Auth"], prefix="/auth")
auth_service = AuthService()


@router.post("/login")
def init_user(data: LoginForm) -> UserLoginResponse:
    tokens = auth_service.login(
        email=data.email,
        password=data.password,
    )
    return UserLoginResponse(tokens=tokens)


@router.post("/token/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True)) -> UserLoginResponse:
    tokens = auth_service.refresh_access_token(refresh_token)
    return UserLoginResponse(tokens=tokens)
