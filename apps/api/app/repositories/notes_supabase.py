from collections.abc import Mapping
from datetime import datetime
from typing import Any, NoReturn

try:
    from datetime import UTC
except ImportError:  # pragma: no cover - local fallback for Python 3.10 runners.
    from datetime import timezone

    UTC = timezone.utc  # noqa: UP017

from app.core.config import Settings
from app.repositories.notes import (
    NoteNotFoundError,
    NotesRepository,
    NotesRepositoryNotConfiguredError,
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

NOTES_TABLE = "notes"


class SupabaseNotesRepository(NotesRepository):
    """Supabase-shaped Notes repository scaffold.

    This class intentionally avoids importing or constructing a live Supabase client.
    A later integration slice can inject a user-scoped client that implements the
    subset of the Supabase query-builder API used here.
    """

    def __init__(self, *, client: Any | None, settings: Settings) -> None:
        self._client = client
        self._settings = settings

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
        table = self._table()
        query = table.select("*", count="exact").eq("user_id", user_id)
        if not include_deleted:
            query = query.eq("is_deleted", False)
        if is_archived is not None:
            query = query.eq("is_archived", is_archived)

        start = (page - 1) * per_page
        end = start + per_page - 1
        response = (
            query.order(sort, desc=order == "desc")
            .order("id", desc=order == "desc")
            .range(start, end)
            .execute()
        )
        total = int(getattr(response, "count", None) or len(getattr(response, "data", [])))
        return ListNotesData(
            items=[note_from_supabase_row(row) for row in getattr(response, "data", [])],
            pagination=PaginationMeta(
                page=page,
                per_page=per_page,
                total=total,
                has_next=page * per_page < total,
            ),
        )

    def create_note(self, *, user_id: str, request: CreateNoteRequest) -> Note:
        response = (
            self._table()
            .insert(create_note_payload(user_id=user_id, request=request))
            .execute()
        )
        return self._single_note(response)

    def get_note(self, *, user_id: str, note_id: str) -> Note:
        response = (
            self._table()
            .select("*")
            .eq("id", note_id)
            .eq("user_id", user_id)
            .eq("is_deleted", False)
            .limit(1)
            .execute()
        )
        rows = list(getattr(response, "data", []))
        if not rows:
            raise NoteNotFoundError

        return note_from_supabase_row(rows[0])

    def update_note(self, *, user_id: str, note_id: str, request: UpdateNoteRequest) -> Note:
        response = (
            self._table()
            .update(update_note_payload(request=request))
            .eq("id", note_id)
            .eq("user_id", user_id)
            .eq("is_deleted", False)
            .eq("version", request.version)
            .execute()
        )
        rows = list(getattr(response, "data", []))
        if rows:
            return note_from_supabase_row(rows[0])

        self._raise_not_found_or_conflict(
            user_id=user_id,
            note_id=note_id,
            expected_version=request.version,
        )

    def delete_note(self, *, user_id: str, note_id: str, request: DeleteNoteRequest) -> Note:
        response = (
            self._table()
            .update(soft_delete_note_payload(request=request))
            .eq("id", note_id)
            .eq("user_id", user_id)
            .eq("is_deleted", False)
            .eq("version", request.version)
            .execute()
        )
        rows = list(getattr(response, "data", []))
        if rows:
            return note_from_supabase_row(rows[0])

        self._raise_not_found_or_conflict(
            user_id=user_id,
            note_id=note_id,
            expected_version=request.version,
        )

    def _raise_not_found_or_conflict(
        self,
        *,
        user_id: str,
        note_id: str,
        expected_version: int,
    ) -> NoReturn:
        response = (
            self._table()
            .select("*")
            .eq("id", note_id)
            .eq("user_id", user_id)
            .eq("is_deleted", False)
            .limit(1)
            .execute()
        )
        rows = list(getattr(response, "data", []))
        if not rows:
            raise NoteNotFoundError

        raise NoteVersionConflictError(
            expected_version=expected_version,
            server_note=note_from_supabase_row(rows[0]),
        )

    def _single_note(self, response: Any) -> Note:
        rows = list(getattr(response, "data", []))
        if not rows:
            raise NotesRepositoryNotConfiguredError("Supabase response did not return a note row")

        return note_from_supabase_row(rows[0])

    def _table(self) -> Any:
        if self._client is None:
            raise NotesRepositoryNotConfiguredError(
                "Supabase Notes repository is configured but no user-scoped client is available"
            )

        return self._client.table(NOTES_TABLE)


def get_supabase_notes_repository(
    settings: Settings,
    *,
    client: Any | None = None,
) -> SupabaseNotesRepository:
    if not is_supabase_notes_repository_configured(settings):
        raise NotesRepositoryNotConfiguredError(
            "Supabase Notes repository requires SUPABASE_URL and a public Data API key"
        )

    if client is None:
        raise NotesRepositoryNotConfiguredError(
            "Supabase Notes repository scaffold requires an injected user-scoped client"
        )

    return SupabaseNotesRepository(client=client, settings=settings)


def is_supabase_notes_repository_configured(settings: Settings) -> bool:
    return bool(
        settings.supabase_url
        and (settings.supabase_publishable_key or settings.supabase_anon_key)
    )


def note_from_supabase_row(row: Mapping[str, Any]) -> Note:
    return Note.model_validate(dict(row))


def create_note_payload(*, user_id: str, request: CreateNoteRequest) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "title": request.title,
        "content": request.content,
        "content_type": request.content_type,
        "is_archived": False,
        "is_deleted": False,
    }


def update_note_payload(*, request: UpdateNoteRequest) -> dict[str, Any]:
    updates = request.model_dump(exclude={"version"}, exclude_none=True)
    return {
        **updates,
        "updated_at": _timestamp(),
        "version": request.version + 1,
    }


def soft_delete_note_payload(*, request: DeleteNoteRequest) -> dict[str, Any]:
    timestamp = _timestamp()
    return {
        "is_deleted": True,
        "deleted_at": timestamp,
        "updated_at": timestamp,
        "version": request.version + 1,
    }


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
