# Next Action

## Objective

Recommended next task: **Slice 8D-C — Minimal summary history screen/component
decision**.

Implement a rendered summary history screen/component only if existing
dependencies support it without package manifest or lockfile changes. If they
do not, create a separate Expo/mobile initialization approval plan before any
rendered UI work.

Slice 8D-B is complete. Do not proceed to OpenAI live provider work, Supabase
live runtime, Docker, RLS, WIF runtime, SDK dependency installation, credential
use, package/dependency changes, rendered frontend implementation, or
persistence work unless those paths are explicitly reopened or selected for the
next approved slice.

## Slice 8D-B Result

Slice 8D-B adds a dependency-free mobile summary history structure:

- Added `apps/mobile/tsconfig.json` for direct TypeScript verification.
- Added `apps/mobile/src` exports for future mobile source code.
- Added an app-level API client construction boundary in `apps/mobile/src/api/synapseClient.ts`.
- Added `summaryHistoryApi` as an injected feature adapter around `client.ai.listNoteSummaries(note_id)`.
- Added deterministic summary history view-state mapping for `idle`, `loading`, `empty`, `success`, and `error`.
- Added a non-rendering note summary history placeholder module for future screen regions.

No rendered React Native or Expo UI was added. No dependencies, package
manifests, lockfiles, credentials, environment variables, Supabase/database
state, real LLM calls, SDK dependencies, SQL/migrations, Docker work, live
provider wiring, WIF runtime, or `.gitleaksignore` broadening were added. The
fake provider remains the default, and the OpenAI SDK dependency remains **NOT
APPROVED / DENIED**.

## Slice 8D-C Gate

- If existing dependencies support a rendered component without manifest or
  lockfile changes, implement the smallest summary history screen/component
  that consumes the 8D-B API/view-state boundary.
- If rendered UI requires Expo, React Native, React, JSX tooling, testing
  packages, or any package/lockfile change, stop and prepare a mobile
  initialization approval plan instead.
- Keep backend behavior unchanged: fake-provider-only and memory-only.

## Live Provider And Supabase Status

- Fake provider remains the default.
- OpenAI live harness remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- Supabase/Docker/live RLS work remains out of scope unless explicitly approved.

## Definition Of Done

- Execute Slice 8D-C only after confirming the dependency/package gate.
- Keep backend behavior unchanged (fake-provider-only and memory-only).
- No live provider, SDK dependency, credential, `.env`, SQL/migration, Supabase generated state, Docker, package/lockfile change, or rendered frontend implementation beyond the approved scope is introduced.
- Verification and security checks pass for any approved changes.
