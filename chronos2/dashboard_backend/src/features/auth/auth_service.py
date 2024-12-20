from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from src.core.configs.config import settings
from src.core.configs.database import session_scope
from src.core.models import User
from src.features.auth.jwt_handler import (
    UserToken,
    create_access_token,
    create_refresh_token,
)
from src.features.auth.password_manager import PasswordManager


class Tokens(BaseModel):
    access: str
    refresh: str


class AuthService:
    def __init__(self):
        self.jwt_secret_key = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.password_manager = PasswordManager()

    def create_user(self, email: str, password: str):
        with session_scope() as session:
            if session.query(User).filter(User.email == email).first():
                return None

            user = User(
                email=email, password=self.password_manager.hash_password(password)
            )
            session.add(user)
            return user

    def authenticate_user(self, email: str, password: str):
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).first()
            session.expunge_all()
            if user:
                if self.password_manager.verify_password(password, user.password):
                    return user
            return None

    def login(self, email: str, password: str):
        user = self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        tokens = self.__create_tokens_from_credentials(user)
        return tokens

    def __create_tokens_from_credentials(self, user):
        user_token = UserToken(
            user_id=str(user.id),
        )
        access_token = create_access_token(user_token)
        refresh_token = create_refresh_token(user_token)
        tokens = Tokens(access=access_token, refresh=refresh_token)
        return tokens
