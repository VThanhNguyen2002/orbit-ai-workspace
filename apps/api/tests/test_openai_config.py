"""Tests for OpenAI configuration shape and fail-closed credential modes."""
from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import fields
from pathlib import Path

import pytest

from app.core.config import (
    AiConfigError,
    Settings,
    get_settings,
    validate_ai_provider_runtime,
)
from app.services.ai_summarization import (
    FakeSummarizationProvider,
    get_summarization_service,
)

_OPENAI_ENV_KEYS = (
    "SYNAPSE_AI_PROVIDER",
    "SYNAPSE_OPENAI_MODEL",
    "SYNAPSE_OPENAI_TIMEOUT_SECONDS",
    "SYNAPSE_OPENAI_MAX_RETRIES",
    "SYNAPSE_OPENAI_REQUEST_BUDGET",
    "SYNAPSE_OPENAI_AUTH_MODE",
)


@pytest.fixture(autouse=True)
def clear_openai_settings_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_openai_config_is_fake_disabled_and_credential_free() -> None:
    settings = get_settings()
    openai_field_names = {
        field.name for field in fields(Settings) if field.name.startswith("openai_")
    }

    assert settings.ai_summarization_enabled is False
    assert settings.ai_provider == "fake"
    assert settings.ai_max_input_chars == 50_000
    assert settings.openai_model == "openai-summary-placeholder"
    assert settings.openai_timeout_seconds == 30
    assert settings.openai_max_retries == 0
    assert settings.openai_request_budget == 0
    assert settings.openai_auth_mode == "fake"
    assert "openai_api_key" not in openai_field_names
    assert "openai_credential" not in openai_field_names
    validate_ai_provider_runtime(settings)


def test_unsupported_ai_provider_is_rejected_without_echoing_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsupported_value = "unsupported-provider-placeholder"
    monkeypatch.setenv("SYNAPSE_AI_PROVIDER", unsupported_value)
    get_settings.cache_clear()

    with pytest.raises(AiConfigError) as exc_info:
        get_settings()

    assert str(exc_info.value) == "Unsupported AI provider"
    assert unsupported_value not in str(exc_info.value)
    assert unsupported_value not in repr(exc_info.value)


def test_unsupported_openai_auth_mode_is_rejected_without_echoing_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsupported_value = "unsupported-auth-placeholder"
    monkeypatch.setenv("SYNAPSE_OPENAI_AUTH_MODE", unsupported_value)
    get_settings.cache_clear()

    with pytest.raises(AiConfigError) as exc_info:
        get_settings()

    assert str(exc_info.value) == "Unsupported OpenAI auth mode"
    assert unsupported_value not in str(exc_info.value)
    assert unsupported_value not in repr(exc_info.value)


def test_api_key_mode_without_future_runtime_fails_closed() -> None:
    settings = Settings(
        ai_provider="openai",
        openai_auth_mode="api_key",
    )

    with pytest.raises(AiConfigError) as exc_info:
        validate_ai_provider_runtime(settings)

    assert str(exc_info.value) == "OpenAI API-key runtime is not implemented"
    assert "provider-token-placeholder" not in str(exc_info.value)
    assert "provider-token-placeholder" not in repr(exc_info.value)


def test_workload_identity_mode_without_future_runtime_fails_closed() -> None:
    settings = Settings(
        ai_provider="openai",
        openai_auth_mode="workload_identity",
    )

    with pytest.raises(AiConfigError) as exc_info:
        validate_ai_provider_runtime(settings)

    assert str(exc_info.value) == "OpenAI workload identity runtime is not implemented"
    assert "oidc-token-placeholder" not in str(exc_info.value)
    assert "oidc-token-placeholder" not in repr(exc_info.value)


def test_fake_mode_does_not_require_credentials() -> None:
    settings = Settings(
        ai_provider="fake",
        openai_auth_mode="fake",
    )

    validate_ai_provider_runtime(settings)


def test_openai_config_does_not_switch_runtime_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SYNAPSE_AI_PROVIDER", "openai")
    monkeypatch.setenv("SYNAPSE_OPENAI_AUTH_MODE", "api_key")
    get_settings.cache_clear()

    service = get_summarization_service()

    assert isinstance(service._provider, FakeSummarizationProvider)


def test_invalid_numeric_openai_config_does_not_echo_raw_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_value = "credential-placeholder-value"
    monkeypatch.setenv("SYNAPSE_OPENAI_TIMEOUT_SECONDS", invalid_value)
    get_settings.cache_clear()

    with pytest.raises(AiConfigError) as exc_info:
        get_settings()

    error_text = str(exc_info.value)
    assert error_text == "SYNAPSE_OPENAI_TIMEOUT_SECONDS must be a positive integer"
    assert invalid_value not in error_text
    assert invalid_value not in repr(exc_info.value)


def test_gitleaksignore_remains_exact_fingerprint_only() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    lines = [
        line
        for line in (repo_root / ".gitleaksignore").read_text().splitlines()
        if line
    ]

    assert lines
    for line in lines:
        assert re.fullmatch(r"[0-9a-f]{40}:[^:]+:[^:]+:[0-9]+", line)
        assert "*" not in line
        assert "?" not in line
        assert not line.startswith("[")
        assert not line.startswith("allowlist")
