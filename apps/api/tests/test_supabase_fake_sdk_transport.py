import socket

import pytest

from app.core.auth import AuthContext
from app.core.config import Settings
from app.core.supabase_client import (
    UserScopedSupabaseClientAdapter,
    UserScopedSupabaseClientDescriptor,
    get_supabase_user_client,
)
from app.repositories.notes_supabase import get_supabase_notes_repository
from tests.helpers.notes_supabase_fake_client import (
    NOTE_ID,
    USER_ID,
    FakeResponse,
    note_row,
)
from tests.helpers.supabase_fake_sdk_transport import (
    FakeSdkClientFactory,
    FakeSdkTransportAdapter,
    FakeSdkTransportError,
)

ACCESS_TOKEN = "verified-local-access-token"
SECOND_ACCESS_TOKEN = "second-verified-local-access-token"
PROJECT_URL = "https://project.example.invalid"
PUBLISHABLE_KEY = "publishable-placeholder-key"
ANON_KEY = "legacy-anon-placeholder-key"
SERVICE_ROLE_KEY = "service-role-placeholder-key"


def test_fake_sdk_transport_uses_request_authorization_and_public_key_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    descriptor = _descriptor(
        settings=_settings(supabase_service_role_key=SERVICE_ROLE_KEY)
    )
    factory = FakeSdkClientFactory([[FakeResponse(data=[note_row()], count=1)]])
    adapter = FakeSdkTransportAdapter(factory)

    assert isinstance(adapter, UserScopedSupabaseClientAdapter)
    client = adapter.build(descriptor)
    repository = get_supabase_notes_repository(_settings(), client=client)
    listing = repository.list_notes(
        user_id=USER_ID,
        page=1,
        per_page=20,
        sort="updated_at",
        order="desc",
        is_archived=None,
        include_deleted=False,
    )

    assert [note.id for note in listing.items] == [NOTE_ID]
    assert adapter.received_descriptor_types == [UserScopedSupabaseClientDescriptor]
    assert adapter.safe_build_calls == [(PROJECT_URL, USER_ID, "publishable")]
    assert factory.safe_create_calls == [(PROJECT_URL, USER_ID, "publishable")]
    assert factory.global_headers == {}
    assert client.auth.calls == []

    request = client.transport.requests[0]
    assert request.authorization == f"Bearer {ACCESS_TOKEN}"
    assert request.public_api_key == PUBLISHABLE_KEY
    assert request.key_source == "publishable"
    assert request.operations == (
        ("select", "*", "exact"),
        ("eq", "user_id", USER_ID),
        ("eq", "is_deleted", False),
        ("order", "updated_at", True),
        ("order", "id", True),
        ("range", 0, 19),
        ("execute",),
    )

    rendered_safe_state = repr((adapter, factory, client, client.transport, request))
    assert ACCESS_TOKEN not in rendered_safe_state
    assert PUBLISHABLE_KEY not in rendered_safe_state
    assert SERVICE_ROLE_KEY not in rendered_safe_state


def test_fake_sdk_transport_uses_legacy_anon_key_as_public_metadata_only() -> None:
    descriptor = _descriptor(
        settings=Settings(
            supabase_url=PROJECT_URL,
            supabase_anon_key=ANON_KEY,
            supabase_service_role_key=SERVICE_ROLE_KEY,
        )
    )
    factory = FakeSdkClientFactory([[FakeResponse(data=[note_row()])]])
    adapter = FakeSdkTransportAdapter(factory)

    client = adapter.build(descriptor)
    repository = get_supabase_notes_repository(
        Settings(supabase_url=PROJECT_URL, supabase_anon_key=ANON_KEY),
        client=client,
    )
    note = repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    request = client.transport.requests[0]
    assert note.id == NOTE_ID
    assert descriptor.key_source == "anon"
    assert request.authorization == f"Bearer {ACCESS_TOKEN}"
    assert request.public_api_key == ANON_KEY
    assert request.key_source == "anon"
    assert SERVICE_ROLE_KEY not in repr((adapter, factory, client, request))


def test_fake_sdk_transport_builds_request_scoped_clients_without_global_auth_mutation() -> None:
    first_descriptor = _descriptor()
    second_descriptor = _descriptor(access_token=SECOND_ACCESS_TOKEN)
    factory = FakeSdkClientFactory(
        [
            [FakeResponse(data=[note_row(title="First request")])],
            [FakeResponse(data=[note_row(title="Second request")])],
        ]
    )
    adapter = FakeSdkTransportAdapter(factory)

    first_client = adapter.build(first_descriptor)
    second_client = adapter.build(second_descriptor)
    first_repository = get_supabase_notes_repository(_settings(), client=first_client)
    second_repository = get_supabase_notes_repository(_settings(), client=second_client)

    first_note = first_repository.get_note(user_id=USER_ID, note_id=NOTE_ID)
    second_note = second_repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    assert first_note.title == "First request"
    assert second_note.title == "Second request"
    assert first_client is not second_client
    assert first_client.transport is not second_client.transport
    assert first_client.auth is not second_client.auth
    assert first_client.auth.calls == []
    assert second_client.auth.calls == []
    assert factory.global_headers == {}
    assert first_client.transport.requests[0].authorization == f"Bearer {ACCESS_TOKEN}"
    assert second_client.transport.requests[0].authorization == (
        f"Bearer {SECOND_ACCESS_TOKEN}"
    )
    assert ACCESS_TOKEN not in repr(second_client.transport.requests[0])
    assert SECOND_ACCESS_TOKEN not in repr(first_client.transport.requests[0])


def test_fake_sdk_transport_rejects_service_role_shape_and_redacts_failures() -> None:
    descriptor = _descriptor(
        settings=_settings(supabase_service_role_key=SERVICE_ROLE_KEY)
    )
    factory = FakeSdkClientFactory([[]])
    adapter = FakeSdkTransportAdapter(factory)
    client = adapter.build(descriptor)
    repository = get_supabase_notes_repository(_settings(), client=client)

    with pytest.raises(FakeSdkTransportError) as exc_info:
        repository.get_note(user_id=USER_ID, note_id=NOTE_ID)

    with pytest.raises(TypeError) as type_error:
        FakeSdkTransportAdapter(factory, service_role_key=SERVICE_ROLE_KEY)

    rendered = " ".join(
        str(value)
        for value in (
            descriptor,
            adapter,
            factory,
            client,
            client.transport,
            client.transport.requests[0],
            exc_info.value,
            type_error.value,
        )
    )
    assert "redacted" in str(exc_info.value)
    assert ACCESS_TOKEN not in rendered
    assert PUBLISHABLE_KEY not in rendered
    assert SERVICE_ROLE_KEY not in rendered


def _descriptor(
    *,
    access_token: str = ACCESS_TOKEN,
    settings: Settings | None = None,
) -> UserScopedSupabaseClientDescriptor:
    return get_supabase_user_client(
        auth_context=AuthContext(
            user_id=USER_ID,
            auth_mode="jwt",
            access_token=access_token,
        ),
        settings=settings or _settings(),
    )


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "supabase_url": PROJECT_URL,
        "supabase_publishable_key": PUBLISHABLE_KEY,
    }
    values.update(overrides)
    return Settings(**values)
