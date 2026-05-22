from typing import Protocol

from app.core.config import Settings, get_settings
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    ListNotesData,
    Note,
    NoteSortField,
    SortOrder,
    UpdateNoteRequest,
)


class NoteNotFoundError(Exception):
    pass


class NoteVersionConflictError(Exception):
    def __init__(self, *, expected_version: int, server_note: Note) -> None:
        self.expected_version = expected_version
        self.server_note = server_note


class NotesRepositoryNotConfiguredError(Exception):
    pass


class NotesRepository(Protocol):
    def list_notes(
        self,
        *,
        user_id: str,
        page: int,
        per_page: int,
        sort: NoteSortField,
        order: SortOrder,
        is_archived: bool | None,
        include_deleted: bool,
    ) -> ListNotesData: ...

    def create_note(self, *, user_id: str, request: CreateNoteRequest) -> Note: ...

    def get_note(self, *, user_id: str, note_id: str) -> Note: ...

    def update_note(self, *, user_id: str, note_id: str, request: UpdateNoteRequest) -> Note: ...

    def delete_note(self, *, user_id: str, note_id: str, request: DeleteNoteRequest) -> Note: ...


def get_notes_repository(settings: Settings | None = None) -> NotesRepository:
    resolved_settings = settings or get_settings()
    if resolved_settings.notes_repository == "supabase":
        from app.repositories.notes_supabase import get_supabase_notes_repository

        return get_supabase_notes_repository(resolved_settings)

    from app.repositories.notes_memory import get_memory_notes_repository

    return get_memory_notes_repository()
