"""Tests for the OpenAI provider adapter boundary.

All tests use injected fake transports only. No SDK, credentials, or network
access are required.
"""
from __future__ import annotations

import builtins
import json
import socket
import sys
from dataclasses import fields
from typing import Literal

import pytest

from app.services.ai_prompting import build_note_summarization_prompt
from app.services.openai_provider import (
    OpenAIProviderActionItem,
    OpenAIProviderError,
    OpenAIProviderErrorCode,
    OpenAIProviderRequest,
    OpenAIProviderResponse,
    OpenAIProviderTransportError,
    OpenAISummarizationProvider,
)

FakeMode = Literal["success", "timeout", "unavailable", "malformed"]


class FakeOpenAITransport:
    def __init__(
        self,
        *,
        mode: FakeMode = "success",
        response: OpenAIProviderResponse | None = None,
        diagnostic: object | None = None,
    ) -> None:
        self._mode = mode
        self._response = response or OpenAIProviderResponse(
            model="test-openai-model",
            summary_text="Synthetic OpenAI summary.",
            action_items=(
                OpenAIProviderActionItem(
                    text="Review synthetic adapter output",
                    priority="high",
                ),
            ),
            created_at="2026-06-01T00:00:00+00:00",
        )
        self._diagnostic = diagnostic
        self.requests: list[OpenAIProviderRequest] = []

    def complete(self, request: OpenAIProviderRequest) -> OpenAIProviderResponse:
        self.requests.append(request)
        if self._mode == "timeout":
            raise OpenAIProviderTransportError(
                kind="timeout",
                diagnostic=self._diagnostic,
            )
        if self._mode == "unavailable":
            raise OpenAIProviderTransportError(
                kind="unavailable",
                diagnostic=self._diagnostic,
            )
        if self._mode == "malformed":
            raise OpenAIProviderTransportError(
                kind="malformed_response",
                diagnostic=self._diagnostic,
            )

        return self._response

    def __repr__(self) -> str:
        return (
            "FakeOpenAITransport("
            f"mode={self._mode!r}, "
            f"request_count={len(self.requests)})"
        )


def _prompt(
    *,
    title: str = "Private adapter planning note",
    content: str = "Adapter prompt content must stay provider-facing only.",
):
    return build_note_summarization_prompt(
        title=title,
        content=content,
        content_type="plain",
    )


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def test_adapter_builds_request_with_injected_transport_and_no_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_create_connection(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("OpenAI adapter tests must not use network sockets")

    monkeypatch.setattr(socket, "create_connection", _fail_create_connection)
    prompt = _prompt()
    transport = FakeOpenAITransport()
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
        max_output_tokens=256,
    )

    result = provider.summarize(source_id="note_123", prompt=prompt)

    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.model == "test-openai-model"
    assert request.max_output_tokens == 256
    assert [message.role for message in request.messages] == ["system", "user"]
    assert prompt.messages[0].content == request.messages[0].content
    assert prompt.messages[1].content == request.messages[1].content
    assert prompt.metadata == request.prompt_metadata
    assert result.source_id == "note_123"
    assert result.source_type == "note"
    assert result.user_id == ""
    assert result.provider == "openai"
    assert result.model == "test-openai-model"
    assert result.content == "Synthetic OpenAI summary."
    assert result.action_items[0].text == "Review synthetic adapter output"
    assert result.action_items[0].priority == "high"


def test_adapter_does_not_require_openai_sdk_import(
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
            raise AssertionError("OpenAI SDK import is not allowed in Slice 7G")
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    transport = FakeOpenAITransport()
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
    )

    provider.summarize(source_id="note_123", prompt=_prompt())

    assert "openai" not in sys.modules


def test_request_and_error_surfaces_exclude_prompt_and_credentials() -> None:
    title = "Private board memo"
    content = "Raw note content should never appear in diagnostics."
    prompt = _prompt(title=title, content=content)
    request = OpenAIProviderRequest.from_prompt(
        model="test-openai-model",
        prompt=prompt,
        max_output_tokens=None,
    )
    field_names = {field.name for field in fields(OpenAIProviderRequest)}
    safe_text = "\n".join(
        (
            repr(request),
            repr(request.messages[0]),
            repr(request.messages[1]),
            _json_text(request.log_safe_metadata()),
        )
    )

    assert "authorization" not in field_names
    assert "api_key" not in field_names
    assert "credential" not in field_names
    assert "headers" not in field_names
    for forbidden in (
        title,
        content,
        prompt.as_provider_text(),
        "provider-key-placeholder",
        "Bearer provider-token-placeholder",
    ):
        assert forbidden not in safe_text


@pytest.mark.parametrize(
    ("mode", "expected_code"),
    [
        ("timeout", "provider_timeout"),
        ("unavailable", "provider_unavailable"),
    ],
)
def test_transport_failures_map_to_safe_provider_errors(
    mode: FakeMode,
    expected_code: OpenAIProviderErrorCode,
) -> None:
    title = "Private timeout note"
    content = "Transport failure content must be redacted."
    prompt = _prompt(title=title, content=content)
    transport = FakeOpenAITransport(
        mode=mode,
        diagnostic={
            "prompt": prompt.as_provider_text(),
            "message": content,
            "headers": {"Authorization": "Bearer provider-token-placeholder"},
            "api_key": "provider-key-placeholder",
        },
    )
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
    )

    with pytest.raises(OpenAIProviderError) as exc_info:
        provider.summarize(source_id="note_123", prompt=prompt)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert error.code == expected_code
    for forbidden in (
        title,
        content,
        prompt.as_provider_text(),
        "Authorization",
        "provider-token-placeholder",
        "provider-key-placeholder",
    ):
        assert forbidden not in safe_text
    assert "[REDACTED]" in safe_text
    assert "[REDACTED_KEY]" in safe_text


def test_malformed_transport_response_maps_to_safe_provider_error() -> None:
    prompt = _prompt(
        title="Private malformed note",
        content="Malformed provider content must stay redacted.",
    )
    transport = FakeOpenAITransport(
        mode="malformed",
        diagnostic={
            "raw_response": prompt.as_provider_text(),
            "headers": {"Authorization": "Bearer provider-token-placeholder"},
        },
    )
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
    )

    with pytest.raises(OpenAIProviderError) as exc_info:
        provider.summarize(source_id="note_123", prompt=prompt)

    safe_text = _json_text(exc_info.value.safe_diagnostic())
    assert exc_info.value.code == "provider_invalid_response"
    assert prompt.as_provider_text() not in safe_text
    assert "provider-token-placeholder" not in safe_text


def test_transport_diagnostics_redact_raw_payload_and_token_fields() -> None:
    title = "Private raw provider payload note"
    content = "Raw provider payload content must stay redacted."
    prompt = _prompt(title=title, content=content)
    transport = FakeOpenAITransport(
        mode="unavailable",
        diagnostic={
            "raw_response": {
                "body": prompt.as_provider_text(),
                "access_token": "synthetic-access-token-placeholder",
            },
            "provider_payload": f"{title} {content}",
            "identity_assertion": "synthetic-oidc-assertion-placeholder",
            "headers": {"Authorization": "Bearer provider-token-placeholder"},
        },
    )
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
    )

    with pytest.raises(OpenAIProviderError) as exc_info:
        provider.summarize(source_id="note_123", prompt=prompt)

    error = exc_info.value
    safe_text = "\n".join(
        (
            str(error),
            repr(error),
            _json_text(error.safe_diagnostic()),
        )
    )
    assert error.code == "provider_unavailable"
    for forbidden in (
        title,
        content,
        prompt.as_provider_text(),
        "raw_response",
        "provider_payload",
        "identity_assertion",
        "access_token",
        "Authorization",
        "synthetic-access-token-placeholder",
        "synthetic-oidc-assertion-placeholder",
        "provider-token-placeholder",
    ):
        assert forbidden not in safe_text
    assert "[REDACTED]" in safe_text
    assert "[REDACTED_KEY]" in safe_text


def test_empty_summary_response_maps_to_safe_provider_error() -> None:
    prompt = _prompt(
        title="Private empty summary note",
        content="Empty summary diagnostics must not leak prompt text.",
    )
    transport = FakeOpenAITransport(
        response=OpenAIProviderResponse(
            model="test-openai-model",
            summary_text="",
            action_items=(),
            created_at="2026-06-01T00:00:00+00:00",
        ),
    )
    provider = OpenAISummarizationProvider(
        transport=transport,
        model="test-openai-model",
    )

    with pytest.raises(OpenAIProviderError) as exc_info:
        provider.summarize(source_id="note_123", prompt=prompt)

    safe_text = _json_text(exc_info.value.safe_diagnostic())
    assert exc_info.value.code == "provider_invalid_response"
    assert prompt.as_provider_text() not in safe_text
    assert "Empty summary diagnostics" not in safe_text
