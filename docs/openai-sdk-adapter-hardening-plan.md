# OpenAI SDK Adapter Hardening Plan

## 1. Objective

Plan hardening work for the dependency-free OpenAI adapter boundary without adding SDK dependency, credentials, live calls, or runtime route changes. The goal is to improve safety, diagnostics, test coverage, and maintainability of the mocked adapter boundary.

## 2. Non-goals

This hardening plan explicitly excludes:
- OpenAI SDK installation
- dependency changes (manifests, lockfiles)
- API calls
- credentials
- `.env` files
- WIF runtime
- live harness
- route/API behavior changes
- SSE/frontend/Supabase work

## 3. Current Safe Baseline

- A mocked SDK adapter boundary exists (`apps/api/app/services/openai_sdk_adapter.py`).
- The fake SDK client is injected in tests.
- There is no real SDK import in the codebase.
- There are no credentials or environment variable reads for the SDK.
- There are no network calls to OpenAI.
- The fake provider remains the default.
- The SDK dependency approval path remains denied.

## 4. Hardening Themes

Planned improvements focus on:
- Typed request/response models for the mocked boundary.
- Safe error taxonomy to prevent leaking underlying provider error details.
- Redaction boundaries for prompts, contents, and any metadata.
- Timeout, rate-limit, and malformed response simulation behavior.
- Unsafe/empty output handling.
- No-network proof mechanisms in tests.
- No-secret fixtures.
- Maintainable adapter isolation from route handlers.

## 5. Test Hardening Plan

Future tests will be designed to cover:
- Stricter fake SDK response validation against expected model shapes.
- Safe diagnostics and `repr()`/`str()` behavior to avoid leaking context.
- Assertion of no prompt/content leakage in errors or logs.
- Assertion of no auth header/token/key leakage.
- Assertion of no environment variable reads during adapter initialization.
- Socket/network patch proof to strictly enforce no-network boundaries.
- Edge cases for empty, oversized, or unsafe output from the fake provider.
- Behavior when a mock SDK-like client is unavailable.
- Deterministic mapping to provider-safe responses.

## 6. Security Hardening Plan

The following security properties must be maintained and verified:
- No raw prompt logging.
- No note content logging.
- No raw SDK body logging.
- No `Authorization` header logging.
- No API key logging.
- No JWT/OIDC/access-token examples in the codebase.
- Only `gitleaks`-safe fixtures are permitted.
- The redaction helper is mandatory for all inputs and outputs crossing the provider boundary.

## 7. Runtime Guardrails

- The fake provider remains the default.
- OpenAI runtime remains disabled/fail-closed.
- No route switch can enable live providers.
- No background summarization tasks can run against a live provider.
- No persisted live outputs are allowed.
- No live harness execution.
- No `workflow_dispatch` live validation.

## 8. Maintainability Plan

- Keep the adapter fully isolated from route logic.
- Keep the internal provider interface stable and protocol-driven.
- Keep the prompt builder as the only prompt assembly boundary.
- Avoid vendor-specific leakage (e.g., OpenAI-specific kwargs) into domain/service layers.
- Keep any future dependency install securely behind the dependency approval gate.

## 9. Approval Boundaries

- This hardening plan **does not** approve SDK installation.
- This hardening plan **does not** approve credentials.
- This hardening plan **does not** approve live API calls.
- This hardening plan **does not** reopen the live harness path.
- The OpenAI SDK dependency approval remains **DENIED**.

## 10. Future Slices

Recommended sequence for following this hardening plan:
- **Slice 7M-I — Provider boundary cleanup/refactor planning** *(Complete — Record: `docs/openai-provider-boundary-cleanup-plan.md`.)*
- **Slice 7M-J — Dependency-free adapter hardening tests** *(Complete — stricter fake SDK response validation, safe malformed-response mapping, redacted diagnostics, no-network/no-env proof.)*
- **Slice 7M-K — Redaction and diagnostics audit for AI provider boundary**
- **Slice 7M-L — Provider boundary cleanup/refactor implementation**
- **Slice 7N — Live harness skeleton** (only if the live path is reopened and approved by all named reviewers)

## 11. Definition of Done

- Docs-only modifications.
- No runtime, dependency, or secret changes.
- Verification pass or manual commit handoff completed.
