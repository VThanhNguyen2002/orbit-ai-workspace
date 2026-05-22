from datetime import datetime

try:
    from datetime import UTC
except ImportError:  # pragma: no cover - local fallback for Python 3.10 runners.
    from datetime import timezone

    UTC = timezone.utc  # noqa: UP017
from uuid import uuid4

from app.repositories.notes import (
    NoteNotFoundError,
    NotesRepository,
    NoteVersionConflictError,
)
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


class InMemoryNotesRepository(NotesRepository):
    def __init__(self) -> None:
        self._notes: dict[str, Note] = {}

    def clear(self) -> None:
        self._notes.clear()

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
        notes = [
            note
            for note in self._notes.values()
            if note.user_id == user_id
            and (include_deleted or not note.is_deleted)
            and (is_archived is None or note.is_archived == is_archived)
        ]
        notes.sort(key=lambda note: (getattr(note, sort), note.id), reverse=order == "desc")

        start = (page - 1) * per_page
        end = start + per_page
        return ListNotesData(
            items=[note.model_copy(deep=True) for note in notes[start:end]],
            pagination=PaginationMeta(
                page=page,
                per_page=per_page,
                total=len(notes),
                has_next=page * per_page < len(notes),
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
        self._notes[note.id] = note.model_copy(deep=True)
        return note.model_copy(deep=True)

    def get_note(self, *, user_id: str, note_id: str) -> Note:
        note = self._get_note(user_id=user_id, note_id=note_id)
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
        self._notes[updated_note.id] = updated_note.model_copy(deep=True)
        return updated_note.model_copy(deep=True)

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
        self._notes[deleted_note.id] = deleted_note.model_copy(deep=True)
        return deleted_note.model_copy(deep=True)

    def _get_note(
        self,
        *,
        user_id: str,
        note_id: str,
        include_deleted: bool = False,
    ) -> Note | None:
        note = self._notes.get(note_id)
        if note is None or note.user_id != user_id:
            return None

        if note.is_deleted and not include_deleted:
            return None

        return note.model_copy(deep=True)


_memory_notes_repository = InMemoryNotesRepository()


def get_memory_notes_repository() -> InMemoryNotesRepository:
    return _memory_notes_repository


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
