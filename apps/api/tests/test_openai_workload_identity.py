"""Tests for the mocked OpenAI Workload Identity Federation boundary.

All tests use synthetic placeholder values only. No SDK, credentials, network,
GitHub OIDC request, or live token exchange is required.
"""
from __future__ import annotations

import builtins
import json
import os
import re
import socket
import sys
from pathlib import Path
from typing import Literal

import pytest

from app.services.openai_workload_identity import (
    FakeWorkloadIdentityTokenExchanger,
    WorkloadIdentityExchangeError,
    WorkloadIdentityExchangeRequest,
    WorkloadIdentityExchangeResult,
    WorkloadIdentitySubject,
)

_ASSERTION_PLACEHOLDER = "synthetic-oidc-assertion-placeholder"
_ACCESS_TOKEN_PLACEHOLDER = "fake-wif-access-token-placeholder"
_MALFORMED_ACCESS_TOKEN_PLACEHOLDER = "fake-malformed-access-token-placeholder"
_ClaimName = Literal[
    "issuer",
    "audience",
    "subject",
    "repository",
    "ref",
    "workflow",
]


def _trusted_subject() -> WorkloadIdentitySubject:
    return WorkloadIdentitySubject(
        issuer="synthetic-ci-issuer",
        audience="synthetic-openai-wif-audience",
        subject="synthetic-main-branch-subject",
        repository="synthetic-owner/synthetic-repo",
        ref="refs/heads/main",
        workflow="ci.yml",
    )


def _subject_with(
    *,
    field_name: _ClaimName,
    field_value: str,
) -> WorkloadIdentitySubject:
    trusted_subject = _trusted_subject()
    issuer = trusted_subject.issuer
    audience = trusted_subject.audience
    subject = trusted_subject.subject
    repository = trusted_subject.repository
    ref = trusted_subject.ref
    workflow = trusted_subject.workflow

    if field_name == "issuer":
        issuer = field_value
    if field_name == "audience":
        audience = field_value
    if field_name == "subject":
        subject = field_value
    if field_name == "repository":
        repository = field_value
    if field_name == "ref":
        ref = field_value
    if field_name == "workflow":
        workflow = field_value

    return WorkloadIdentitySubject(
        issuer=issuer,
        audience=audience,
        subject=subject,
        repository=repository,
        ref=ref,
        workflow=workflow,
    )


def _request(
    *,
    subject: WorkloadIdentitySubject | None = None,
    identity_assertion: str = _ASSERTION_PLACEHOLDER,
) -> WorkloadIdentityExchangeRequest:
    return WorkloadIdentityExchangeRequest(
        identity_assertion=identity_assertion,
        subject=subject or _trusted_subject(),
    )


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def test_fake_exchanger_returns_deterministic_short_lived_placeholder_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_create_connection(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("Mocked WIF tests must not use network sockets")

    monkeypatch.setattr(socket, "create_connection", _fail_create_connection)
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
    )
    request = _request()

    result = exchanger.exchange(request)

    assert result.access_token == _ACCESS_TOKEN_PLACEHOLDER
    assert result.expires_in_seconds == 900
    assert result.token_type == "Bearer"
    assert exchanger.requests == [request]
    assert _ACCESS_TOKEN_PLACEHOLDER not in repr(result)
    assert _ASSERTION_PLACEHOLDER not in repr(request)


@pytest.mark.parametrize(
    "field_name",
    ["issuer", "audience", "subject"],
)
def test_request_requires_explicit_issuer_audience_and_subject_metadata(
    field_name: Literal["issuer", "audience", "subject"],
) -> None:
    issuer = "synthetic-ci-issuer"
    audience = "synthetic-openai-wif-audience"
    subject = "synthetic-main-branch-subject"

    if field_name == "issuer":
        issuer = " "
    if field_name == "audience":
        audience = " "
    if field_name == "subject":
        subject = " "

    with pytest.raises(ValueError) as exc_info:
        WorkloadIdentitySubject(
            issuer=issuer,
            audience=audience,
            subject=subject,
            repository="synthetic-owner/synthetic-repo",
            ref="refs/heads/main",
            workflow="ci.yml",
        )

    assert str(exc_info.value) == f"Workload identity {field_name} is required"
    assert _ASSERTION_PLACEHOLDER not in str(exc_info.value)
    assert _ASSERTION_PLACEHOLDER not in repr(exc_info.value)


def test_request_requires_explicit_identity_assertion() -> None:
    with pytest.raises(ValueError) as exc_info:
        _request(identity_assertion=" ")

    assert str(exc_info.value) == "Workload identity assertion is required"
    assert _ASSERTION_PLACEHOLDER not in str(exc_info.value)
    assert _ASSERTION_PLACEHOLDER not in repr(exc_info.value)


@pytest.mark.parametrize(
    ("field_name", "reason"),
    [
        ("issuer", "issuer_not_allowed"),
        ("audience", "audience_not_allowed"),
        ("subject", "subject_not_allowed"),
        ("repository", "repository_not_allowed"),
        ("ref", "ref_not_allowed"),
        ("workflow", "workflow_not_allowed"),
    ],
)
def test_unsupported_claim_metadata_fails_closed_without_echoing_values(
    field_name: _ClaimName,
    reason: str,
) -> None:
    unsupported_value = f"unsupported-{field_name}-placeholder"
    request = _request(
        subject=_subject_with(
            field_name=field_name,
            field_value=unsupported_value,
        )
    )
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
    )

    with pytest.raises(WorkloadIdentityExchangeError) as exc_info:
        exchanger.exchange(request)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            repr(request.subject),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert error.code == "exchange_invalid_request"
    assert reason in safe_text
    assert unsupported_value not in safe_text
    assert _ASSERTION_PLACEHOLDER not in safe_text


def test_exchange_unavailable_maps_to_safe_error() -> None:
    request = _request()
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
        mode="unavailable",
    )

    with pytest.raises(WorkloadIdentityExchangeError) as exc_info:
        exchanger.exchange(request)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert error.code == "exchange_unavailable"
    assert "exchange_unavailable" in safe_text
    assert _ASSERTION_PLACEHOLDER not in safe_text


def test_malformed_exchange_result_maps_to_safe_error() -> None:
    request = _request()
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
        mode="malformed_response",
        result=WorkloadIdentityExchangeResult(
            access_token=_MALFORMED_ACCESS_TOKEN_PLACEHOLDER,
            expires_in_seconds=0,
        ),
    )

    with pytest.raises(WorkloadIdentityExchangeError) as exc_info:
        exchanger.exchange(request)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert error.code == "exchange_invalid_response"
    assert "invalid_expires_in_seconds" in safe_text
    assert _ASSERTION_PLACEHOLDER not in safe_text
    assert _MALFORMED_ACCESS_TOKEN_PLACEHOLDER not in safe_text


def test_request_result_and_error_surfaces_exclude_token_values() -> None:
    request = _request()
    result = WorkloadIdentityExchangeResult(
        access_token=_ACCESS_TOKEN_PLACEHOLDER,
        expires_in_seconds=900,
    )
    error = WorkloadIdentityExchangeError(
        code="exchange_invalid_response",
        diagnostic={
            "reason": "synthetic_failure",
            "identity_assertion": _ASSERTION_PLACEHOLDER,
            "access_token": _ACCESS_TOKEN_PLACEHOLDER,
        },
        sensitive_terms=(
            _ASSERTION_PLACEHOLDER,
            _ACCESS_TOKEN_PLACEHOLDER,
        ),
    )
    safe_text = "\n".join(
        (
            repr(request),
            repr(request.subject),
            repr(result),
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )

    assert _ASSERTION_PLACEHOLDER not in safe_text
    assert _ACCESS_TOKEN_PLACEHOLDER not in safe_text
    assert "[REDACTED]" in safe_text


def test_wif_error_redacts_raw_assertion_and_token_field_names() -> None:
    error = WorkloadIdentityExchangeError(
        code="exchange_invalid_response",
        diagnostic={
            "raw_response": {
                "identity_assertion": _ASSERTION_PLACEHOLDER,
                "access_token": _ACCESS_TOKEN_PLACEHOLDER,
            },
            "provider_payload": "wif synthetic-provider-payload-placeholder",
        },
    )
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )

    for forbidden in (
        "raw_response",
        "identity_assertion",
        "access_token",
        "provider_payload",
        _ASSERTION_PLACEHOLDER,
        _ACCESS_TOKEN_PLACEHOLDER,
        "synthetic-provider-payload-placeholder",
    ):
        assert forbidden not in safe_text
    assert "[REDACTED]" in safe_text
    assert "[REDACTED_KEY]" in safe_text


def test_fake_exchanger_does_not_require_environment_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_getenv(_name: str, _default: str | None = None) -> str | None:
        raise AssertionError("Mocked WIF exchange must not read environment")

    monkeypatch.setattr(os, "getenv", _fail_getenv)
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
    )

    result = exchanger.exchange(_request())

    assert result.access_token == _ACCESS_TOKEN_PLACEHOLDER


def test_fake_exchanger_does_not_require_openai_sdk_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import = builtins.__import__

    def _guarded_import(
        name: str,
        globals_: object | None = None,
        locals_: object | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "openai" or name.startswith("openai."):
            raise AssertionError("OpenAI SDK import is not allowed in Slice 7J")
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    exchanger = FakeWorkloadIdentityTokenExchanger(
        trusted_subject=_trusted_subject(),
    )

    exchanger.exchange(_request())

    assert "openai" not in sys.modules


def test_synthetic_tokens_do_not_look_like_real_compact_jwts() -> None:
    compact_jwt_pattern = re.compile(
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
    )

    for token_value in (
        _ASSERTION_PLACEHOLDER,
        _ACCESS_TOKEN_PLACEHOLDER,
        _MALFORMED_ACCESS_TOKEN_PLACEHOLDER,
    ):
        assert compact_jwt_pattern.search(token_value) is None
        assert not token_value.startswith("sk-")
        assert token_value.count(".") == 0


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
