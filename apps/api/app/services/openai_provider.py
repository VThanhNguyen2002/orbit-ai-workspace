"""OpenAI summarization provider adapter boundary.

This module is intentionally transport-only and network-free by default:
- no OpenAI SDK import
- no HTTP client
- no credential or environment lookup
- no logging of prompts, note content, tokens, keys, or auth headers
"""
from __future__ import annotations

import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol
from zoneinfo import ZoneInfo

from app.services.ai_prompting import (
    NoteSummarizationPrompt,
    NoteSummarizationPromptMetadata,
    PromptRole,
    redact_diagnostic,
)
from app.services.ai_summarization import AiActionItem, AiSummaryResult

OpenAIProviderFailureKind = Literal["timeout", "unavailable", "malformed_response"]
OpenAIProviderErrorCode = Literal[
    "provider_timeout",
    "provider_unavailable",
    "provider_invalid_response",
]
ActionItemPriority = Literal["urgent", "high", "medium", "low"]

_UTC = ZoneInfo("UTC")
_ALLOWED_PRIORITIES: frozenset[str] = frozenset(("urgent", "high", "medium", "low"))
_FAILURE_CODES: dict[OpenAIProviderFailureKind, OpenAIProviderErrorCode] = {
    "timeout": "provider_timeout",
    "unavailable": "provider_unavailable",
    "malformed_response": "provider_invalid_response",
}
_FAILURE_MESSAGES: dict[OpenAIProviderErrorCode, str] = {
    "provider_timeout": "OpenAI provider request timed out",
    "provider_unavailable": "OpenAI provider is unavailable",
    "provider_invalid_response": "OpenAI provider returned an invalid response",
}


@dataclass(frozen=True)
class OpenAIProviderMessage:
    role: PromptRole
    content: str = field(repr=False)


@dataclass(frozen=True)
class OpenAIProviderRequest:
    model: str
    prompt_metadata: NoteSummarizationPromptMetadata
    messages: tuple[OpenAIProviderMessage, ...] = field(repr=False)
    max_output_tokens: int | None = None

    @classmethod
    def from_prompt(
        cls,
        *,
        model: str,
        prompt: NoteSummarizationPrompt,
        max_output_tokens: int | None,
    ) -> OpenAIProviderRequest:
        return cls(
            model=model,
            prompt_metadata=prompt.metadata,
            messages=tuple(
                OpenAIProviderMessage(role=message.role, content=message.content)
                for message in prompt.messages
            ),
            max_output_tokens=max_output_tokens,
        )

    def sensitive_terms(self) -> tuple[str, ...]:
        """Return provider-facing prompt terms that must not leave diagnostics."""
        terms: list[str] = [self._provider_text()]
        for message in self.messages:
            terms.append(message.content)
            terms.extend(line for line in message.content.splitlines() if line)

        return tuple(term for term in terms if term)

    def log_safe_metadata(self) -> dict[str, int | str | None]:
        metadata = self.prompt_metadata.as_dict()
        return {
            "model": self.model,
            "source_type": metadata["source_type"],
            "content_type": metadata["content_type"],
            "title_chars": metadata["title_chars"],
            "content_chars": metadata["content_chars"],
            "message_count": len(self.messages),
            "max_output_tokens": self.max_output_tokens,
        }

    def _provider_text(self) -> str:
        return "\n\n".join(
            f"{message.role.upper()}:\n{message.content}"
            for message in self.messages
        )


@dataclass(frozen=True)
class OpenAIProviderActionItem:
    text: str = field(repr=False)
    priority: ActionItemPriority


@dataclass(frozen=True)
class OpenAIProviderResponse:
    model: str
    summary_text: str = field(repr=False)
    action_items: tuple[OpenAIProviderActionItem, ...] = field(repr=False)
    created_at: str | None = None


class OpenAIProviderTransport(Protocol):
    """Injected transport boundary for future OpenAI provider calls."""

    def complete(self, request: OpenAIProviderRequest) -> OpenAIProviderResponse: ...


class OpenAIProviderTransportError(Exception):
    """Safe transport error raised by injected transports."""

    def __init__(
        self,
        *,
        kind: OpenAIProviderFailureKind,
        diagnostic: object | None = None,
    ) -> None:
        self.kind = kind
        self._diagnostic = diagnostic
        super().__init__(_FAILURE_MESSAGES[_FAILURE_CODES[kind]])

    @property
    def diagnostic(self) -> object | None:
        return self._diagnostic

    def __repr__(self) -> str:
        return f"OpenAIProviderTransportError(kind={self.kind!r})"


class OpenAIProviderError(Exception):
    """Provider-facing safe error with redacted diagnostics only."""

    def __init__(
        self,
        *,
        code: OpenAIProviderErrorCode,
        diagnostic: object,
        sensitive_terms: Iterable[str],
    ) -> None:
        self.code = code
        self._safe_diagnostic = redact_diagnostic(
            diagnostic,
            sensitive_terms=sensitive_terms,
        )
        super().__init__(_FAILURE_MESSAGES[code])

    def safe_diagnostic(self) -> object:
        return self._safe_diagnostic

    def __repr__(self) -> str:
        return f"OpenAIProviderError(code={self.code!r})"


class OpenAISummarizationProvider:
    """SummarizationProvider-compatible adapter with injected transport only."""

    def __init__(
        self,
        *,
        transport: OpenAIProviderTransport,
        model: str,
        max_output_tokens: int | None = None,
    ) -> None:
        if not model.strip():
            msg = "OpenAI provider model must be configured"
            raise ValueError(msg)
        if max_output_tokens is not None and max_output_tokens < 1:
            msg = "OpenAI provider max_output_tokens must be positive"
            raise ValueError(msg)

        self._transport = transport
        self._model = model
        self._max_output_tokens = max_output_tokens

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def summarize(
        self,
        *,
        source_id: str,
        prompt: NoteSummarizationPrompt,
    ) -> AiSummaryResult:
        request = OpenAIProviderRequest.from_prompt(
            model=self._model,
            prompt=prompt,
            max_output_tokens=self._max_output_tokens,
        )

        try:
            response = self._transport.complete(request)
        except OpenAIProviderTransportError as exc:
            raise self._safe_error(
                code=_FAILURE_CODES[exc.kind],
                request=request,
                diagnostic={
                    "request": request.log_safe_metadata(),
                    "transport": exc.diagnostic,
                },
            ) from None
        except TimeoutError:
            raise self._safe_error(
                code="provider_timeout",
                request=request,
                diagnostic={"request": request.log_safe_metadata()},
            ) from None

        return self._result_from_response(
            source_id=source_id,
            request=request,
            response=response,
        )

    def _result_from_response(
        self,
        *,
        source_id: str,
        request: OpenAIProviderRequest,
        response: OpenAIProviderResponse,
    ) -> AiSummaryResult:
        if not response.summary_text.strip():
            raise self._safe_error(
                code="provider_invalid_response",
                request=request,
                diagnostic={
                    "request": request.log_safe_metadata(),
                    "response": {"summary_text": response.summary_text},
                },
            )

        action_items = self._validated_action_items(
            request=request,
            response=response,
        )

        return AiSummaryResult(
            id=str(uuid.uuid4()),
            user_id="",
            source_id=source_id,
            source_type="note",
            content=response.summary_text,
            action_items=action_items,
            provider=self.provider_name,
            model=response.model or self.model_name,
            created_at=response.created_at or datetime.now(_UTC).isoformat(),
        )

    def _validated_action_items(
        self,
        *,
        request: OpenAIProviderRequest,
        response: OpenAIProviderResponse,
    ) -> list[AiActionItem]:
        action_items: list[AiActionItem] = []
        for item in response.action_items:
            if not item.text.strip() or item.priority not in _ALLOWED_PRIORITIES:
                raise self._safe_error(
                    code="provider_invalid_response",
                    request=request,
                    diagnostic={
                        "request": request.log_safe_metadata(),
                        "response": {"action_item_priority": item.priority},
                    },
                )
            action_items.append(AiActionItem(text=item.text, priority=item.priority))

        return action_items

    def _safe_error(
        self,
        *,
        code: OpenAIProviderErrorCode,
        request: OpenAIProviderRequest,
        diagnostic: object,
    ) -> OpenAIProviderError:
        return OpenAIProviderError(
            code=code,
            diagnostic={
                "provider": self.provider_name,
                "model": self.model_name,
                "request": request.log_safe_metadata(),
                "diagnostic": diagnostic,
            },
            sensitive_terms=request.sensitive_terms(),
        )
