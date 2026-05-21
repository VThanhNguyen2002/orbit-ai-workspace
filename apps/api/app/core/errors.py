from collections.abc import Sequence
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.responses import ApiErrorCode, ApiErrorDetail, error_envelope


class ApiError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: ApiErrorCode,
        message: str,
        details: Sequence[ApiErrorDetail] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = list(details) if details is not None else None


STATUS_CODE_TO_API_ERROR: dict[int, ApiErrorCode] = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "UNPROCESSABLE",
    429: "RATE_LIMITED",
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_envelope(
                request,
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ApiErrorDetail(
                field=_format_error_location(error.get("loc", ())),
                message=str(error.get("msg", "Invalid request value")),
            )
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=error_envelope(
                request,
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = STATUS_CODE_TO_API_ERROR.get(exc.status_code, "INTERNAL_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_envelope(
                request,
                code=code,
                message=_http_error_message(exc),
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_envelope(
                request,
                code="INTERNAL_ERROR",
                message="Internal server error",
            ).model_dump(exclude_none=True),
        )


def _format_error_location(location: Sequence[object]) -> str:
    parts = [str(part) for part in location if part not in {"body", "query", "path"}]
    return ".".join(parts) or "request"


def _http_error_message(exc: StarletteHTTPException) -> str:
    if isinstance(exc.detail, str) and exc.detail:
        return exc.detail

    try:
        return HTTPStatus(exc.status_code).phrase
    except ValueError:
        return "Request failed"
