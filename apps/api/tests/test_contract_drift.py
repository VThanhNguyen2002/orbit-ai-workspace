import inspect
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from app.models.responses import ApiMeta
from app.routers.notes import list_notes
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    ListNotesData,
    Note,
    PaginationMeta,
    UpdateNoteRequest,
)

SCHEMAS_DIR = (
    Path(__file__).resolve().parents[3] / "packages" / "shared" / "dist" / "schemas" / "domain"
)
STABLE_NOTES_SCHEMAS = {
    "note",
    "create_note_request",
    "update_note_request",
    "delete_note_request",
    "get_note_response",
    "list_notes_request",
    "list_notes_response",
    "create_note_response",
    "update_note_response",
    "delete_note_response",
}
SHARED_OPTIONAL_NOTE_FIELDS = {"sync_metadata"}
SHARED_OPTIONAL_META_FIELDS = {"pagination"}
SERVER_CONTROLLED_CREATE_FIELDS = {
    "id",
    "user_id",
    "is_archived",
    "is_deleted",
    "created_at",
    "updated_at",
    "deleted_at",
    "version",
    "sync_metadata",
}
SNAKE_CASE_FIELD = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def test_stable_notes_json_schema_artifacts_are_exported() -> None:
    missing = sorted(
        name for name in STABLE_NOTES_SCHEMAS if not _schema_path(name).is_file()
    )

    assert not missing, (
        "Missing exported shared Notes schemas. Run "
        "`pnpm --filter @synapse/shared contracts:export` before backend tests: "
        f"{missing}"
    )


@pytest.mark.parametrize(
    ("schema_name", "backend_model"),
    [
        ("create_note_request", CreateNoteRequest),
        ("update_note_request", UpdateNoteRequest),
        ("delete_note_request", DeleteNoteRequest),
    ],
)
def test_note_request_fields_and_effective_required_status_match_pydantic(
    schema_name: str,
    backend_model: type[BaseModel],
) -> None:
    shared_schema = _schema(schema_name)
    backend_schema = backend_model.model_json_schema()

    assert _properties(shared_schema) == _properties(backend_schema)
    assert _effective_required(shared_schema) == _required(backend_schema)
    assert shared_schema["additionalProperties"] is False
    assert backend_schema["additionalProperties"] is False
    _assert_snake_case(_properties(shared_schema))


def test_create_note_defaults_and_server_controlled_fields_remain_bounded() -> None:
    shared_schema = _schema("create_note_request")
    backend_defaults = {
        name: field.default
        for name, field in CreateNoteRequest.model_fields.items()
        if not field.is_required()
    }

    assert _defaults(shared_schema) == backend_defaults == {
        "content": "",
        "content_type": "plain",
    }
    assert SERVER_CONTROLLED_CREATE_FIELDS.isdisjoint(_properties(shared_schema))

    for field_name in SERVER_CONTROLLED_CREATE_FIELDS:
        with pytest.raises(ValidationError):
            CreateNoteRequest.model_validate({"title": "Bounded note", field_name: "rejected"})


def test_list_notes_request_fields_and_defaults_match_route_query_contract() -> None:
    shared_schema = _schema("list_notes_request")
    parameters = inspect.signature(list_notes).parameters
    non_query_parameters = {"request", "service", "auth_context"}
    query_fields = set(parameters) - non_query_parameters
    route_defaults = {
        name: parameters[name].default
        for name in query_fields
        if parameters[name].default is not None
    }

    assert _properties(shared_schema) == query_fields
    assert _effective_required(shared_schema) == set()
    assert _defaults(shared_schema) == route_defaults == {
        "page": 1,
        "per_page": 20,
        "sort": "updated_at",
        "order": "desc",
        "include_deleted": False,
    }
    _assert_snake_case(query_fields)


def test_note_schema_and_single_note_response_envelopes_match_backend_shape() -> None:
    _assert_note_data_shape(_schema("note"))

    for schema_name in {
        "get_note_response",
        "create_note_response",
        "update_note_response",
        "delete_note_response",
    }:
        shared_schema = _schema(schema_name)
        _assert_success_envelope(shared_schema)
        _assert_note_data_shape(shared_schema["properties"]["data"])


def test_list_notes_response_retains_items_and_pagination_shape() -> None:
    shared_schema = _schema("list_notes_response")
    _assert_success_envelope(shared_schema)
    data_schema = shared_schema["properties"]["data"]

    assert _properties(data_schema) == set(ListNotesData.model_fields) == {"items", "pagination"}
    assert _required(data_schema) == _required(ListNotesData.model_json_schema())
    assert data_schema["additionalProperties"] is False
    _assert_note_data_shape(data_schema["properties"]["items"]["items"])

    pagination_schema = data_schema["properties"]["pagination"]
    backend_pagination_schema = PaginationMeta.model_json_schema()
    assert _properties(pagination_schema) == _properties(backend_pagination_schema)
    assert _required(pagination_schema) == _required(backend_pagination_schema)
    _assert_snake_case(_properties(pagination_schema))


def test_notes_dto_validation_failures_remain_400_validation_error(client: TestClient) -> None:
    create_response = client.post(
        "/v1/notes",
        json={"title": "Rejected note", "id": "server-controlled"},
    )
    assert create_response.status_code == 400
    assert create_response.json()["error"]["code"] == "VALIDATION_ERROR"

    note = _create_note(client)
    for response in [
        client.patch(f"/v1/notes/{note['id']}", json={"title": "Missing version"}),
        client.request("DELETE", f"/v1/notes/{note['id']}", json={}),
    ]:
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_notes_stale_versions_remain_409_conflict(client: TestClient) -> None:
    note = _create_note(client)

    for response in [
        client.patch(f"/v1/notes/{note['id']}", json={"title": "Stale", "version": 0}),
        client.request("DELETE", f"/v1/notes/{note['id']}", json={"version": 0}),
    ]:
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"


def _schema(name: str) -> dict[str, Any]:
    path = _schema_path(name)
    assert path.is_file(), (
        "Missing exported shared Notes schema. Run "
        "`pnpm --filter @synapse/shared contracts:export` before backend tests: "
        f"{path}"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_path(name: str) -> Path:
    return SCHEMAS_DIR / f"{name}.schema.json"


def _properties(schema: Mapping[str, Any]) -> set[str]:
    return set(schema.get("properties", {}))


def _required(schema: Mapping[str, Any]) -> set[str]:
    return set(schema.get("required", []))


def _defaults(schema: Mapping[str, Any]) -> dict[str, Any]:
    return {
        name: property_schema["default"]
        for name, property_schema in schema.get("properties", {}).items()
        if "default" in property_schema
    }


def _effective_required(schema: Mapping[str, Any]) -> set[str]:
    return _required(schema) - set(_defaults(schema))


def _assert_success_envelope(schema: Mapping[str, Any]) -> None:
    assert _properties(schema) == {"data", "meta"}
    assert _required(schema) == {"data", "meta"}
    meta_schema = schema["properties"]["meta"]
    backend_meta_schema = ApiMeta.model_json_schema()
    assert _properties(meta_schema) - SHARED_OPTIONAL_META_FIELDS == _properties(
        backend_meta_schema
    )
    assert SHARED_OPTIONAL_META_FIELDS <= _properties(meta_schema)
    assert SHARED_OPTIONAL_META_FIELDS.isdisjoint(_required(meta_schema))
    assert _required(meta_schema) == _required(backend_meta_schema)
    _assert_snake_case(_properties(meta_schema))


def _assert_note_data_shape(schema: Mapping[str, Any]) -> None:
    backend_schema = Note.model_json_schema()
    assert _properties(schema) - SHARED_OPTIONAL_NOTE_FIELDS == _properties(backend_schema)
    assert SHARED_OPTIONAL_NOTE_FIELDS <= _properties(schema)
    assert SHARED_OPTIONAL_NOTE_FIELDS.isdisjoint(_required(schema))
    assert _required(schema) == _required(backend_schema)
    assert schema["additionalProperties"] is False
    assert backend_schema["additionalProperties"] is False
    _assert_snake_case(_properties(schema))


def _assert_snake_case(fields: set[str]) -> None:
    assert all(SNAKE_CASE_FIELD.fullmatch(field) for field in fields)


def _create_note(client: TestClient) -> dict[str, Any]:
    response = client.post("/v1/notes", json={"title": "Drift guard note"})
    assert response.status_code == 201
    return response.json()["data"]
