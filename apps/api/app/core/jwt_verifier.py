from dataclasses import dataclass
from typing import Annotated, Literal, Protocol
from uuid import UUID

import jwt
from fastapi import Depends
from jwt import PyJWTError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.config import Settings, get_settings


class JwtVerificationError(Exception):
    """Raised when a bearer token cannot be accepted as authenticated."""


class VerifiedJwtClaims(BaseModel):
    model_config = ConfigDict(extra="allow")

    sub: str = Field(min_length=1)
    role: Literal["authenticated"]

    @field_validator("sub")
    @classmethod
    def require_non_empty_subject(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("subject must not be blank")
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError("subject must be a UUID") from exc
        return value


class JwtVerifier(Protocol):
    def verify(self, token: str) -> VerifiedJwtClaims: ...


@dataclass(frozen=True)
class PyJwtRsaVerifier:
    public_key: str
    issuer: str
    audience: str

    def verify(self, token: str) -> VerifiedJwtClaims:
        try:
            claims = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
            return VerifiedJwtClaims.model_validate(claims)
        except (PyJWTError, ValidationError, TypeError, ValueError) as exc:
            raise JwtVerificationError("JWT verification failed") from exc


def get_jwt_verifier(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JwtVerifier | None:
    if not settings.jwt_public_key or not settings.jwt_issuer or not settings.jwt_audience:
        return None

    return PyJwtRsaVerifier(
        public_key=settings.jwt_public_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
