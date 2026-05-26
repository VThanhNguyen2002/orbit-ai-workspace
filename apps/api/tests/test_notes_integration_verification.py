from fastapi.testclient import TestClient

from tests.helpers.notes_assertions import PAGINATION_FIELDS, assert_note_contract


def test_notes_backend_wire_contract_round_trip(client: TestClient) -> None:
    create_response = client.post(
        "/v1/notes",
        json={
            "title": "Integration note",
            "content": "Verify Notes contracts across backend boundaries.",
            "content_type": "markdown",
        },
    )
    assert create_response.status_code == 201
    created_note = create_response.json()["data"]
    assert_note_contract(created_note)
    assert created_note["user_id"] == "dev_user"
    assert created_note["version"] == 1

    list_response = client.get(
        "/v1/notes?page=1&per_page=5&sort=updated_at&order=desc&include_deleted=false",
    )
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert set(list_body["data"]) == {"items", "pagination"}
    assert set(list_body["data"]["pagination"]) == PAGINATION_FIELDS
    assert [note["id"] for note in list_body["data"]["items"]] == [created_note["id"]]

    update_response = client.patch(
        f"/v1/notes/{created_note['id']}",
        json={
            "title": "Archived integration note",
            "is_archived": True,
            "version": created_note["version"],
        },
    )
    assert update_response.status_code == 200
    updated_note = update_response.json()["data"]
    assert_note_contract(updated_note)
    assert updated_note["title"] == "Archived integration note"
    assert updated_note["is_archived"] is True
    assert updated_note["version"] == created_note["version"] + 1

    archived_response = client.get("/v1/notes?is_archived=true")
    active_response = client.get("/v1/notes?is_archived=false")
    assert archived_response.status_code == 200
    assert active_response.status_code == 200
    assert [note["id"] for note in archived_response.json()["data"]["items"]] == [
        created_note["id"],
    ]
    assert active_response.json()["data"]["items"] == []

    delete_response = client.request(
        "DELETE",
        f"/v1/notes/{created_note['id']}",
        json={"version": updated_note["version"]},
    )
    assert delete_response.status_code == 200
    deleted_note = delete_response.json()["data"]
    assert_note_contract(deleted_note)
    assert deleted_note["is_deleted"] is True
    assert deleted_note["deleted_at"] is not None
    assert deleted_note["version"] == updated_note["version"] + 1

    hidden_response = client.get("/v1/notes")
    include_deleted_response = client.get("/v1/notes?include_deleted=true")
    assert hidden_response.status_code == 200
    assert include_deleted_response.status_code == 200
    assert hidden_response.json()["data"]["items"] == []
    assert [note["id"] for note in include_deleted_response.json()["data"]["items"]] == [
        created_note["id"],
    ]


def test_notes_conflict_error_contract_includes_full_server_data(client: TestClient) -> None:
    create_response = client.post(
        "/v1/notes",
        json={
            "title": "Conflict note",
            "content": "",
            "content_type": "plain",
        },
    )
    assert create_response.status_code == 201
    note = create_response.json()["data"]

    conflict_response = client.patch(
        f"/v1/notes/{note['id']}",
        json={
            "title": "Stale title",
            "version": note["version"] - 1,
        },
    )
    assert conflict_response.status_code == 409
    detail = conflict_response.json()["error"]["details"][0]
    assert detail["field"] == "version"
    assert detail["message"] == "version_conflict"
    assert detail["expected"] == note["version"] - 1
    assert detail["actual"] == note["version"]
    assert_note_contract(detail["server_data"])
    assert detail["server_data"] == note
