from app.repositories.notes import NotesRepository, get_notes_repository
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    ListNotesData,
    Note,
    NoteSortField,
    SortOrder,
    UpdateNoteRequest,
)


class NoteService:
    def __init__(self, repository: NotesRepository) -> None:
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
        return self._repository.list_notes(
            user_id=user_id,
            page=page,
            per_page=per_page,
            sort=sort,
            order=order,
            is_archived=is_archived,
            include_deleted=include_deleted,
        )

    def create_note(self, *, user_id: str, request: CreateNoteRequest) -> Note:
        return self._repository.create_note(
            user_id=user_id,
            request=request,
        )

    def get_note(self, *, user_id: str, note_id: str) -> Note:
        return self._repository.get_note(user_id=user_id, note_id=note_id)

    def update_note(self, *, user_id: str, note_id: str, request: UpdateNoteRequest) -> Note:
        return self._repository.update_note(
            user_id=user_id,
            note_id=note_id,
            request=request,
        )

    def delete_note(self, *, user_id: str, note_id: str, request: DeleteNoteRequest) -> Note:
        return self._repository.delete_note(
            user_id=user_id,
            note_id=note_id,
            request=request,
        )


def get_note_service() -> NoteService:
    return NoteService(get_notes_repository())
