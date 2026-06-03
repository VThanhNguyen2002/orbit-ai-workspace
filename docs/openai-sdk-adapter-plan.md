# OpenAI SDK Adapter Plan

## Status

Slice 7M began as a documentation-only planning slice for a future OpenAI
SDK-backed provider adapter. Slice 7M-B adds only a mocked SDK adapter
interface boundary and dependency-free tests. It does not install the SDK, add
credentials, import the real SDK, make network calls, or change runtime
behavior.

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G decision). This plan does not reopen, satisfy, or bypass
that gate.

## 1. Objective

Plan how a future OpenAI SDK-backed provider adapter would be built, tested,
and gated safely within the existing Synapse backend, while keeping the fake
provider as the default for all local development, tests, and CI.

This plan is not live implementation permission. It does not install the OpenAI
SDK, add any dependency, change any config default, enable any live provider
path, or authorize runtime route selection.

## 2. Non-Goals

This slice explicitly excludes:

- OpenAI SDK dependency installation (`openai` package or any equivalent).
- Any `pip install`, `pnpm add`, `npm install`, or lockfile change.
- Real OpenAI API calls.
- Provider credentials of any kind.
- `.env` files or committed credential values.
- WIF runtime implementation.
- Token exchange implementation.
- GitHub OIDC token requests.
- Live harness execution or opt-in harness skeleton.
- Backend route changes or route behavior switches.
- API client method changes.
- SSE streaming implementation.
- Frontend, Expo, or UI work.
- Supabase/RLS work, SQL, migrations, or generated Supabase state.
- Production deployment.
- Any `.gitleaksignore` changes.

## 3. Current Baseline

### Backend

- `FakeSummarizationProvider` is the only runtime-enabled provider. It is
  deterministic, network-free, and credential-free.
- `apps/api/app/services/openai_provider.py` defines a network-free OpenAI
  adapter boundary with injected transport and fake transport tests. It reads
  no credentials, imports no OpenAI SDK, creates no HTTP client, and is not
  wired into runtime provider selection.
- `apps/api/app/services/openai_sdk_adapter.py` defines a mocked SDK adapter
  boundary with typed SDK-like request/response/protocol shapes. It accepts only
  an injected fake SDK-like client in tests, imports no SDK, reads no
  credentials or environment values, creates no network clients, and is not
  wired into runtime provider selection.
- `apps/api/app/services/openai_workload_identity.py` defines a mocked WIF
  token exchange boundary with fake exchanger tests only. It performs no real
  token exchange, reads no environment credentials, and is not wired into
  provider auth or runtime selection.
- `apps/api/app/core/config.py` accepts future OpenAI provider and auth-mode
  names but fails closed for live runtime paths. `ai_provider=openai` and
  `openai_auth_mode=api_key` / `workload_identity` are all rejected by runtime
  validation. Fake provider mode remains the only runtime-enabled default.
- `apps/api/app/services/ai_prompting.py` provides the prompt builder and
  diagnostic redaction boundary. It keeps raw note content, auth headers, API
  keys, OIDC/JWT values, and Supabase key names out of logs and error surfaces.

### Approval state

- Live harness approval: **DENIED / NOT GRANTED**.
- Live harness path: **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST** (Slice
  7L-G — 0 of 8 named reviewer approvals found).
- OpenAI SDK dependency: **NOT APPROVED / DENIED** (Slice 7M-C — all 12
  gates MISSING; Slice 7M-D — all 12 gates PREPARED / STILL NOT APPROVED).
  Record: `docs/openai-sdk-dependency-approval-record.md`.
  Prerequisites: `docs/openai-sdk-dependency-prerequisites.md`.
- No live execution, credential use, SDK installation, or real API calls are
  approved.

### API client

- `client.ai.summarizeNote(note_id)` exists against the existing backend route.
- No new client method or SSE parser is needed for this planning slice.

## 4. Official API Direction To Review Before Coding

A future implementer must review official OpenAI documentation before writing
any SDK-backed adapter code. This plan does not paste documentation, keys, or
executable setup commands.

Key areas to review:

| Topic | What to check |
|---|---|
| Official SDKs and libraries page | Confirm the current supported SDK for the target language (Python). |
| Responses API direction | OpenAI has indicated the Responses API is the direction for new projects; confirm whether it supersedes the Chat Completions API for the project's use case. |
| API key secrecy rules | Confirm that API keys must be server-side only, never committed, never logged, never sent to the client. |
| Data retention opt-out | Confirm the correct API settings path for opting out of training data use. |
| Rate limit and budget documentation | Confirm tier limits, retry guidance, and cost tracking APIs. |

No key values, bearer tokens, or executable curl/SDK commands may be included
in docs or committed to the repository. All config values must remain
placeholder-only until a future approved implementation slice.

## 5. Future SDK Adapter Boundary

A future SDK-backed adapter must respect the existing backend architecture
boundaries:

- **Provider interface**: The future `OpenAISummarizationProvider` must
  implement the same `SummarizationProvider` protocol that `FakeSummarizationProvider`
  uses. Routers must never call the SDK directly.
- **Prompt boundary**: The prompt builder (`ai_prompting.py`) remains the
  only boundary that constructs provider-facing prompt objects from note
  `title`, `content`, and bounded metadata. The SDK adapter accepts prompt
  objects only; it must not re-assemble raw note fields.
- **Transport injection**: The SDK adapter must accept an injectable transport
  or SDK client interface so tests can inject a fake SDK client without
  installing the real SDK or making network calls.
- **Redaction boundary**: All diagnostics (errors, timeouts, rate-limit
  responses, malformed responses) must pass through the redaction helper before
  reaching logs or public error surfaces.
- **Fake provider default**: `FakeSummarizationProvider` remains the default
  for all local development, tests, and CI. The SDK adapter must not be
  selectable by default config.
- **No direct SDK import at module level**: The SDK import must be guarded
  behind the provider selection path so it does not affect modules that do not
  need it and does not cause import errors when the SDK is absent.

### Mocked adapter shape (implemented for tests only)

```text
OpenAISDKAdapter(
    client: OpenAISDKClient,              # injected fake SDK-like client
    timeout_seconds: int,                 # explicit metadata, no env lookup
    request_budget: int,                  # explicit metadata, no env lookup
)
```

The adapter implements the existing injected-transport shape by accepting an
`OpenAIProviderRequest`, building an `OpenAISDKRequest`, calling only the
injected client, validating the typed SDK-like response, and returning an
`OpenAIProviderResponse`. The real SDK client remains unimplemented and
unapproved.

## 6. Credential Constraints

The following credential rules apply regardless of which auth mode is chosen:

- No credential values may be committed to the repository.
- No `.env` file may be committed.
- No API key, access token, OIDC value, or JWT value may appear in logs,
  docs, screenshots, error messages, reprs, or client bundles.
- No auth header value may be logged.
- `OPENAI_API_KEY` local-only mode: not approved for use until the credential-
  mode reviewer provides explicit sign-off per evidence packet section 5.3.
- WIF preferred for CI/cloud: WIF is the preferred future credential direction
  where supported, but WIF runtime is not implemented and not approved.
- Production API-key fallback: not approved. Any future production use must go
  through the deployment secret manager with explicit reviewer sign-off.
- Fake provider remains the only credential-free, network-free default until a
  future approved runtime slice changes it.

## 7. Runtime Selection Constraints

- `ai_provider=fake` remains the only runtime-enabled default. Config must not
  be changed in this slice.
- `ai_provider=openai` must continue to fail closed at runtime until a separate
  approved runtime implementation slice enables it.
- No route or service behavior switches to the OpenAI adapter in this slice.
- The live harness path remains closed and blocked until all 8 named reviewer
  approvals are recorded per evidence packet sections 5.1–5.8.
- Default push CI must remain fake-only, credential-free, and network-free.
- No `workflow_dispatch` live provider job may be added without a separate
  approved slice.

## 8. Testing Strategy for Future SDK Adapter

All default tests must remain network-free and credential-free.

| Test type | Approach |
|---|---|
| Fake transport tests | Inject a fake SDK client; prove request construction, success mapping, failure mapping. No network, no SDK install required. |
| Mocked SDK client tests | Use an injected fake SDK-like client or mocks; prove timeout, rate-limit, unavailable, malformed response, and unsafe output behavior. |
| Malformed SDK response tests | Inject fake responses with missing/invalid fields; prove the adapter rejects them before returning public responses. |
| Redaction tests | Assert that SDK error messages, timeout details, and rate-limit messages are redacted before logging. |
| No-network proof | Patch `socket.socket` or equivalent at the test level; assert no network attempt is made during default test runs. |
| No-credential proof | Assert that no environment credential read occurs during adapter construction or fake-transport test runs. |
| Fail-closed config tests | Assert that the adapter cannot be instantiated without required config; assert that missing budget config blocks calls. |

Live provider tests (real SDK, real network) must be skipped by default and
must require explicit opt-in flags. They must never be prerequisites for normal
CI, local unit tests, or contract checks.

## 9. Failure Modes To Plan

A future SDK adapter implementation must handle all of the following:

| Failure | Planned handling |
|---|---|
| SDK unavailable (import error) | Fail closed at provider construction time; never propagate ImportError to routers. |
| Unsupported SDK version | Fail closed at startup config validation; log only coarse version metadata (no raw SDK internals). |
| Invalid auth mode | Fail closed at config validation; return coarse provider/auth error; never reveal mode-specific details. |
| Missing credentials | Fail closed before any SDK call; return coarse credential/config error; never reveal which env var is missing. |
| Request timeout | Stop within configured timeout; retry only within bounded policy; map to coarse timeout error. |
| Rate limit (429) | Return coarse rate-limit error; respect `Retry-After` header within bounded retry policy; do not reveal rate-limit internals. |
| Malformed SDK response | Reject during output validation before constructing public response; do not pass raw SDK body to routers. |
| Unsafe or empty output | Reject as invalid provider output or policy failure; return coarse error. |
| Budget exceeded | Reject before SDK call where estimable; return coarse over-budget error; do not attempt hidden retries. |
| Redaction failure | If diagnostic output cannot be redacted, drop the diagnostic; never log or return unredacted content. |

All failure paths must return only coarse public errors. No raw SDK response
body, prompt text, note content, auth header, API key, OIDC token, JWT value,
or raw payload may appear in public errors, logs, or structured metadata.

## 10. Cost/Token Guardrails

A future SDK adapter must define all guardrails before any provider call:

| Guardrail | Placeholder label |
|---|---|
| Max prompt length (chars) | `TO_BE_APPROVED_MAX_PROMPT_LENGTH` |
| Max output tokens | `TO_BE_APPROVED_MAX_OUTPUT_TOKENS` |
| Max retries | `TO_BE_APPROVED_MAX_RETRIES` |
| Max timeout (seconds) | `TO_BE_APPROVED_MAX_TIMEOUT` |
| Max requests per run | `TO_BE_APPROVED_MAX_REQUESTS_PER_RUN` |
| Max spend ceiling | `TO_BE_APPROVED_MAX_SPEND_CEILING` |

All placeholder labels must be replaced with actual numeric values approved by
the cost/budget reviewer (evidence packet section 5.2) before any live
implementation proceeds.

Allowed usage metadata: provider name, model name, operation name, coarse
input/output token counts, request count, elapsed duration bucket, estimated
cost bucket. Must not include note content, prompt text, raw SDK response body,
credentials, provider headers, auth headers, OIDC/JWT values, access tokens, or
raw payloads.

The adapter must fail closed if any guardrail configuration is missing or
invalid.

## 11. Approval Gates Before Real SDK Runtime Implementation

No real SDK dependency-backed or runtime-wired adapter implementation may begin
until all of the following are approved and recorded in the relevant approval
documents:

| Gate | Required approver | Evidence location |
|---|---|---|
| Dependency approval | Named dependency reviewer | New approval record (future slice) |
| Security/privacy approval | `TBD_SECURITY_PRIVACY_REVIEWER` | Evidence packet section 5.1 |
| Credential-mode approval | `TBD_CREDENTIAL_MODE_REVIEWER` | Evidence packet section 5.3 |
| Cost/budget approval | `TBD_COST_BUDGET_REVIEWER` | Evidence packet section 5.2 |
| Live harness path decision | All 8 named reviewers | Evidence packet sections 5.1–5.8 |
| External review gate | `TBD_EXTERNAL_REVIEWER` | Evidence packet section 5.8 |
| Rollback/disable plan | `TBD_ROLLBACK_REVIEWER` | Evidence packet section 5.5 |
| No-default-CI proof | `TBD_CI_REVIEWER` | Evidence packet section 5.6 |

Approval must be explicit, named, and tied to a commit or PR review before any
SDK installation, credential use, or runtime wiring is authorized.

This plan does not satisfy any of these gates.

## 12. Future Slices

Recommended follow-up slices:

- **Slice 7M-A — OpenAI SDK dependency review packet.** Docs-only. Research
  the `openai` Python SDK version, license, transitive dependencies, size, and
  security track record. Produce a dependency review packet without installing
  anything. *(Complete — packet added, dependency NOT APPROVED.)*
- **Slice 7M-B — Mocked SDK adapter interface tests.** Add dependency-free
  mocked SDK adapter boundary tests. No real SDK install, no network, no
  credentials. *(Complete — fake-only boundary added, not runtime-wired.)*
- **Slice 7M-C — SDK dependency approval or denial record.** Named reviewers
  complete every dependency approval gate and record their decision.
  *(Complete — decision: NOT APPROVED / DENIED. All 12 gates MISSING.
  Record: `docs/openai-sdk-dependency-approval-record.md`.)*
- **Slice 7M-D — Resolve OpenAI SDK dependency approval prerequisites.**
  Address each denial rationale item. Docs-only. No install.
  *(Complete — all 12 gates PREPARED / STILL NOT APPROVED.
  Record: `docs/openai-sdk-dependency-prerequisites.md`.)*
- **Slice 7M-E — Re-evaluate SDK dependency approval with evidence.**
  *(Complete — all evidence missing. Record: `docs/openai-sdk-dependency-reevaluation-record.md`. Decision remains NOT APPROVED / DENIED.)*
- **Slice 7M-F — Optional SDK dependency install.** Only after Slice 7M-H
  records explicit named approval for every gate.
- **Slice 7M-G — Keep mocked adapter path dependency-free.** Permanent strategy since approval denied.
- **Slice 7N — Opt-in live provider harness skeleton.** Only reachable after
  all 8 named reviewer approvals exist and a separate implementation slice is
  approved. Not authorized by this plan.

Do not proceed to any of the above automatically.

## 13. Definition of Done

This slice is complete when:

- `docs/openai-sdk-adapter-plan.md` exists.
- `docs/openai-sdk-dependency-review-packet.md` exists.
- `apps/api/app/services/openai_sdk_adapter.py` exists as a mocked,
  dependency-free SDK boundary only.
- `apps/api/tests/test_openai_sdk_adapter.py` covers fake SDK client request
  construction, success mapping, safe failure mapping, no SDK import,
  no-credential/no-network behavior, and redaction.
- Referenced docs are minimally updated to point to both documents.
- `docs/next-action.md` recommends Slice 7M-C.
- No real SDK, dependency install, credential, `.env` file, API call, token
  exchange, WIF runtime, backend route, API client method, SSE/frontend,
  Supabase, SQL, migration, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- Verification passes or any blocked verification is explicitly reported.
