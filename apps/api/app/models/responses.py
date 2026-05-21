from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

ApiErrorCode = Literal[
    "VALIDATION_ERROR",
    "UNAUTHORIZED",
    "FORBIDDEN",
    "NOT_FOUND",
    "CONFLICT",
    "UNPROCESSABLE",
    "RATE_LIMITED",
    "INTERNAL_ERROR",
]


class ApiMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1, max_length=128)


class ApiErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str | None = Field(default=None, min_length=1)
    message: str | None = Field(default=None, min_length=1)
    expected: Any | None = None
    actual: Any | None = None
    server_data: Any | None = None


class ApiErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ApiErrorCode
    message: str = Field(min_length=1)
    details: list[ApiErrorDetail] | None = None


class ApiErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ApiErrorPayload
    meta: ApiMeta


class ApiSuccessEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: Any
    meta: ApiMeta


def request_id_from(request: Request) -> str:
    return str(getattr(request.state, "request_id", "req_unknown"))


def success_envelope(request: Request, data: Any) -> ApiSuccessEnvelope:
    return ApiSuccessEnvelope(
        data=data,
        meta=ApiMeta(request_id=request_id_from(request)),
    )


def error_envelope(
    request: Request,
    *,
    code: ApiErrorCode,
    message: str,
    details: list[ApiErrorDetail] | None = None,
) -> ApiErrorEnvelope:
    return ApiErrorEnvelope(
        error=ApiErrorPayload(code=code, message=message, details=details),
        meta=ApiMeta(request_id=request_id_from(request)),
    )
