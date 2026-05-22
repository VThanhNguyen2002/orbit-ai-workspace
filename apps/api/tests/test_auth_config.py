import pytest
from starlette.requests import Request

from app.core.auth import AuthContext, get_auth_context
from app.core.config import Settings, get_settings
from app.core.errors import ApiError


def test_settings_do_not_require_supabase_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.auth_mode == "dev"
    assert settings.notes_repository == "memory"
    assert settings.supabase_url is None
    assert settings.supabase_anon_key is None
    assert settings.supabase_jwt_secret is None
    assert settings.supabase_service_role_key is None


def test_dev_auth_context_returns_safe_dev_user() -> None:
    auth_context = get_auth_context(
        request=_request(),
        settings=Settings(auth_mode="dev", dev_user_id="dev_user"),
    )

    assert auth_context == AuthContext(user_id="dev_user", auth_mode="dev")


def test_jwt_auth_boundary_rejects_missing_bearer_token() -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(),
            settings=Settings(auth_mode="jwt", supabase_jwt_secret="placeholder"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"


def test_jwt_auth_boundary_is_explicitly_deferred() -> None:
    with pytest.raises(ApiError) as exc_info:
        get_auth_context(
            request=_request(authorization="Bearer placeholder-token"),
            settings=Settings(auth_mode="jwt", supabase_jwt_secret="placeholder"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "JWT auth validation is not implemented"


def _request(*, authorization: str | None = None) -> Request:
    headers = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode()))

    return Request({"type": "http", "headers": headers})
