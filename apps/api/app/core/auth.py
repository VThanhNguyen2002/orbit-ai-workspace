from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.core.config import AuthMode, Settings, get_settings
from app.core.errors import ApiError
from app.core.jwt_verifier import JwtVerificationError, JwtVerifier, get_jwt_verifier
from app.models.responses import ApiErrorDetail

AuthContextMode = AuthMode


class AuthContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    auth_mode: AuthContextMode
    access_token: SecretStr | None = Field(default=None, min_length=1)


def get_auth_context(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    jwt_verifier: Annotated[JwtVerifier | None, Depends(get_jwt_verifier)] = None,
) -> AuthContext:
    if settings.auth_mode == "dev":
        return AuthContext(user_id=settings.dev_user_id, auth_mode="dev")

    if settings.auth_mode == "jwt":
        return _jwt_auth_context(request=request, jwt_verifier=jwt_verifier)

    raise _unauthorized("Unsupported auth mode")


def _jwt_auth_context(*, request: Request, jwt_verifier: JwtVerifier | None) -> AuthContext:
    token = _bearer_token(request)

    if jwt_verifier is None:
        raise _unauthorized("JWT auth is not configured")

    try:
        claims = jwt_verifier.verify(token)
    except JwtVerificationError as exc:
        raise _unauthorized("Invalid bearer token") from exc

    return AuthContext(user_id=claims.sub, auth_mode="jwt", access_token=token)


def _bearer_token(request: Request) -> str:
    value = request.headers.get("authorization")
    if value is None:
        raise _unauthorized("Missing bearer token")

    parts = value.split()
    if len(parts) != 2:
        raise _unauthorized("Malformed bearer token")

    scheme, token = parts
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized("Malformed bearer token")

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
