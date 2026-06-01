"""Prompt assembly and redaction helpers for AI service boundaries."""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from app.schemas.notes import NoteContentType

PromptRole = Literal["system", "user"]
NotePromptSourceType = Literal["note"]

_REDACTED = "[REDACTED]"
_REDACTED_KEY = "[REDACTED_KEY]"
_SUMMARY_SYSTEM_PROMPT = (
    "You summarize one user-owned note. Return a concise summary and concrete "
    "action items. Do not infer or include user identity, credentials, access "
    "tokens, authorization headers, internal entity IDs, or unrelated metadata."
)

_SENSITIVE_KEY_NAMES = frozenset(
    {
        "api_key",
        "authorization",
        "auth_header",
        "bearer_token",
        "content",
        "jwt",
        "note_content",
        "note_title",
        "openai_api_key",
        "prompt",
        "raw_user_payload",
        "secret",
        "supabase_anon_key",
        "supabase_jwt_secret",
        "supabase_publishable_key",
        "supabase_service_role_key",
        "title",
        "token",
    }
)
_SENSITIVE_KEY_FRAGMENTS = (
    "authorization",
    "api_key",
    "auth_header",
    "bearer_token",
    "openai_api_key",
    "service_role",
)
_SENSITIVE_LITERAL_NAMES = (
    "OPENAI_API_KEY",
    "SUPABASE_ANON_KEY",
    "SUPABASE_JWT_SECRET",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
)
_TOKEN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?i)\bauthorization\s*[:=]\s*bearer\s+[A-Za-z0-9._~+/=-]+"),
        _REDACTED,
    ),
    (
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
        _REDACTED,
    ),
    (
        re.compile(
            r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
        ),
        _REDACTED,
    ),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"), _REDACTED),
)


@dataclass(frozen=True)
class PromptMessage:
    role: PromptRole
    content: str = field(repr=False)


@dataclass(frozen=True)
class NoteSummarizationPromptMetadata:
    source_type: NotePromptSourceType
    content_type: NoteContentType
    title_chars: int
    content_chars: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "source_type": self.source_type,
            "content_type": self.content_type,
            "title_chars": self.title_chars,
            "content_chars": self.content_chars,
        }


@dataclass(frozen=True)
class NoteSummarizationPrompt:
    messages: tuple[PromptMessage, ...] = field(repr=False)
    metadata: NoteSummarizationPromptMetadata

    def as_provider_text(self) -> str:
        return "\n\n".join(
            f"{message.role.upper()}:\n{message.content}" for message in self.messages
        )

    def log_safe_metadata(self) -> dict[str, int | str]:
        return {
            **self.metadata.as_dict(),
            "message_count": len(self.messages),
        }


def build_note_summarization_prompt(
    *,
    title: str,
    content: str,
    content_type: NoteContentType,
) -> NoteSummarizationPrompt:
    """Build the provider-facing prompt from explicit note fields only."""
    metadata = NoteSummarizationPromptMetadata(
        source_type="note",
        content_type=content_type,
        title_chars=len(title),
        content_chars=len(content),
    )
    user_prompt = (
        "Summarize the following note.\n"
        f"Content type: {content_type}\n\n"
        "Title:\n"
        f"{title}\n\n"
        "Content:\n"
        f"{content}"
    )

    return NoteSummarizationPrompt(
        messages=(
            PromptMessage(role="system", content=_SUMMARY_SYSTEM_PROMPT),
            PromptMessage(role="user", content=user_prompt),
        ),
        metadata=metadata,
    )


def redact_diagnostic(
    value: object,
    *,
    sensitive_terms: Iterable[str] = (),
) -> object:
    """Return a log/public-safe diagnostic object with secret-bearing data masked."""
    terms = tuple(term for term in sensitive_terms if term)
    return _redact_value(value, sensitive_terms=terms)


def _redact_value(value: object, *, sensitive_terms: tuple[str, ...]) -> object:
    if isinstance(value, str):
        return _redact_text(value, sensitive_terms=sensitive_terms)

    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            safe_key = _redact_key(key)
            if _is_sensitive_key(key):
                redacted[safe_key] = _REDACTED
            else:
                redacted[safe_key] = _redact_value(
                    raw_value,
                    sensitive_terms=sensitive_terms,
                )
        return redacted

    if isinstance(value, Sequence):
        return [
            _redact_value(item, sensitive_terms=sensitive_terms) for item in value
        ]

    return value


def _redact_key(key: str) -> str:
    if _is_sensitive_key(key):
        return _REDACTED_KEY

    return _redact_text(key, sensitive_terms=())


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    if normalized in _SENSITIVE_KEY_NAMES:
        return True

    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _redact_text(text: str, *, sensitive_terms: tuple[str, ...]) -> str:
    redacted = text
    for term in sorted(sensitive_terms, key=len, reverse=True):
        redacted = redacted.replace(term, _REDACTED)

    for literal_name in _SENSITIVE_LITERAL_NAMES:
        redacted = re.sub(
            rf"\b{re.escape(literal_name)}\s*[:=]\s*\S+",
            _REDACTED,
            redacted,
        )
        redacted = redacted.replace(literal_name, _REDACTED_KEY)

    for pattern, replacement in _TOKEN_PATTERNS:
        redacted = pattern.sub(replacement, redacted)

    return redacted
