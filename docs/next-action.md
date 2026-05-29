# Next Action

## Objective

Prepare **Slice 6H-3B-4C-LA - Grant local-only RLS dry-run approval**.

Slice 6H-3B-4C-L adds
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
with the local-only objective, non-goals, current status, preconditions,
preflight checklist, manual dry-run sequence, evidence format, cleanup
checklist, and approval decision point.

The next bounded step is an approval decision only. It may grant local-only
dry-run execution approval or keep execution blocked. It must not execute the
artifact automatically.

## Why This Is Next

Local execution approval is still pending, but the previously missing
preflight, evidence, redaction, and rollback/cleanup expectations are now
documented for review.

Hosted staging planning remains deferred until local-only execution approval is
granted or explicitly deferred.

## Expected Files To Change

- The local RLS execution approval record, if a reviewer grants approval or
  records that execution remains blocked.
- Minimal references from planning docs, if the approval decision changes the
  recommended next task.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, generated Supabase state, `.env` files, SQL files, migrations, or RLS
test execution.

## Commands To Run

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

- The approval decision is recorded explicitly.
- If granted, approval is limited to a disposable local-only dry-run with
  synthetic users, synthetic Notes rows, redacted evidence, and cleanup
  requirements.
- If not granted, execution remains blocked and the reason is recorded.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  service-role request-path usage, live repository mode, and public Notes API
  behavior remain out of scope.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, local Supabase run, or RLS validation execution is
  introduced automatically.

## Risks

- Approval language could be mistaken for hosted or production execution unless
  it stays explicitly local-only.
- Cleanup plans remain untested until an approved disposable local dry-run
  occurs.
- Service-role values must remain outside request-path validation.
- The local-only artifact still does not prove hosted staging readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## External Review Gate

Before considering the next slice complete:

1. Render the full final report clearly and structurally.
2. Include approval scope, non-goals, risks, deferred work, verification
   evidence, CI status, and security observations.
3. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
4. Do not automatically continue to execution after rendering the report.
5. Wait for external ChatGPT review feedback before proceeding further.
