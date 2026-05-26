from dataclasses import dataclass
from typing import Any

from app.core.config import Settings
from app.repositories.notes_supabase import SupabaseNotesRepository, get_supabase_notes_repository

USER_ID = "11111111-1111-4111-8111-111111111111"
NOTE_ID = "22222222-2222-4222-8222-222222222222"
PROJECT_URL = "https://project.example.invalid"
PUBLIC_KEY = "publishable-placeholder-key"
TIMESTAMP = "2026-05-26T03:00:00.000Z"


@dataclass(frozen=True)
class FakeResponse:
    data: list[dict[str, Any]]
    count: int | None = None


class FakeQuery:
    def __init__(self, client: "FakeSupabaseClient") -> None:
        self._client = client
        self.operations: list[tuple[object, ...]] = []

    def select(self, fields: str, *, count: str | None = None) -> "FakeQuery":
        self.operations.append(("select", fields, count))
        return self

    def insert(self, payload: dict[str, Any]) -> "FakeQuery":
        self.operations.append(("insert", payload))
        return self

    def update(self, payload: dict[str, Any]) -> "FakeQuery":
        self.operations.append(("update", payload))
        return self

    def eq(self, field: str, value: object) -> "FakeQuery":
        self.operations.append(("eq", field, value))
        return self

    def order(self, field: str, *, desc: bool) -> "FakeQuery":
        self.operations.append(("order", field, desc))
        return self

    def range(self, start: int, end: int) -> "FakeQuery":
        self.operations.append(("range", start, end))
        return self

    def limit(self, value: int) -> "FakeQuery":
        self.operations.append(("limit", value))
        return self

    def execute(self) -> FakeResponse:
        self.operations.append(("execute",))
        return self._client.next_response()


class FakeSupabaseClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = responses
        self.table_names: list[str] = []
        self.queries: list[FakeQuery] = []

    def table(self, table_name: str) -> FakeQuery:
        self.table_names.append(table_name)
        query = FakeQuery(self)
        self.queries.append(query)
        return query

    def next_response(self) -> FakeResponse:
        if not self._responses:
            raise AssertionError("Fake Supabase response queue is empty")
        return self._responses.pop(0)


def fake_repository(
    *responses: FakeResponse,
    settings: Settings | None = None,
) -> tuple[SupabaseNotesRepository, FakeSupabaseClient]:
    client = FakeSupabaseClient(list(responses))
    repository = get_supabase_notes_repository(settings or fake_settings(), client=client)
    return repository, client


def fake_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "notes_repository": "supabase",
        "supabase_url": PROJECT_URL,
        "supabase_publishable_key": PUBLIC_KEY,
    }
    values.update(overrides)
    return Settings(**values)


def note_row(
    *,
    title: str = "Planning note",
    is_deleted: bool = False,
    deleted_at: str | None = None,
    version: int = 1,
) -> dict[str, Any]:
    return {
        "id": NOTE_ID,
        "user_id": USER_ID,
        "title": title,
        "content": "Private content",
        "content_type": "plain",
        "is_archived": False,
        "is_deleted": is_deleted,
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "deleted_at": deleted_at,
        "version": version,
    }
