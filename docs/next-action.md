# Next Action

## Objective

Prepare **Slice 6H-3B-4C-L - Local-only RLS execution dry-run preparation**.

Slice 6H-3B-4C-R records the local execution approval gate in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
That record keeps local RLS execution approval pending and explicitly does not
approve running the local artifact or opt-in RLS validation tests.

The next bounded step is to prepare the local-only dry-run checklist needed
before a reviewer can grant execution approval. This should remain
documentation/preparation only.

## Why This Is Next

Local execution approval is still pending because the repository does not yet
record the disposable local target assumptions, exact manual command boundary,
rollback/cleanup procedure, evidence format, redaction checklist, and reviewer
sign-off format for a future local-only execution attempt.

Hosted staging planning remains deferred until local-only execution approval is
granted or explicitly deferred.

## Expected Files To Change

- Local-only dry-run preparation documentation for the disposable local target,
  command boundary, cleanup/rollback steps, evidence format, and redaction
  checklist.
- Minimal references from existing RLS approval or validation docs, if needed.

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

- The local-only dry-run preparation is documented without executing anything.
- The preparation identifies the disposable local target assumptions and keeps
  hosted staging and production out of scope.
- Cleanup/rollback steps, evidence format, redaction requirements, and reviewer
  sign-off format are explicit.
- Local RLS execution approval remains pending unless a separate approval record
  explicitly grants it.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, local Supabase run, or RLS validation execution is
  introduced by default.

## Risks

- Preparation language could be mistaken for execution approval if the pending
  approval state is not repeated clearly.
- Cleanup plans may be incomplete until tested against a disposable local target.
- Service-role values must remain outside request-path validation.
- The local-only artifact still does not prove hosted staging readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## External Review Gate

Before considering the slice complete:

1. Render the full final report clearly and structurally.
2. Include architectural decisions, tradeoffs, risks, deferred work,
   verification evidence, CI status, and security observations.
3. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
4. Do not automatically continue to execution after rendering the report.
5. Wait for external ChatGPT review feedback before proceeding further.
