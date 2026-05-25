import socket

import pytest

from app.core.auth import AuthContext
from app.core.config import Settings
from app.core.supabase_client import (
    SupabaseUserClientConfigurationError,
    UserScopedSupabaseClientDescriptor,
    get_supabase_user_client,
)

USER_ID = "11111111-1111-4111-8111-111111111111"
ACCESS_TOKEN = "verified-local-access-token"
PROJECT_URL = "https://project.example.invalid"
PUBLISHABLE_KEY = "publishable-placeholder-key"
ANON_KEY = "legacy-anon-placeholder-key"
SERVICE_ROLE_KEY = "service-role-placeholder-key"


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


def _jwt_context() -> AuthContext:
    return AuthContext(user_id=USER_ID, auth_mode="jwt", access_token=ACCESS_TOKEN)


def _settings() -> Settings:
    return Settings(supabase_url=PROJECT_URL, supabase_publishable_key=PUBLISHABLE_KEY)
