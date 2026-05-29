from __future__ import annotations

import socket
from dataclasses import dataclass

import pytest

from tests.integration.supabase_live_harness import (
    MODE_ENV,
    OPT_IN_ENV,
    PUBLISHABLE_KEY_ENV,
    SERVICE_ROLE_ENV,
    URL_ENV,
    USER_A_TOKEN_ENV,
    USER_B_TOKEN_ENV,
    inspect_supabase_live_harness,
)

PROJECT_URL = "https://project.example.invalid"
PUBLISHABLE_KEY = "publishable-placeholder-key"
USER_A_TOKEN = "synthetic-user-a-access-token"
USER_B_TOKEN = "synthetic-user-b-access-token"
SERVICE_ROLE_KEY = "service-role-placeholder-key"

SCAFFOLD_ONLY_REASON = (
    "Notes RLS validation is scaffold-only in Slice 6H-3B-4C; no live "
    "Supabase client, artifact execution approval, or applied RLS target is "
    "available in this slice"
)


@dataclass(frozen=True)
class NotesRlsValidationCase:
    case_id: str
    expected_behavior: str


RLS_VALIDATION_CASES = (
    NotesRlsValidationCase(
        case_id="user_a_selects_own_notes",
        expected_behavior="user A can select own notes",
    ),
    NotesRlsValidationCase(
        case_id="user_a_cannot_select_user_b_notes",
        expected_behavior="user A cannot select user B notes",
    ),
    NotesRlsValidationCase(
        case_id="user_a_cannot_update_user_b_notes",
        expected_behavior="user A cannot update user B notes",
    ),
    NotesRlsValidationCase(
        case_id="user_a_cannot_soft_delete_user_b_notes",
        expected_behavior="user A cannot soft-delete user B notes",
    ),
    NotesRlsValidationCase(
        case_id="insert_binds_to_authenticated_user",
        expected_behavior="insert binds to the authenticated user",
    ),
    NotesRlsValidationCase(
        case_id="include_deleted_owner_scoped",
        expected_behavior="include_deleted remains owner-scoped",
    ),
    NotesRlsValidationCase(
        case_id="no_request_path_physical_delete",
        expected_behavior="physical delete is not part of request-path CRUD",
    ),
)


def test_notes_rls_validation_cases_are_defined_without_live_clients() -> None:
    assert [case.case_id for case in RLS_VALIDATION_CASES] == [
        "user_a_selects_own_notes",
        "user_a_cannot_select_user_b_notes",
        "user_a_cannot_update_user_b_notes",
        "user_a_cannot_soft_delete_user_b_notes",
        "insert_binds_to_authenticated_user",
        "include_deleted_owner_scoped",
        "no_request_path_physical_delete",
    ]
    assert all(case.expected_behavior for case in RLS_VALIDATION_CASES)


def test_notes_rls_validation_defaults_to_disabled_without_opt_in() -> None:
    decision = inspect_supabase_live_harness({})

    assert decision.enabled is False
    assert OPT_IN_ENV in decision.reason


def test_notes_rls_validation_requires_synthetic_user_token_placeholders() -> None:
    decision = inspect_supabase_live_harness(
        {
            OPT_IN_ENV: "1",
            MODE_ENV: "local",
            URL_ENV: PROJECT_URL,
            PUBLISHABLE_KEY_ENV: PUBLISHABLE_KEY,
        }
    )

    assert decision.enabled is False
    assert USER_A_TOKEN_ENV in decision.missing_env
    assert USER_B_TOKEN_ENV in decision.missing_env


def test_notes_rls_validation_rejects_service_role_inputs() -> None:
    decision = inspect_supabase_live_harness(
        _enabled_env(**{SERVICE_ROLE_ENV: SERVICE_ROLE_KEY})
    )

    assert decision.enabled is False
    assert decision.invalid_env == (SERVICE_ROLE_ENV,)
    assert SERVICE_ROLE_KEY not in repr(decision)


def test_notes_rls_validation_default_path_makes_no_network_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    decision = inspect_supabase_live_harness({})

    assert decision.enabled is False


@pytest.mark.integration
@pytest.mark.supabase_live
def test_user_a_can_select_own_notes() -> None:
    _skip_unless_notes_rls_validation_can_execute("user_a_selects_own_notes")


@pytest.mark.integration
@pytest.mark.supabase_live
def test_user_a_cannot_select_user_b_notes() -> None:
    _skip_unless_notes_rls_validation_can_execute(
        "user_a_cannot_select_user_b_notes"
    )


@pytest.mark.integration
@pytest.mark.supabase_live
def test_user_a_cannot_update_user_b_notes() -> None:
    _skip_unless_notes_rls_validation_can_execute(
        "user_a_cannot_update_user_b_notes"
    )


@pytest.mark.integration
@pytest.mark.supabase_live
def test_user_a_cannot_soft_delete_user_b_notes() -> None:
    _skip_unless_notes_rls_validation_can_execute(
        "user_a_cannot_soft_delete_user_b_notes"
    )


@pytest.mark.integration
@pytest.mark.supabase_live
def test_insert_binds_to_authenticated_user() -> None:
    _skip_unless_notes_rls_validation_can_execute(
        "insert_binds_to_authenticated_user"
    )


@pytest.mark.integration
@pytest.mark.supabase_live
def test_include_deleted_remains_owner_scoped() -> None:
    _skip_unless_notes_rls_validation_can_execute("include_deleted_owner_scoped")


@pytest.mark.integration
@pytest.mark.supabase_live
def test_physical_delete_is_not_part_of_request_path_crud() -> None:
    _skip_unless_notes_rls_validation_can_execute(
        "no_request_path_physical_delete"
    )


def _skip_unless_notes_rls_validation_can_execute(case_id: str) -> None:
    decision = inspect_supabase_live_harness()
    if not decision.enabled:
        pytest.skip(decision.reason)

    pytest.skip(f"{case_id}: {SCAFFOLD_ONLY_REASON}")


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
