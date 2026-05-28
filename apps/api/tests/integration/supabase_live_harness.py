from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field

OPT_IN_ENV = "SYNAPSE_SUPABASE_INTEGRATION_TESTS"
MODE_ENV = "SYNAPSE_SUPABASE_TEST_MODE"
URL_ENV = "SUPABASE_URL"
PUBLISHABLE_KEY_ENV = "SUPABASE_PUBLISHABLE_KEY"
ANON_KEY_ENV = "SUPABASE_ANON_KEY"
USER_A_TOKEN_ENV = "SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN"
USER_B_TOKEN_ENV = "SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN"
SERVICE_ROLE_ENV = "SUPABASE_SERVICE_ROLE_KEY"

VALID_MODES = ("local", "staging")
SYNTHETIC_PREFIX_ROOT = "synapse-live-harness"
_SAFE_COMPONENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


@dataclass(frozen=True)
class SupabaseLiveTestConfig:
    mode: str
    public_key_source: str
    supabase_url: str = field(repr=False)
    public_api_key: str = field(repr=False)
    user_a_access_token: str = field(repr=False)
    user_b_access_token: str = field(repr=False)

    def __repr__(self) -> str:
        return (
            "SupabaseLiveTestConfig("
            f"mode={self.mode!r}, "
            f"public_key_source={self.public_key_source!r}, "
            "supabase_url=<redacted>, public_api_key=<redacted>, "
            "user_a_access_token=<redacted>, user_b_access_token=<redacted>)"
        )

    __str__ = __repr__


@dataclass(frozen=True)
class SupabaseLiveHarnessDecision:
    enabled: bool
    reason: str
    missing_env: tuple[str, ...] = ()
    invalid_env: tuple[str, ...] = ()
    config: SupabaseLiveTestConfig | None = field(default=None, repr=False)

    def __repr__(self) -> str:
        return (
            "SupabaseLiveHarnessDecision("
            f"enabled={self.enabled!r}, "
            f"reason={self.reason!r}, "
            f"missing_env={self.missing_env!r}, "
            f"invalid_env={self.invalid_env!r}, "
            "config=<redacted>)"
        )

    __str__ = __repr__


def should_run_supabase_live_tests(env: Mapping[str, str] | None = None) -> bool:
    return inspect_supabase_live_harness(env).enabled


def get_supabase_live_test_config(
    env: Mapping[str, str] | None = None,
) -> SupabaseLiveTestConfig:
    decision = inspect_supabase_live_harness(env)
    if not decision.enabled or decision.config is None:
        raise RuntimeError(decision.reason)

    return decision.config


def inspect_supabase_live_harness(
    env: Mapping[str, str] | None = None,
) -> SupabaseLiveHarnessDecision:
    values = os.environ if env is None else env
    if values.get(OPT_IN_ENV) != "1":
        return SupabaseLiveHarnessDecision(
            enabled=False,
            reason=f"{OPT_IN_ENV}=1 is required to enable Supabase live tests",
        )

    mode = values.get(MODE_ENV)
    if mode not in VALID_MODES:
        return SupabaseLiveHarnessDecision(
            enabled=False,
            reason=f"{MODE_ENV} must be one of: {', '.join(VALID_MODES)}",
            invalid_env=(MODE_ENV,),
        )

    if _present(values, SERVICE_ROLE_ENV):
        return SupabaseLiveHarnessDecision(
            enabled=False,
            reason=f"{SERVICE_ROLE_ENV} is not accepted by request-path live tests",
            invalid_env=(SERVICE_ROLE_ENV,),
        )

    missing = _missing_required_env(values)
    if missing:
        return SupabaseLiveHarnessDecision(
            enabled=False,
            reason="Supabase live tests are missing required environment names",
            missing_env=missing,
        )

    public_key_source = (
        "publishable" if _present(values, PUBLISHABLE_KEY_ENV) else "anon"
    )
    public_api_key = (
        values[PUBLISHABLE_KEY_ENV]
        if public_key_source == "publishable"
        else values[ANON_KEY_ENV]
    )
    return SupabaseLiveHarnessDecision(
        enabled=True,
        reason="Supabase live tests are explicitly enabled",
        config=SupabaseLiveTestConfig(
            mode=mode,
            supabase_url=values[URL_ENV],
            public_key_source=public_key_source,
            public_api_key=public_api_key,
            user_a_access_token=values[USER_A_TOKEN_ENV],
            user_b_access_token=values[USER_B_TOKEN_ENV],
        ),
    )


def build_synthetic_note_prefix(*, run_id: str, user_label: str) -> str:
    _validate_safe_component(run_id, "run_id")
    _validate_safe_component(user_label, "user_label")
    return f"{SYNTHETIC_PREFIX_ROOT}-{user_label}-{run_id}"


def redact_live_test_config(config: SupabaseLiveTestConfig) -> str:
    return repr(config)


def _missing_required_env(values: Mapping[str, str]) -> tuple[str, ...]:
    missing: list[str] = []
    for name in (URL_ENV, USER_A_TOKEN_ENV, USER_B_TOKEN_ENV):
        if not _present(values, name):
            missing.append(name)

    if not _present(values, PUBLISHABLE_KEY_ENV) and not _present(values, ANON_KEY_ENV):
        missing.append(f"{PUBLISHABLE_KEY_ENV} or {ANON_KEY_ENV}")

    return tuple(missing)


def _present(values: Mapping[str, str], name: str) -> bool:
    return bool(values.get(name))


def _validate_safe_component(value: str, field_name: str) -> None:
    if not _SAFE_COMPONENT_RE.fullmatch(value):
        raise ValueError(
            f"{field_name} must use only lowercase letters, digits, underscores, or hyphens"
        )
