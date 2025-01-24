from typing import Annotated

from fastapi import Request, Security, status
from fastapi.responses import JSONResponse
from src.core.common import exceptions as ex
from src.features.auth.jwt_handler import UserToken, get_current_user_from_jwt_token


async def exception_handler(_: Request, exc: ex.GenericError) -> JSONResponse:
    if isinstance(exc, ex.ServiceUnavailable):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error_code": exc.code or 999,
                "message": exc.message or "unknown error",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": exc.code or 999,
            "message": exc.message or "unknown error",
        },
    )


async def get_current_user(
    current_user: Annotated[UserToken, Security(get_current_user_from_jwt_token)],
) -> UserToken:
    return current_user
