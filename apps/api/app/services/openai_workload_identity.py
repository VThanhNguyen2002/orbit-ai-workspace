"""Mocked Workload Identity Federation boundary for future OpenAI auth.

This module is intentionally fake-only and network-free:
- no OpenAI SDK import
- no environment lookup
- no token parsing or cryptographic validation
- no OIDC/JWT or access-token logging
- no runtime provider wiring
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol

from app.services.ai_prompting import redact_diagnostic

WorkloadIdentityExchangeErrorCode = Literal[
    "exchange_invalid_request",
    "exchange_unavailable",
    "exchange_invalid_response",
]
FakeWorkloadIdentityExchangeMode = Literal[
    "success",
    "unavailable",
    "malformed_response",
]
AccessTokenType = Literal["Bearer"]

_FAKE_ACCESS_TOKEN_PLACEHOLDER = "fake-wif-access-token-placeholder"
_DEFAULT_EXPIRES_IN_SECONDS = 900
_MAX_EXPIRES_IN_SECONDS = 3600
_ERROR_MESSAGES: dict[WorkloadIdentityExchangeErrorCode, str] = {
    "exchange_invalid_request": "Workload identity exchange request is invalid",
    "exchange_unavailable": "Workload identity exchange is unavailable",
    "exchange_invalid_response": "Workload identity exchange returned invalid data",
}


@dataclass(frozen=True, repr=False)
class WorkloadIdentitySubject:
    """Claim metadata needed to evaluate a future WIF trust policy."""

    issuer: str
    audience: str
    subject: str
    repository: str
    ref: str
    workflow: str
    environment: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer", self.issuer),
            ("audience", self.audience),
            ("subject", self.subject),
            ("repository", self.repository),
            ("ref", self.ref),
            ("workflow", self.workflow),
        ):
            if not value.strip():
                msg = f"Workload identity {name} is required"
                raise ValueError(msg)

        if self.environment is not None and not self.environment.strip():
            msg = "Workload identity environment must be omitted or non-empty"
            raise ValueError(msg)

    def log_safe_metadata(self) -> dict[str, bool]:
        return {
            "issuer_configured": bool(self.issuer.strip()),
            "audience_configured": bool(self.audience.strip()),
            "subject_configured": bool(self.subject.strip()),
            "repository_configured": bool(self.repository.strip()),
            "ref_configured": bool(self.ref.strip()),
            "workflow_configured": bool(self.workflow.strip()),
            "environment_configured": self.environment is not None,
        }

    def __repr__(self) -> str:
        metadata = self.log_safe_metadata()
        return (
            "WorkloadIdentitySubject("
            f"issuer_configured={metadata['issuer_configured']!r}, "
            f"audience_configured={metadata['audience_configured']!r}, "
            f"subject_configured={metadata['subject_configured']!r}, "
            f"repository_configured={metadata['repository_configured']!r}, "
            f"ref_configured={metadata['ref_configured']!r}, "
            f"workflow_configured={metadata['workflow_configured']!r}, "
            f"environment_configured={metadata['environment_configured']!r})"
        )


@dataclass(frozen=True)
class WorkloadIdentityExchangeRequest:
    """Opaque identity assertion plus explicit claim metadata."""

    identity_assertion: str = field(repr=False)
    subject: WorkloadIdentitySubject
    target_provider: Literal["openai"] = "openai"

    def __post_init__(self) -> None:
        if not self.identity_assertion.strip():
            msg = "Workload identity assertion is required"
            raise ValueError(msg)
        if self.target_provider != "openai":
            msg = "Workload identity target provider is unsupported"
            raise ValueError(msg)

    def sensitive_terms(self) -> tuple[str, ...]:
        return (self.identity_assertion,)

    def log_safe_metadata(self) -> dict[str, bool | str]:
        return {
            "target_provider": self.target_provider,
            "identity_assertion_present": bool(self.identity_assertion.strip()),
            **self.subject.log_safe_metadata(),
        }


@dataclass(frozen=True)
class WorkloadIdentityExchangeResult:
    """Future provider access token result, kept redacted by repr."""

    access_token: str = field(repr=False)
    expires_in_seconds: int
    token_type: AccessTokenType = field(default="Bearer", repr=False)

    def log_safe_metadata(self) -> dict[str, bool | int]:
        return {
            "access_token_present": bool(self.access_token.strip()),
            "expires_in_seconds": self.expires_in_seconds,
        }

    def __repr__(self) -> str:
        metadata = self.log_safe_metadata()
        return (
            "WorkloadIdentityExchangeResult("
            f"access_token_present={metadata['access_token_present']!r}, "
            f"expires_in_seconds={metadata['expires_in_seconds']!r})"
        )


class WorkloadIdentityTokenExchanger(Protocol):
    """Interface for a future token exchange implementation."""

    def exchange(
        self,
        request: WorkloadIdentityExchangeRequest,
    ) -> WorkloadIdentityExchangeResult: ...


class WorkloadIdentityExchangeError(Exception):
    """Safe WIF exchange error with redacted diagnostics only."""

    def __init__(
        self,
        *,
        code: WorkloadIdentityExchangeErrorCode,
        diagnostic: object,
        sensitive_terms: tuple[str, ...] = (),
    ) -> None:
        self.code = code
        self._safe_diagnostic = redact_diagnostic(
            diagnostic,
            sensitive_terms=sensitive_terms,
        )
        super().__init__(_ERROR_MESSAGES[code])

    def safe_diagnostic(self) -> object:
        return self._safe_diagnostic

    def __repr__(self) -> str:
        return f"WorkloadIdentityExchangeError(code={self.code!r})"


class FakeWorkloadIdentityTokenExchanger:
    """Deterministic fake exchanger for boundary tests only."""

    def __init__(
        self,
        *,
        trusted_subject: WorkloadIdentitySubject,
        mode: FakeWorkloadIdentityExchangeMode = "success",
        result: WorkloadIdentityExchangeResult | None = None,
    ) -> None:
        self._trusted_subject = trusted_subject
        self._mode = mode
        self._result = result
        self.requests: list[WorkloadIdentityExchangeRequest] = []

    def exchange(
        self,
        request: WorkloadIdentityExchangeRequest,
    ) -> WorkloadIdentityExchangeResult:
        self.requests.append(request)

        if self._mode == "unavailable":
            raise _safe_exchange_error(
                code="exchange_unavailable",
                request=request,
                reason="exchange_unavailable",
            )

        self._validate_subject(request)
        result = self._result
        if result is None and self._mode == "malformed_response":
            result = WorkloadIdentityExchangeResult(
                access_token="",
                expires_in_seconds=0,
            )
        if result is None:
            result = WorkloadIdentityExchangeResult(
                access_token=_FAKE_ACCESS_TOKEN_PLACEHOLDER,
                expires_in_seconds=_DEFAULT_EXPIRES_IN_SECONDS,
            )

        return _validated_result(result=result, request=request)

    def _validate_subject(self, request: WorkloadIdentityExchangeRequest) -> None:
        for reason, actual, expected in (
            ("issuer_not_allowed", request.subject.issuer, self._trusted_subject.issuer),
            (
                "audience_not_allowed",
                request.subject.audience,
                self._trusted_subject.audience,
            ),
            (
                "subject_not_allowed",
                request.subject.subject,
                self._trusted_subject.subject,
            ),
            (
                "repository_not_allowed",
                request.subject.repository,
                self._trusted_subject.repository,
            ),
            ("ref_not_allowed", request.subject.ref, self._trusted_subject.ref),
            (
                "workflow_not_allowed",
                request.subject.workflow,
                self._trusted_subject.workflow,
            ),
            (
                "environment_not_allowed",
                request.subject.environment,
                self._trusted_subject.environment,
            ),
        ):
            if actual != expected:
                raise _safe_exchange_error(
                    code="exchange_invalid_request",
                    request=request,
                    reason=reason,
                )


def _validated_result(
    *,
    result: WorkloadIdentityExchangeResult,
    request: WorkloadIdentityExchangeRequest,
) -> WorkloadIdentityExchangeResult:
    if not result.access_token.strip():
        raise _safe_exchange_error(
            code="exchange_invalid_response",
            request=request,
            reason="missing_access_token",
            extra_sensitive_terms=(result.access_token,),
        )
    if result.expires_in_seconds < 1:
        raise _safe_exchange_error(
            code="exchange_invalid_response",
            request=request,
            reason="invalid_expires_in_seconds",
            extra_sensitive_terms=(result.access_token,),
        )
    if result.expires_in_seconds > _MAX_EXPIRES_IN_SECONDS:
        raise _safe_exchange_error(
            code="exchange_invalid_response",
            request=request,
            reason="expires_in_seconds_too_large",
            extra_sensitive_terms=(result.access_token,),
        )
    if result.token_type != "Bearer":
        raise _safe_exchange_error(
            code="exchange_invalid_response",
            request=request,
            reason="invalid_token_type",
            extra_sensitive_terms=(result.access_token,),
        )

    return result


def _safe_exchange_error(
    *,
    code: WorkloadIdentityExchangeErrorCode,
    request: WorkloadIdentityExchangeRequest,
    reason: str,
    extra_sensitive_terms: tuple[str, ...] = (),
) -> WorkloadIdentityExchangeError:
    return WorkloadIdentityExchangeError(
        code=code,
        diagnostic={
            "reason": reason,
            "request": request.log_safe_metadata(),
        },
        sensitive_terms=(
            *request.sensitive_terms(),
            *extra_sensitive_terms,
        ),
    )
