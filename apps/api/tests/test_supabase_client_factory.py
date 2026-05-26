import socket

import pytest

from app.core.auth import AuthContext
from app.core.config import Settings
from app.core.supabase_client import (
    SupabaseUserClientConfigurationError,
    UserScopedSupabaseClient,
    UserScopedSupabaseClientAdapter,
    UserScopedSupabaseClientDescriptor,
    UserScopedSupabaseQuery,
    get_supabase_user_client,
)
from app.repositories.notes_supabase import get_supabase_notes_repository
from tests.helpers.notes_supabase_fake_client import (
    NOTE_ID,
    FakeResponse,
    FakeSupabaseClient,
    note_row,
)

USER_ID = "11111111-1111-4111-8111-111111111111"
ACCESS_TOKEN = "verified-local-access-token"
PROJECT_URL = "https://project.example.invalid"
PUBLISHABLE_KEY = "publishable-placeholder-key"
ANON_KEY = "legacy-anon-placeholder-key"
SERVICE_ROLE_KEY = "service-role-placeholder-key"
SECOND_ACCESS_TOKEN = "second-verified-local-access-token"


class FakeUserScopedSupabaseClientAdapter:
    def __init__(self, response_batches: list[list[FakeResponse]]) -> None:
        self._response_batches = response_batches
        self.safe_build_calls: list[tuple[str, str, str]] = []
        self.clients: list[FakeSupabaseClient] = []

    def build(self, descriptor: UserScopedSupabaseClientDescriptor) -> FakeSupabaseClient:
        self.safe_build_calls.append(
            (descriptor.project_url, descriptor.user_id, descriptor.key_source)
        )
        client = FakeSupabaseClient(self._response_batches.pop(0))
        self.clients.append(client)
        return client


def test_user_scoped_client_rejects_dev_auth_context() -> None:
    with pytest.raises(SupabaseUserClientConfigurationError) as exc_info:
        get_supabase_user_client(
            auth_context=AuthContext(user_id="dev_user", auth_mode="dev"),
            settings=_settings(),
        )

    assert str(exc_info.value) == "User-scoped Supabase clients require JWT authentication"


def test_user_scoped_client_rejects_missing_access_token() -> None:
    with pytest.raises(SupabaseUserClientConfigurationError) as exc_info:
        get_supabase_user_client(
            auth_context=AuthContext(user_id=USER_ID, auth_mode="jwt"),
            settings=_settings(),
        )

    assert str(exc_info.value) == "User-scoped Supabase clients require a verified access token"


@pytest.mark.parametrize(
    "settings",
    [
        Settings(supabase_publishable_key=PUBLISHABLE_KEY),
        Settings(supabase_url=PROJECT_URL),
        Settings(supabase_url=PROJECT_URL, supabase_service_role_key=SERVICE_ROLE_KEY),
    ],
)
def test_user_scoped_client_rejects_missing_public_configuration(settings: Settings) -> None:
    with pytest.raises(SupabaseUserClientConfigurationError) as exc_info:
        get_supabase_user_client(auth_context=_jwt_context(), settings=settings)

    assert str(exc_info.value) == "User-scoped Supabase client is not configured"
    assert ACCESS_TOKEN not in str(exc_info.value)
    assert SERVICE_ROLE_KEY not in str(exc_info.value)


def test_user_scoped_client_builds_redacted_descriptor_from_verified_jwt_context() -> None:
    descriptor = get_supabase_user_client(auth_context=_jwt_context(), settings=_settings())

    assert isinstance(descriptor, UserScopedSupabaseClientDescriptor)
    assert descriptor.project_url == PROJECT_URL
    assert descriptor.user_id == USER_ID
    assert descriptor.key_source == "publishable"
    assert descriptor.public_api_key.get_secret_value() == PUBLISHABLE_KEY
    assert descriptor.access_token.get_secret_value() == ACCESS_TOKEN

    rendered = f"{descriptor!r} {descriptor}"
    assert ACCESS_TOKEN not in rendered
    assert PUBLISHABLE_KEY not in rendered
    assert "<redacted>" in rendered


def test_user_scoped_client_uses_legacy_anon_key_only_as_public_fallback() -> None:
    descriptor = get_supabase_user_client(
        auth_context=_jwt_context(),
        settings=Settings(supabase_url=PROJECT_URL, supabase_anon_key=ANON_KEY),
    )

    assert descriptor.key_source == "anon"
    assert descriptor.public_api_key.get_secret_value() == ANON_KEY


def test_user_scoped_client_never_selects_service_role_key() -> None:
    descriptor = get_supabase_user_client(
        auth_context=_jwt_context(),
        settings=Settings(
            supabase_url=PROJECT_URL,
            supabase_publishable_key=PUBLISHABLE_KEY,
            supabase_anon_key=ANON_KEY,
            supabase_service_role_key=SERVICE_ROLE_KEY,
        ),
    )

    assert descriptor.key_source == "publishable"
    assert descriptor.public_api_key.get_secret_value() == PUBLISHABLE_KEY
    assert SERVICE_ROLE_KEY not in repr(descriptor)


def test_user_scoped_client_descriptor_construction_makes_no_network_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    descriptor = get_supabase_user_client(auth_context=_jwt_context(), settings=_settings())

    assert descriptor.user_id == USER_ID


def test_fake_adapter_satisfies_protocol_and_supports_notes_query_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    descriptor = get_supabase_user_client(auth_context=_jwt_context(), settings=_settings())
    adapter = FakeUserScopedSupabaseClientAdapter([[FakeResponse(data=[note_row()])]])

    assert isinstance(adapter, UserScopedSupabaseClientAdapter)
    client = adapter.build(descriptor)
    assert isinstance(client, UserScopedSupabaseClient)

    repository = get_supabase_notes_repository(_settings(), client=client)
    note = repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    assert note.user_id == USER_ID
    assert isinstance(client.queries[0], UserScopedSupabaseQuery)
    assert adapter.safe_build_calls == [(PROJECT_URL, USER_ID, "publishable")]


def test_fake_adapter_builds_distinct_request_clients_without_secret_propagation() -> None:
    settings = Settings(
        supabase_url=PROJECT_URL,
        supabase_publishable_key=PUBLISHABLE_KEY,
        supabase_service_role_key=SERVICE_ROLE_KEY,
    )
    first_descriptor = get_supabase_user_client(
        auth_context=_jwt_context(), settings=settings
    )
    second_descriptor = get_supabase_user_client(
        auth_context=_jwt_context(access_token=SECOND_ACCESS_TOKEN), settings=settings
    )
    adapter = FakeUserScopedSupabaseClientAdapter([[], []])

    first_client = adapter.build(first_descriptor)
    second_client = adapter.build(second_descriptor)

    assert first_client is not second_client
    assert first_descriptor.access_token != second_descriptor.access_token
    rendered_calls = repr(adapter.safe_build_calls)
    assert ACCESS_TOKEN not in rendered_calls
    assert SECOND_ACCESS_TOKEN not in rendered_calls
    assert SERVICE_ROLE_KEY not in rendered_calls


def _jwt_context(*, access_token: str = ACCESS_TOKEN) -> AuthContext:
    return AuthContext(user_id=USER_ID, auth_mode="jwt", access_token=access_token)


def _settings() -> Settings:
    return Settings(supabase_url=PROJECT_URL, supabase_publishable_key=PUBLISHABLE_KEY)
