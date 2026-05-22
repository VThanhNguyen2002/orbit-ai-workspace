from app.schemas.notes import Note, NoteSortField, SortOrder


class InMemoryNotesRepository:
    def __init__(self) -> None:
        self._notes: dict[str, Note] = {}

    def clear(self) -> None:
        self._notes.clear()

    def create(self, note: Note) -> Note:
        self._notes[note.id] = note.model_copy(deep=True)
        return note.model_copy(deep=True)

    def get(self, *, note_id: str, user_id: str, include_deleted: bool = False) -> Note | None:
        note = self._notes.get(note_id)
        if note is None or note.user_id != user_id:
            return None

        if note.is_deleted and not include_deleted:
            return None

        return note.model_copy(deep=True)

    def list(
        self,
        *,
        user_id: str,
        page: int,
        per_page: int,
        sort: NoteSortField,
        order: SortOrder,
        is_archived: bool | None,
        include_deleted: bool,
    ) -> tuple[list[Note], int]:
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
        return [note.model_copy(deep=True) for note in notes[start:end]], len(notes)

    def save(self, note: Note) -> Note:
        self._notes[note.id] = note.model_copy(deep=True)
        return note.model_copy(deep=True)


_notes_repository = InMemoryNotesRepository()


def get_notes_repository() -> InMemoryNotesRepository:
    return _notes_repository
