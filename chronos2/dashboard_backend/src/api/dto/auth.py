from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel
from src.features.auth.auth_service import Tokens


class LoginForm(BaseModel):
    email: str
    password: str


class UserLoginResponse(BaseModel):
    tokens: Tokens
