"""Mocked OpenAI SDK adapter boundary.

This module defines the application-owned shape around a future SDK client. It
is intentionally dependency-free and inert unless a caller injects a client:
- no real OpenAI SDK import
- no environment or credential lookup
- no network client construction
- no runtime route or provider selection wiring
- no raw prompt, note content, credential, header, or SDK body diagnostics
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal, Protocol

from app.services.ai_prompting import (
    NoteSummarizationPromptMetadata,
    PromptRole,
    redact_diagnostic,
)
from app.services.openai_provider import (
    ActionItemPriority,
    OpenAIProviderActionItem,
    OpenAIProviderFailureKind,
    OpenAIProviderRequest,
    OpenAIProviderResponse,
    OpenAIProviderTransportError,
)

OpenAISDKAdapterErrorCode = Literal[
    "sdk_timeout",
    "sdk_rate_limited",
    "sdk_unavailable",
    "sdk_invalid_response",
]

_ALLOWED_PRIORITIES: frozenset[str] = frozenset(("urgent", "high", "medium", "low"))
_UNSAFE_OUTPUT_MARKERS: tuple[str, ...] = (
    "access token",
    "api key",
    "api_key",
    "auth header",
    "auth_header",
    "authorization",
    "bearer ",
    "id token",
    "jwt",
    "oidc",
    "openai_api_key",
    "token:",
)
_PROVIDER_FAILURE_KIND_BY_CODE: dict[
    OpenAISDKAdapterErrorCode,
    OpenAIProviderFailureKind,
] = {
    "sdk_timeout": "timeout",
    "sdk_rate_limited": "unavailable",
    "sdk_unavailable": "unavailable",
    "sdk_invalid_response": "malformed_response",
}


@dataclass(frozen=True)
class OpenAISDKUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("input_tokens", self.input_tokens),
            ("output_tokens", self.output_tokens),
            ("total_tokens", self.total_tokens),
        ):
            if value is not None and value < 0:
                msg = f"OpenAI SDK usage {name} must be non-negative"
                raise ValueError(msg)

    def log_safe_metadata(self) -> dict[str, bool | int | None]:
        return {
            "input_tokens_present": self.input_tokens is not None,
            "output_tokens_present": self.output_tokens is not None,
            "total_tokens_present": self.total_tokens is not None,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True)
class OpenAISDKMessage:
    role: PromptRole
    content: str = field(repr=False)

    def log_safe_metadata(self) -> dict[str, int | str]:
        return {
            "role": self.role,
            "content_chars": len(self.content),
        }


@dataclass(frozen=True)
class OpenAISDKRequest:
    model: str
    prompt_metadata: NoteSummarizationPromptMetadata
    messages: tuple[OpenAISDKMessage, ...] = field(repr=False)
    timeout_seconds: int
    request_budget: int
    max_output_tokens: int | None = None

    def __post_init__(self) -> None:
        if not self.model.strip():
            msg = "OpenAI SDK request model must be configured"
            raise ValueError(msg)
        if not self.messages:
            msg = "OpenAI SDK request requires messages"
            raise ValueError(msg)
        if self.timeout_seconds < 1:
            msg = "OpenAI SDK request timeout must be positive"
            raise ValueError(msg)
        if self.request_budget < 0:
            msg = "OpenAI SDK request budget must be non-negative"
            raise ValueError(msg)
        if self.max_output_tokens is not None and self.max_output_tokens < 1:
            msg = "OpenAI SDK request max_output_tokens must be positive"
            raise ValueError(msg)

    @classmethod
    def from_provider_request(
        cls,
        *,
        request: OpenAIProviderRequest,
        timeout_seconds: int,
        request_budget: int,
    ) -> OpenAISDKRequest:
        return cls(
            model=request.model,
            prompt_metadata=request.prompt_metadata,
            messages=tuple(
                OpenAISDKMessage(role=message.role, content=message.content)
                for message in request.messages
            ),
            timeout_seconds=timeout_seconds,
            request_budget=request_budget,
            max_output_tokens=request.max_output_tokens,
        )

    def log_safe_metadata(self) -> dict[str, object]:
        metadata = self.prompt_metadata.as_dict()
        return {
            "model": self.model,
            "source_type": metadata["source_type"],
            "content_type": metadata["content_type"],
            "title_chars": metadata["title_chars"],
            "content_chars": metadata["content_chars"],
            "message_count": len(self.messages),
            "messages": [message.log_safe_metadata() for message in self.messages],
            "timeout_seconds": self.timeout_seconds,
            "request_budget": self.request_budget,
            "max_output_tokens": self.max_output_tokens,
        }


@dataclass(frozen=True)
class OpenAISDKActionItem:
    text: str = field(repr=False)
    priority: ActionItemPriority

    def log_safe_metadata(self) -> dict[str, int | str | None]:
        return {
            "text_chars": len(self.text) if isinstance(self.text, str) else None,
            "text_type": type(self.text).__name__,
            "priority": self.priority,
            "priority_type": type(self.priority).__name__,
        }


@dataclass(frozen=True)
class OpenAISDKResponse:
    model: str
    summary_text: str = field(repr=False)
    action_items: tuple[OpenAISDKActionItem, ...] = field(default=(), repr=False)
    usage: OpenAISDKUsage = field(default_factory=OpenAISDKUsage)
    created_at: str | None = None

    def log_safe_metadata(self) -> dict[str, object]:
        action_items = self.action_items if isinstance(self.action_items, tuple) else ()
        usage = (
            self.usage.log_safe_metadata()
            if isinstance(self.usage, OpenAISDKUsage)
            else {"usage_type": type(self.usage).__name__}
        )
        return {
            "model_present": isinstance(self.model, str) and bool(self.model.strip()),
            "model_type": type(self.model).__name__,
            "summary_chars": (
                len(self.summary_text) if isinstance(self.summary_text, str) else None
            ),
            "summary_type": type(self.summary_text).__name__,
            "action_item_count": len(action_items),
            "action_items_type": type(self.action_items).__name__,
            "action_items": [
                item.log_safe_metadata()
                if isinstance(item, OpenAISDKActionItem)
                else {"item_type": type(item).__name__}
                for item in action_items
            ],
            "usage": usage,
            "created_at_present": self.created_at is not None,
            "created_at_type": type(self.created_at).__name__,
        }


class OpenAISDKClient(Protocol):
    """Injected SDK-like client boundary used by default tests."""

    def create_response(self, request: OpenAISDKRequest) -> object: ...


class OpenAISDKClientRateLimitError(Exception):
    """Synthetic SDK-like rate-limit error for fake clients."""

    def __init__(self, *, diagnostic: object | None = None) -> None:
        self._diagnostic = diagnostic
        super().__init__("OpenAI SDK client rate limited")

    @property
    def diagnostic(self) -> object | None:
        return self._diagnostic

    def __repr__(self) -> str:
        return "OpenAISDKClientRateLimitError()"


class OpenAISDKClientUnavailableError(Exception):
    """Synthetic SDK-like unavailable error for fake clients."""

    def __init__(self, *, diagnostic: object | None = None) -> None:
        self._diagnostic = diagnostic
        super().__init__("OpenAI SDK client unavailable")

    @property
    def diagnostic(self) -> object | None:
        return self._diagnostic

    def __repr__(self) -> str:
        return "OpenAISDKClientUnavailableError()"


class OpenAISDKAdapterError(OpenAIProviderTransportError):
    """Safe adapter error with redacted diagnostics only."""

    def __init__(
        self,
        *,
        code: OpenAISDKAdapterErrorCode,
        diagnostic: object,
        sensitive_terms: Iterable[str] = (),
    ) -> None:
        self.code = code
        safe_diagnostic = redact_diagnostic(
            diagnostic,
            sensitive_terms=sensitive_terms,
        )
        self._safe_diagnostic = safe_diagnostic
        super().__init__(
            kind=_PROVIDER_FAILURE_KIND_BY_CODE[code],
            diagnostic=safe_diagnostic,
        )

    def safe_diagnostic(self) -> object:
        return self._safe_diagnostic

    def __repr__(self) -> str:
        return f"OpenAISDKAdapterError(code={self.code!r})"


class OpenAISDKAdapter:
    """Transport-compatible SDK adapter using only an injected client."""

    def __init__(
        self,
        *,
        client: OpenAISDKClient,
        timeout_seconds: int,
        request_budget: int,
    ) -> None:
        if timeout_seconds < 1:
            msg = "OpenAI SDK adapter timeout must be positive"
            raise ValueError(msg)
        if request_budget < 0:
            msg = "OpenAI SDK adapter request budget must be non-negative"
            raise ValueError(msg)

        self._client = client
        self._timeout_seconds = timeout_seconds
        self._request_budget = request_budget

    def complete(self, request: OpenAIProviderRequest) -> OpenAIProviderResponse:
        sdk_request = OpenAISDKRequest.from_provider_request(
            request=request,
            timeout_seconds=self._timeout_seconds,
            request_budget=self._request_budget,
        )

        try:
            raw_response = self._client.create_response(sdk_request)
        except TimeoutError:
            raise self._safe_error(
                code="sdk_timeout",
                request=sdk_request,
                provider_request=request,
                diagnostic={"reason": "timeout"},
            ) from None
        except OpenAISDKClientRateLimitError as exc:
            raise self._safe_error(
                code="sdk_rate_limited",
                request=sdk_request,
                provider_request=request,
                diagnostic={
                    "reason": "rate_limited",
                    "client": exc.diagnostic,
                },
            ) from None
        except OpenAISDKClientUnavailableError as exc:
            raise self._safe_error(
                code="sdk_unavailable",
                request=sdk_request,
                provider_request=request,
                diagnostic={
                    "reason": "unavailable",
                    "client": exc.diagnostic,
                },
            ) from None
        except ConnectionError:
            raise self._safe_error(
                code="sdk_unavailable",
                request=sdk_request,
                provider_request=request,
                diagnostic={"reason": "connection_unavailable"},
            ) from None

        response = self._validated_response(
            raw_response=raw_response,
            request=sdk_request,
            provider_request=request,
        )
        return OpenAIProviderResponse(
            model=response.model,
            summary_text=response.summary_text,
            action_items=tuple(
                OpenAIProviderActionItem(
                    text=item.text,
                    priority=item.priority,
                )
                for item in response.action_items
            ),
            created_at=response.created_at,
        )

    def _validated_response(
        self,
        *,
        raw_response: object,
        request: OpenAISDKRequest,
        provider_request: OpenAIProviderRequest,
    ) -> OpenAISDKResponse:
        if not isinstance(raw_response, OpenAISDKResponse):
            raise self._safe_error(
                code="sdk_invalid_response",
                request=request,
                provider_request=provider_request,
                diagnostic={
                    "reason": "unexpected_response_type",
                    "response_type": type(raw_response).__name__,
                },
            )

        if not isinstance(raw_response.model, str):
            raise self._invalid_response_error(
                reason="invalid_model_type",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if not raw_response.model.strip():
            raise self._invalid_response_error(
                reason="missing_model",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if not isinstance(raw_response.summary_text, str):
            raise self._invalid_response_error(
                reason="invalid_summary_type",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if not raw_response.summary_text.strip():
            raise self._invalid_response_error(
                reason="missing_summary",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if _contains_unsafe_output_marker(raw_response.summary_text):
            raise self._invalid_response_error(
                reason="unsafe_summary",
                response=raw_response,
                request=request,
                provider_request=provider_request,
                extra_sensitive_terms=(raw_response.summary_text,),
            )

        if not isinstance(raw_response.action_items, tuple):
            raise self._invalid_response_error(
                reason="invalid_action_items_type",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if not isinstance(raw_response.usage, OpenAISDKUsage):
            raise self._invalid_response_error(
                reason="invalid_usage_type",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )
        if raw_response.created_at is not None and not isinstance(
            raw_response.created_at,
            str,
        ):
            raise self._invalid_response_error(
                reason="invalid_created_at_type",
                response=raw_response,
                request=request,
                provider_request=provider_request,
            )

        for item in raw_response.action_items:
            if not isinstance(item, OpenAISDKActionItem):
                raise self._invalid_response_error(
                    reason="unexpected_action_item_type",
                    response=raw_response,
                    request=request,
                    provider_request=provider_request,
                )
            if not isinstance(item.text, str):
                raise self._invalid_response_error(
                    reason="invalid_action_item_text_type",
                    response=raw_response,
                    request=request,
                    provider_request=provider_request,
                )
            if not item.text.strip():
                raise self._invalid_response_error(
                    reason="missing_action_item_text",
                    response=raw_response,
                    request=request,
                    provider_request=provider_request,
                )
            if item.priority not in _ALLOWED_PRIORITIES:
                raise self._invalid_response_error(
                    reason="invalid_action_item_priority",
                    response=raw_response,
                    request=request,
                    provider_request=provider_request,
                )
            if _contains_unsafe_output_marker(item.text):
                raise self._invalid_response_error(
                    reason="unsafe_action_item_text",
                    response=raw_response,
                    request=request,
                    provider_request=provider_request,
                    extra_sensitive_terms=(item.text,),
                )

        return raw_response

    def _invalid_response_error(
        self,
        *,
        reason: str,
        response: OpenAISDKResponse,
        request: OpenAISDKRequest,
        provider_request: OpenAIProviderRequest,
        extra_sensitive_terms: tuple[str, ...] = (),
    ) -> OpenAISDKAdapterError:
        return self._safe_error(
            code="sdk_invalid_response",
            request=request,
            provider_request=provider_request,
            diagnostic={
                "reason": reason,
                "response": response.log_safe_metadata(),
            },
            extra_sensitive_terms=extra_sensitive_terms,
        )

    def _safe_error(
        self,
        *,
        code: OpenAISDKAdapterErrorCode,
        request: OpenAISDKRequest,
        provider_request: OpenAIProviderRequest,
        diagnostic: object,
        extra_sensitive_terms: tuple[str, ...] = (),
    ) -> OpenAISDKAdapterError:
        return OpenAISDKAdapterError(
            code=code,
            diagnostic={
                "adapter": "openai_sdk",
                "request": request.log_safe_metadata(),
                "diagnostic": diagnostic,
            },
            sensitive_terms=(
                *_provider_request_sensitive_terms(provider_request),
                *extra_sensitive_terms,
            ),
        )


def _provider_request_sensitive_terms(
    request: OpenAIProviderRequest,
) -> tuple[str, ...]:
    terms: list[str] = []
    for message in request.messages:
        terms.append(message.content)
        terms.extend(line for line in message.content.splitlines() if line)

    return tuple(terms)


def _contains_unsafe_output_marker(value: str) -> bool:
    normalized = value.lower()
    return any(marker in normalized for marker in _UNSAFE_OUTPUT_MARKERS)
