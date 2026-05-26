import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.models.responses import ApiMeta
from app.schemas.notes import Note

SCHEMAS_DIR = (
    Path(__file__).resolve().parents[4] / "packages" / "shared" / "dist" / "schemas" / "domain"
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


def load_schema(name: str) -> dict[str, Any]:
    path = schema_path(name)
    assert path.is_file(), (
        "Missing exported shared Notes schema. Run "
        "`pnpm --filter @synapse/shared contracts:export` before backend tests: "
        f"{path}"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def schema_path(name: str) -> Path:
    return SCHEMAS_DIR / f"{name}.schema.json"


def properties(schema: Mapping[str, Any]) -> set[str]:
    return set(schema.get("properties", {}))


def required(schema: Mapping[str, Any]) -> set[str]:
    return set(schema.get("required", []))


def defaults(schema: Mapping[str, Any]) -> dict[str, Any]:
    return {
        name: property_schema["default"]
        for name, property_schema in schema.get("properties", {}).items()
        if "default" in property_schema
    }


def effective_required(schema: Mapping[str, Any]) -> set[str]:
    return required(schema) - set(defaults(schema))


def assert_success_envelope(schema: Mapping[str, Any]) -> None:
    assert properties(schema) == {"data", "meta"}
    assert required(schema) == {"data", "meta"}
    meta_schema = schema["properties"]["meta"]
    backend_meta_schema = ApiMeta.model_json_schema()
    assert properties(meta_schema) - SHARED_OPTIONAL_META_FIELDS == properties(
        backend_meta_schema
    )
    assert SHARED_OPTIONAL_META_FIELDS <= properties(meta_schema)
    assert SHARED_OPTIONAL_META_FIELDS.isdisjoint(required(meta_schema))
    assert required(meta_schema) == required(backend_meta_schema)
    assert_snake_case(properties(meta_schema))


def assert_note_data_shape(schema: Mapping[str, Any]) -> None:
    backend_schema = Note.model_json_schema()
    assert properties(schema) - SHARED_OPTIONAL_NOTE_FIELDS == properties(backend_schema)
    assert SHARED_OPTIONAL_NOTE_FIELDS <= properties(schema)
    assert SHARED_OPTIONAL_NOTE_FIELDS.isdisjoint(required(schema))
    assert required(schema) == required(backend_schema)
    assert schema["additionalProperties"] is False
    assert backend_schema["additionalProperties"] is False
    assert_snake_case(properties(schema))


def assert_snake_case(fields: set[str]) -> None:
    assert all(SNAKE_CASE_FIELD.fullmatch(field) for field in fields)
