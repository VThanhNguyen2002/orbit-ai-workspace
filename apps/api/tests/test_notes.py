from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthContext, get_auth_context
from app.repositories.notes_memory import get_memory_notes_repository


@pytest.fixture(autouse=True)
def reset_notes_repository() -> Generator[None, None, None]:
    get_memory_notes_repository().clear()
    yield
    get_memory_notes_repository().clear()


def test_notes_route_boots_with_empty_list(client: TestClient) -> None:
    response = client.get("/v1/notes", headers={"x-request-id": "req_notes_boot"})

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "items": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "has_next": False,
            },
        },
        "meta": {
            "request_id": "req_notes_boot",
        },
    }


def test_create_note_success(client: TestClient) -> None:
    response = client.post(
        "/v1/notes",
        json={
            "title": "Planning note",
            "content": "Decisions and follow-up items.",
            "content_type": "markdown",
        },
        headers={"x-request-id": "req_create_note"},
    )

    assert response.status_code == 201
    body = response.json()
    note = body["data"]
    UUID(note["id"])
    assert body["meta"] == {"request_id": "req_create_note"}
    assert note["user_id"] == "dev_user"
    assert note["title"] == "Planning note"
    assert note["content"] == "Decisions and follow-up items."
    assert note["content_type"] == "markdown"
    assert note["is_archived"] is False
    assert note["is_deleted"] is False
    assert note["deleted_at"] is None
    assert note["version"] == 1
    assert isinstance(note["created_at"], str)
    assert isinstance(note["updated_at"], str)


def test_create_note_rejects_server_controlled_fields(client: TestClient) -> None:
    response = client.post(
        "/v1/notes",
        json={
            "id": "22222222-2222-4222-8222-222222222222",
            "user_id": "11111111-1111-4111-8111-111111111111",
            "title": "Planning note",
            "content": "Decisions and follow-up items.",
            "content_type": "plain",
            "is_archived": False,
            "is_deleted": False,
            "created_at": "2026-05-19T10:30:00.000Z",
            "updated_at": "2026-05-19T10:30:00.000Z",
            "deleted_at": None,
            "version": 1,
        },
        headers={"x-request-id": "req_reject_server_fields"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    fields = {detail["field"] for detail in body["error"]["details"]}
    assert {
        "id",
        "user_id",
        "is_archived",
        "is_deleted",
        "created_at",
        "updated_at",
        "deleted_at",
        "version",
    }.issubset(fields)


def test_list_notes_response_shape(client: TestClient) -> None:
    first = _create_note(client, title="B note")
    second = _create_note(client, title="A note")

    response = client.get("/v1/notes?sort=title&order=asc", headers={"x-request-id": "req_list"})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"data", "meta"}
    assert set(body["data"]) == {"items", "pagination"}
    assert body["data"]["pagination"] == {
        "page": 1,
        "per_page": 20,
        "total": 2,
        "has_next": False,
    }
    assert [note["id"] for note in body["data"]["items"]] == [second["id"], first["id"]]
    assert body["meta"] == {"request_id": "req_list"}


def test_get_note_success(client: TestClient) -> None:
    note = _create_note(client)

    response = client.get(f"/v1/notes/{note['id']}", headers={"x-request-id": "req_get_note"})

    assert response.status_code == 200
    assert response.json() == {
        "data": note,
        "meta": {
            "request_id": "req_get_note",
        },
    }


def test_notes_routes_hide_cross_user_notes(client: TestClient) -> None:
    client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_a",
        auth_mode="dev",
    )
    note = _create_note(client)
    assert note["user_id"] == "user_a"

    client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_b",
        auth_mode="dev",
    )

    list_response = client.get("/v1/notes")
    get_response = client.get(f"/v1/notes/{note['id']}")
    patch_response = client.patch(
        f"/v1/notes/{note['id']}",
        json={"title": "Cross-user edit", "version": note["version"]},
    )
    delete_response = client.request(
        "DELETE",
        f"/v1/notes/{note['id']}",
        json={"version": note["version"]},
    )

    assert list_response.status_code == 200
    assert list_response.json()["data"]["items"] == []
    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404


def test_missing_note_returns_404(client: TestClient) -> None:
    response = client.get("/v1/notes/missing-note", headers={"x-request-id": "req_missing_note"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Note not found",
            "details": [
                {
                    "field": "note_id",
                    "message": "note_not_found",
                },
            ],
        },
        "meta": {
            "request_id": "req_missing_note",
        },
    }


def test_patch_requires_version(client: TestClient) -> None:
    note = _create_note(client)

    response = client.patch(
        f"/v1/notes/{note['id']}",
        json={"title": "Updated title"},
        headers={"x-request-id": "req_patch_requires_version"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "version"


def test_patch_version_conflict(client: TestClient) -> None:
    note = _create_note(client)

    response = client.patch(
        f"/v1/notes/{note['id']}",
        json={"title": "Updated title", "version": 0},
        headers={"x-request-id": "req_patch_conflict"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["message"] == "Note version conflict"
    assert body["error"]["details"] == [
        {
            "field": "version",
            "message": "version_conflict",
            "expected": 0,
            "actual": 1,
            "server_data": note,
        },
    ]


def test_delete_requires_version(client: TestClient) -> None:
    note = _create_note(client)

    response = client.request(
        "DELETE",
        f"/v1/notes/{note['id']}",
        json={},
        headers={"x-request-id": "req_delete_requires_version"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "version"


def test_delete_version_conflict(client: TestClient) -> None:
    note = _create_note(client)

    response = client.request(
        "DELETE",
        f"/v1/notes/{note['id']}",
        json={"version": 0},
        headers={"x-request-id": "req_delete_conflict"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["details"] == [
        {
            "field": "version",
            "message": "version_conflict",
            "expected": 0,
            "actual": 1,
            "server_data": note,
        },
    ]


def test_delete_soft_deletes_note(client: TestClient) -> None:
    note = _create_note(client)

    response = client.request(
        "DELETE",
        f"/v1/notes/{note['id']}",
        json={"version": note["version"]},
        headers={"x-request-id": "req_delete_note"},
    )

    assert response.status_code == 200
    deleted_note = response.json()["data"]
    assert deleted_note["id"] == note["id"]
    assert deleted_note["is_deleted"] is True
    assert deleted_note["deleted_at"] is not None
    assert deleted_note["version"] == note["version"] + 1


def test_deleted_note_hidden_from_normal_list_and_get(client: TestClient) -> None:
    note = _create_note(client)
    client.request("DELETE", f"/v1/notes/{note['id']}", json={"version": note["version"]})

    get_response = client.get(f"/v1/notes/{note['id']}")
    list_response = client.get("/v1/notes")

    assert get_response.status_code == 404
    assert list_response.status_code == 200
    assert list_response.json()["data"]["items"] == []
    assert list_response.json()["data"]["pagination"]["total"] == 0


def test_note_responses_use_snake_case(client: TestClient) -> None:
    note = _create_note(client)

    assert "content_type" in note
    assert "is_archived" in note
    assert "is_deleted" in note
    assert "created_at" in note
    assert "updated_at" in note
    assert "deleted_at" in note
    assert "contentType" not in note
    assert "isArchived" not in note
    assert "isDeleted" not in note
    assert "createdAt" not in note
    assert "updatedAt" not in note
    assert "deletedAt" not in note


def _create_note(
    client: TestClient,
    *,
    title: str = "Planning note",
    content: str = "Decisions and follow-up items.",
    content_type: str = "plain",
) -> dict:
    response = client.post(
        "/v1/notes",
        json={
            "title": title,
            "content": content,
            "content_type": content_type,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]
