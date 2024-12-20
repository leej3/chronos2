from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.api.dto.auth import LoginForm, UserLoginResponse
from src.features.auth.auth_service import AuthService

router = APIRouter(tags=["Auth"], prefix="/auth")
auth_service = AuthService()


@router.get("/init_user")
def init_user():
    auth_service.create_user(
        email="admin@gmail.com",
        password="Aa123456@",
    )
    return JSONResponse(content={"message": "User created successfully"})


@router.post("/login")
def init_user(data: LoginForm) -> UserLoginResponse:
    tokens = auth_service.login(
        email=data.email,
        password=data.password,
    )
    return UserLoginResponse(tokens=tokens)
