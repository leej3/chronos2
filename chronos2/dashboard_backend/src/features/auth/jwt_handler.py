import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated, TypedDict
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from pydantic import BaseModel
from src.core.common.exceptions import JWTInvalid
from src.core.configs.config import settings


class UserToken(BaseModel):
    user_id: str


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"


class PayloadField(str, Enum):
    USER_ID = "user_id"
    EXPIRES = "exp"
    TOKEN_TYPE = "token_type"


scheme = HTTPBearer()


class Payload(TypedDict):
    sub: str
    exp: float
    token_type: TokenType


class AccessPayload(Payload):
    username: str


class RefreshPayload(Payload):
    pass


def encode_jwt_token(payload: Payload) -> str:
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> Payload:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise JWTInvalid(message="This token is expired")


def create_refresh_token(user_token: UserToken) -> str:
    payload: AccessPayload = {
        "sub": user_token.user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        "token_type": TokenType.REFRESH,
    }
    return encode_jwt_token(payload)


def create_access_token(user_token: UserToken) -> str:
    payload: AccessPayload = {
        "sub": user_token.user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "token_type": TokenType.ACCESS,
    }
    return encode_jwt_token(payload)


def verify_access_token(token: str) -> AccessPayload:
    return verify_token_type(token, TokenType.ACCESS)


def verify_token_type(token: str, token_type: TokenType) -> Payload:
    payload: AccessPayload = decode_jwt_token(token)
    if payload["token_type"] != token_type:
        raise JWTInvalid(message="Wrong token type")
    return payload


def verify_refresh_token(token: str) -> RefreshPayload:
    return verify_token_type(token, TokenType.REFRESH)


async def revoke_user_tokens(user_id: UUID) -> None:
    # TODO: revoke tokens
    return


async def get_current_user_from_jwt_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(scheme)]
) -> UserToken:
    try:
        payload = verify_access_token(token.credentials)
        return UserToken(
            user_id=payload["sub"],
        )
    except JWTInvalid as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
