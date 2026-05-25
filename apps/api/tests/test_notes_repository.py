import pytest

from app.core.config import Settings
from app.repositories.notes import (
    NoteNotFoundError,
    NotesRepositoryNotConfiguredError,
    NoteVersionConflictError,
    get_notes_repository,
)
from app.repositories.notes_memory import InMemoryNotesRepository
from app.repositories.notes_supabase import (
    create_note_payload,
    get_supabase_notes_repository,
    is_supabase_notes_repository_configured,
    note_from_supabase_row,
    soft_delete_note_payload,
    update_note_payload,
)
from app.schemas.notes import CreateNoteRequest, DeleteNoteRequest, UpdateNoteRequest


def test_notes_repository_factory_defaults_to_memory() -> None:
    repository = get_notes_repository(Settings(notes_repository="memory"))

    assert isinstance(repository, InMemoryNotesRepository)


def test_memory_repository_hides_cross_user_notes() -> None:
    repository = InMemoryNotesRepository()
    note = repository.create_note(
        user_id="user_a",
        request=CreateNoteRequest(title="Private note"),
    )

    with pytest.raises(NoteNotFoundError):
        repository.get_note(user_id="user_b", note_id=note.id)

    listing = repository.list_notes(
        user_id="user_b",
        page=1,
        per_page=20,
        sort="updated_at",
        order="desc",
        is_archived=None,
        include_deleted=False,
    )
    assert listing.items == []
    assert listing.pagination.total == 0


def test_memory_repository_version_conflict_returns_server_data() -> None:
    repository = InMemoryNotesRepository()
    note = repository.create_note(
        user_id="user_a",
        request=CreateNoteRequest(title="Private note"),
    )

    with pytest.raises(NoteVersionConflictError) as exc_info:
        repository.update_note(
            user_id="user_a",
            note_id=note.id,
            request=UpdateNoteRequest(title="Stale edit", version=0),
        )

    assert exc_info.value.expected_version == 0
    assert exc_info.value.server_note == note


def test_memory_repository_soft_delete_is_hidden_from_normal_reads() -> None:
    repository = InMemoryNotesRepository()
    note = repository.create_note(
        user_id="user_a",
        request=CreateNoteRequest(title="Private note"),
    )

    deleted_note = repository.delete_note(
        user_id="user_a",
        note_id=note.id,
        request=DeleteNoteRequest(version=note.version),
    )

    assert deleted_note.is_deleted is True
    assert deleted_note.deleted_at is not None
    assert deleted_note.version == note.version + 1
    with pytest.raises(NoteNotFoundError):
        repository.get_note(user_id="user_a", note_id=note.id)


def test_supabase_repository_is_not_configured_without_env_values() -> None:
    settings = Settings(notes_repository="supabase")

    assert is_supabase_notes_repository_configured(settings) is False
    with pytest.raises(NotesRepositoryNotConfiguredError):
        get_supabase_notes_repository(settings)


def test_supabase_repository_requires_injected_user_scoped_client() -> None:
    settings = Settings(
        notes_repository="supabase",
        supabase_url="https://example.supabase.co",
        supabase_anon_key="placeholder-anon-key",
    )

    assert is_supabase_notes_repository_configured(settings) is True
    with pytest.raises(NotesRepositoryNotConfiguredError):
        get_supabase_notes_repository(settings)


def test_supabase_repository_accepts_publishable_key_configuration_but_remains_scaffolded(
) -> None:
    settings = Settings(
        notes_repository="supabase",
        supabase_url="https://example.supabase.co",
        supabase_publishable_key="placeholder-publishable-key",
    )

    assert is_supabase_notes_repository_configured(settings) is True
    with pytest.raises(NotesRepositoryNotConfiguredError):
        get_supabase_notes_repository(settings)


def test_supabase_scaffold_maps_rows_without_network() -> None:
    row = {
        "id": "22222222-2222-4222-8222-222222222222",
        "user_id": "11111111-1111-4111-8111-111111111111",
        "title": "Planning note",
        "content": "Decisions and follow-up items.",
        "content_type": "markdown",
        "is_archived": False,
        "is_deleted": False,
        "created_at": "2026-05-22T03:00:00.000Z",
        "updated_at": "2026-05-22T03:00:00.000Z",
        "deleted_at": None,
        "version": 1,
    }

    note = note_from_supabase_row(row)

    assert note.model_dump() == row


def test_supabase_scaffold_payloads_keep_server_controlled_fields_out_of_client_input() -> None:
    create_payload = create_note_payload(
        user_id="user_a",
        request=CreateNoteRequest(title="Planning note"),
    )
    update_payload = update_note_payload(
        request=UpdateNoteRequest(title="Updated note", version=1),
    )
    delete_payload = soft_delete_note_payload(request=DeleteNoteRequest(version=3))

    assert create_payload == {
        "user_id": "user_a",
        "title": "Planning note",
        "content": "",
        "content_type": "plain",
        "is_archived": False,
        "is_deleted": False,
    }
    assert update_payload["title"] == "Updated note"
    assert update_payload["version"] == 2
    assert isinstance(update_payload["updated_at"], str)
    assert delete_payload["is_deleted"] is True
    assert delete_payload["version"] == 4
    assert isinstance(delete_payload["deleted_at"], str)
    assert delete_payload["deleted_at"] == delete_payload["updated_at"]
