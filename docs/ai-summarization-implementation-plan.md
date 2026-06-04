# AI Summarization Implementation Plan

## Slice 7A — Docs-First Planning

Date: 2026-05-30

---

## 1. Objective

Plan the end-to-end AI summarization feature for Synapse Notes without
implementing any provider runtime code, adding credentials, calling APIs, or
changing public Notes behavior. This document is the source of truth for all
downstream AI summarization implementation slices (7B and later provider
integration slices).

---

## 2. Non-Goals (This Plan)

This plan explicitly excludes:

- Real OpenAI / Groq / Gemini API calls.
- Provider SDK integration or credential wiring.
- `OPENAI_API_KEY`, `.env` files, or any credentials in the repo.
- Vector embeddings and semantic search integration.
- Frontend / Expo UI screens.
- Supabase / RLS work (paused — see
  [notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md)).
- Production deployment.
- Background / automatic summarization without explicit user action.
- Fine-tuned models.

---

## 3. Current Baseline

### Shared AI Contracts (`packages/shared/src/ai/index.ts`)

All core wire contracts already exist and are registered in the schema registry:

| Schema | Status | Notes |
|---|---|---|
| `SummarizeRequestSchema` | ✅ Exists | `source_id`, `source_type`, `content` (max 50k), `max_sentences` |
| `SummarizeResponseSchema` | ✅ Exists | `summary`, `action_items[]` |
| `AiUsageSchema` | ✅ Exists | `provider`, `model`, `input_tokens`, `output_tokens`, `estimated_cost_usd`, `operation` |
| `AiStreamTokenEventSchema` | ✅ Exists | SSE `token` event |
| `AiStreamActionItemsEventSchema` | ✅ Exists | SSE `action_items` event |
| `AiStreamDoneEventSchema` | ✅ Exists | SSE `done` event with optional `summary_id` and `usage` |
| `AiStreamErrorEventSchema` | ✅ Exists | SSE `error` event with `code`, `message`, `retryable` |
| `AiStreamEventSchema` | ✅ Exists | discriminated union of all SSE events |
| `SemanticSearchRequestSchema` | ✅ Exists | (deferred — semantic search is out of scope) |

### Domain Types (`packages/shared/src/domain/index.ts`)

| Type | Status |
|---|---|
| `SummarySchema` | ✅ Exists — `id`, `user_id`, `source_id`, `source_type`, `content`, `action_items[]`, `provider`, `model`, `created_at` |
| `SummaryActionItemSchema` | ✅ Exists — `text`, `priority` |
| `SummarySourceTypeSchema` | ✅ Exists — `"note" \| "transcript"` |

### Architecture (`docs/architecture/ai-integration.md`)

- AI is a **backend-only concern** — client never calls providers directly.
- `LLMProvider` abstract base class defined (Python).
- Provider selection is config-driven (`llm_provider` setting).
- Summarization flow: fetch note → stream LLM → extract action items → SSE to client.
- System prompt format defined (summary + `---ACTION_ITEMS---` + JSON array).
- Streaming: SSE token events → `action_items` event → `done` event.
- Token chunking strategy defined for long content.
- Cost tracking via `AIUsage` dataclass.

### Backend Status

- Memory-only `NotesRepository` is current default.
- Supabase live wiring deferred.
- Auth: RS256 JWT verifier implemented; JWKS not yet wired for live Supabase.
- No AI routes implemented yet.

### API Client Status

- Notes CRUD client methods exist.
- No AI summarization client methods yet.

---

## 4. User-Facing Feature Concept

When an operator enables AI summarization (opt-in, user-initiated only):

1. **Summarize one note** — user taps "Summarize" on a note; receives streamed
   summary and extracted action items. Original note content is never modified.
2. **Summary stored** — result persists as a `Summary` entity linked to the
   source note. Subsequent calls for unchanged notes may return the cached summary
   (Phase 2 caching, not in scope now).
3. **User-owned isolation** — only the authenticated owner of a note may
   request its summarization. No cross-user access.
4. **Action items** — optional list of concrete, prioritized tasks extracted from
   the note. User may choose to promote them to `Task` entities later.
5. **Streaming** — summary text appears token-by-token for immediate feedback.

Explicitly not in scope: auto-summarize on save, batch background summarization,
cross-note summarization, summarization in offline mode.

---

## 5. API Contract Plan

### Endpoints (Planning Only — Not Implemented)

```
POST /v1/ai/notes/{note_id}/summarize
```

Request body: matches `SummarizeRequestSchema` with `source_type = "note"`.
Alternatively: body may be omitted for the note-level route (API fetches content).

```
POST /v1/ai/notes/summarize-batch        (deferred — Phase 2)
```

Response: **Server-Sent Events (SSE)** stream using `AiStreamEventSchema`.

### SSE Event Sequence

```
data: {"event": "token", "data": {"text": "This note discusses..."}}
data: {"event": "token", "data": {"text": " Q3 planning goals."}}
data: {"event": "action_items", "data": {"items": [{"text": "...", "priority": "high"}]}}
data: {"event": "done", "data": {"summary_id": "uuid", "usage": {...}}}
```

Error path:

```
data: {"event": "error", "data": {"code": "provider_unavailable", "message": "...", "retryable": true}}
```

### HTTP Conventions

- Method: `POST` (summarization is a write + compute operation).
- Content-Type response: `text/event-stream`.
- Auth: `Authorization: Bearer <user-jwt>` required.
- 404 if `note_id` does not belong to authenticated user (no 403 — prevent enumeration).
- 400 if content exceeds `max_content_length` policy.
- 503 if provider unavailable.
- 429 if rate limit exceeded.

---

## 6. Shared Contract Gap Analysis

All wire contracts for summarization already exist (section 3). Gap contracts
needed for the API-level HTTP envelope:

| Contract | Status | Action |
|---|---|---|
| `SummarizeNoteResponseEnvelope` | Deferred for streaming — SSE bypasses envelope | No new schema needed |
| `SummarizeErrorResponse` | Covered by existing `ApiErrorEnvelopeSchema` | No new schema needed |
| `SummarizeBatchRequest` | Not scoped (Phase 2) | Skip |
| `GetSummaryRequest` / `GetSummaryResponse` | Not yet in registry | Add in Slice 7B |

Slice 7B should register `get_summary_response` entry using the existing
`SummarySchema` wrapped in `createApiSuccessEnvelopeSchema`.

---

## 7. Backend Architecture Plan

```
apps/api/app/
├── routers/
│   └── ai.py                    # POST /v1/ai/notes/{note_id}/summarize
├── services/
│   └── ai/
│       ├── base.py              # LLMProvider ABC (already in architecture doc)
│       ├── fake_provider.py     # Deterministic fake — returns canned text, no network
│       ├── openai_provider.py   # Deferred (Slice 7F)
│       ├── summarization_service.py  # Orchestrates: auth → fetch → build prompt → stream
│       └── prompt_builder.py    # Builds system prompt; unit testable with synthetic content
└── core/
    └── config.py               # Add: llm_provider, llm_model, summarize_max_content_len
```

Layer boundaries:

| Layer | Responsibility | Must Not |
|---|---|---|
| Router | parse path params, auth context, stream response | touch provider |
| Service | orchestrate note fetch, ownership check, size check, call provider | log content |
| Prompt builder | construct system prompt + user content | include user identity in prompt |
| Provider interface | `LLMProvider` ABC — `complete()` / `stream()` | depend on HTTP session |
| Fake provider | return deterministic canned output | make network calls |
| OpenAI provider | call OpenAI API (deferred) | run in CI without explicit flag |

Redaction boundary: logs may record `note_id`, `user_id` (UUID only), `provider`,
`model`, `input_tokens`, `output_tokens`. Logs must never record note content,
prompt text, token values, API keys, or bearer tokens.

---

## 8. Provider / Auth Strategy

### Phase-by-Phase Provider Plan

| Phase | Provider | Credential | When |
|---|---|---|---|
| Now (Slice 7C) | `FakeProvider` | None | Default for dev/CI |
| Slice 7F | OpenAI | Workload Identity Federation (preferred for CI/cloud) | When live test needed |
| Slice 7F fallback | OpenAI | `OPENAI_API_KEY` env var (gitignored, local only) | When WIF not available |
| Phase 3+ | Groq / Gemini | Config-driven, same pattern | When cost optimisation needed |

### Credential Rules

- `OPENAI_API_KEY` (and any provider key) must never be committed.
- `.env` files must be gitignored and `gitleaks` clean.
- CI must not require any live provider key. All CI tests use `FakeProvider`.
- Workload Identity Federation (WIF) is the preferred credential method for
  GCP/cloud deployments because it eliminates long-lived keys.
- Service-role key is never used on the summarization request path.

### Settings Additions (Planned for Slice 7C)

```python
# apps/api/app/core/config.py additions
llm_provider: Literal["fake", "openai", "groq", "gemini"] = "fake"
llm_model: str = "gpt-4o-mini"
summarize_max_content_len: int = 50_000  # matches SummarizeRequestSchema
summarize_enabled: bool = False          # opt-in flag; default off
```

---

## 9. Privacy / Security Rules

These rules apply to every AI summarization implementation slice:

| Rule | Requirement |
|---|---|
| Content logging | Never log note content, prompt text, or AI response text |
| Token / key logging | Never log bearer tokens, API keys, or auth headers |
| User identity in prompts | Never include email or display name in prompts |
| Ownership check | Verify `note.user_id == auth_context.user_id` before any AI call |
| Service-role path | Never use service-role credential on the summarization request path |
| Request size limit | Reject if content > `summarize_max_content_len` (default 50k chars) |
| Output validation | Validate AI response structure before sending to client |
| Rate limiting | Plan per-user rate limit (Slice 7E or 7F); enforce before provider call |
| Abuse / cost guardrails | Hard budget ceiling per user per day (Phase 2); log usage always |
| Diagnostic redaction | Error responses include only error code and coarse message; no content |
| No background processing | Summarization is always user-initiated; no auto-summarize on save |

Inherited from `docs/security/privacy-and-data-handling.md`:

- No PII in prompts.
- Only use providers with data-retention opt-out.
- AI calls logged with timestamp, model, token count — not content.
- Auth token not logged in any path.

---

## 10. Cost / Token Strategy

| Concern | Plan |
|---|---|
| Input size limit | `summarize_max_content_len = 50_000` chars (≈ 12,500 tokens) |
| Truncation | If content > limit: reject with 400 (Phase 1); chunking in Phase 2 |
| Token counting | Estimate using word count × 1.3 (same as embedding strategy) |
| Usage tracking | Record `AiUsage` after every provider call (provider, model, in/out tokens, cost_usd) |
| Cost visibility | Usage logged to structured log; Phase 2 stores aggregate to DB |
| Budget guardrail | Hard daily per-user limit (Phase 2); Phase 1 relies on rate limiting |
| Caching | Phase 2 — skip re-summarize if content hash unchanged and model unchanged |
| No hidden cost | Summarization requires explicit user action every time in Phase 1 |

---

## 11. Testing Strategy

All tests are network-free by default. Live provider tests require explicit
opt-in environment variable and never run in default CI.

| Test Layer | What | How |
|---|---|---|
| Shared contract tests | Schema shape, parse/serialize, round-trip | `contracts:check` Zod parse tests |
| Prompt builder unit tests | System prompt format, synthetic content only | pytest, no network |
| Fake provider tests | Canned output, streaming events, action item extraction | pytest, no network |
| Router / service tests | Auth enforcement, ownership check, size check, SSE event sequence | pytest with fake provider |
| API client tests | Client serializes request, deserializes SSE events | jest/vitest, no network |
| Security tests | Missing auth → 401, wrong user → 404, content too long → 400, key not logged | pytest |
| Log redaction tests | Assert content / tokens do not appear in structured log output | pytest |
| Live provider tests | Real OpenAI call | Opt-in via env var, not in default CI |

---

## 12. Failure Modes

| Failure | Detection | Response |
|---|---|---|
| Provider unavailable | `ConnectionError` / non-2xx from provider | SSE `error` event: `provider_unavailable`, `retryable: true`; 503 fallback |
| Provider timeout (30 s) | `asyncio.TimeoutError` | Retry once; then SSE `error`: `provider_timeout`, `retryable: true` |
| Malformed AI response | Parse failure after stream completes | SSE `error`: `invalid_response`, `retryable: false` |
| Over-limit input | `len(content) > max_content_len` | 400 before any provider call |
| Unauthorized / wrong user | `note.user_id != auth.user_id` | 404 (do not leak existence) |
| Missing auth | No / invalid bearer token | 401 |
| Rate limit | Provider 429 | SSE `error`: `rate_limit`, `retryable: true`; respect `Retry-After` |
| Budget exceeded | Per-user daily limit hit | 429 with `Retry-After` header |
| Unsafe output | Content policy violation from provider | SSE `error`: `content_policy`, `retryable: false` |

---

## 13. Future Slices

| Slice | Goal |
|---|---|
| **7B** | AI summarization shared contracts — register `get_summary_response` in schema registry; add API client summarization types |
| **7C** | Backend fake-provider summarization route skeleton — `POST /v1/ai/notes/{id}/summarize`, `FakeProvider`, SSE streaming, auth + ownership + size checks |
| **7D** | API client summarization methods — `summarizeNote()`, SSE event parser, typed events |
| **7E** | Prompt builder and redaction tests — `prompt_builder.py`, log-redaction assertions, security tests |
| **7F** | OpenAI provider integration planning — provider boundary, credential/WIF strategy, testing plan, safety gate |
| **7G** | OpenAI provider adapter interface and fake transport tests |
| **7H** | OpenAI config and credential-mode validation |
| **7I** | Workload Identity Federation planning/approval record |
| **7J** | Mocked WIF token exchange boundary tests |
| **7K** | OpenAI provider live harness planning |
| **7L** | OpenAI live harness approval record |
| **7L-A** | Deny local-only live harness approval until prerequisites exist |
| **7L-B** | Resolve live harness approval prerequisites |
| **7L-C** | Grant or deny local-only live harness approval with evidence |
| **7L-D** | Prepare OpenAI live harness approval evidence packet |
| **7L-E** | Fill approval evidence packet with reviewer decisions |
| **7L-F** | Resolve missing OpenAI live harness approval evidence (required-action records) |
| **7L-G** | Collect explicit reviewer approvals or close live harness path *(Complete — CLOSED / BLOCKED, 0/8 approvals)* |
| **7M** | OpenAI SDK adapter planning — docs-only, no credentials *(Complete — plan added, no SDK, approval DENIED)* |
| **7M-A** | OpenAI SDK dependency review packet — docs-only, no installation *(Complete — packet added, dependency NOT APPROVED)* |
| **7M-B** | Mocked SDK adapter interface tests without SDK dependency *(Complete — fake-only boundary added, not runtime-wired)* |
| **7M-C** | SDK dependency approval or denial record *(Complete — NOT APPROVED / DENIED, all 12 gates MISSING)* |
| **7M-D** | Resolve OpenAI SDK dependency approval prerequisites — docs-only *(Complete — all 12 gates PREPARED / STILL NOT APPROVED)* |
| **7M-E** | Re-evaluate SDK dependency approval with evidence *(Complete — all evidence missing, decision remains NOT APPROVED / DENIED)* |
| **7M-F** | Optional SDK dependency install — only if approved by 7M-H |
| **7M-G** | Keep mocked adapter path dependency-free *(Complete — Record: `docs/openai-sdk-dependency-free-strategy.md`)* |
| **7M-H** | Dependency-free OpenAI adapter hardening plan *(Complete — Record: `docs/openai-sdk-adapter-hardening-plan.md`)* |
| **7M-I** | Provider boundary cleanup/refactor planning *(Complete — Record: `docs/openai-provider-boundary-cleanup-plan.md`)* |
| **7M-J** | Dependency-free adapter hardening tests *(Complete — stricter SDK-like response validation and redaction/no-network/no-env tests)* |
| **7M-K** | Redaction and diagnostics audit for AI provider boundary *(Complete — Record: `docs/openai-provider-redaction-diagnostics-audit.md`)* |
| **7M-L** | Provider boundary cleanup/refactor implementation |
| **7N** | Opt-in live provider harness skeleton — only after all 8 approvals exist |
| **8A** | Backend AI summary history with fake provider only |
| **8B** | Summary history API client contract/client integration *(Complete — client method and tests added)* |
| **8C** | Summary history UI/API consumption planning or backend persistence planning |

### Slice 7E Update — 2026-06-01

Slice 7E adds a backend-only prompt boundary in
`apps/api/app/services/ai_prompting.py`. The summarization service now builds a
provider-facing prompt from explicit note `title`, `content`, and bounded note
metadata before calling the provider. Raw note fields stay out of prompt object
reprs and log-safe metadata.

The same module adds diagnostic redaction for sensitive keys, note title/content
terms, prompt text, bearer/JWT-like values, provider API keys, and Supabase key
names. Tests cover prompt assembly, safe metadata, redaction, over-limit
rejection before provider calls, public error leakage, and continued fake
provider response compatibility.

No OpenAI SDK, provider credential, `.env` file, SSE streaming, frontend, SQL,
migration, Supabase validation, new backend route, or API client method was
added. Slice 7F remains planning-only for OpenAI provider integration.

### Slice 7F Update — 2026-06-01

Slice 7F adds the docs-only
[OpenAI provider integration plan](openai-provider-integration-plan.md). The
plan defines the future provider adapter boundary, fake-provider default,
config-driven provider selection, credential and Workload Identity Federation
strategy, request/response safety rules, provider failure mapping, testing
strategy, cost/token guardrails, and future slices.

No runtime provider code, OpenAI SDK, provider dependency, credential, `.env`
file, API call, WIF runtime, SSE streaming, frontend, SQL, migration, Supabase
state, backend route behavior, or API client method was added. Slice 7G should
start with provider adapter interface work and fake transport tests only.

### Slice 7G Update — 2026-06-01

Slice 7G adds a backend-only OpenAI provider adapter boundary in
`apps/api/app/services/openai_provider.py`. The boundary defines internal
request/response DTOs, an injected transport protocol, safe provider errors, and
fake-transport test coverage. It is not selected by runtime configuration and is
not wired into `POST /v1/ai/notes/{note_id}/summarize`.

No OpenAI SDK, provider dependency, credential, `.env` file, API call, WIF
runtime, SSE streaming, frontend, SQL, migration, Supabase state, backend route
behavior, or API client method was added. Slice 7H should validate future
OpenAI config and credential-mode settings without enabling live provider calls.

### Slice 7H Update — 2026-06-01

Slice 7H adds safe OpenAI configuration shape and validation in
`apps/api/app/core/config.py`. Defaults remain `ai_provider="fake"`,
`openai_auth_mode="fake"`, summarization disabled, and credential-free. Unknown
AI provider and OpenAI auth mode values fail closed, while `api_key` and
`workload_identity` modes are rejected by runtime validation until future
approved slices implement those credential paths.

No OpenAI SDK, provider dependency, credential, `.env` file, API call, WIF
runtime, SSE streaming, frontend, SQL, migration, Supabase state, backend route
behavior, or API client method was added. Slice 7I should produce the Workload
Identity Federation planning/approval record only.

### Slice 7I Update — 2026-06-01

Slice 7I adds the docs-only
[OpenAI Workload Identity approval record](openai-workload-identity-approval-record.md).
The record documents future WIF candidate environments, approval requirements,
GitHub Actions checklist, security risks, fake-only testing strategy, and
decision status.

WIF remains preferred for future CI/cloud provider authentication where
supported, but WIF runtime is not approved for implementation yet. API-key
fallback is not approved for production. No SDK, credential, token exchange,
API call, workflow configuration, route behavior, frontend, SQL, migration, or
Supabase work was added.

### Slice 7J Update — 2026-06-01

Slice 7J adds a mocked, network-free WIF token exchange boundary in
`apps/api/app/services/openai_workload_identity.py`. It defines typed subject
metadata, request/result objects, an exchanger protocol, fake exchanger, and
safe errors for invalid or unavailable exchange outcomes.

The boundary performs no real token exchange, reads no environment credentials,
requests no GitHub OIDC token, imports no OpenAI SDK, makes no network calls,
and is not wired into provider selection, routes, GitHub Actions, frontend, or
API clients.

### Slice 7K Update — 2026-06-02

Slice 7K adds the docs-only
[OpenAI live provider harness plan](openai-live-provider-harness-plan.md). The
plan describes a future optional live OpenAI provider validation harness with
explicit opt-in variables, fake-only default CI, synthetic-prompt-only live test
boundaries, credential handling rules, redaction/logging requirements,
safety-stop conditions, cost/token guardrails, and approval requirements.

No live harness, SDK, credential, `.env` file, real provider call, WIF runtime,
token exchange, GitHub Actions WIF wiring, route behavior, API client behavior,
SSE/frontend work, SQL, migration, Supabase state, or generated state was added.
Slice 7L should produce the live harness approval record only.

### Slice 7L Update — 2026-06-02

Slice 7L adds the docs-only
[OpenAI live harness approval record](openai-live-harness-approval-record.md).
The record keeps live harness execution status pending/not granted, documents a
candidate local-only synthetic smoke-test scope that is not yet granted, and
defines required approvals, pre-execution checklist, credential constraints,
stop conditions, evidence requirements, and WIF separation.

No live OpenAI API call, SDK implementation, credential use, WIF runtime,
default CI live test, GitHub Actions WIF wiring, route behavior switch,
background summarization, persisted live provider output, SQL, migration,
Supabase state, frontend work, SSE, or API client change is approved or added.
Slice 7L-A should record the local-only approval decision only.

### Slice 7L-A Update — 2026-06-02

Slice 7L-A updates the
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
to record that local-only live harness approval is not granted. The denial is
based on missing explicit security/privacy approval, cost/budget approval,
credential-mode approval, redaction evidence format, rollback/disable plan, and
local-only execution checklist evidence.

The candidate local-only scope remains documented but unauthorized. The next
approval path is Slice 7L-B to resolve prerequisites, then Slice 7L-C to grant
or deny local-only approval with evidence. No SDK, credential, live API call,
live harness, WIF runtime, token exchange, workflow wiring, route behavior, API
client behavior, SSE/frontend work, SQL, migration, Supabase state, or persisted
live provider output is approved or added.

### Slice 7L-B Update — 2026-06-02

Slice 7L-B adds the docs-only
[OpenAI live harness prerequisites](openai-live-harness-prerequisites.md)
packet. It prepares prerequisite checklists for security/privacy, cost/budget,
credential mode, redacted evidence, rollback/disable, no-default-CI proof, and
the local-only execution boundary.

Approval remains not granted. No SDK, credential, live API call, live harness,
WIF runtime, token exchange, workflow wiring, route behavior, API client
behavior, SSE/frontend work, SQL, migration, Supabase state, or persisted live
provider output is approved or added. Slice 7L-C should grant or deny
local-only approval with evidence only.

### Slice 7L-C Update — 2026-06-02

Slice 7L-C updates the
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
with an evidence checklist and records the decision as denied/not granted. The
review finds the redacted evidence template and fail-closed config proof
present, but security/privacy approval, cost/budget approval, credential-mode
decision, synthetic prompt fixture, rollback/disable plan, no-default-CI proof,
local-only boundary evidence, and external review sign-off are missing or
insufficient.

No SDK, credential, live API call, live harness, WIF runtime, token exchange,
workflow wiring, route behavior, API client behavior, SSE/frontend work, SQL,
migration, Supabase state, or persisted live provider output is approved or
added. Slice 7L-D should prepare the missing approval evidence packet only.

### Slice 7L-D Update — 2026-06-02

Slice 7L-D adds the docs-only
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md).
The packet prepares a future evidence matrix, reviewer placeholders,
security/privacy review requirements, placeholder-only cost/budget labels,
credential-mode comparison, synthetic prompt fixture requirements, redacted
report format, rollback/disable requirements, no-default-CI proof requirements,
local-only boundary evidence requirements, and a future approval path.

Approval remains denied/not granted. No SDK, credential, live API call, live
harness, WIF runtime, token exchange, workflow wiring, route behavior, API
client behavior, SSE/frontend work, SQL, migration, Supabase state, or persisted
live provider output is approved or added. Slice 7L-E should fill the evidence
packet with reviewer decisions only.

### Slice 7L-E Update — 2026-06-02

Slice 7L-E fills the
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
with explicit reviewer decision sections and a final evidence decision matrix.
2 of 10 evidence items are PRESENT; 4 are MISSING; 4 are INSUFFICIENT; 0 have
been approved by a named reviewer. Approval remains denied/not granted and no
live execution or credential use is approved.

### Slice 7L-F Update — 2026-06-02

Slice 7L-F converts each MISSING and INSUFFICIENT evidence item in the
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
into a concrete required-action record. 8 items are now `PREPARED / STILL NOT
APPROVED`; 2 remain PRESENT. `PREPARED / STILL NOT APPROVED` is not an
approval state. Approval remains denied/not granted and no live execution or
credential use is approved.

### Slice 7L-G Update — 2026-06-02

Slice 7L-G reviewed the evidence packet and approval record to determine
whether named reviewer approvals exist. **0 of 8 required named approvals
exist.** All eight `TBD_*` reviewer slots remain placeholder-only. Decision:
**CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**. Approval remains denied/not
granted and no live execution or credential use is approved. The live harness
path may be reopened if named reviewers provide explicit sign-off per sections
5.1–5.8 of the evidence packet.

### Slice 7M Update — 2026-06-03

Slice 7M adds the docs-only
[OpenAI SDK adapter plan](openai-sdk-adapter-plan.md). The plan covers the
future SDK adapter boundary, injectable transport design, credential
constraints, runtime selection rules, test strategy, failure modes, cost/token
guardrails, approval gates, and recommended follow-up slices.

No SDK installation, credential use, OpenAI API call, live harness execution,
WIF runtime, token exchange, workflow change, default CI live test, route
behavior switch, API client change, SSE/frontend work, SQL, migration, Supabase
work, or persisted live provider output is approved or added. Approval remains
denied/not granted. Fake provider remains the default.

### Slice 7M-A Update — 2026-06-03

Slice 7M-A adds the docs-only
[OpenAI SDK dependency review packet](openai-sdk-dependency-review-packet.md).
The packet covers supply-chain risk, runtime risk, credential/security
constraints, testing plan, CI impact checklist, dependency approval gates, and
decision status for a future `openai` Python SDK dependency.

No SDK installation, dependency manifest change, lockfile change, credential
use, live API call, runtime import, WIF runtime, token exchange, route behavior
switch, API client change, SSE/frontend work, SQL, migration, Supabase work, or
generated state is approved or added. **OpenAI SDK dependency decision: NOT
APPROVED.** Fake provider remains the default.

### Slice 7M-B Update — 2026-06-03

Slice 7M-B adds a mocked SDK adapter boundary in
`apps/api/app/services/openai_sdk_adapter.py` and tests in
`apps/api/tests/test_openai_sdk_adapter.py`.

The boundary uses typed dataclasses and a protocol for SDK-like messages,
requests, responses, usage metadata, and an injected client. It maps existing
provider requests into SDK-like requests, maps deterministic fake SDK responses
back to provider-safe responses, and maps timeout, rate-limit, unavailable,
malformed, empty, or unsafe output cases to redacted safe errors.

No real OpenAI SDK import, dependency install, credential use, environment
lookup, network client creation, live API call, WIF runtime, token exchange,
route behavior switch, API client change, SSE/frontend work, SQL, migration,
Supabase work, or generated state is approved or added. **OpenAI SDK dependency
decision remains NOT APPROVED.** Fake provider remains the default. Slice 7M-C
should record dependency approval or denial only.

### Slice 7M-C Update — 2026-06-03

Slice 7M-C adds the docs-only
[OpenAI SDK dependency approval record](openai-sdk-dependency-approval-record.md).
The record explicitly denies the `openai` Python SDK dependency. All 12
required approval gates (dependency owner, security/privacy, license,
supply-chain, CI impact, rollback, no-default-live-run, external review, pinned
version, transitive dep review, vulnerability scan plan, update policy) are
MISSING. Decision: **NOT APPROVED / DENIED**.

No SDK install, dependency manifest change, lockfile change, credential use,
live API call, WIF runtime, token exchange, route behavior switch, API client
change, SSE/frontend work, SQL, migration, Supabase work, or generated state is
approved or added. Fake provider remains the default. Slice 7M-D should resolve
the specific denial prerequisite items only.

### Slice 7M-D Update — 2026-06-03

Slice 7M-D adds the docs-only
[OpenAI SDK dependency prerequisites](openai-sdk-dependency-prerequisites.md).
The document prepares required-action checklists for all 12 missing approval
gates. All gates move from MISSING to PREPARED / STILL NOT APPROVED. PREPARED /
STILL NOT APPROVED is not an approval state.

No SDK install, dependency manifest change, lockfile change, credential use,
live API call, WIF runtime, token exchange, route behavior switch, API client
change, SSE/frontend work, SQL, migration, Supabase work, or generated state is
### Slice 7M-E Update — 2026-06-03

Slice 7M-E adds the docs-only
[OpenAI SDK dependency re-evaluation record](openai-sdk-dependency-reevaluation-record.md).
The record formally re-evaluates the dependency decision against the prepared
checklists. All 12 approval gates remain MISSING since no named reviewer has
provided explicit, concrete sign-offs or evidence.

Decision remains **NOT APPROVED / DENIED**. No SDK install, dependency manifest
change, lockfile change, credential use, live API call, WIF runtime, token
exchange, route behavior switch, API client change, SSE/frontend work, SQL,
migration, Supabase work, or generated state is approved or added. Fake
provider remains the default. Slice 7M-G should document keeping the mocked
adapter path dependency-free.

### Slice 7M-I Update — 2026-06-03

Slice 7M-I adds the docs-only
[OpenAI provider boundary cleanup plan](openai-provider-boundary-cleanup-plan.md).
The plan documents current route, service, prompt builder, fake provider,
OpenAI provider transport, dependency-free SDK adapter, config/fail-closed
validation, and test boundaries.

It identifies future cleanup themes and refactor candidates for clearer
provider protocol naming, prompt/request separation, diagnostics redaction,
adapter isolation, stable typed dataclasses/protocols, vendor-specific leakage
prevention, shared error taxonomy, and fake-provider default preservation.

No runtime code, tests, SDK install, dependency manifest change, lockfile
change, credential use, `.env` file, live API call, WIF runtime, token
exchange, route behavior switch, API client change, SSE/frontend work, SQL,
migration, Supabase work, live harness, or generated state is approved or
added. OpenAI SDK dependency remains **NOT APPROVED / DENIED**. Slice 7M-J
should add dependency-free adapter hardening tests only.

### Slice 7M-J Update — 2026-06-03

Slice 7M-J adds dependency-free hardening tests for
`apps/api/app/services/openai_sdk_adapter.py` in
`apps/api/tests/test_openai_sdk_adapter.py`.

The tests cover stricter SDK-like response field validation, malformed response
safe-error mapping, empty and unsafe output rejection, redacted
timeout/rate-limit/unavailable diagnostics, `repr()`/`str()`/safe diagnostic
surfaces, API-key/token/auth-header placeholder redaction, no environment-read
proof, and no socket/network-construction proof.

The adapter now maps malformed SDK-like field shapes to `sdk_invalid_response`
instead of relying on incidental Python attribute errors. No real OpenAI SDK
import, dependency install, credential use, `.env` file, live API call, WIF
runtime, token exchange, route behavior switch, API client change,
SSE/frontend work, SQL, migration, Supabase work, live harness, or generated
state is approved or added. OpenAI SDK dependency remains **NOT APPROVED /
DENIED**. Slice 7M-K should audit provider redaction and diagnostics only.

### Slice 7M-K Update — 2026-06-03

Slice 7M-K adds the
[OpenAI provider redaction diagnostics audit](openai-provider-redaction-diagnostics-audit.md).
The audit covers prompt builder diagnostics, summarization provider boundaries,
OpenAI provider transport errors, dependency-free SDK adapter errors, mocked WIF
exchange errors, config fail-closed errors, fixture hygiene, and exact
fingerprint-only `.gitleaksignore` posture.

Focused tests were added or extended to ensure prompt text, note content, raw
provider payloads, SDK-like raw bodies, auth-header fields, API-key fields,
access-token fields, identity assertion fields, WIF fake assertion placeholders,
and WIF fake access-token placeholders do not appear in safe diagnostics,
`repr()` output, `str()` output, or public error surfaces.

The redaction helper now treats raw provider/SDK payload keys and token/assertion
diagnostic keys as sensitive. No SDK install, dependency manifest change,
lockfile change, credential use, `.env` file, live API call, WIF runtime, token
exchange, route behavior switch, API client change, SSE/frontend work, SQL,
migration, Supabase work, live harness, `.gitleaksignore` broadening, or
generated state is approved or added. OpenAI SDK dependency remains **NOT
APPROVED / DENIED**. Slice 7M-L should implement provider boundary cleanup only
within the existing fake-only, dependency-free constraints.

### Slice 7M-L Update — 2026-06-03

Slice 7M-L implements a small provider boundary cleanup from the
[OpenAI provider boundary cleanup plan](openai-provider-boundary-cleanup-plan.md).
`OpenAIProviderRequest` now owns the provider-facing sensitive-term derivation
used for safe diagnostics, and both `OpenAISummarizationProvider` and the
dependency-free `OpenAISDKAdapter` use that request-owned list when building
safe errors.

This removes duplicate prompt/request sensitive-term helpers from the provider
and SDK adapter modules while keeping behavior unchanged. Focused tests cover
request-owned sensitive-term redaction through provider-safe errors.

No SDK install, dependency manifest change, lockfile change, credential use,
`.env` file, live API call, WIF runtime, token exchange, route behavior switch,
API client change, SSE/frontend work, SQL, migration, Supabase work, live
harness, `.gitleaksignore` broadening, or generated state is approved or
added. OpenAI SDK dependency remains **NOT APPROVED / DENIED**.

### Slice 8A Update — 2026-06-03

Slice 8A adds backend-only summary history for the fake summarization flow.
Successful fake `POST /v1/ai/notes/{note_id}/summarize` responses are recorded
in an in-memory summary history store, and `GET /v1/ai/notes/{note_id}/summaries`
returns the current user's recorded summaries for that owned note.

History is memory-only for local demos and tests. It stores only provider-safe
summary fields that are already returned by the summarize route; it does not
store prompt text, raw provider payloads, diagnostics, credentials, or live
provider data. Missing, deleted, or cross-user notes keep the existing safe 404
behavior.

The shared contracts now include a snake_case `ListSummariesResponse` envelope
for the history list endpoint. No OpenAI SDK install, dependency manifest
change, lockfile change, credential use, `.env` file, live API call, WIF
runtime, token exchange, route/client live OpenAI behavior, SSE/frontend work,
SQL, migration, Supabase work, live harness, `.gitleaksignore` broadening, or
generated Supabase state is approved or added. OpenAI SDK dependency remains
**NOT APPROVED / DENIED**. Slice 8B should add summary history API client
contract/client integration only.

### Slice 8B Update — 2026-06-04

Slice 8B adds API client support for the backend summary history endpoint from
Slice 8A. `client.ai.listNoteSummaries(note_id)` calls
`GET /v1/ai/notes/{note_id}/summaries`, URL-encodes the note id, preserves the
existing success/error envelope behavior, and validates returned history data
with the shared snake_case summary list contract.

Focused API client tests cover the request path, valid history parsing, safe
404 error mapping, and rejection of camelCase summary history fields. No
shared contract shape change was needed because `ListSummariesResponse` already
exists.

No backend route behavior change, frontend UI, SSE streaming, persistence,
database, SQL, migration, Supabase work, Docker work, OpenAI SDK dependency,
credential, `.env` file, live API call, WIF runtime, live provider route
wiring, `.gitleaksignore` broadening, or generated Supabase state is approved
or added. OpenAI SDK dependency remains **NOT APPROVED / DENIED**. Slice 8C
should plan either summary history UI/API consumption or backend persistence,
depending on product priority.

---

## 14. Definition Of Done (This Slice)

- [x] `docs/ai-summarization-implementation-plan.md` written and committed.
- [x] `docs/next-action.md` updated to Slice 7B.
- [x] All existing contract checks pass (`contracts:check`).
- [x] `ruff check` passes (no Python changed).
- [x] `pnpm lint / typecheck / test / build` pass (no runtime code changed).
- [x] `gitleaks detect --redact` clean.
- [x] No `.env`, SQL, migrations, credentials, or Supabase state changed.
- [x] No provider SDK, no network call, no `OPENAI_API_KEY` added.
