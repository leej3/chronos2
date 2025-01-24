import os
from datetime import datetime

from fastapi import HTTPException, status
from jose import JWTError
from pydantic import BaseModel
from src.core.configs.config import settings
from src.core.configs.database import session_scope
from src.core.models import User
from src.features.auth.jwt_handler import (
    UserToken,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
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
            user = session.query(User).filter(User.email == email).first()

            if user:
                user.password = self.password_manager.hash_password(password)
                session.commit()
                return user
            else:
                hashed_password = self.password_manager.hash_password(password)
                new_user = User(
                    email=email, password=hashed_password, created_at=datetime.utcnow()
                )
                session.add(new_user)
                session.commit()
                return new_user

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

    def create_or_update_user(self):
        user_index = 1
        while True:
            email_key = f"USER_{user_index}_EMAIL"
            password_key = f"USER_{user_index}_PASSWORD"

            email = os.getenv(email_key)
            password = os.getenv(password_key)

            if email and password:
                self.create_user(email=email, password=password)
                user_index += 1
            else:
                break

    def refresh_access_token(self, refresh_token: str):
        try:
            payload = verify_refresh_token(refresh_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if payload["exp"] < datetime.utcnow().timestamp():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        user_id = payload["sub"]
        new_access_token = create_access_token(UserToken(user_id=user_id))

        return Tokens(access=new_access_token, refresh=refresh_token)
