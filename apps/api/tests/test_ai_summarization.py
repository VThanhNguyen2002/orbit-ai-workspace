"""Tests for POST /v1/ai/notes/{note_id}/summarize.

All tests are network-free.
No provider SDK or credentials required.
Memory repository only; no Supabase wiring.
"""
from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthContext, get_auth_context
from app.repositories.notes_memory import get_memory_notes_repository
from app.services.ai_summarization import get_summary_history_repository
from tests.helpers.notes_assertions import create_note as _create_note


@pytest.fixture(autouse=True)
def reset_notes_repository() -> Generator[None, None, None]:
    get_memory_notes_repository().clear()
    get_summary_history_repository().clear()
    yield
    get_memory_notes_repository().clear()
    get_summary_history_repository().clear()


@pytest.fixture
def ai_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Client with AI summarization enabled via env var."""
    monkeypatch.setenv("SYNAPSE_AI_SUMMARIZATION_ENABLED", "true")
    from app.core.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as c:
            yield c
    finally:
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Disabled by default
# ---------------------------------------------------------------------------


def test_summarize_disabled_by_default(client: TestClient) -> None:
    note = _create_note(client)

    response = client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_disabled"},
    )

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "UNPROCESSABLE"
    assert "enabled" in body["error"]["message"].lower()
    detail_messages = [d["message"] for d in body["error"]["details"]]
    assert "feature_disabled" in detail_messages


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_summarize_note_success(ai_client: TestClient) -> None:
    note = _create_note(
        ai_client,
        title="Planning session",
        content="Decisions and follow-up items from the planning session.",
    )

    response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_success"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {"request_id": "req_ai_success"}
    summary = body["data"]
    UUID(summary["id"])  # must be a valid UUID
    assert summary["source_id"] == note["id"]
    assert summary["source_type"] == "note"
    assert summary["user_id"] == "dev_user"
    assert isinstance(summary["content"], str)
    assert len(summary["content"]) > 0
    assert isinstance(summary["action_items"], list)
    assert len(summary["action_items"]) >= 1
    assert summary["provider"] == "fake"
    assert summary["model"] == "fake-model-v1"
    assert isinstance(summary["created_at"], str)


def test_summarize_note_fake_provider_is_deterministic(ai_client: TestClient) -> None:
    note = _create_note(ai_client, title="Determinism check", content="Some content.")

    resp1 = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")
    resp2 = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    s1 = resp1.json()["data"]
    s2 = resp2.json()["data"]
    # Content and action_items are identical; only generated id/created_at differ
    assert s1["content"] == s2["content"]
    assert s1["action_items"] == s2["action_items"]
    assert s1["provider"] == s2["provider"]
    assert s1["model"] == s2["model"]


def test_summarization_service_builds_provider_prompt_from_note_fields(
    ai_client: TestClient,
) -> None:
    from app.core.config import Settings
    from app.services.ai_prompting import NoteSummarizationPrompt
    from app.services.ai_summarization import (
        AiSummaryResult,
        SummarizationService,
    )
    from app.services.notes import get_note_service

    note = _create_note(
        ai_client,
        title="Provider prompt source title",
        content="Provider prompt source content.",
    )

    class CapturingProvider:
        captured_prompt: NoteSummarizationPrompt | None = None

        @property
        def provider_name(self) -> str:
            return "fake"

        @property
        def model_name(self) -> str:
            return "fake-model-v1"

        def summarize(
            self,
            *,
            source_id: str,
            prompt: NoteSummarizationPrompt,
        ) -> AiSummaryResult:
            self.captured_prompt = prompt
            return AiSummaryResult(
                id="summary-id",
                user_id="",
                source_id=source_id,
                source_type="note",
                content="summary",
                action_items=[],
                provider=self.provider_name,
                model=self.model_name,
                created_at="2026-06-01T00:00:00+00:00",
            )

    provider = CapturingProvider()
    service = SummarizationService(
        note_service=get_note_service(),
        provider=provider,
        summary_history_repository=get_summary_history_repository(),
        settings=Settings(ai_summarization_enabled=True),
    )

    result = service.summarize_note(user_id="dev_user", note_id=note["id"])

    assert result.user_id == "dev_user"
    assert provider.captured_prompt is not None
    provider_text = provider.captured_prompt.as_provider_text()
    assert note["title"] in provider_text
    assert note["content"] in provider_text
    assert note["id"] not in provider_text
    assert "dev_user" not in provider_text
    assert "Bearer " not in provider_text


# ---------------------------------------------------------------------------
# Snake_case enforcement
# ---------------------------------------------------------------------------


def test_summarize_response_uses_snake_case(ai_client: TestClient) -> None:
    note = _create_note(ai_client)
    response = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")

    assert response.status_code == 200
    summary = response.json()["data"]
    assert "source_id" in summary
    assert "source_type" in summary
    assert "action_items" in summary
    assert "created_at" in summary
    # camelCase must not appear
    assert "sourceId" not in summary
    assert "sourceType" not in summary
    assert "actionItems" not in summary
    assert "createdAt" not in summary


def test_action_items_use_snake_case(ai_client: TestClient) -> None:
    note = _create_note(ai_client, content="Content with tasks.")
    response = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")

    assert response.status_code == 200
    items = response.json()["data"]["action_items"]
    for item in items:
        assert "text" in item
        assert "priority" in item


# ---------------------------------------------------------------------------
# In-memory fake summary history
# ---------------------------------------------------------------------------


def test_summarize_note_records_fake_summary_history(ai_client: TestClient) -> None:
    note = _create_note(
        ai_client,
        title="History source note",
        content="Synthetic history source content.",
    )

    summarize_response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_history_create"},
    )
    history_response = ai_client.get(
        f"/v1/ai/notes/{note['id']}/summaries",
        headers={"x-request-id": "req_ai_history_list"},
    )

    assert summarize_response.status_code == 200
    assert history_response.status_code == 200
    summary = summarize_response.json()["data"]
    history_body = history_response.json()
    assert history_body["meta"] == {"request_id": "req_ai_history_list"}
    assert history_body["data"] == {"items": [summary]}
    assert history_body["data"]["items"][0]["provider"] == "fake"
    assert history_body["data"]["items"][0]["model"] == "fake-model-v1"


def test_repeated_fake_summaries_list_newest_first(ai_client: TestClient) -> None:
    note = _create_note(ai_client, title="Repeated history", content="Synthetic content.")

    first = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize").json()["data"]
    second = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize").json()["data"]
    history_response = ai_client.get(f"/v1/ai/notes/{note['id']}/summaries")

    assert history_response.status_code == 200
    items = history_response.json()["data"]["items"]
    assert items == [second, first]
    assert items[0]["id"] != items[1]["id"]


def test_note_detail_demo_flow_lists_fake_summaries_without_sensitive_ai_leaks(
    ai_client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    private_title = "Private launch retrospective"
    private_content = (
        "Internal decision notes with OPENAI_API_KEY, sk-demo-placeholder-token, "
        "and Bearer demo-placeholder-token examples."
    )
    note = _create_note(
        ai_client,
        title=private_title,
        content=private_content,
    )

    detail_response = ai_client.get(
        f"/v1/notes/{note['id']}",
        headers={"x-request-id": "req_demo_note_detail"},
    )
    empty_history_response = ai_client.get(
        f"/v1/ai/notes/{note['id']}/summaries",
        headers={"x-request-id": "req_demo_history_empty"},
    )
    first_summary_response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_demo_summary_first"},
    )
    second_summary_response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_demo_summary_second"},
    )
    history_response = ai_client.get(
        f"/v1/ai/notes/{note['id']}/summaries",
        headers={"x-request-id": "req_demo_history_full"},
    )

    assert detail_response.status_code == 200
    assert detail_response.json()["data"] == note
    assert empty_history_response.status_code == 200
    assert empty_history_response.json()["data"] == {"items": []}
    assert first_summary_response.status_code == 200
    assert second_summary_response.status_code == 200
    assert history_response.status_code == 200

    first_summary = first_summary_response.json()["data"]
    second_summary = second_summary_response.json()["data"]
    history_items = history_response.json()["data"]["items"]
    assert history_items == [second_summary, first_summary]
    assert {summary["source_id"] for summary in history_items} == {note["id"]}
    assert {summary["provider"] for summary in history_items} == {"fake"}
    assert {summary["model"] for summary in history_items} == {"fake-model-v1"}

    ai_surface_text = "\n".join(
        [
            empty_history_response.text,
            first_summary_response.text,
            second_summary_response.text,
            history_response.text,
            caplog.text,
        ]
    )
    for forbidden in (
        private_title,
        private_content,
        "Summarize the following note",
        "raw_response",
        "provider_payload",
        "sdk_response",
        "OPENAI_API_KEY",
        "Bearer ",
        "sk-",
    ):
        assert forbidden not in ai_surface_text


def test_summary_history_returns_empty_list_for_owned_note_without_summaries(
    ai_client: TestClient,
) -> None:
    note = _create_note(ai_client, title="No summary yet", content="Synthetic content.")

    response = ai_client.get(
        f"/v1/ai/notes/{note['id']}/summaries",
        headers={"x-request-id": "req_ai_history_empty"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {"items": []},
        "meta": {"request_id": "req_ai_history_empty"},
    }


def test_summary_history_missing_note_returns_404(ai_client: TestClient) -> None:
    response = ai_client.get(
        "/v1/ai/notes/no-such-note/summaries",
        headers={"x-request-id": "req_ai_history_missing"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    detail_messages = [d["message"] for d in body["error"]["details"]]
    assert "note_not_found" in detail_messages
    assert "no-such-note" not in response.text


def test_summary_history_cross_user_note_returns_404(ai_client: TestClient) -> None:
    ai_client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_a",
        auth_mode="dev",
    )
    note = _create_note(ai_client)
    ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")

    ai_client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_b",
        auth_mode="dev",
    )
    response = ai_client.get(
        f"/v1/ai/notes/{note['id']}/summaries",
        headers={"x-request-id": "req_ai_history_cross_user"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "This note covers key decisions" not in response.text


def test_summary_history_does_not_store_prompt_or_diagnostics(
    ai_client: TestClient,
) -> None:
    private_title = "Private history prompt title"
    private_content = "Private history prompt content must not be stored."
    note = _create_note(
        ai_client,
        title=private_title,
        content=private_content,
    )

    ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")
    response = ai_client.get(f"/v1/ai/notes/{note['id']}/summaries")

    assert response.status_code == 200
    body_text = response.text
    for forbidden in (
        private_title,
        private_content,
        "Summarize the following note",
        "raw_response",
        "provider_payload",
        "sdk_response",
        "OPENAI_API_KEY",
        "Bearer ",
        "sk-",
    ):
        assert forbidden not in body_text


# ---------------------------------------------------------------------------
# Not found / deleted / cross-user all hidden as 404
# ---------------------------------------------------------------------------


def test_summarize_missing_note_returns_404(ai_client: TestClient) -> None:
    response = ai_client.post(
        "/v1/ai/notes/no-such-note/summarize",
        headers={"x-request-id": "req_ai_missing"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    detail_messages = [d["message"] for d in body["error"]["details"]]
    assert "note_not_found" in detail_messages


def test_summarize_deleted_note_returns_404(ai_client: TestClient) -> None:
    note = _create_note(ai_client)
    ai_client.request(
        "DELETE", f"/v1/notes/{note['id']}", json={"version": note["version"]}
    )

    response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_deleted"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_summarize_cross_user_note_returns_404(ai_client: TestClient) -> None:
    ai_client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_a",
        auth_mode="dev",
    )
    note = _create_note(ai_client)
    assert note["user_id"] == "user_a"

    ai_client.app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user_id="user_b",
        auth_mode="dev",
    )
    response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_cross_user"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Input size limit
# ---------------------------------------------------------------------------


def test_summarize_over_limit_content_returns_400(ai_client: TestClient) -> None:
    # Create a valid note, then patch ai_max_input_chars lower to trigger the guard.
    from app.core.config import Settings
    from app.services.ai_prompting import NoteSummarizationPrompt
    from app.services.ai_summarization import (
        AiSummaryResult,
        SummarizationService,
    )
    from app.services.notes import get_note_service

    private_title = "Private launch retrospective"
    private_content = "SECRET_NOTE_CONTENT must stay out of public errors. " * 3
    note = _create_note(
        ai_client,
        title=private_title,
        content=private_content,
    )

    class ProviderShouldNotBeCalled:
        @property
        def provider_name(self) -> str:
            return "fake"

        @property
        def model_name(self) -> str:
            return "fake-model-v1"

        def summarize(
            self,
            *,
            source_id: str,
            prompt: NoteSummarizationPrompt,
        ) -> AiSummaryResult:
            raise AssertionError("provider must not be called for over-limit input")

    # Patch the summarization service to use limit = 50 chars
    tight_settings = Settings(
        ai_summarization_enabled=True,
        ai_max_input_chars=50,  # very tight limit to trigger 400
    )

    def _tight_service() -> SummarizationService:
        return SummarizationService(
            note_service=get_note_service(),
            provider=ProviderShouldNotBeCalled(),
            summary_history_repository=get_summary_history_repository(),
            settings=tight_settings,
        )

    from app.services.ai_summarization import get_summarization_service

    ai_client.app.dependency_overrides[get_summarization_service] = _tight_service

    response = ai_client.post(
        f"/v1/ai/notes/{note['id']}/summarize",
        headers={"x-request-id": "req_ai_too_long"},
    )

    ai_client.app.dependency_overrides.pop(get_summarization_service, None)

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    detail_messages = [d["message"] for d in body["error"]["details"]]
    assert "content_too_long" in detail_messages
    assert private_title not in response.text
    assert private_content not in response.text
    assert "Summarize the following note" not in response.text


# ---------------------------------------------------------------------------
# No secrets / no raw diagnostics in response
# ---------------------------------------------------------------------------


def test_summarize_response_contains_no_raw_diagnostics(ai_client: TestClient) -> None:
    note = _create_note(ai_client, content="Some content for summarization.")
    response = ai_client.post(f"/v1/ai/notes/{note['id']}/summarize")

    assert response.status_code == 200
    body_text = response.text
    # No token/key/prompt-style leakage expected in fake provider responses
    assert "OPENAI_API_KEY" not in body_text
    assert "Bearer " not in body_text
    assert "sk-" not in body_text
    assert "prompt" not in body_text.lower()
