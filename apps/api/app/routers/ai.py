"""AI routes for note summarization and fake-provider summary history.

Note: SSE streaming is deferred to a future slice. This slice returns a
standard JSON success envelope with the full summary result.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.auth import AuthContext, get_auth_context
from app.models.responses import success_envelope
from app.repositories.notes import NoteNotFoundError
from app.services.ai_summarization import (
    AiInputTooLongError,
    AiSummarizationDisabledError,
    SummarizationService,
    get_summarization_service,
    note_not_found_error,
    summarization_disabled_error,
    summarization_input_too_long_error,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/notes/{note_id}/summarize", status_code=200)
def summarize_note(
    note_id: str,
    request: Request,
    service: Annotated[SummarizationService, Depends(get_summarization_service)],
    auth_context: Annotated[AuthContext, Depends(get_auth_context)],
):
    """Summarize a note using the configured AI provider.

    - Requires authentication.
    - Only the owner of the note may request summarization.
    - Missing, deleted, or cross-user notes are returned as 404.
    - Input exceeding ai_max_input_chars is rejected with 400.
    - Disabled by default; enable via SYNAPSE_AI_SUMMARIZATION_ENABLED=true.
    - SSE streaming is deferred to a future slice.
    """
    try:
        result = service.summarize_note(
            user_id=auth_context.user_id,
            note_id=note_id,
        )
    except AiSummarizationDisabledError:
        raise summarization_disabled_error() from None
    except NoteNotFoundError as exc:
        raise note_not_found_error() from exc
    except AiInputTooLongError as exc:
        raise summarization_input_too_long_error(exc) from exc

    return success_envelope(request, result.as_dict())


@router.get("/notes/{note_id}/summaries")
def list_note_summaries(
    note_id: str,
    request: Request,
    service: Annotated[SummarizationService, Depends(get_summarization_service)],
    auth_context: Annotated[AuthContext, Depends(get_auth_context)],
):
    """List in-memory fake summary history for a user-owned note."""
    try:
        summaries = service.list_note_summaries(
            user_id=auth_context.user_id,
            note_id=note_id,
        )
    except NoteNotFoundError as exc:
        raise note_not_found_error() from exc

    return success_envelope(
        request,
        {"items": [summary.as_dict() for summary in summaries]},
    )
