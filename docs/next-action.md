# Next Action

## Objective

Recommended next task: **Slice 6H-3B-4C-B2 — Resolve remaining local RLS
dry-run blockers**.

Slice 6H-3B-4C-E2 re-attempted preflight on 2026-05-30 and was blocked for
a second consecutive time. Blockers are identical to the prior attempt:
no disposable local Supabase target, no Supabase CLI on PATH, and all
required environment variables are absent. See updated
[notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md).

Slice 6H-3B-4C-LA records constrained approval for a future local-only RLS
dry-run attempt in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
The approval is limited to a disposable local Supabase target, the local-only
Markdown artifact, opt-in local harness, synthetic users, synthetic Notes rows,
redacted evidence, and cleanup verification.

Slice 6H-3B-4C-DR added the local-only execution runbook in
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
without executing the artifact, running Supabase locally, or validating RLS.

Slice 6H-3B-4C-E attempted preflight and stopped before execution because the
required disposable local target configuration and synthetic user token inputs
were absent. The blocked result is recorded in
[notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md).

Slice 6H-3B-4C-B records the blocker-resolution checklist in
[notes-local-rls-dry-run-blocker-resolution.md](notes-local-rls-dry-run-blocker-resolution.md).

The next bounded step is to re-attempt the local-only dry-run only after those
blockers are resolved outside git. Execution must not happen automatically
merely because approval has been recorded, the runbook exists, a blocked report
exists, or the blocker-resolution checklist exists. The operator must re-check
every precondition immediately before retrying the dry-run.

## Why This Is Next

The local-only approval boundary, runbook, blocked report, and
blocker-resolution checklist are explicit, but RLS behavior has not been
validated. The next step is to retry Slice 6H-3B-4C-E only after the disposable
local target, synthetic users, public-key value, synthetic caller tokens, and
cleanup plan are prepared outside git and verified without printing raw values.

Hosted staging planning remains deferred until the local-only dry-run is either
completed with accepted evidence or explicitly deferred.

## Expected Files To Change

- A redacted local-only dry-run execution report, if the checklist is satisfied
  and the runbook is followed.
- A refreshed blocked report, if the checklist is still not satisfied.
- Minimal references from planning docs, if the re-attempt outcome changes
  status.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, generated Supabase state, `.env` files, SQL files, migrations, or RLS
test execution outside the approved manual local-only runbook flow.

## Commands To Run

Re-check the blocker-resolution checklist and runbook preconditions before
retrying manual local-only execution. The dry-run must use only a disposable
local target, synthetic users, synthetic Notes rows, local-only public key plus
caller-token inputs, and redacted evidence. Stop if any checklist or runbook
stop condition applies.

```bash
pnpm --filter @synapse/shared contracts:export
pnpm --filter @synapse/shared contracts:check

cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/shared test
pnpm --filter @synapse/api-client test
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- Missing local-only prerequisites are prepared outside git before execution,
  or execution remains explicitly blocked.
- No real URL, key, token, user identifier, note identifier, or note content is
  committed.
- The operator can prove that cleanup is actionable before retrying the dry-run.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  service-role request-path usage, live repository mode, and public Notes API
  behavior remain out of scope.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, or automatic RLS validation execution is introduced.

## Risks

- A retry could be mistaken for hosted or production permission unless the
  approved local-only scope is re-checked immediately before execution.
- Cleanup remains unproven until an actual disposable local target exists.
- Service-role values must remain outside request-path validation.
- The local-only dry-run remains blocked until local target and synthetic token
  inputs exist.
- A future successful local-only dry-run still will not prove hosted staging
  readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## External Review Gate

Before considering the next slice complete:

1. Render the full final report clearly and structurally.
2. Include runbook scope, non-goals, risks, deferred work, verification
   evidence, CI status, and security observations.
3. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
4. Do not automatically continue to hosted staging planning after rendering the
   report.
5. Wait for external ChatGPT review feedback before proceeding further.
