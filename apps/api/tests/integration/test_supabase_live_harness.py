import socket

import pytest

from tests.integration.supabase_live_harness import (
    ANON_KEY_ENV,
    MODE_ENV,
    OPT_IN_ENV,
    PUBLISHABLE_KEY_ENV,
    SERVICE_ROLE_ENV,
    URL_ENV,
    USER_A_TOKEN_ENV,
    USER_B_TOKEN_ENV,
    build_synthetic_note_prefix,
    get_supabase_live_test_config,
    inspect_supabase_live_harness,
    redact_live_test_config,
    should_run_supabase_live_tests,
)

PROJECT_URL = "https://project.example.invalid"
PUBLISHABLE_KEY = "publishable-placeholder-key"
ANON_KEY = "legacy-anon-placeholder-key"
USER_A_TOKEN = "synthetic-user-a-access-token"
USER_B_TOKEN = "synthetic-user-b-access-token"
SERVICE_ROLE_KEY = "service-role-placeholder-key"


def test_default_state_skips_live_harness() -> None:
    decision = inspect_supabase_live_harness({})

    assert decision.enabled is False
    assert should_run_supabase_live_tests({}) is False
    assert OPT_IN_ENV in decision.reason
    assert USER_A_TOKEN not in repr(decision)


def test_missing_flag_skips_even_when_other_values_exist() -> None:
    env = _enabled_env()
    env.pop(OPT_IN_ENV)

    decision = inspect_supabase_live_harness(env)

    assert decision.enabled is False
    assert decision.missing_env == ()
    assert OPT_IN_ENV in decision.reason


def test_missing_required_env_skips_with_names_only() -> None:
    decision = inspect_supabase_live_harness({OPT_IN_ENV: "1", MODE_ENV: "local"})

    assert decision.enabled is False
    assert URL_ENV in decision.missing_env
    assert USER_A_TOKEN_ENV in decision.missing_env
    assert USER_B_TOKEN_ENV in decision.missing_env
    assert f"{PUBLISHABLE_KEY_ENV} or {ANON_KEY_ENV}" in decision.missing_env
    rendered = repr(decision)
    assert PROJECT_URL not in rendered
    assert USER_A_TOKEN not in rendered


def test_invalid_mode_skips_safely() -> None:
    decision = inspect_supabase_live_harness(
        _enabled_env(**{MODE_ENV: "production"})
    )

    assert decision.enabled is False
    assert decision.invalid_env == (MODE_ENV,)
    assert "production" not in repr(decision)


def test_service_role_env_is_rejected_for_request_path_live_tests() -> None:
    decision = inspect_supabase_live_harness(
        _enabled_env(**{SERVICE_ROLE_ENV: SERVICE_ROLE_KEY})
    )

    assert decision.enabled is False
    assert decision.invalid_env == (SERVICE_ROLE_ENV,)
    assert SERVICE_ROLE_ENV in decision.reason
    assert SERVICE_ROLE_KEY not in repr(decision)


def test_enabled_config_redacts_values_and_prefers_publishable_key() -> None:
    config = get_supabase_live_test_config(_enabled_env())

    assert config.mode == "local"
    assert config.public_key_source == "publishable"
    rendered = f"{config!r} {config} {redact_live_test_config(config)}"
    assert "redacted" in rendered
    assert PROJECT_URL not in rendered
    assert PUBLISHABLE_KEY not in rendered
    assert USER_A_TOKEN not in rendered
    assert USER_B_TOKEN not in rendered


def test_legacy_anon_key_can_be_used_as_public_fallback() -> None:
    env = _enabled_env(**{PUBLISHABLE_KEY_ENV: "", ANON_KEY_ENV: ANON_KEY})

    config = get_supabase_live_test_config(env)

    assert config.public_key_source == "anon"
    assert ANON_KEY not in repr(config)


def test_synthetic_data_naming_rules_are_enforced() -> None:
    prefix = build_synthetic_note_prefix(run_id="run-001", user_label="user-a")

    assert prefix == "synapse-live-harness-user-a-run-001"
    with pytest.raises(ValueError):
        build_synthetic_note_prefix(run_id="Run 001", user_label="user-a")
    with pytest.raises(ValueError):
        build_synthetic_note_prefix(run_id="run-001", user_label="user@example.invalid")


def test_default_harness_path_makes_no_network_call(monkeypatch: pytest.MonkeyPatch) -> None:
    def reject_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    decision = inspect_supabase_live_harness({})

    assert decision.enabled is False


@pytest.mark.integration
@pytest.mark.supabase_live
def test_supabase_live_harness_placeholder_is_skipped_until_later_slices() -> None:
    decision = inspect_supabase_live_harness()
    if not decision.enabled:
        pytest.skip(decision.reason)

    pytest.skip(
        "Supabase live harness skeleton only; live adapter, approved migration, "
        "and RLS validation are not implemented"
    )


def _enabled_env(**overrides: str) -> dict[str, str]:
    values = {
        OPT_IN_ENV: "1",
        MODE_ENV: "local",
        URL_ENV: PROJECT_URL,
        PUBLISHABLE_KEY_ENV: PUBLISHABLE_KEY,
        USER_A_TOKEN_ENV: USER_A_TOKEN,
        USER_B_TOKEN_ENV: USER_B_TOKEN,
    }
    values.update(overrides)
    return values
