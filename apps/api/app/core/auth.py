from typing import Annotated, Literal

from fastapi import Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.models.responses import ApiErrorDetail

AuthContextMode = Literal["dev", "jwt"]


class AuthContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    auth_mode: AuthContextMode
    access_token: str | None = Field(default=None, min_length=1)


def get_auth_context(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthContext:
    if settings.auth_mode == "dev":
        return AuthContext(user_id=settings.dev_user_id, auth_mode="dev")

    return _jwt_auth_context(request=request, settings=settings)


def _jwt_auth_context(*, request: Request, settings: Settings) -> AuthContext:
    credentials = _bearer_token(request)
    if credentials is None:
        raise _unauthorized("Missing bearer token")

    if not settings.supabase_jwt_secret:
        raise _unauthorized("JWT auth is not configured")

    # Slice 6E establishes the auth boundary without committing a JWT library or
    # requiring live Supabase in CI. Full signature/audience/expiry validation is
    # intentionally deferred behind this function.
    raise _unauthorized("JWT auth validation is not implemented")


def _bearer_token(request: Request) -> str | None:
    value = request.headers.get("authorization")
    if value is None:
        return None

    scheme, _, token = value.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token


def _unauthorized(message: str) -> ApiError:
    return ApiError(
        status_code=401,
        code="UNAUTHORIZED",
        message=message,
        details=[
            ApiErrorDetail(
                field="authorization",
                message="unauthorized",
            ),
        ],
    )
