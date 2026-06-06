# Next Action

## Objective

Recommended next task: **Slice 8G — Rendered mobile demo unblock decision packet**.

Create a docs-only approval/evidence packet that decides whether the project can
move from API-level fake-provider demo readiness toward a rendered mobile demo.
This should revisit the deferred Expo/React Native initialization gates without
initializing runtime UI unless explicit approvals already exist.

Suggested inspection targets:

1. `docs/mobile-expo-initialization-approval-plan.md`
2. `docs/mobile-expo-initialization-approval-record.md`
3. `docs/summary-history-ui-consumption-plan.md`
4. `docs/backend-product-demo-polish-record.md`
5. `apps/mobile/src/features/notes/*`

Keep the work dependency-free and decision-focused. If approval evidence is
still missing, record the blocker clearly and leave rendered mobile UI deferred.

## Slice 8F Result

Slice 8F completed the dependency-free API-level demo runbook for the existing
fake-provider flow:

- `docs/backend-product-demo-polish-record.md` now documents the exact API demo sequence: create a demo note, load note detail, list empty summary history, generate fake summaries, and list generated summaries newest first.
- The runbook names the memory-only summary-history reset limitation.
- The runbook points to the existing backend test that verifies the full demo sequence and AI surface/log leak checks.
- No API behavior, backend service code, API client code, mobile view-state code, tests, package manifests, lockfiles, dependencies, Expo runtime, rendered mobile UI, live provider, OpenAI SDK, credentials, `.env`, WIF runtime, SQL, migrations, Supabase state, Docker work, or generated state was added.

## Slice 8G Gate

- Do not install dependencies, modify package manifests, or modify lockfiles.
- Do not initialize Expo, React Native runtime UI, routers, or native files unless the packet finds explicit approvals for all required gates and the slice scope is updated accordingly.
- Do not introduce a live provider, OpenAI SDK, credentials, `.env`, WIF runtime, SSE streaming, SQL, migrations, Supabase state, Docker work, or generated state.
- Use only the existing fake-provider endpoints and memory-only backend state.
- Do not change API behavior, mobile runtime behavior, or rendered UI in a docs-only decision packet.

## Definition Of Done

- The packet states whether rendered mobile demo initialization is approved, deferred, or blocked.
- Missing approval evidence is listed as concrete prerequisites.
- If still deferred or blocked, the next safe product step is named.
- Fake-provider-only demo constraints remain unchanged.
- Security/privacy constraints remain unchanged and fast checks pass.
