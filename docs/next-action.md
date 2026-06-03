# Next Action

## Objective

Recommended next task: **Slice 7M-H — Dependency-free OpenAI adapter hardening plan**.

Slice 7M-G is complete. The dependency-free strategy for the OpenAI SDK adapter has been formalized since the SDK dependency approval was denied.

## Slice 7M-G Result

Slice 7M-G adds:

- `docs/openai-sdk-dependency-free-strategy.md` — documents the safe baseline, allowed future work, explicitly blocked work, and testing direction for keeping the mocked SDK adapter dependency-free.

No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, backend route change, API client change, SSE/frontend work, SQL, migration, Supabase work, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 7M-H Scope

Dependency-free OpenAI adapter hardening plan:

- Plan how to refine the mocked SDK adapter boundary and type interfaces without introducing the real SDK dependency.
- Document fail-closed improvements and provider boundary cleanup.

Docs-only. No SDK install, credential, live harness, or runtime change.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED / DENIED.** All dependency approval gates must be satisfied before any SDK install is authorized.

## Definition Of Done

- Hardening plan is documented.
- No SDK install, dependency manifest change, lockfile change, credential, `.env` file, live API call, WIF runtime, token exchange, live harness, route behavior change, API client change, SSE/frontend work, SQL, migration, Supabase work, or generated state is added.
- Fake provider remains the default.

Do NOT proceed to Slice 7M-H or 7M-I automatically.
