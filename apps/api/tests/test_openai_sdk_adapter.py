"""Tests for the mocked OpenAI SDK adapter boundary.

All tests use injected fake SDK-like clients only. No real SDK import,
credentials, environment lookup, or network access is required.
"""
from __future__ import annotations

import builtins
import inspect
import json
import os
import re
import socket
import sys
from dataclasses import fields
from typing import Literal

import pytest

from app.services.ai_prompting import build_note_summarization_prompt
from app.services.openai_provider import (
    OpenAIProviderRequest,
    OpenAIProviderTransportError,
)
from app.services.openai_sdk_adapter import (
    OpenAISDKActionItem,
    OpenAISDKAdapter,
    OpenAISDKAdapterError,
    OpenAISDKAdapterErrorCode,
    OpenAISDKClientRateLimitError,
    OpenAISDKClientUnavailableError,
    OpenAISDKMessage,
    OpenAISDKRequest,
    OpenAISDKResponse,
    OpenAISDKUsage,
)

FakeSDKMode = Literal["success", "timeout", "rate_limit", "unavailable"]

_AUTH_HEADER_PLACEHOLDER = "Bearer synthetic-credential-placeholder"
_UNSAFE_OUTPUT_PLACEHOLDER = f"Authorization: {_AUTH_HEADER_PLACEHOLDER}"
_API_KEY_OUTPUT_PLACEHOLDER = "openai_api_key: synthetic-api-key-placeholder"
_TOKEN_OUTPUT_PLACEHOLDER = "access token: synthetic-token-placeholder"


class FakeSDKClient:
    def __init__(
        self,
        *,
        mode: FakeSDKMode = "success",
        response: object | None = None,
        diagnostic: object | None = None,
    ) -> None:
        self._mode = mode
        self._response = response
        self._diagnostic = diagnostic
        self.requests: list[OpenAISDKRequest] = []

    def create_response(self, request: OpenAISDKRequest) -> object:
        self.requests.append(request)
        if self._mode == "timeout":
            raise TimeoutError
        if self._mode == "rate_limit":
            raise OpenAISDKClientRateLimitError(diagnostic=self._diagnostic)
        if self._mode == "unavailable":
            raise OpenAISDKClientUnavailableError(diagnostic=self._diagnostic)

        return self._response or OpenAISDKResponse(
            model="test-openai-model",
            summary_text="Synthetic SDK summary.",
            action_items=(
                OpenAISDKActionItem(
                    text="Review synthetic SDK adapter output",
                    priority="high",
                ),
            ),
            usage=OpenAISDKUsage(
                input_tokens=12,
                output_tokens=8,
                total_tokens=20,
            ),
            created_at="2026-06-03T00:00:00+00:00",
        )

    def __repr__(self) -> str:
        return (
            "FakeSDKClient("
            f"mode={self._mode!r}, "
            f"request_count={len(self.requests)})"
        )


def _provider_request(
    *,
    title: str = "Private SDK adapter planning note",
    content: str = "Provider-facing SDK prompt content must stay private.",
) -> tuple[OpenAIProviderRequest, str, str]:
    prompt = build_note_summarization_prompt(
        title=title,
        content=content,
        content_type="plain",
    )
    return (
        OpenAIProviderRequest.from_prompt(
            model="test-openai-model",
            prompt=prompt,
            max_output_tokens=128,
        ),
        title,
        content,
    )


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def test_adapter_builds_sdk_request_and_maps_success_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_create_connection(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("Mocked SDK adapter tests must not use network sockets")

    monkeypatch.setattr(socket, "create_connection", _fail_create_connection)
    provider_request, _title, _content = _provider_request()
    client = FakeSDKClient()
    adapter = OpenAISDKAdapter(
        client=client,
        timeout_seconds=17,
        request_budget=4096,
    )

    response = adapter.complete(provider_request)

    assert len(client.requests) == 1
    sdk_request = client.requests[0]
    assert sdk_request.model == "test-openai-model"
    assert sdk_request.timeout_seconds == 17
    assert sdk_request.request_budget == 4096
    assert sdk_request.max_output_tokens == 128
    assert sdk_request.prompt_metadata == provider_request.prompt_metadata
    assert [message.role for message in sdk_request.messages] == ["system", "user"]
    assert sdk_request.messages[0].content == provider_request.messages[0].content
    assert sdk_request.messages[1].content == provider_request.messages[1].content
    assert response.model == "test-openai-model"
    assert response.summary_text == "Synthetic SDK summary."
    assert response.action_items[0].text == "Review synthetic SDK adapter output"
    assert response.action_items[0].priority == "high"
    assert response.created_at == "2026-06-03T00:00:00+00:00"


def test_adapter_does_not_require_openai_sdk_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import = builtins.__import__
    previous_openai_module = sys.modules.pop("openai", None)

    def _guarded_import(
        name: str,
        globals_: object | None = None,
        locals_: object | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "openai" or name.startswith("openai."):
            raise AssertionError("OpenAI SDK import is not allowed in Slice 7M-B")
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    try:
        adapter = OpenAISDKAdapter(
            client=FakeSDKClient(),
            timeout_seconds=17,
            request_budget=4096,
        )
        provider_request, _title, _content = _provider_request()

        adapter.complete(provider_request)

        assert "openai" not in sys.modules
    finally:
        if previous_openai_module is not None:
            sys.modules["openai"] = previous_openai_module


def test_adapter_does_not_require_environment_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_getenv(_name: str, _default: str | None = None) -> str | None:
        raise AssertionError("Mocked SDK adapter must not read environment values")

    monkeypatch.setattr(os, "getenv", _fail_getenv)
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(),
        timeout_seconds=17,
        request_budget=4096,
    )
    provider_request, _title, _content = _provider_request()

    response = adapter.complete(provider_request)

    assert response.summary_text == "Synthetic SDK summary."


def test_adapter_does_not_read_environment_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingEnviron(dict[str, str]):
        def get(self, *_args: object, **_kwargs: object) -> str | None:
            raise AssertionError("Mocked SDK adapter must not inspect os.environ")

        def __getitem__(self, _key: str) -> str:
            raise AssertionError("Mocked SDK adapter must not index os.environ")

    monkeypatch.setattr(os, "environ", FailingEnviron())
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(),
        timeout_seconds=17,
        request_budget=4096,
    )
    provider_request, _title, _content = _provider_request()

    response = adapter.complete(provider_request)

    assert response.summary_text == "Synthetic SDK summary."


def test_adapter_does_not_construct_network_sockets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_socket(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("Mocked SDK adapter must not construct network sockets")

    monkeypatch.setattr(socket, "socket", _fail_socket)
    monkeypatch.setattr(socket, "create_connection", _fail_socket)
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(),
        timeout_seconds=17,
        request_budget=4096,
    )
    provider_request, _title, _content = _provider_request()

    response = adapter.complete(provider_request)

    assert response.summary_text == "Synthetic SDK summary."


@pytest.mark.parametrize(
    ("mode", "expected_code", "expected_provider_kind"),
    [
        ("timeout", "sdk_timeout", "timeout"),
        ("rate_limit", "sdk_rate_limited", "unavailable"),
        ("unavailable", "sdk_unavailable", "unavailable"),
    ],
)
def test_sdk_failures_map_to_safe_transport_errors(
    mode: FakeSDKMode,
    expected_code: OpenAISDKAdapterErrorCode,
    expected_provider_kind: str,
) -> None:
    provider_request, title, content = _provider_request(
        title="Private SDK failure note",
        content="SDK failure prompt text must be redacted.",
    )
    client = FakeSDKClient(
        mode=mode,
        diagnostic={
            "prompt": provider_request.messages[1].content,
            "headers": {"Authorization": _AUTH_HEADER_PLACEHOLDER},
            "api_key": "synthetic-api-key-placeholder",
            "access_token": "synthetic-access-token-placeholder",
            "identity_assertion": "synthetic-oidc-assertion-placeholder",
            "raw_response": {"body": provider_request.messages[1].content},
            "token": "synthetic-token-placeholder",
            "message": "OPENAI_API_KEY=synthetic-api-key-placeholder",
            "raw_user_payload": content,
        },
    )
    adapter = OpenAISDKAdapter(
        client=client,
        timeout_seconds=17,
        request_budget=4096,
    )

    with pytest.raises(OpenAISDKAdapterError) as exc_info:
        adapter.complete(provider_request)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert isinstance(error, OpenAIProviderTransportError)
    assert error.code == expected_code
    assert error.kind == expected_provider_kind
    for forbidden in (
        title,
        content,
        provider_request.messages[1].content,
        "Authorization",
        "synthetic-credential-placeholder",
        "synthetic-api-key-placeholder",
        "synthetic-access-token-placeholder",
        "synthetic-oidc-assertion-placeholder",
        "synthetic-token-placeholder",
        "OPENAI_API_KEY",
        "raw_response",
        "access_token",
        "identity_assertion",
    ):
        assert forbidden not in safe_text
    if mode != "timeout":
        assert "[REDACTED]" in safe_text
        assert "[REDACTED_KEY]" in safe_text


def test_malformed_sdk_response_maps_to_safe_error() -> None:
    provider_request, title, content = _provider_request(
        title="Private malformed SDK note",
        content="Malformed SDK response diagnostics must stay redacted.",
    )
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(response=object()),
        timeout_seconds=17,
        request_budget=4096,
    )

    with pytest.raises(OpenAISDKAdapterError) as exc_info:
        adapter.complete(provider_request)

    safe_text = _json_text(exc_info.value.safe_diagnostic())
    assert exc_info.value.code == "sdk_invalid_response"
    assert exc_info.value.kind == "malformed_response"
    assert "unexpected_response_type" in safe_text
    assert title not in safe_text
    assert content not in safe_text


@pytest.mark.parametrize(
    ("response", "expected_reason"),
    [
        (
            OpenAISDKResponse(
                model="",
                summary_text="Synthetic SDK summary.",
            ),
            "missing_model",
        ),
        (
            OpenAISDKResponse(
                model=object(),  # type: ignore[arg-type]
                summary_text="Synthetic SDK summary.",
            ),
            "invalid_model_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text=object(),  # type: ignore[arg-type]
            ),
            "invalid_summary_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                action_items=[
                    OpenAISDKActionItem(
                        text="Review synthetic SDK adapter output",
                        priority="high",
                    ),
                ],  # type: ignore[arg-type]
            ),
            "invalid_action_items_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                action_items=(object(),),  # type: ignore[arg-type]
            ),
            "unexpected_action_item_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                action_items=(
                    OpenAISDKActionItem(
                        text=object(),  # type: ignore[arg-type]
                        priority="high",
                    ),
                ),
            ),
            "invalid_action_item_text_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                action_items=(
                    OpenAISDKActionItem(
                        text="Review synthetic SDK adapter output",
                        priority="unsupported",  # type: ignore[arg-type]
                    ),
                ),
            ),
            "invalid_action_item_priority",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                usage=object(),  # type: ignore[arg-type]
            ),
            "invalid_usage_type",
        ),
        (
            OpenAISDKResponse(
                model="test-openai-model",
                summary_text="Synthetic SDK summary.",
                created_at=object(),  # type: ignore[arg-type]
            ),
            "invalid_created_at_type",
        ),
    ],
)
def test_malformed_sdk_response_fields_map_to_safe_error(
    response: OpenAISDKResponse,
    expected_reason: str,
) -> None:
    provider_request, title, content = _provider_request(
        title="Private malformed SDK field note",
        content="Malformed SDK field diagnostics must stay redacted.",
    )
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(response=response),
        timeout_seconds=17,
        request_budget=4096,
    )

    with pytest.raises(OpenAISDKAdapterError) as exc_info:
        adapter.complete(provider_request)

    safe_text = "\n".join(
        (
            str(exc_info.value),
            repr(exc_info.value),
            _json_text(exc_info.value.safe_diagnostic()),
        )
    )
    assert exc_info.value.code == "sdk_invalid_response"
    assert exc_info.value.kind == "malformed_response"
    assert expected_reason in safe_text
    assert title not in safe_text
    assert content not in safe_text
    assert provider_request.messages[1].content not in safe_text


@pytest.mark.parametrize(
    "response",
    [
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text="",
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text=_UNSAFE_OUTPUT_PLACEHOLDER,
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text=_API_KEY_OUTPUT_PLACEHOLDER,
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text=_TOKEN_OUTPUT_PLACEHOLDER,
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text="Synthetic SDK summary.",
            action_items=(
                OpenAISDKActionItem(
                    text=" ",
                    priority="high",
                ),
            ),
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text="Synthetic SDK summary.",
            action_items=(
                OpenAISDKActionItem(
                    text=_UNSAFE_OUTPUT_PLACEHOLDER,
                    priority="high",
                ),
            ),
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text="Synthetic SDK summary.",
            action_items=(
                OpenAISDKActionItem(
                    text=_API_KEY_OUTPUT_PLACEHOLDER,
                    priority="high",
                ),
            ),
        ),
        OpenAISDKResponse(
            model="test-openai-model",
            summary_text="Synthetic SDK summary.",
            action_items=(
                OpenAISDKActionItem(
                    text=_TOKEN_OUTPUT_PLACEHOLDER,
                    priority="high",
                ),
            ),
        ),
    ],
)
def test_empty_or_unsafe_output_maps_to_safe_error(
    response: OpenAISDKResponse,
) -> None:
    provider_request, title, content = _provider_request()
    adapter = OpenAISDKAdapter(
        client=FakeSDKClient(response=response),
        timeout_seconds=17,
        request_budget=4096,
    )

    with pytest.raises(OpenAISDKAdapterError) as exc_info:
        adapter.complete(provider_request)

    safe_text = "\n".join(
        (
            str(exc_info.value),
            repr(exc_info.value),
            _json_text(exc_info.value.safe_diagnostic()),
        )
    )
    assert exc_info.value.code == "sdk_invalid_response"
    assert title not in safe_text
    assert content not in safe_text
    assert "Authorization" not in safe_text
    assert "synthetic-credential-placeholder" not in safe_text
    assert "openai_api_key" not in safe_text
    assert "synthetic-api-key-placeholder" not in safe_text
    assert "access token" not in safe_text
    assert "synthetic-token-placeholder" not in safe_text


def test_request_response_and_error_surfaces_exclude_raw_prompt_content() -> None:
    provider_request, title, content = _provider_request(
        title="Private SDK repr note",
        content="SDK repr and diagnostics must not reveal this content.",
    )
    sdk_request = OpenAISDKRequest.from_provider_request(
        request=provider_request,
        timeout_seconds=17,
        request_budget=4096,
    )
    error = OpenAISDKAdapterError(
        code="sdk_invalid_response",
        diagnostic={
            "prompt": provider_request.messages[1].content,
            "raw_body": {"content": content},
        },
        sensitive_terms=(
            title,
            content,
            provider_request.messages[0].content,
            provider_request.messages[1].content,
        ),
    )
    safe_text = "\n".join(
        (
            repr(provider_request),
            repr(provider_request.messages[0]),
            repr(provider_request.messages[1]),
            repr(sdk_request),
            repr(sdk_request.messages[0]),
            repr(sdk_request.messages[1]),
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )

    assert title not in safe_text
    assert content not in safe_text
    assert provider_request.messages[0].content not in safe_text
    assert provider_request.messages[1].content not in safe_text
    assert "[REDACTED]" in safe_text


def test_adapter_error_redacts_raw_sdk_diagnostic_field_names() -> None:
    provider_request, title, content = _provider_request(
        title="Private raw SDK diagnostic note",
        content="Raw SDK diagnostic content must stay redacted.",
    )
    error = OpenAISDKAdapterError(
        code="sdk_invalid_response",
        diagnostic={
            "sdk_response": {
                "raw_body": provider_request.messages[1].content,
                "access_token": "synthetic-access-token-placeholder",
            },
            "identity_assertion": "synthetic-oidc-assertion-placeholder",
            "provider_payload": f"{title} {content}",
        },
        sensitive_terms=(
            title,
            content,
            provider_request.messages[0].content,
            provider_request.messages[1].content,
        ),
    )
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )

    for forbidden in (
        title,
        content,
        provider_request.messages[1].content,
        "sdk_response",
        "raw_body",
        "provider_payload",
        "access_token",
        "identity_assertion",
        "synthetic-access-token-placeholder",
        "synthetic-oidc-assertion-placeholder",
    ):
        assert forbidden not in safe_text
    assert "[REDACTED]" in safe_text
    assert "[REDACTED_KEY]" in safe_text


def test_credential_fields_are_not_part_of_adapter_boundaries() -> None:
    boundary_field_names = {
        field.name
        for boundary in (
            OpenAISDKRequest,
            OpenAISDKMessage,
            OpenAISDKResponse,
            OpenAISDKUsage,
        )
        for field in fields(boundary)
    }
    adapter_parameter_names = set(inspect.signature(OpenAISDKAdapter).parameters)

    for forbidden in (
        "api_key",
        "auth_header",
        "authorization",
        "credential",
        "headers",
    ):
        assert forbidden not in boundary_field_names
        assert forbidden not in adapter_parameter_names


def test_synthetic_placeholders_do_not_look_like_real_secret_values() -> None:
    compact_jwt_pattern = re.compile(
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
    )

    for value in (
        _AUTH_HEADER_PLACEHOLDER,
        _UNSAFE_OUTPUT_PLACEHOLDER,
        _API_KEY_OUTPUT_PLACEHOLDER,
        _TOKEN_OUTPUT_PLACEHOLDER,
    ):
        assert compact_jwt_pattern.search(value) is None
        assert not value.startswith("sk-")
        assert value.count(".") == 0
