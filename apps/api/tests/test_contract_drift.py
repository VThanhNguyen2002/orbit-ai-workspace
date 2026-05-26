import inspect

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from app.routers.notes import list_notes
from app.schemas.notes import (
    CreateNoteRequest,
    DeleteNoteRequest,
    ListNotesData,
    PaginationMeta,
    UpdateNoteRequest,
)
from tests.helpers.contract_drift_helpers import (
    SERVER_CONTROLLED_CREATE_FIELDS,
    STABLE_NOTES_SCHEMAS,
    assert_note_data_shape,
    assert_snake_case,
    assert_success_envelope,
    defaults,
    effective_required,
    load_schema,
    properties,
    required,
    schema_path,
)
from tests.helpers.notes_assertions import create_note


def test_stable_notes_json_schema_artifacts_are_exported() -> None:
    missing = sorted(
        name for name in STABLE_NOTES_SCHEMAS if not schema_path(name).is_file()
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
    shared_schema = load_schema(schema_name)
    backend_schema = backend_model.model_json_schema()

    assert properties(shared_schema) == properties(backend_schema)
    assert effective_required(shared_schema) == required(backend_schema)
    assert shared_schema["additionalProperties"] is False
    assert backend_schema["additionalProperties"] is False
    assert_snake_case(properties(shared_schema))


def test_create_note_defaults_and_server_controlled_fields_remain_bounded() -> None:
    shared_schema = load_schema("create_note_request")
    backend_defaults = {
        name: field.default
        for name, field in CreateNoteRequest.model_fields.items()
        if not field.is_required()
    }

    assert defaults(shared_schema) == backend_defaults == {
        "content": "",
        "content_type": "plain",
    }
    assert SERVER_CONTROLLED_CREATE_FIELDS.isdisjoint(properties(shared_schema))

    for field_name in SERVER_CONTROLLED_CREATE_FIELDS:
        with pytest.raises(ValidationError):
            CreateNoteRequest.model_validate({"title": "Bounded note", field_name: "rejected"})


def test_list_notes_request_fields_and_defaults_match_route_query_contract() -> None:
    shared_schema = load_schema("list_notes_request")
    parameters = inspect.signature(list_notes).parameters
    non_query_parameters = {"request", "service", "auth_context"}
    query_fields = set(parameters) - non_query_parameters
    route_defaults = {
        name: parameters[name].default
        for name in query_fields
        if parameters[name].default is not None
    }

    assert properties(shared_schema) == query_fields
    assert effective_required(shared_schema) == set()
    assert defaults(shared_schema) == route_defaults == {
        "page": 1,
        "per_page": 20,
        "sort": "updated_at",
        "order": "desc",
        "include_deleted": False,
    }
    assert_snake_case(query_fields)


def test_note_schema_and_single_note_response_envelopes_match_backend_shape() -> None:
    assert_note_data_shape(load_schema("note"))

    for schema_name in {
        "get_note_response",
        "create_note_response",
        "update_note_response",
        "delete_note_response",
    }:
        shared_schema = load_schema(schema_name)
        assert_success_envelope(shared_schema)
        assert_note_data_shape(shared_schema["properties"]["data"])


def test_list_notes_response_retains_items_and_pagination_shape() -> None:
    shared_schema = load_schema("list_notes_response")
    assert_success_envelope(shared_schema)
    data_schema = shared_schema["properties"]["data"]

    assert properties(data_schema) == set(ListNotesData.model_fields) == {"items", "pagination"}
    assert required(data_schema) == required(ListNotesData.model_json_schema())
    assert data_schema["additionalProperties"] is False
    assert_note_data_shape(data_schema["properties"]["items"]["items"])

    pagination_schema = data_schema["properties"]["pagination"]
    backend_pagination_schema = PaginationMeta.model_json_schema()
    assert properties(pagination_schema) == properties(backend_pagination_schema)
    assert required(pagination_schema) == required(backend_pagination_schema)
    assert_snake_case(properties(pagination_schema))


def test_notes_dto_validation_failures_remain_400_validation_error(client: TestClient) -> None:
    create_response = client.post(
        "/v1/notes",
        json={"title": "Rejected note", "id": "server-controlled"},
    )
    assert create_response.status_code == 400
    assert create_response.json()["error"]["code"] == "VALIDATION_ERROR"

    note = create_note(client, title="Drift guard note")
    for response in [
        client.patch(f"/v1/notes/{note['id']}", json={"title": "Missing version"}),
        client.request("DELETE", f"/v1/notes/{note['id']}", json={}),
    ]:
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_notes_stale_versions_remain_409_conflict(client: TestClient) -> None:
    note = create_note(client, title="Drift guard note")

    for response in [
        client.patch(f"/v1/notes/{note['id']}", json={"title": "Stale", "version": 0}),
        client.request("DELETE", f"/v1/notes/{note['id']}", json={"version": 0}),
    ]:
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"
