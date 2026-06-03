# Next Action

## Objective

Recommended next task: **Slice 7M-L — Provider boundary cleanup/refactor implementation**.

Slice 7M-K is complete. Redaction and diagnostics behavior across the AI provider boundary has been audited and hardened.

## Slice 7M-K Result

Slice 7M-K adds:

- `docs/openai-provider-redaction-diagnostics-audit.md` — records the AI provider redaction and diagnostics audit outcome.
- focused tests for prompt/content redaction, raw provider/SDK payload redaction,
  auth/key/token/assertion field redaction, WIF fake error safety, and fixture hygiene.
- stricter redaction helper key coverage for raw payload and token/assertion
  diagnostic fields.

No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, backend route change, API client change, SSE/frontend work, SQL, migration, Supabase work, live runtime, `.gitleaksignore` broadening, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 7M-L Scope

Provider boundary cleanup/refactor implementation:

- Implement selected provider boundary cleanup/refactor work from
  `docs/openai-provider-boundary-cleanup-plan.md`.
- Preserve route behavior, fake provider default, fail-closed OpenAI runtime,
  redaction guarantees, no-network tests, no SDK dependency, and no live path.

No SDK install, credential, live harness, route/API behavior change, dependency change, or live provider runtime.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED / DENIED.** All dependency approval gates must be satisfied before any SDK install is authorized.

## Definition Of Done

- Provider boundary cleanup/refactor implementation is completed with focused tests and unchanged runtime/live scope.
- No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, live harness, route behavior change, API client change, SSE/frontend work, SQL, migration, Supabase work, or generated state is added.
- Fake provider remains the default.

Do NOT proceed to Slice 7M-L automatically.
