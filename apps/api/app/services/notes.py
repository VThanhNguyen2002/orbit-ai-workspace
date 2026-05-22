from datetime import datetime

try:
    from datetime import UTC
except ImportError:  # pragma: no cover - local fallback for Python 3.10 runners.
    from datetime import timezone

    UTC = timezone.utc  # noqa: UP017
from uuid import uuid4

from app.repositories.notes import InMemoryNotesRepository, get_notes_repository
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    ListNotesData,
    Note,
    NoteSortField,
    PaginationMeta,
    SortOrder,
    UpdateNoteRequest,
)

# Temporary placeholder until Supabase JWT auth is wired in a later slice.
DEV_USER_ID = "dev_user"


class NoteNotFoundError(Exception):
    pass


class NoteVersionConflictError(Exception):
    def __init__(self, *, expected_version: int, server_note: Note) -> None:
        self.expected_version = expected_version
        self.server_note = server_note


class NoteService:
    def __init__(self, repository: InMemoryNotesRepository) -> None:
        self._repository = repository

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
    ) -> ListNotesData:
        notes, total = self._repository.list(
            user_id=user_id,
            page=page,
            per_page=per_page,
            sort=sort,
            order=order,
            is_archived=is_archived,
            include_deleted=include_deleted,
        )
        return ListNotesData(
            items=notes,
            pagination=PaginationMeta(
                page=page,
                per_page=per_page,
                total=total,
                has_next=page * per_page < total,
            ),
        )

    def create_note(self, *, user_id: str, request: CreateNoteRequest) -> Note:
        timestamp = _timestamp()
        note = Note(
            id=str(uuid4()),
            user_id=user_id,
            title=request.title,
            content=request.content,
            content_type=request.content_type,
            is_archived=False,
            is_deleted=False,
            created_at=timestamp,
            updated_at=timestamp,
            deleted_at=None,
            version=1,
        )
        return self._repository.create(note)

    def get_note(self, *, user_id: str, note_id: str) -> Note:
        note = self._repository.get(note_id=note_id, user_id=user_id)
        if note is None:
            raise NoteNotFoundError

        return note

    def update_note(self, *, user_id: str, note_id: str, request: UpdateNoteRequest) -> Note:
        note = self.get_note(user_id=user_id, note_id=note_id)
        if note.version != request.version:
            raise NoteVersionConflictError(
                expected_version=request.version,
                server_note=note,
            )

        updates = request.model_dump(exclude={"version"}, exclude_none=True)
        updated_note = note.model_copy(
            update={
                **updates,
                "updated_at": _timestamp(),
                "version": note.version + 1,
            },
        )
        return self._repository.save(updated_note)

    def delete_note(self, *, user_id: str, note_id: str, request: DeleteNoteRequest) -> Note:
        note = self.get_note(user_id=user_id, note_id=note_id)
        if note.version != request.version:
            raise NoteVersionConflictError(
                expected_version=request.version,
                server_note=note,
            )

        timestamp = _timestamp()
        deleted_note = note.model_copy(
            update={
                "is_deleted": True,
                "deleted_at": timestamp,
                "updated_at": timestamp,
                "version": note.version + 1,
            },
        )
        return self._repository.save(deleted_note)


def get_note_service() -> NoteService:
    return NoteService(get_notes_repository())


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
