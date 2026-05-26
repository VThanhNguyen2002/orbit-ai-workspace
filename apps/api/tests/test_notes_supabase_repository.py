import socket

import pytest

from app.repositories.notes import NoteNotFoundError, NoteVersionConflictError
from app.schemas.notes import CreateNoteRequest, DeleteNoteRequest, UpdateNoteRequest
from app.services.notes import NoteService
from tests.helpers.notes_supabase_fake_client import (
    NOTE_ID,
    USER_ID,
    FakeResponse,
    fake_repository,
    fake_settings,
    note_row,
)

SERVICE_ROLE_KEY = "service-role-placeholder-key"
TIMESTAMP = "2026-05-26T03:00:00.000Z"


def test_list_notes_scopes_query_to_user_and_applies_pagination() -> None:
    repository, client = fake_repository(FakeResponse(data=[note_row()], count=6))

    listing = repository.list_notes(
        user_id=USER_ID,
        page=2,
        per_page=5,
        sort="updated_at",
        order="desc",
        is_archived=True,
        include_deleted=True,
    )

    assert [note.id for note in listing.items] == [NOTE_ID]
    assert listing.pagination.model_dump() == {
        "page": 2,
        "per_page": 5,
        "total": 6,
        "has_next": False,
    }
    assert client.queries[0].operations == [
        ("select", "*", "exact"),
        ("eq", "user_id", USER_ID),
        ("eq", "is_archived", True),
        ("order", "updated_at", True),
        ("order", "id", True),
        ("range", 5, 9),
        ("execute",),
    ]


def test_list_notes_excludes_deleted_rows_by_default() -> None:
    repository, client = fake_repository(FakeResponse(data=[]))

    repository.list_notes(
        user_id=USER_ID,
        page=1,
        per_page=20,
        sort="updated_at",
        order="desc",
        is_archived=None,
        include_deleted=False,
    )

    assert ("eq", "user_id", USER_ID) in client.queries[0].operations
    assert ("eq", "is_deleted", False) in client.queries[0].operations


def test_list_notes_include_deleted_does_not_apply_deleted_filter() -> None:
    repository, client = fake_repository(
        FakeResponse(data=[note_row(is_deleted=True, deleted_at=TIMESTAMP)])
    )

    listing = repository.list_notes(
        user_id=USER_ID,
        page=1,
        per_page=20,
        sort="updated_at",
        order="desc",
        is_archived=None,
        include_deleted=True,
    )

    assert listing.items[0].is_deleted is True
    assert ("eq", "user_id", USER_ID) in client.queries[0].operations
    assert ("eq", "is_deleted", False) not in client.queries[0].operations


def test_create_note_uses_service_supplied_user_id_in_insert_payload() -> None:
    repository, client = fake_repository(FakeResponse(data=[note_row(title="Created note")]))
    service = NoteService(repository)

    created_note = service.create_note(
        user_id=USER_ID,
        request=CreateNoteRequest(title="Created note", content="Private content"),
    )

    assert created_note.user_id == USER_ID
    assert client.queries[0].operations == [
        (
            "insert",
            {
                "user_id": USER_ID,
                "title": "Created note",
                "content": "Private content",
                "content_type": "plain",
                "is_archived": False,
                "is_deleted": False,
            },
        ),
        ("execute",),
    ]


def test_get_note_filters_by_note_id_owner_and_visibility() -> None:
    repository, client = fake_repository(FakeResponse(data=[note_row()]))

    note = repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    assert note.id == NOTE_ID
    assert client.queries[0].operations == [
        ("select", "*", None),
        ("eq", "id", NOTE_ID),
        ("eq", "user_id", USER_ID),
        ("eq", "is_deleted", False),
        ("limit", 1),
        ("execute",),
    ]


def test_get_note_hides_missing_or_cross_user_rows_returned_as_empty() -> None:
    repository, client = fake_repository(FakeResponse(data=[]))

    with pytest.raises(NoteNotFoundError):
        repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    assert ("eq", "user_id", USER_ID) in client.queries[0].operations


def test_update_note_requires_matching_version_in_conditional_write() -> None:
    repository, client = fake_repository(FakeResponse(data=[note_row(title="Updated", version=4)]))

    note = repository.update_note(
        user_id=USER_ID,
        note_id=NOTE_ID,
        request=UpdateNoteRequest(title="Updated", version=3),
    )

    assert note.version == 4
    operations = client.queries[0].operations
    assert operations[0][0] == "update"
    assert operations[0][1]["title"] == "Updated"
    assert operations[0][1]["version"] == 4
    assert ("eq", "id", NOTE_ID) in operations
    assert ("eq", "user_id", USER_ID) in operations
    assert ("eq", "is_deleted", False) in operations
    assert ("eq", "version", 3) in operations


def test_update_note_maps_stale_version_to_owner_scoped_conflict() -> None:
    repository, client = fake_repository(
        FakeResponse(data=[]),
        FakeResponse(data=[note_row(title="Server title", version=2)]),
    )

    with pytest.raises(NoteVersionConflictError) as exc_info:
        repository.update_note(
            user_id=USER_ID,
            note_id=NOTE_ID,
            request=UpdateNoteRequest(title="Stale title", version=1),
        )

    assert exc_info.value.expected_version == 1
    assert exc_info.value.server_note.title == "Server title"
    assert exc_info.value.server_note.version == 2
    assert ("eq", "version", 1) in client.queries[0].operations
    assert client.queries[1].operations == [
        ("select", "*", None),
        ("eq", "id", NOTE_ID),
        ("eq", "user_id", USER_ID),
        ("eq", "is_deleted", False),
        ("limit", 1),
        ("execute",),
    ]


def test_update_note_hides_missing_or_cross_user_conditional_write_miss() -> None:
    repository, client = fake_repository(FakeResponse(data=[]), FakeResponse(data=[]))

    with pytest.raises(NoteNotFoundError):
        repository.update_note(
            user_id=USER_ID,
            note_id=NOTE_ID,
            request=UpdateNoteRequest(title="Invisible title", version=1),
        )

    assert ("eq", "user_id", USER_ID) in client.queries[0].operations
    assert ("eq", "user_id", USER_ID) in client.queries[1].operations


def test_delete_note_is_a_version_gated_soft_delete_update() -> None:
    repository, client = fake_repository(
        FakeResponse(data=[note_row(is_deleted=True, deleted_at=TIMESTAMP, version=2)])
    )

    note = repository.delete_note(
        user_id=USER_ID,
        note_id=NOTE_ID,
        request=DeleteNoteRequest(version=1),
    )

    assert note.is_deleted is True
    assert note.version == 2
    operations = client.queries[0].operations
    assert operations[0][0] == "update"
    payload = operations[0][1]
    assert payload["is_deleted"] is True
    assert payload["version"] == 2
    assert payload["deleted_at"] == payload["updated_at"]
    assert ("eq", "id", NOTE_ID) in operations
    assert ("eq", "user_id", USER_ID) in operations
    assert ("eq", "is_deleted", False) in operations
    assert ("eq", "version", 1) in operations


def test_delete_note_maps_stale_version_to_owner_scoped_conflict() -> None:
    repository, client = fake_repository(
        FakeResponse(data=[]),
        FakeResponse(data=[note_row(version=2)]),
    )

    with pytest.raises(NoteVersionConflictError) as exc_info:
        repository.delete_note(
            user_id=USER_ID,
            note_id=NOTE_ID,
            request=DeleteNoteRequest(version=1),
        )

    assert exc_info.value.expected_version == 1
    assert exc_info.value.server_note.version == 2
    assert ("eq", "version", 1) in client.queries[0].operations
    assert ("eq", "user_id", USER_ID) in client.queries[1].operations


def test_delete_note_hides_missing_or_cross_user_conditional_write_miss() -> None:
    repository, client = fake_repository(FakeResponse(data=[]), FakeResponse(data=[]))

    with pytest.raises(NoteNotFoundError):
        repository.delete_note(
            user_id=USER_ID,
            note_id=NOTE_ID,
            request=DeleteNoteRequest(version=1),
        )

    assert ("eq", "user_id", USER_ID) in client.queries[0].operations
    assert ("eq", "user_id", USER_ID) in client.queries[1].operations


def test_injected_fake_client_makes_no_network_request(monkeypatch: pytest.MonkeyPatch) -> None:
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    repository, client = fake_repository(FakeResponse(data=[note_row()]))

    repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    assert client.table_names == ["notes"]


def test_repository_does_not_pass_service_role_setting_to_injected_client() -> None:
    settings = fake_settings(supabase_service_role_key=SERVICE_ROLE_KEY)
    repository, client = fake_repository(FakeResponse(data=[note_row()]), settings=settings)

    repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    rendered_operations = repr((client.table_names, client.queries[0].operations))
    assert SERVICE_ROLE_KEY not in rendered_operations
    assert client.table_names == ["notes"]
