from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.core.errors import ApiError
from app.models.responses import ApiErrorDetail, success_envelope
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    NoteSortField,
    SortOrder,
    UpdateNoteRequest,
)
from app.services.notes import (
    DEV_USER_ID,
    NoteNotFoundError,
    NoteService,
    NoteVersionConflictError,
    get_note_service,
)

router = APIRouter(prefix="/notes", tags=["notes"])


def get_current_user_id() -> str:
    """Temporary auth placeholder until Supabase JWT auth is added."""
    return DEV_USER_ID


@router.get("")
def list_notes(
    request: Request,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    sort: NoteSortField = "updated_at",
    order: SortOrder = "desc",
    is_archived: bool | None = None,
    include_deleted: bool = False,
):
    notes = service.list_notes(
        user_id=user_id,
        page=page,
        per_page=per_page,
        sort=sort,
        order=order,
        is_archived=is_archived,
        include_deleted=include_deleted,
    )
    return success_envelope(request, notes.model_dump())


@router.post("", status_code=201)
def create_note(
    request: Request,
    payload: CreateNoteRequest,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    note = service.create_note(user_id=user_id, request=payload)
    return success_envelope(request, note.model_dump())


@router.get("/{note_id}")
def get_note(
    note_id: str,
    request: Request,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    try:
        note = service.get_note(user_id=user_id, note_id=note_id)
    except NoteNotFoundError as exc:
        raise _note_not_found() from exc

    return success_envelope(request, note.model_dump())


@router.patch("/{note_id}")
def update_note(
    note_id: str,
    request: Request,
    payload: UpdateNoteRequest,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    try:
        note = service.update_note(user_id=user_id, note_id=note_id, request=payload)
    except NoteNotFoundError as exc:
        raise _note_not_found() from exc
    except NoteVersionConflictError as exc:
        raise _version_conflict(exc) from exc

    return success_envelope(request, note.model_dump())


@router.delete("/{note_id}")
def delete_note(
    note_id: str,
    request: Request,
    payload: DeleteNoteRequest,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    try:
        note = service.delete_note(user_id=user_id, note_id=note_id, request=payload)
    except NoteNotFoundError as exc:
        raise _note_not_found() from exc
    except NoteVersionConflictError as exc:
        raise _version_conflict(exc) from exc

    return success_envelope(request, note.model_dump())


def _note_not_found() -> ApiError:
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


def _version_conflict(exc: NoteVersionConflictError) -> ApiError:
    return ApiError(
        status_code=409,
        code="CONFLICT",
        message="Note version conflict",
        details=[
            ApiErrorDetail(
                field="version",
                message="version_conflict",
                expected=exc.expected_version,
                actual=exc.server_note.version,
                server_data=exc.server_note.model_dump(),
            ),
        ],
    )
