# OpenAI Provider Boundary Cleanup Plan

## 1. Objective

Plan provider boundary cleanup/refactor work for the AI summarization provider
layer without implementing it. The goal is to improve maintainability,
separation of concerns, naming clarity, diagnostics safety, and testability
while preserving the current fake-only runtime posture.

This document is planning only. It does not authorize code changes, dependency
changes, credentials, live provider execution, route behavior changes, or SDK
installation.

## 2. Non-goals

This planning slice explicitly excludes:

- Runtime code changes.
- Test changes.
- OpenAI SDK installation.
- Dependency manifest, lockfile, or package changes.
- Credentials or credential wiring.
- `.env` files.
- OpenAI API calls.
- WIF runtime.
- Live harness implementation or execution.
- Route/API behavior changes.
- SSE, frontend, Supabase, SQL, migration, or generated-state work.

## 3. Current Boundary Map

- **Route layer**: `apps/api/app/routers/ai.py` owns HTTP routing, auth
  dependency injection, public error mapping, and the existing JSON success
  envelope. It depends on `SummarizationService` and must not import provider
  SDKs, transports, credentials, or vendor-specific request shapes.
- **Summarization service**: `apps/api/app/services/ai_summarization.py` owns
  note lookup, ownership enforcement through `NoteService`, input-size checks,
  prompt construction, provider invocation, and user-id injection into the
  returned domain result. It exposes the current `SummarizationProvider`
  protocol and backend `AiSummaryResult`/`AiActionItem` dataclasses.
- **Prompt builder**: `apps/api/app/services/ai_prompting.py` builds
  `NoteSummarizationPrompt` from explicit note title, content, content type,
  and bounded metadata. It also owns diagnostic redaction helpers for prompt
  text, note content, credential-like keys, auth headers, API-key-like strings,
  and token-like values.
- **Fake provider**: `FakeSummarizationProvider` remains deterministic,
  network-free, credential-free, and the default provider for local runtime,
  tests, and CI.
- **OpenAI provider transport boundary**:
  `apps/api/app/services/openai_provider.py` defines provider-owned
  request/response dataclasses, an injected `OpenAIProviderTransport` protocol,
  safe provider/transport errors, and `OpenAISummarizationProvider`. It imports
  no OpenAI SDK, creates no HTTP client, reads no credentials, and is not wired
  into runtime provider selection.
- **Dependency-free SDK adapter boundary**:
  `apps/api/app/services/openai_sdk_adapter.py` defines SDK-like dataclasses,
  an injected fake-client protocol, dependency-free request mapping, response
  validation, and safe adapter errors. It accepts `OpenAIProviderRequest` and
  returns `OpenAIProviderResponse`, but imports no real SDK and reads no
  environment credentials.
- **Config/fail-closed validation**: `apps/api/app/core/config.py` accepts
  future provider/auth-mode names while `validate_ai_provider_runtime` rejects
  unimplemented OpenAI runtime modes. `get_summarization_service` still selects
  the fake provider.
- **Tests**: `apps/api/tests/test_openai_provider.py` and
  `apps/api/tests/test_openai_sdk_adapter.py` use fake transports/clients,
  no-network socket guards, no-SDK-import guards, no-env-read guards, redaction
  assertions, malformed-response checks, and placeholder hygiene checks.

## 4. Cleanup Themes

Future cleanup should focus on:

- Clearer provider protocol naming so domain/service-level provider interfaces
  are distinguishable from OpenAI transport and SDK-like client protocols.
- Stronger separation between provider-facing prompts and SDK-like requests, so
  raw note fields and vendor-specific request shapes do not leak into service
  or route layers.
- Safer diagnostics boundaries that make redaction helper usage explicit before
  any provider, transport, or adapter diagnostic reaches logs or public errors.
- Adapter isolation from routes and services, keeping OpenAI transport and
  SDK-like concerns behind provider-owned modules.
- Stable typed dataclasses/protocols for domain results, provider requests,
  provider responses, SDK-like requests, SDK-like responses, and injected fake
  client/transport boundaries.
- Avoiding vendor-specific leakage into domain/service layers, including
  OpenAI-specific parameters, raw SDK response bodies, credential mode details,
  or retry internals.
- Reducing duplicate error mapping where provider and SDK adapter taxonomies
  overlap, without weakening existing safe public error behavior.
- Preserving the fake provider as the default runtime and CI path.

## 5. Refactor Candidates

Candidate future refactors include:

- Shared provider error taxonomy for timeout, unavailable/rate-limited, and
  malformed-response cases.
- Shared provider result type only if it simplifies domain mapping without
  exposing vendor-specific fields.
- Explicit diagnostic redaction helper usage at every provider, transport, and
  SDK-like adapter error boundary.
- Clearer module ownership between `openai_provider.py` and
  `openai_sdk_adapter.py`, especially around request/response conversion and
  failure mapping.
- Test fixture consolidation for fake prompts, fake transports, fake SDK
  clients, placeholder diagnostics, and no-network/no-env/no-import guards.
- Fake client naming cleanup so test doubles are clearly separated from any
  future real SDK client wrapper.
- Config validation boundary documentation for the difference between accepted
  future config names and runtime-enabled provider modes.

## 6. Risk Analysis

- **Breaking route compatibility**: Moving provider/domain types can
  accidentally alter `result.as_dict()` shape, status codes, or public error
  envelopes.
- **Weakening fail-closed runtime behavior**: Cleanup could accidentally wire
  `ai_provider=openai` into runtime selection or relax auth-mode validation.
- **Leaking prompt/content into diagnostics**: Refactors around errors,
  dataclass reprs, or fixtures can expose raw prompt text, titles, note content,
  or SDK-like bodies.
- **Accidentally adding dependency imports**: Pulling in real OpenAI SDK imports
  during cleanup would violate the denied dependency path.
- **Making SDK path look approved**: Naming or docs changes could imply a real
  SDK-backed runtime is authorized when it remains dependency-free and mocked.
- **Expanding scope into live provider work**: Boundary cleanup must not become
  credential wiring, WIF runtime, live harness setup, or provider execution.
- **Over-refactoring without tests**: Moving protocols/dataclasses without
  focused coverage risks regressions in route behavior, fake provider defaults,
  and redaction guarantees.

## 7. Testing Requirements Before Implementation

Before any future implementation slice changes provider boundary code, require:

- Focused pytest coverage for provider boundary modules.
- No-network socket patch tests for provider and SDK-like adapter paths.
- No environment-read assertions for dependency-free adapter construction and
  fake-client execution.
- No real SDK import assertions.
- No credential fixtures and no real-looking key, token, JWT, OIDC, or auth
  header examples.
- Redaction tests for prompts, note content, provider diagnostics, adapter
  diagnostics, auth-header-like fields, API-key-like fields, and SDK-like bodies.
- Route behavior compatibility checks for existing path, response envelope,
  public error mapping, and disabled/input-too-long/not-found behavior.
- Existing fake provider behavior preserved, including fake default selection
  in `get_summarization_service`.

## 8. Security Guardrails

Future cleanup must preserve these guardrails:

- No raw prompt logging.
- No note title or note content logging.
- No auth header, API key, credential, token, JWT, or OIDC logging.
- No token/JWT/OIDC examples in docs, tests, fixtures, screenshots, or logs.
- `gitleaks`-safe fixtures only, using synthetic placeholders that do not match
  real secret patterns.
- Fake provider remains the default.
- Dependency path remains **NOT APPROVED / DENIED**.
- Redaction must happen before diagnostics leave provider/adapter boundaries.

## 9. Implementation Sequencing

Future implementation should be split into small, explicit slices:

- Start with a small focused refactor slice that names the exact modules and
  public behavior that must remain unchanged.
- Use test-first boundary cleanup for protocol names, dataclass moves, error
  taxonomy consolidation, and diagnostic redaction behavior.
- Update docs after tests pass and after no runtime/dependency/secret changes
  are confirmed.
- Do not combine boundary cleanup with dependency install, credentials, live
  runtime, WIF runtime, route behavior changes, or live harness work.

## 10. Approval Boundaries

- This planning doc does not approve refactor implementation.
- This planning doc does not approve the OpenAI SDK dependency.
- This planning doc does not approve credentials or `.env` files.
- This planning doc does not approve live OpenAI API calls.
- This planning doc does not approve WIF runtime or token exchange.
- This planning doc does not reopen the live harness path.
- The OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- The live harness path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.

## 11. Future Slices

Recommended future sequence:

- **Slice 7M-J — Dependency-free adapter hardening tests** *(Complete — focused dependency-free adapter tests added; no SDK, credentials, network, or runtime route change.)*
- **Slice 7M-K — Redaction and diagnostics audit for AI provider boundary**
- **Slice 7M-L — Provider boundary cleanup/refactor implementation**
- **Slice 7N — Live harness skeleton** only if the live path is reopened and
  approved by the required named reviewers.

## 12. Definition Of Done

- This docs-only plan exists.
- Referenced docs are minimally updated to point to this plan and the next
  recommended task.
- No runtime code, tests, dependency manifests, lockfiles, CI workflows,
  `.env` files, SQL, migrations, generated state, credentials, SDK imports,
  network calls, WIF runtime, live harness, routes, API clients, SSE, frontend,
  Supabase, or public behavior are changed.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- Fake provider remains the default.
- Fast verification passes, or manual commit handoff is documented.
