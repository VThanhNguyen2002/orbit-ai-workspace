from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient

NOTE_FIELDS = {
    "id",
    "user_id",
    "title",
    "content",
    "content_type",
    "is_archived",
    "is_deleted",
    "created_at",
    "updated_at",
    "deleted_at",
    "version",
}
PAGINATION_FIELDS = {
    "page",
    "per_page",
    "total",
    "has_next",
}


def create_note(
    client: TestClient,
    *,
    title: str = "Planning note",
    content: str = "Decisions and follow-up items.",
    content_type: str = "plain",
) -> dict[str, Any]:
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


def assert_note_contract(note: Mapping[str, object]) -> None:
    assert set(note) == NOTE_FIELDS
    assert all(field == field.lower() for field in note)
    assert "contentType" not in note
    assert "isArchived" not in note
    assert "isDeleted" not in note
    assert "createdAt" not in note
    assert "updatedAt" not in note
    assert "deletedAt" not in note
