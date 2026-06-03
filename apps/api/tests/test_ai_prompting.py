"""Tests for AI prompt assembly and diagnostic redaction."""
from __future__ import annotations

import json

from app.services.ai_prompting import (
    build_note_summarization_prompt,
    redact_diagnostic,
)


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def test_prompt_builder_keeps_raw_note_fields_provider_facing_only() -> None:
    title = "Confidential launch plan"
    content = "Keep this rollout note inside the provider prompt path only."

    prompt = build_note_summarization_prompt(
        title=title,
        content=content,
        content_type="markdown",
    )

    provider_text = prompt.as_provider_text()
    assert title in provider_text
    assert content in provider_text
    assert "Content type: markdown" in provider_text
    assert prompt.metadata.as_dict() == {
        "source_type": "note",
        "content_type": "markdown",
        "title_chars": len(title),
        "content_chars": len(content),
    }

    log_safe_text = _json_text(prompt.log_safe_metadata())
    repr_text = repr(prompt)
    for forbidden in (title, content, provider_text):
        assert forbidden not in log_safe_text
        assert forbidden not in repr_text


def test_prompt_builder_excludes_identity_and_secret_metadata() -> None:
    prompt = build_note_summarization_prompt(
        title="Roadmap summary",
        content="Prioritize offline sync reliability.",
        content_type="plain",
    )

    combined = "\n".join(
        (
            prompt.as_provider_text(),
            _json_text(prompt.log_safe_metadata()),
            repr(prompt),
        )
    )
    for forbidden in (
        "operator@example.com",
        "Jane Operator",
        "Bearer live-token",
        "OPENAI_API_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "note_internal_id_123",
        "dev_user",
    ):
        assert forbidden not in combined


def test_redact_diagnostic_masks_sensitive_keys_terms_and_token_values() -> None:
    title = "Quarterly partner note"
    content = "Private roadmap details stay out of diagnostics."
    prompt_text = (
        "SYSTEM: summarize\n\n"
        f"USER: Title: {title}\nContent: {content}"
    )
    diagnostic = {
        "note_title": title,
        "note_content": content,
        "prompt": prompt_text,
        "jwt": "synthetic-jwt-placeholder",
        "headers": {
            "Authorization": "Bearer synthetic-secret-placeholder",
        },
        "message": (
            f"{title} {content} {prompt_text} "
            "OPENAI_API_KEY placeholder "
            "SUPABASE_SERVICE_ROLE_KEY placeholder"
        ),
        "items": ["Bearer nested-placeholder"],
    }

    redacted = redact_diagnostic(
        diagnostic,
        sensitive_terms=(title, content, prompt_text),
    )
    redacted_text = _json_text(redacted)

    for forbidden in (
        title,
        content,
        prompt_text,
        "Authorization",
        "Bearer synthetic-secret-placeholder",
        "Bearer nested-placeholder",
        "OPENAI_API_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "synthetic-jwt-placeholder",
    ):
        assert forbidden not in redacted_text

    assert "[REDACTED]" in redacted_text
    assert "[REDACTED_KEY]" in redacted_text


def test_redact_diagnostic_masks_raw_payload_and_token_field_names() -> None:
    title = "Private provider diagnostics title"
    content = "Private provider diagnostics content."
    diagnostic = {
        "raw_response": {
            "body": f"Provider body echoed {title} and {content}",
            "access_token": "synthetic-access-token-placeholder",
        },
        "sdk_response": {
            "raw_body": "SDK-like raw body synthetic-sensitive-placeholder",
        },
        "provider_payload": "Provider payload synthetic-payload-placeholder",
        "identity_assertion": "synthetic-oidc-assertion-placeholder",
        "id_token": "synthetic-id-token-placeholder",
        "oidc_token": "synthetic-oidc-token-placeholder",
        "authorization_header": "Bearer synthetic-auth-placeholder",
        "nested": [
            {
                "raw_payload": f"{title} {content}",
            }
        ],
    }

    redacted = redact_diagnostic(
        diagnostic,
        sensitive_terms=(title, content),
    )
    redacted_text = _json_text(redacted)

    for forbidden in (
        title,
        content,
        "raw_response",
        "raw_body",
        "raw_payload",
        "sdk_response",
        "provider_payload",
        "identity_assertion",
        "access_token",
        "id_token",
        "oidc_token",
        "authorization_header",
        "synthetic-access-token-placeholder",
        "synthetic-sensitive-placeholder",
        "synthetic-payload-placeholder",
        "synthetic-oidc-assertion-placeholder",
        "synthetic-id-token-placeholder",
        "synthetic-oidc-token-placeholder",
        "synthetic-auth-placeholder",
    ):
        assert forbidden not in redacted_text

    assert "[REDACTED]" in redacted_text
    assert "[REDACTED_KEY]" in redacted_text
