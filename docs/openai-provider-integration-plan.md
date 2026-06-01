# OpenAI Provider Integration Plan

## Objective

Plan a future OpenAI provider integration for note summarization without
implementing provider runtime code, adding dependencies, wiring credentials, or
changing public API behavior.

This plan defines the backend provider boundary, credential strategy, Workload
Identity Federation (WIF) approach, local fallback rules, testing strategy,
security guardrails, failure handling, cost controls, and future implementation
slices.

## Non-Goals

This slice explicitly excludes:

- OpenAI SDK dependency installation.
- Real OpenAI API calls.
- Provider credentials.
- `.env` files.
- WIF runtime implementation.
- SSE streaming.
- Embeddings, vector search, or pgvector work.
- Frontend or UI work.
- Supabase/RLS work.
- SQL files, migrations, or generated Supabase state.
- Production deployment.

## Current Baseline

The backend exposes:

```text
POST /v1/ai/notes/{note_id}/summarize
```

The route is backed by `SummarizationService` and the deterministic
`FakeSummarizationProvider`. The fake provider is network-free, returns a canned
summary, and remains the default provider for local development, tests, and CI.

The API client exposes:

```ts
client.ai.summarizeNote(note_id)
```

The route currently returns the same snake_case `Summary` shape used by shared
domain contracts. SSE streaming remains deferred.

Slice 7E added `apps/api/app/services/ai_prompting.py`, which builds
provider-facing note summarization prompts from explicit note `title`,
`content`, and bounded note metadata. Prompt object reprs and log-safe metadata
exclude raw note title/content. The same module provides diagnostic redaction for
sensitive keys, prompt text, note title/content terms, bearer/JWT-like values,
OpenAI-style keys, and Supabase key names.

Shared AI contracts already include `SummarizeRequestSchema`,
`SummarizeResponseSchema`, `GetSummaryResponseSchema`, `AiUsageSchema`, and SSE
event schemas. The OpenAI provider runtime is still deferred.

## Provider Interface Plan

Future provider work should keep the existing backend boundary:

- `SummarizationProvider` remains the service-level protocol.
- `FakeSummarizationProvider` remains the default and CI provider.
- A future `OpenAISummarizationProvider` may implement the same protocol.
- Provider selection should be config-driven and resolved in the dependency
  factory, not in the router.
- Routers must never import an OpenAI SDK or call provider APIs directly.
- Direct SDK or HTTP calls must be isolated inside the provider adapter.
- Provider adapters must accept provider-facing prompt objects, not raw request
  payloads or auth contexts.
- The service must remain responsible for note fetch, ownership enforcement,
  input size checks, prompt construction, provider invocation, and output
  validation.

The future adapter should return backend domain objects matching the existing
`AiSummaryResult`/`AiActionItem` shape. It should not expose OpenAI raw response
objects to routers, public responses, or logs.

## Credential Strategy

Provider credentials must never be committed to the repository. No provider key,
token, `.env` file, or generated secret material belongs in git history.

Default environments:

- Local default: fake provider.
- Test default: fake provider.
- CI default: fake provider.

Local developer fallback may use gitignored environment variables only after a
future explicit implementation slice. Any fallback that uses a long-lived API key
must be opt-in, documented, and excluded from default test/CI paths.

Production and cloud environments should prefer a short-lived credential
strategy where the provider and deployment platform support it. Long-lived
`OPENAI_API_KEY` usage is only a fallback path, and any use must be stored in the
deployment secret manager, never in source files, logs, CI output, or client
bundles.

The backend must never send user auth tokens, Supabase service-role credentials,
or raw client headers to OpenAI.

## Workload Identity Federation Strategy

WIF is the preferred future CI/cloud credential strategy where the provider and
cloud environment support a secure token-exchange flow.

Future WIF work must be split into an explicit slice and reviewed before any
runtime wiring. This slice does not implement WIF runtime behavior.

Requirements for a future WIF design:

- GitHub Actions or cloud workload identity exchange happens only in an approved
  future slice.
- Raw OIDC tokens, JWTs, exchanged credentials, and provider access tokens are
  never printed.
- Token exchange diagnostics are redacted before logging.
- Audience, issuer, repository, branch/ref, workflow, and subject claims are
  strictly validated.
- Exchanged credentials are short-lived and scoped to the provider operation.
- Fallback to API-key auth is explicit, reviewed, and disabled by default.
- Failed token exchange maps to a coarse provider/auth error and never exposes
  token contents.

No code path should treat WIF as a reason to bypass provider opt-in gates,
ownership checks, request size checks, rate limits, or budget limits.

## Config Plan

Future settings should be added in a dedicated config slice, with validation and
tests before runtime provider use.

Planned settings:

| Setting | Purpose |
|---|---|
| `ai_provider` | Selects `fake` or a future live provider. |
| `openai_model` | Selects the summarization model name. |
| `openai_timeout_seconds` | Bounds provider request duration. |
| `openai_max_retries` | Bounds retry attempts for retryable failures. |
| `openai_request_budget` | Caps per-request token/cost budget. |
| `openai_auth_mode` | Selects `fake`, `api_key`, or `workload_identity`. |
| `ai_summarization_enabled` | Keeps summarization opt-in and disabled by default. |

Settings must contain no secret values in docs or defaults. Secret-bearing
values must be read only by a future credential boundary and kept out of public
config dumps, reprs, errors, and logs.

## Request and Response Behavior

The future OpenAI provider path must preserve the existing request ordering:

1. Authenticate request.
2. Fetch note through the note service.
3. Return 404 for missing, deleted, or cross-user notes.
4. Reject over-limit content before building or sending provider requests.
5. Build the provider-facing prompt through the prompt builder.
6. Invoke the selected provider adapter.
7. Validate provider output before returning it.
8. Return the existing shared-contract-compatible summary shape.

Provider timeout, unavailable, rate-limit, malformed response, and invalid
credential failures must map to coarse public errors. Public errors must not
include raw note content, prompt text, provider response bodies, auth headers,
API keys, OIDC tokens, JWTs, or raw user payloads.

Routers must not change endpoint paths or response casing as part of provider
integration.

## Privacy and Security Guardrails

Every future provider slice must preserve these rules:

- Never log note content.
- Never log prompt text.
- Never log auth headers.
- Never log API keys, access tokens, OIDC tokens, or JWTs.
- Never use a Supabase service-role credential on the summarization request
  path.
- Emit only redacted diagnostics.
- Keep summarization user-initiated.
- Enforce rate and budget guardrails before provider calls where possible.
- Enforce request size limits before provider calls.
- Validate provider output before sending a public response.
- Do not include user email, display name, user auth token, provider
  credential, internal note IDs, or Supabase credentials in prompts.
- Keep fake provider as the default for CI and tests.

Usage metadata may include provider name, model name, coarse token counts,
operation, and estimated cost. It must not include note content, prompt text, raw
AI response text, credentials, or request headers.

## Testing Strategy

Default tests must remain network-free.

Required future coverage:

- Fake provider remains the default CI path.
- No live provider tests run by default.
- Provider adapter unit tests use mocked transport only.
- WIF token exchange tests use a fake token exchange only.
- Provider error diagnostics pass through redaction.
- Malformed provider responses are rejected before public response creation.
- Timeout and retry behavior is bounded and deterministic.
- Rate-limit and over-budget paths return safe public errors.
- Ownership and input size checks happen before provider calls.
- Optional live provider tests require explicit opt-in and are skipped in default
  CI.

Optional live provider harnesses must never be prerequisites for normal CI,
local unit tests, or contract checks.

## Failure Modes

| Failure | Planned Handling |
|---|---|
| Provider unavailable | Return coarse unavailable error; redact provider details. |
| Timeout | Stop within configured timeout; retry only within bounded policy. |
| Invalid credentials | Return coarse provider auth/config error; never reveal credential values. |
| WIF exchange failure | Return coarse credential exchange error; redact OIDC/JWT data. |
| Malformed provider response | Reject during validation; do not pass raw provider body to clients. |
| Unsafe or empty output | Reject as invalid provider output or policy failure. |
| Over-budget request | Reject before provider call where estimable; avoid hidden retries. |
| Rate limit | Return rate-limit/unavailable response; respect retry bounds. |
| Unauthorized/cross-user note | Return 404 before provider call. |

## Cost and Token Strategy

Future runtime work should use layered budgets:

- Input character limit remains enforced before provider calls.
- Token estimates should be computed before provider calls for budget checks.
- Summary output budget should cap maximum provider response length.
- Retry budget should prevent hidden repeated cost.
- Usage metadata should record provider, model, operation, coarse input/output
  token counts, and estimated cost.
- Automatic background summarization remains out of scope.
- Repeated summarization should remain user-initiated unless a separately
  approved caching/background design is introduced.

Budget failures should be safe public errors, not provider attempts.

## Future Slices

Recommended follow-up slices:

- **Slice 7G — OpenAI provider adapter interface and fake transport tests.**
- **Slice 7H — OpenAI config and credential-mode validation.**
- **Slice 7I — Workload Identity Federation planning/approval record.**
- **Slice 7J — Mocked OpenAI provider adapter tests.**
- **Slice 7K — Optional live provider harness planning.**

Do not proceed from planning to runtime provider calls without explicit approval
and a reviewed safety gate.

### Slice 7G Update — 2026-06-01

Slice 7G adds `apps/api/app/services/openai_provider.py` as a network-free
adapter boundary. It defines provider request/response DTOs, an injected
transport protocol, safe provider/transport errors, and an
`OpenAISummarizationProvider` adapter that maps deterministic transport results
to the backend `AiSummaryResult` shape.

The adapter is not wired into the route factory. `FakeSummarizationProvider`
remains the default runtime provider for local development, tests, and CI. The
new adapter reads no environment variables, accepts no credentials, imports no
OpenAI SDK, creates no HTTP client, and makes no network calls by itself.

Tests use an in-file fake transport to cover request construction, synthetic
success mapping, no-network behavior, no SDK import requirement, safe repr/log
metadata, timeout/unavailable/malformed response mapping, and redacted
diagnostic output. Public API behavior remains unchanged. Slice 7H should add
configuration and credential-mode validation only; live runtime remains
deferred.

### Slice 7H Update — 2026-06-01

Slice 7H adds future OpenAI config shape to `apps/api/app/core/config.py`:
`ai_provider`, `openai_model`, timeout, retry budget, request budget, and
`openai_auth_mode`. Defaults remain fake-only, disabled, credential-free, and
network-free.

Unknown AI provider values and unknown OpenAI auth modes fail closed during
settings parsing without echoing raw values. A runtime validation helper rejects
OpenAI `api_key` and `workload_identity` modes because neither credential path
is implemented yet. The existing summarization service factory still returns
`FakeSummarizationProvider`; OpenAI config does not switch runtime provider
behavior.

Tests cover default fake config, unsupported provider/auth modes, API-key and
workload-identity fail-closed paths, fake mode without credentials, safe error
messages, unchanged fake runtime selection, and exact-fingerprint-only
`.gitleaksignore` entries. Slice 7I should remain a WIF planning/approval
record only; WIF runtime remains deferred.

## Definition of Done

This docs-only slice is complete when:

- The OpenAI provider integration plan is documented.
- Existing AI summarization docs link to the plan.
- Security docs include the provider credential/WIF guardrails.
- `docs/next-action.md` points to Slice 7G.
- Verification passes without adding provider code, provider SDKs, credentials,
  `.env` files, SQL, migrations, Supabase state, SSE, API client methods,
  frontend work, or OpenAI API calls.

Safety gate:

- Keep fake provider as default.
- Keep live provider runtime deferred.
- Keep WIF runtime deferred.
- Keep optional live provider tests out of default CI.
- Keep public diagnostics redacted and contract-compatible.
