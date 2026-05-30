"""AI summarization service.

Layer boundaries
----------------
- FakeSummarizationProvider: deterministic, no network, no logging of content.
- SummarizationService: auth boundary, ownership check, size check, calls provider.
- Nothing here logs note content, prompt text, tokens, keys, or auth headers.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.models.responses import ApiErrorDetail
from app.repositories.notes import get_notes_repository
from app.schemas.notes import Note
from app.services.notes import NoteService

# ---------------------------------------------------------------------------
# Domain models (backend-only, snake_case — aligned with shared SummarySchema)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AiActionItem:
    text: str
    priority: str  # "urgent" | "high" | "medium" | "low"

    def as_dict(self) -> dict[str, str]:
        return {"text": self.text, "priority": self.priority}


@dataclass(frozen=True)
class AiSummaryResult:
    id: str
    user_id: str
    source_id: str
    source_type: str
    content: str
    action_items: list[AiActionItem]
    provider: str
    model: str
    created_at: str

    def as_dict(self) -> dict:  # type: ignore[type-arg]
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "content": self.content,
            "action_items": [item.as_dict() for item in self.action_items],
            "provider": self.provider,
            "model": self.model,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------


class SummarizationProvider(Protocol):
    """Protocol for all summarization providers.

    Implementations MUST NOT:
    - log content, prompt text, or token values
    - make network calls without an explicit flag
    - raise generic exceptions that leak provider internals
    """

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    def summarize(self, *, source_id: str, content: str) -> AiSummaryResult: ...


# ---------------------------------------------------------------------------
# Fake provider — deterministic, no network, safe for CI
# ---------------------------------------------------------------------------

_FAKE_SUMMARY_TEMPLATE = (
    "This note covers key decisions and next steps identified during the session. "
    "Several action items were extracted for follow-up."
)
_FAKE_ACTION_ITEMS: list[AiActionItem] = [
    AiActionItem(text="Review and confirm the key decisions", priority="high"),
    AiActionItem(text="Schedule a follow-up to track progress", priority="medium"),
]


class FakeSummarizationProvider:
    """Network-free deterministic provider for development and CI.

    Returns the same canned output for any input.
    Never logs content.
    """

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-model-v1"

    def summarize(
        self,
        *,
        source_id: str,
        content: str,  # noqa: ARG002 — intentionally unused; fake ignores content
    ) -> AiSummaryResult:
        return AiSummaryResult(
            id=str(uuid.uuid4()),
            user_id="",  # filled in by service layer
            source_id=source_id,
            source_type="note",
            content=_FAKE_SUMMARY_TEMPLATE,
            action_items=list(_FAKE_ACTION_ITEMS),
            provider=self.provider_name,
            model=self.model_name,
            created_at=datetime.now(UTC).isoformat(),
        )


# ---------------------------------------------------------------------------
# Specific error types
# ---------------------------------------------------------------------------


class AiSummarizationDisabledError(Exception):
    """Raised when ai_summarization_enabled is False."""


class AiInputTooLongError(Exception):
    """Raised when note content exceeds ai_max_input_chars."""

    def __init__(self, length: int, limit: int) -> None:
        self.length = length
        self.limit = limit
        super().__init__(f"Input length {length} exceeds limit {limit}")


# ---------------------------------------------------------------------------
# Summarization service
# ---------------------------------------------------------------------------


class SummarizationService:
    """Orchestrates note fetch, ownership, size check, and provider call.

    Security invariants (must never be violated):
    - note.user_id must match auth user_id (enforced by NoteService)
    - content is never logged
    - deleted notes are surfaced as 404
    """

    def __init__(
        self,
        note_service: NoteService,
        provider: SummarizationProvider,
        settings: Settings,
    ) -> None:
        self._note_service = note_service
        self._provider = provider
        self._settings = settings

    def summarize_note(self, *, user_id: str, note_id: str) -> AiSummaryResult:
        if not self._settings.ai_summarization_enabled:
            raise AiSummarizationDisabledError

        # Ownership + existence check: NoteService raises NoteNotFoundError for
        # missing, deleted, or cross-user notes — all hidden as 404.
        note: Note = self._note_service.get_note(user_id=user_id, note_id=note_id)

        # Size check — measured on content only (title is small by schema constraint)
        input_chars = len(note.content)
        if input_chars > self._settings.ai_max_input_chars:
            raise AiInputTooLongError(input_chars, self._settings.ai_max_input_chars)

        result = self._provider.summarize(source_id=note.id, content=note.content)

        # Inject auth user_id — provider must not know the calling user
        return AiSummaryResult(
            id=result.id,
            user_id=user_id,
            source_id=result.source_id,
            source_type=result.source_type,
            content=result.content,
            action_items=result.action_items,
            provider=result.provider,
            model=result.model,
            created_at=result.created_at,
        )


# ---------------------------------------------------------------------------
# Dependency factory
# ---------------------------------------------------------------------------


def get_summarization_service() -> SummarizationService:
    settings = get_settings()
    provider: SummarizationProvider = FakeSummarizationProvider()
    note_service = NoteService(get_notes_repository())
    return SummarizationService(
        note_service=note_service,
        provider=provider,
        settings=settings,
    )


# ---------------------------------------------------------------------------
# ApiError helpers (used by router)
# ---------------------------------------------------------------------------


def summarization_disabled_error() -> ApiError:
    return ApiError(
        status_code=503,
        code="UNPROCESSABLE",
        message="AI summarization is not enabled",
        details=[
            ApiErrorDetail(
                field="ai_summarization_enabled",
                message="feature_disabled",
            ),
        ],
    )


def summarization_input_too_long_error(exc: AiInputTooLongError) -> ApiError:
    return ApiError(
        status_code=400,
        code="VALIDATION_ERROR",
        message="Note content exceeds maximum input length for summarization",
        details=[
            ApiErrorDetail(
                field="content",
                message="content_too_long",
                actual=exc.length,
                expected=exc.limit,
            ),
        ],
    )


def note_not_found_error() -> ApiError:
    return ApiError(
        status_code=404,
        code="NOT_FOUND",
        message="Note not found",
        details=[
            ApiErrorDetail(
                field="note_id",
                message="note_not_found",
            ),
        ],
    )
