import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.auth import AuthContext, get_auth_context
from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.main import create_app


def test_settings_do_not_require_supabase_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "SYNAPSE_JWT_ISSUER",
        "SYNAPSE_JWT_AUDIENCE",
        "SYNAPSE_JWT_PUBLIC_KEY",
        "SUPABASE_URL",
        "SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.auth_mode == "dev"
    assert settings.notes_repository == "memory"
    assert settings.jwt_issuer is None
    assert settings.jwt_audience is None
    assert settings.jwt_public_key is None
    assert settings.supabase_url is None
    assert settings.supabase_publishable_key is None
    assert settings.supabase_anon_key is None
    assert settings.supabase_jwt_secret is None
    assert settings.supabase_service_role_key is None


def test_settings_preserve_unsupported_auth_mode_for_fail_closed_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SYNAPSE_AUTH_MODE", "unsupported")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.auth_mode == "unsupported"


def test_dev_auth_context_returns_safe_dev_user() -> None:
    auth_context = get_auth_context(
        request=_request(),
        settings=Settings(auth_mode="dev", dev_user_id="dev_user"),
    )

    assert auth_context == AuthContext(user_id="dev_user", auth_mode="dev")


def test_jwt_auth_boundary_rejects_missing_authorization() -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(),
            settings=Settings(auth_mode="jwt"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.parametrize(
    "authorization",
    [
        "",
        "token placeholder-token",
        "Bearer",
        "Bearer placeholder-token extra",
    ],
)
def test_jwt_auth_boundary_rejects_malformed_authorization(authorization: str) -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(authorization=authorization),
            settings=Settings(auth_mode="jwt"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"


def test_jwt_auth_boundary_without_verifier_config_fails_closed() -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(authorization="Bearer placeholder-token"),
            settings=Settings(auth_mode="jwt"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"
    assert exc_info.value.message == "JWT auth is not configured"


def test_settings_read_local_jwt_verifier_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SYNAPSE_JWT_ISSUER", "https://issuer.example.invalid/auth/v1")
    monkeypatch.setenv("SYNAPSE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setenv("SYNAPSE_JWT_PUBLIC_KEY", "public-key-placeholder")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.jwt_issuer == "https://issuer.example.invalid/auth/v1"
    assert settings.jwt_audience == "authenticated"
    assert settings.jwt_public_key == "public-key-placeholder"


def test_settings_read_public_supabase_client_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://project.example.invalid")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "publishable-placeholder-key")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.supabase_url == "https://project.example.invalid"
    assert settings.supabase_publishable_key == "publishable-placeholder-key"


def test_unsupported_auth_mode_fails_closed() -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(),
            settings=Settings(auth_mode="unsupported"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"
    assert exc_info.value.message == "Unsupported auth mode"


def test_notes_route_in_jwt_mode_rejects_missing_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SYNAPSE_AUTH_MODE", "jwt")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get("/v1/notes", headers={"x-request-id": "req_jwt_missing"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert response.json()["meta"] == {"request_id": "req_jwt_missing"}


def test_notes_route_with_unsupported_auth_mode_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SYNAPSE_AUTH_MODE", "unsupported")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get("/v1/notes", headers={"x-request-id": "req_auth_mode"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert response.json()["meta"] == {"request_id": "req_auth_mode"}


def _request(*, authorization: str | None = None) -> Request:
    headers = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode()))

    return Request({"type": "http", "headers": headers})
