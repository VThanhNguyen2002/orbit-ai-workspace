# Next Action

## Objective

Prepare **Slice 6H-3B-4C-DR - Local-only RLS dry-run execution runbook**.

Slice 6H-3B-4C-LA records constrained approval for a future local-only RLS
dry-run attempt in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
The approval is limited to a disposable local Supabase target, the local-only
Markdown artifact, opt-in local harness, synthetic users, synthetic Notes rows,
redacted evidence, and cleanup verification.

The next bounded step is to prepare the careful execution runbook. The dry-run
must not execute automatically merely because approval has been recorded.

## Why This Is Next

The local-only approval boundary is now explicit, but execution still needs a
runbook that walks through preflight checks, stop conditions, evidence capture,
rollback/cleanup verification, and post-run reporting before any approved local
attempt begins.

Hosted staging planning remains deferred until the local-only dry-run is either
completed with accepted evidence or explicitly deferred.

## Expected Files To Change

- A local-only RLS dry-run execution runbook, if created by the next slice.
- Minimal references from the approval, validation, harness, policy, or
  next-action docs, if needed.

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

- The runbook is documented without executing the dry-run automatically.
- The runbook repeats the approved local-only scope and the explicitly not
  approved items.
- Pre-execution checks, stop conditions, redacted evidence capture, and cleanup
  verification are operationally clear.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  service-role request-path usage, live repository mode, and public Notes API
  behavior remain out of scope.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, local Supabase run, or RLS validation execution is
  introduced automatically.

## Risks

- A runbook could be mistaken for permission to run against hosted or
  production targets unless the approved local-only scope is repeated clearly.
- Cleanup remains unproven until the approved disposable local dry-run occurs.
- Service-role values must remain outside request-path validation.
- The local-only dry-run still will not prove hosted staging readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## External Review Gate

Before considering the next slice complete:

1. Render the full final report clearly and structurally.
2. Include runbook scope, non-goals, risks, deferred work, verification
   evidence, CI status, and security observations.
3. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
4. Do not automatically continue to execution after rendering the report.
5. Wait for external ChatGPT review feedback before proceeding further.
