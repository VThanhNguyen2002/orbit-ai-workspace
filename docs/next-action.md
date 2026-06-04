# Next Action

## Objective

Recommended next task: **Slice 8D — Minimal summary history UI consumption**
(split into **Slice 8D-A — Inspect/init minimal mobile screen structure** and **Slice 8D-B — Summary history UI consumption**).

Slice 8C is complete. Do not proceed to OpenAI live provider work, Supabase
live runtime, Docker, RLS, WIF runtime, SDK dependency installation, credential
use, frontend implementation, or persistence work unless those paths are
explicitly reopened or selected for the next approved slice.

## Slice 8C Result

Slice 8C adds the frontend consumption plan for note summary history:

- Created `docs/summary-history-ui-consumption-plan.md`.
- Documented note details demo flow, transience / memory-only reset warning, empty history, loading, and error states.
- Clarified UI/API boundary requiring the UI to consume `packages/api-client` through an app-level API access layer or state hook rather than direct raw fetch inside screen components.
- Identified the uninitialized `apps/mobile` directory as a key implementation risk and split the next phase (Slice 8D) into 8D-A (mobile boilerplate/structure inspection & init) and 8D-B (UI consumption implementation).
- Evaluated candidate integration options and confirmed Option A (minimal component in `apps/mobile`) as the recommended direction.
- Updated `docs/security/privacy-and-data-handling.md` to establish strict constraints against UI leakage of LLM credentials, provider details, or diagnostics.

No runtime code, tests, package/lockfile configurations, credentials, environment variables, Supabase/database state, real LLM calls, or SDK dependencies were added. The fake provider remains the default, and the OpenAI SDK dependency remains **NOT APPROVED / DENIED**.

## Slice 8D Sub-Slices

- **Slice 8D-A — Inspect/init minimal mobile screen structure**: Initialize standard React Native/Expo structure or inspect the boilerplate in `apps/mobile` to ensure the project can build, lint, and typecheck successfully.
- **Slice 8D-B — Summary history UI consumption**: Implement the UI hook, empty/loading/error states, history list render, summarize trigger, and reset warning.

## Live Provider And Supabase Status

- Fake provider remains the default.
- OpenAI live harness remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- Supabase/Docker/live RLS work remains out of scope unless explicitly approved.

## Definition Of Done

- Execute Slice 8D-A before writing UI components.
- Keep backend behavior unchanged (fake-provider-only and memory-only).
- No live provider, SDK dependency, credential, `.env`, SQL/migration, Supabase generated state, Docker, or SSE/frontend implementation beyond the approved scope is introduced.
- Verification and security checks pass for any approved changes.
