# Next Action

## Objective

Recommended next task: **Slice 7M-D — Resolve OpenAI SDK dependency approval
prerequisites**.

Slice 7M-C is complete. The OpenAI SDK dependency approval record records the
dependency decision as NOT APPROVED / DENIED. All 12 required approval gates
are MISSING. No named reviewer approval exists for any gate.

## Slice 7M-C Result

Slice 7M-C adds:

- `docs/openai-sdk-dependency-approval-record.md` — explicit denial record for
  the `openai` Python SDK dependency. Decision: **NOT APPROVED / DENIED**.
  All 12 gate items (dependency owner, security/privacy, license, supply-chain,
  CI impact, rollback, no-default-live-run, external review, pinned version,
  transitive dep review, vulnerability scan plan, update policy) are MISSING.

No SDK install, dependency manifest change, lockfile change, credential,
`.env` file, live API call, WIF runtime, token exchange, backend route change,
API client change, SSE/frontend work, SQL, migration, Supabase work, or
generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 7M-D Scope

Resolve the specific denial rationale items from the approval record:

- Select candidate SDK package and version.
- Review and document SDK license.
- Enumerate transitive dependencies.
- Prepare a vulnerability scan plan.
- Review CI/build impact.
- Document a rollback plan.
- Solicit named reviewers for each gate.

Docs-only. No SDK install, credential, live harness, or runtime change.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED / DENIED.** All dependency approval gates
must be satisfied before any SDK install is authorized.

## Definition Of Done

- Denial rationale items are addressed with concrete evidence.
- No SDK install, dependency manifest change, lockfile change, credential,
  `.env` file, live API call, WIF runtime, token exchange, live harness, route
  behavior change, API client change, SSE/frontend work, SQL, migration,
  Supabase work, or generated state is added.
- Fake provider remains the default.

Do NOT proceed to Slice 7M-D automatically.
