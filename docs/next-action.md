# Next Action

## Objective

Recommended next task: **Slice 7M-I — Provider boundary cleanup/refactor planning**.

Slice 7M-H is complete. The dependency-free OpenAI adapter hardening plan has been documented.

## Slice 7M-H Result

Slice 7M-H adds:

- `docs/openai-sdk-adapter-hardening-plan.md` — documents the plan to harden the mocked SDK adapter boundary (tests, diagnostics, redaction) without installing the SDK.

No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, backend route change, API client change, SSE/frontend work, SQL, migration, Supabase work, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 7M-I Scope

Provider boundary cleanup/refactor planning:

- Plan the cleanup of the provider boundary (e.g., separating protocol definitions, consolidating provider logic).
- Ensure vendor-specific logic does not leak into the core domain layers.

Docs-only. No SDK install, credential, live harness, or runtime change.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED / DENIED.** All dependency approval gates must be satisfied before any SDK install is authorized.

## Definition Of Done

- Cleanup/refactor plan is documented.
- No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, live harness, route behavior change, API client change, SSE/frontend work, SQL, migration, Supabase work, or generated state is added.
- Fake provider remains the default.

Do NOT proceed to Slice 7M-I automatically.
