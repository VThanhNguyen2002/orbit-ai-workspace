# OpenAI SDK Dependency-Free Strategy

## 1. Objective

Keep the OpenAI SDK adapter path dependency-free after dependency approval was denied. This document closes the current SDK dependency approval path as denied and defines how future work should continue without installing the OpenAI SDK.

## 2. Current Decision Status

- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- No SDK install is approved.
- No manifest/lockfile change is approved.
- No runtime import is approved.
- No credential use is approved.
- No OpenAI API call is approved.

## 3. Current Safe Baseline

- A mocked SDK adapter boundary exists (`apps/api/app/services/openai_sdk_adapter.py`).
- Tests use an injected fake SDK client without needing the real SDK.
- No real OpenAI SDK import is present in the codebase.
- No credentials are required or wired.
- No network calls are made.
- Fake provider remains the default for all runtime and CI paths.
- Route behavior is unchanged.
- Live harness is closed and blocked until named approvals exist.

## 4. Dependency-Free Strategy

Future work on the adapter must follow these rules:
- Continue using application-owned protocols and dataclasses for SDK boundaries.
- Keep the SDK client injected and mocked for all tests.
- Avoid importing any vendor SDK until explicit dependency approval exists.
- Keep the provider adapter boundary strictly isolated from route layers.
- Keep the prompt builder and redaction boundary mandatory for any request handling.
- Keep runtime provider selection fake-only by default.

## 5. Allowed Future Work

The following work is explicitly allowed without reopening the dependency approval gate:
- Mocked adapter tests.
- Typed interface refinement for the mocked boundaries.
- Redaction and fail-closed improvements.
- Docs planning.
- Provider boundary cleanup and refactoring.
- No-network proof tests.
- Dependency approval evidence preparation (docs-only).

## 6. Explicitly Blocked Work

The following work remains explicitly blocked:
- SDK installation.
- Dependency manifest or lockfile edits (`pyproject.toml`, `package.json`, etc.).
- Runtime OpenAI import.
- Live OpenAI calls.
- Credential usage or wiring.
- Workload Identity Federation (WIF) runtime implementation.
- Route or provider switches to enable live provider by default.
- Default CI live tests.
- `workflow_dispatch` live provider job.
- Production API-key fallback.

## 7. Testing Direction

- Keep all tests dependency-free and network-free.
- The fake SDK client remains the definitive test boundary.
- Patch sockets or equivalents for no-network proof tests where applicable.
- Keep malformed response, timeout, and rate-limit simulation tests.
- Keep secret redaction tests active.
- Avoid adding real-looking keys, tokens, or JWTs in tests or fixtures.

## 8. Runtime Guardrails

- Fake provider remains the only enabled default.
- `ai_provider=openai` must remain fail-closed unless explicitly approved by a future runtime slice.
- No route switch is allowed.
- No background summarization is allowed.
- No persisted live provider outputs are permitted.
- No live harness execution is permitted.

## 9. Reopen Criteria

The SDK dependency path may reopen only if ALL of the following are satisfied:
- Named reviewer approvals exist for the dependency gates.
- Exact SDK version is selected and pinned.
- License is reviewed and approved.
- Transitive dependencies are enumerated and reviewed.
- Vulnerability scan plan is approved.
- CI/build impact is reviewed.
- Rollback plan is approved.
- Credential mode is separately approved.
- External review sign-off exists.

## 10. Future Path

Recommended next steps for the dependency-free adapter:
- **Slice 7M-H — Dependency-free OpenAI adapter hardening plan** *(Complete — Record: `docs/openai-sdk-adapter-hardening-plan.md`.)*
- **Slice 7M-I — Provider boundary cleanup/refactor planning**
- **Slice 7N — Live harness skeleton** (only if live path is reopened and approved by all 8 reviewers)
