from dataclasses import dataclass, field
from typing import Any

from app.core.supabase_client import (
    UserScopedSupabaseClientDescriptor,
)
from tests.helpers.notes_supabase_fake_client import FakeResponse


class FakeSdkTransportError(Exception):
    """Sanitized fake transport failure used by adapter-boundary tests."""


@dataclass(frozen=True)
class FakeTransportRequest:
    project_url: str
    table_name: str
    user_id: str
    key_source: str
    authorization: str = field(repr=False)
    public_api_key: str = field(repr=False)
    operations: tuple[tuple[object, ...], ...] = field(default_factory=tuple)

    def __repr__(self) -> str:
        return (
            "FakeTransportRequest("
            f"project_url={self.project_url!r}, "
            f"table_name={self.table_name!r}, "
            f"user_id={self.user_id!r}, "
            f"key_source={self.key_source!r}, "
            f"operations_count={len(self.operations)}, "
            "authorization=<redacted>, public_api_key=<redacted>)"
        )

    __str__ = __repr__


class FakeSdkAuthBoundary:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def set_session(self, *_args: object, **_kwargs: object) -> None:
        self.calls.append("set_session")
        raise AssertionError("fake SDK auth session mutation is not allowed")

    def refresh_session(self, *_args: object, **_kwargs: object) -> None:
        self.calls.append("refresh_session")
        raise AssertionError("fake SDK token refresh is not allowed")

    def persist_session(self, *_args: object, **_kwargs: object) -> None:
        self.calls.append("persist_session")
        raise AssertionError("fake SDK session persistence is not allowed")

    def __repr__(self) -> str:
        return f"FakeSdkAuthBoundary(calls={self.calls!r})"


class FakeSdkTransport:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = responses
        self.requests: list[FakeTransportRequest] = []

    def execute(self, request: FakeTransportRequest) -> FakeResponse:
        self.requests.append(request)
        if not self._responses:
            raise FakeSdkTransportError(
                "Fake Supabase SDK transport response queue is empty "
                "for request authorization=<redacted> public_api_key=<redacted>"
            )

        return self._responses.pop(0)

    def __repr__(self) -> str:
        return (
            "FakeSdkTransport("
            f"requests_count={len(self.requests)}, "
            f"responses_remaining={len(self._responses)})"
        )


class FakeSdkQuery:
    def __init__(self, *, client: "FakeSdkClient", table_name: str) -> None:
        self._client = client
        self._table_name = table_name
        self.operations: list[tuple[object, ...]] = []

    def select(self, fields: str, *, count: str | None = None) -> "FakeSdkQuery":
        self.operations.append(("select", fields, count))
        return self

    def insert(self, payload: dict[str, Any]) -> "FakeSdkQuery":
        self.operations.append(("insert", payload))
        return self

    def update(self, payload: dict[str, Any]) -> "FakeSdkQuery":
        self.operations.append(("update", payload))
        return self

    def eq(self, field: str, value: object) -> "FakeSdkQuery":
        self.operations.append(("eq", field, value))
        return self

    def order(self, field: str, *, desc: bool) -> "FakeSdkQuery":
        self.operations.append(("order", field, desc))
        return self

    def range(self, start: int, end: int) -> "FakeSdkQuery":
        self.operations.append(("range", start, end))
        return self

    def limit(self, value: int) -> "FakeSdkQuery":
        self.operations.append(("limit", value))
        return self

    def execute(self) -> FakeResponse:
        self.operations.append(("execute",))
        return self._client.execute_query(
            table_name=self._table_name,
            operations=tuple(self.operations),
        )


class FakeSdkClient:
    def __init__(
        self,
        *,
        project_url: str,
        user_id: str,
        key_source: str,
        authorization: str,
        public_api_key: str,
        transport: FakeSdkTransport,
        auth: FakeSdkAuthBoundary,
    ) -> None:
        self._project_url = project_url
        self._user_id = user_id
        self._key_source = key_source
        self._authorization = authorization
        self._public_api_key = public_api_key
        self.transport = transport
        self.auth = auth
        self.queries: list[FakeSdkQuery] = []

    def table(self, table_name: str) -> FakeSdkQuery:
        query = FakeSdkQuery(client=self, table_name=table_name)
        self.queries.append(query)
        return query

    def execute_query(
        self,
        *,
        table_name: str,
        operations: tuple[tuple[object, ...], ...],
    ) -> FakeResponse:
        return self.transport.execute(
            FakeTransportRequest(
                project_url=self._project_url,
                table_name=table_name,
                user_id=self._user_id,
                key_source=self._key_source,
                authorization=self._authorization,
                public_api_key=self._public_api_key,
                operations=operations,
            )
        )

    def __repr__(self) -> str:
        return (
            "FakeSdkClient("
            f"project_url={self._project_url!r}, "
            f"user_id={self._user_id!r}, "
            f"key_source={self._key_source!r}, "
            f"queries_count={len(self.queries)}, "
            "authorization=<redacted>, public_api_key=<redacted>)"
        )

    __str__ = __repr__


class FakeSdkClientFactory:
    def __init__(self, response_batches: list[list[FakeResponse]]) -> None:
        self._response_batches = response_batches
        self.safe_create_calls: list[tuple[str, str, str]] = []
        self.clients: list[FakeSdkClient] = []
        self.global_headers: dict[str, str] = {}

    def create_client(
        self,
        *,
        project_url: str,
        user_id: str,
        key_source: str,
        authorization: str,
        public_api_key: str,
    ) -> FakeSdkClient:
        self.safe_create_calls.append((project_url, user_id, key_source))
        responses = self._response_batches.pop(0) if self._response_batches else []
        client = FakeSdkClient(
            project_url=project_url,
            user_id=user_id,
            key_source=key_source,
            authorization=authorization,
            public_api_key=public_api_key,
            transport=FakeSdkTransport(responses),
            auth=FakeSdkAuthBoundary(),
        )
        self.clients.append(client)
        return client

    def __repr__(self) -> str:
        return (
            "FakeSdkClientFactory("
            f"safe_create_calls={self.safe_create_calls!r}, "
            f"clients_count={len(self.clients)}, "
            f"global_headers={self.global_headers!r})"
        )


class FakeSdkTransportAdapter:
    def __init__(self, factory: FakeSdkClientFactory) -> None:
        self._factory = factory
        self.received_descriptor_types: list[type[UserScopedSupabaseClientDescriptor]] = []
        self.safe_build_calls: list[tuple[str, str, str]] = []

    def build(self, descriptor: UserScopedSupabaseClientDescriptor) -> FakeSdkClient:
        self.received_descriptor_types.append(type(descriptor))
        self.safe_build_calls.append(
            (descriptor.project_url, descriptor.user_id, descriptor.key_source)
        )
        return self._factory.create_client(
            project_url=descriptor.project_url,
            user_id=descriptor.user_id,
            key_source=descriptor.key_source,
            authorization=f"Bearer {descriptor.access_token.get_secret_value()}",
            public_api_key=descriptor.public_api_key.get_secret_value(),
        )

    def __repr__(self) -> str:
        return (
            "FakeSdkTransportAdapter("
            f"safe_build_calls={self.safe_build_calls!r}, "
            f"received_descriptor_count={len(self.received_descriptor_types)})"
        )
