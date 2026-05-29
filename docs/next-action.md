# Next Action

## Objective

Prepare **Slice 6H-3B-4C-R - Record explicit local RLS execution approval**.

Slice 6H-3B-4C adds skipped-by-default Notes RLS validation case scaffolding in
`apps/api/tests/integration/test_notes_rls_validation.py`. The tests define the
required user A/user B validation matrix and safety gates behind the existing
opt-in live harness, but they do not execute RLS validation.

The local-only Markdown artifact at
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md)
has still not been executed and is not approved for automatic execution.

## Why This Is Next

No explicit local RLS execution approval is recorded. Before the local artifact
or RLS validation cases may be executed, reviewers need a bounded approval
record that identifies the disposable local target, synthetic user/data rules,
cleanup expectations, evidence format, redaction requirements, and exact manual
command boundary.

This remains separate from hosted staging validation. Hosted staging planning
can follow after local execution approval is recorded or explicitly deferred.

## Expected Files To Change

- A local RLS execution approval record or equivalent approval handoff document.
- Minimal references from the RLS validation plan or approval record, if needed.

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

- Explicit local RLS execution approval is recorded, or the decision to defer it
  is recorded with rationale.
- The approval record names the disposable local target type and states that
  hosted staging and production remain out of scope.
- Synthetic-only user/data rules, cleanup evidence, redaction requirements, and
  no-service-role request-path constraints are explicit.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, or RLS validation execution is introduced by default.

## Risks

- Approval language could accidentally authorize hosted staging or production
  execution if the target boundary is vague.
- Validation could create false confidence if the approved artifact is not
  actually applied before the RLS cases run.
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
4. Do not automatically continue to the next slice after rendering the report.
5. Wait for external ChatGPT review feedback before proceeding further.
