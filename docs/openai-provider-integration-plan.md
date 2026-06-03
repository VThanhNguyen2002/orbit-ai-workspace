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

Slice 7M-B adds `apps/api/app/services/openai_sdk_adapter.py` as a mocked SDK
adapter boundary. It defines typed SDK-like messages, requests, responses,
usage metadata, an injected client protocol, and safe adapter errors. It imports
no real SDK, reads no environment credentials, creates no network clients, and
is not wired into runtime provider selection.

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
- **Slice 7J — Mocked WIF token exchange boundary tests.**
- **Slice 7K — OpenAI provider live harness planning.**
- **Slice 7L — OpenAI live harness approval record.**
- **Slice 7L-A — Deny local-only live harness approval until prerequisites exist.**
- **Slice 7L-B — Resolve live harness approval prerequisites.**
- **Slice 7L-C — Grant or deny local-only live harness approval with evidence.**
- **Slice 7L-D — Prepare OpenAI live harness approval evidence packet.**
- **Slice 7L-E — Fill approval evidence packet with reviewer decisions.** *(Complete — evidence filled, approval remains DENIED.)*
- **Slice 7L-F — Resolve missing OpenAI live harness approval evidence.** *(Complete — required-action records added, approval remains DENIED.)*
- **Slice 7L-G — Collect explicit reviewer approvals or close live harness path.** *(Complete — 0 of 8 named approvals, path CLOSED / BLOCKED.)*
- **Slice 7M — OpenAI SDK adapter planning.** *(Complete — docs-only plan added, no credentials, no SDK.)*
- **Slice 7M-A — OpenAI SDK dependency review packet.** *(Complete — packet added, dependency NOT APPROVED.)*
- **Slice 7M-B — Mocked SDK adapter interface tests without SDK dependency.** *(Complete — fake-only boundary added, not runtime-wired.)*
- **Slice 7M-C — SDK dependency approval or denial record.** *(Complete — NOT APPROVED / DENIED, all 12 gates MISSING. Record: `docs/openai-sdk-dependency-approval-record.md`.)*
- **Slice 7M-D — Resolve OpenAI SDK dependency approval prerequisites.** Docs-only.
  *(Complete — all 12 gates PREPARED / STILL NOT APPROVED.
  Record: `docs/openai-sdk-dependency-prerequisites.md`.)*
- **Slice 7M-E — Re-evaluate SDK dependency approval with evidence.** *(Complete — all evidence missing. Record: `docs/openai-sdk-dependency-reevaluation-record.md`. Decision remains NOT APPROVED / DENIED.)*
- **Slice 7M-F — Optional SDK dependency install.** Only if 7M-H grants approval.
- **Slice 7M-G — Keep mocked adapter path dependency-free.** Recommended since approval denied.
- **Slice 7N — Opt-in live provider harness skeleton.** *(Reachable only after all 8 approvals exist.)*

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

### Slice 7I Update — 2026-06-01

Slice 7I adds the docs-only
[OpenAI Workload Identity approval record](openai-workload-identity-approval-record.md).
The record defines candidate environments, approval requirements, future GitHub
Actions checklist, security risks, fake-only testing strategy, decision status,
and follow-up slices for mocked token exchange and live harness planning.

WIF remains the preferred future CI/cloud credential direction where supported,
but WIF runtime is not approved. API-key fallback is not approved for
production. No token exchange, provider SDK, credential, API call, route
behavior, workflow configuration, or live provider harness was added.

### Slice 7J Update — 2026-06-01

Slice 7J adds a mocked WIF token exchange boundary in
`apps/api/app/services/openai_workload_identity.py`. The boundary defines typed
subject metadata, exchange request/result objects, an exchanger protocol, a fake
exchanger, and safe exchange errors for unavailable or invalid exchange
outcomes.

The fake exchanger performs only deterministic in-memory checks against explicit
trusted issuer, audience, subject, repository, ref, workflow, and optional
environment metadata. It does not parse OIDC/JWT values, perform cryptographic
validation, read environment variables, import an OpenAI SDK, create network
clients, or request GitHub OIDC tokens.

Tests cover fake success, required claim metadata, fail-closed unsupported claim
metadata, unavailable exchange, malformed exchange result mapping, redaction of
identity assertion and access-token placeholders from reprs/errors/diagnostics,
no-network behavior, no credential environment reads, no OpenAI SDK import
requirement, synthetic token shape hygiene, and exact-fingerprint-only
`.gitleaksignore`.

The boundary is not wired into `OpenAISummarizationProvider`, summarization
routes, config runtime selection, GitHub Actions, or API clients. WIF runtime and
live token exchange remain deferred.

### Slice 7K Update — 2026-06-02

Slice 7K adds the docs-only
[OpenAI live provider harness plan](openai-live-provider-harness-plan.md). The
plan defines a future optional live-provider validation harness, required
opt-in gates, fake-only default CI posture, credential handling rules,
redaction/logging requirements, safety stop conditions, test boundaries, CI
considerations, cost/token guardrails, approval requirements, and future slices.

This is planning only. It does not add an OpenAI SDK, credentials, `.env` file,
real API call, live harness code, WIF runtime, token exchange, GitHub Actions
WIF wiring, backend route behavior, API client behavior, SSE/frontend work,
Supabase work, SQL, migrations, or generated state. Fake provider remains the
default runtime path.

### Slice 7L Update — 2026-06-02

Slice 7L adds the docs-only
[OpenAI live harness approval record](openai-live-harness-approval-record.md).
The record sets live harness execution status to pending/not granted, documents
the candidate local-only smoke-test scope that is not yet granted, lists
explicitly unapproved modes, and defines required approvals, pre-execution
checks, credential constraints, stop conditions, evidence requirements, and the
relationship to WIF.

No live OpenAI API call, SDK implementation, credential use, WIF runtime,
default CI live test, GitHub Actions WIF wiring, route behavior switch,
background summarization, persisted live provider output, SQL, migration,
Supabase state, frontend work, SSE, or API client change is approved or added.
Fake provider remains the default runtime path.

### Slice 7L-A Update — 2026-06-02

Slice 7L-A updates the
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
to deny local-only live harness approval until prerequisites exist. The record
now requires explicit security/privacy approval, cost/budget ceiling,
credential-mode decision, synthetic prompt fixture, redacted evidence template,
no-default-CI proof, fail-closed config proof, local-only execution boundary,
rollback/disable plan, and external review gate evidence before a future
approval can be considered.

The candidate local-only scope remains documented but unauthorized. No live
execution, SDK implementation, credential use, WIF runtime, token exchange,
default CI live test, workflow wiring, route behavior switch, API client change,
SSE/frontend work, SQL, migration, Supabase work, or persisted live provider
output is approved or added.

### Slice 7L-B Update — 2026-06-02

Slice 7L-B adds the docs-only
[OpenAI live harness prerequisites](openai-live-harness-prerequisites.md)
packet. It prepares security/privacy, cost/budget, credential-mode, redacted
evidence, rollback/disable, no-default-CI, and local-only execution boundary
checklists for a later approval decision.

Approval remains not granted. This slice does not approve execution,
credentials, SDK/runtime work, WIF runtime, token exchange, live API calls,
workflow changes, default CI live tests, route behavior switches, API client
changes, SSE/frontend work, SQL, migrations, Supabase work, or persisted live
provider output.

### Slice 7L-C Update — 2026-06-02

Slice 7L-C updates the
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
with an evidence checklist and denies local-only live harness approval. The
redacted evidence template and fail-closed config proof are present, but
security/privacy approval, cost/budget approval, credential-mode decision,
synthetic prompt fixture, rollback/disable plan, no-default-CI proof,
local-only boundary evidence, and external review sign-off are missing or
insufficient.

The candidate local-only scope remains unauthorized. No live execution,
credential use, OpenAI API call, SDK/runtime work, WIF runtime, token exchange,
workflow change, default CI live test, route behavior switch, API client change,
SSE/frontend work, SQL, migration, Supabase work, or persisted live provider
output is approved or added.

### Slice 7L-D Update — 2026-06-02

Slice 7L-D adds the docs-only
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md).
The packet prepares a future evidence matrix, reviewer placeholders,
security/privacy review requirements, placeholder-only cost/budget labels,
credential-mode comparison, synthetic fixture requirements, redacted report
format, rollback/disable requirements, no-default-CI proof requirements, and
local-only boundary evidence requirements.

Approval remains denied/not granted. No live execution, credential use, OpenAI
API call, SDK/runtime work, WIF runtime, token exchange, workflow change,
default CI live test, route behavior switch, API client change, SSE/frontend
work, SQL, migration, Supabase work, or persisted live provider output is
approved or added.

### Slice 7L-E Update — 2026-06-02

Slice 7L-E fills the
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
with explicit reviewer decision sections and a final evidence decision matrix.
2 of 10 evidence items are PRESENT; 4 are MISSING; 4 are INSUFFICIENT; 0 have
been approved by a named reviewer.

Approval remains **DENIED / NOT GRANTED**. No live execution, credential use,
OpenAI API call, SDK/runtime work, WIF runtime, token exchange, workflow
change, default CI live test, route behavior switch, API client change,
SSE/frontend work, SQL, migration, Supabase work, or persisted live provider
output is approved or added.

### Slice 7L-F Update — 2026-06-02

Slice 7L-F converts each MISSING and INSUFFICIENT evidence item in the
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
into a concrete required-action record. 8 items are now `PREPARED / STILL NOT
APPROVED`. 2 items remain PRESENT (redacted template, fail-closed config).

`PREPARED / STILL NOT APPROVED` is not an approval state. Approval remains
**DENIED / NOT GRANTED**. No live execution, credential use, OpenAI API call,
SDK/runtime work, WIF runtime, token exchange, workflow change, default CI
live test, route behavior switch, API client change, SSE/frontend work, SQL,
migration, Supabase work, or persisted live provider output is approved or
added.

### Slice 7L-G Update — 2026-06-02

Slice 7L-G reviewed the evidence packet and approval record for named reviewer
approvals. **0 of 8 required named reviewer approvals exist.** All eight
`TBD_*` reviewer slots remain placeholder-only.

**Decision: CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**

Approval remains **DENIED / NOT GRANTED**. No live execution, credential use,
OpenAI API call, SDK/runtime work, WIF runtime, token exchange, workflow change,
default CI live test, route behavior switch, API client change, SSE/frontend
work, SQL, migration, Supabase work, or persisted live provider output is
approved or added.

### Slice 7M Update — 2026-06-03

Slice 7M adds the docs-only
[OpenAI SDK adapter plan](openai-sdk-adapter-plan.md). The plan covers the
future SDK adapter boundary, injectable transport design, credential
constraints, runtime selection rules, test strategy, failure modes, cost/token
guardrails, approval gates, and recommended follow-up slices.

No SDK installation, credential use, OpenAI API call, live harness execution,
WIF runtime, token exchange, workflow change, default CI live test, route
behavior switch, API client change, SSE/frontend work, SQL, migration, Supabase
work, or persisted live provider output is approved or added.

### Slice 7M-A Update — 2026-06-03

Slice 7M-A adds the docs-only
[OpenAI SDK dependency review packet](openai-sdk-dependency-review-packet.md).
The packet covers supply-chain risk, runtime risk, credential/security
constraints, testing plan, CI impact checklist, dependency approval gates, and
decision status for a future OpenAI Python SDK dependency.

No SDK installation, dependency manifest change, lockfile change, credential
use, live API call, runtime import, WIF runtime, token exchange, route behavior
switch, API client change, SSE/frontend work, SQL, migration, Supabase work, or
generated state is approved or added. **OpenAI SDK dependency decision: NOT
APPROVED.**

### Slice 7M-B Update — 2026-06-03

Slice 7M-B adds a mocked SDK adapter boundary in
`apps/api/app/services/openai_sdk_adapter.py` and dependency-free tests in
`apps/api/tests/test_openai_sdk_adapter.py`.

The boundary accepts only an injected SDK-like client, builds typed SDK-like
requests from existing provider requests, maps deterministic fake SDK responses
back to provider-safe responses, and maps timeout, rate-limit, unavailable,
malformed, empty, or unsafe output cases to redacted safe errors. It imports no
real OpenAI SDK, reads no credentials or environment values, creates no network
clients, and is not wired into runtime route or provider selection.

OpenAI SDK dependency remains **NOT APPROVED / DENIED**. Fake provider remains
the runtime default.

### Slice 7M-D Update — 2026-06-03

Slice 7M-D adds the docs-only
[OpenAI SDK dependency prerequisites](openai-sdk-dependency-prerequisites.md).
The document prepares required-action checklists for all 12 missing approval
gates. All gates move from MISSING to PREPARED / STILL NOT APPROVED.

remains **NOT APPROVED / DENIED**. No SDK install, dependency manifest change,
lockfile change, credential use, live API call, WIF runtime, token exchange,
route behavior switch, API client change, SSE/frontend work, SQL, migration,
Supabase work, or generated state is approved or added. Fake provider remains
the default.

### Slice 7M-E Update — 2026-06-03

Slice 7M-E adds the docs-only
[OpenAI SDK dependency re-evaluation record](openai-sdk-dependency-reevaluation-record.md).
The record formally re-evaluates the dependency decision against the prepared
checklists. All 12 approval gates remain MISSING since no named reviewer has
provided explicit, concrete sign-offs or evidence.

Decision remains **NOT APPROVED / DENIED**. No SDK install, dependency manifest change,
lockfile change, credential use, live API call, WIF runtime, token exchange,
route behavior switch, API client change, SSE/frontend work, SQL, migration,
Supabase work, or generated state is approved or added. Fake provider remains
the default.

Slice 7M-G should document keeping the mocked adapter path dependency-free.

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
