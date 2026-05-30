# Next Action

## Objective

Recommended next task: **Slice 6H-3B-4C-E - Execute local-only RLS dry-run**.

Slice 6H-3B-4C-LA records constrained approval for a future local-only RLS
dry-run attempt in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
The approval is limited to a disposable local Supabase target, the local-only
Markdown artifact, opt-in local harness, synthetic users, synthetic Notes rows,
redacted evidence, and cleanup verification.

Slice 6H-3B-4C-DR adds the local-only execution runbook in
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
without executing the artifact, running Supabase locally, or validating RLS.

The next bounded step is to execute the local-only dry-run manually by
following that runbook in a disposable local target. Execution must not happen
automatically merely because approval has been recorded or the runbook exists.
The operator must re-check every precondition immediately before the attempt.

## Why This Is Next

The local-only approval boundary and runbook are now explicit, but RLS behavior
has not been validated. The next step is a deliberate local-only attempt that
walks through the runbook's preflight checks, stop conditions, evidence
capture, rollback/cleanup verification, and post-run reporting.

Hosted staging planning remains deferred until the local-only dry-run is either
completed with accepted evidence or explicitly deferred.

## Expected Files To Change

- A redacted local-only dry-run execution report, if the manual attempt is
  performed and evidence is accepted for commit.
- Minimal references from the runbook, approval, validation, harness, policy,
  or next-action docs, if needed.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, generated Supabase state, `.env` files, SQL files, migrations, or RLS
test execution outside the approved manual local-only runbook flow.

## Commands To Run

Re-check the runbook preconditions before any manual local-only execution. The
dry-run must use only a disposable local target, synthetic users, synthetic
Notes rows, local-only public key plus caller-token inputs, and redacted
evidence. Stop if any runbook stop condition applies.

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

- The dry-run is executed manually only after re-checking the runbook
  preconditions, or local execution is explicitly deferred.
- Any execution report uses redacted evidence and labels scaffold-only skips as
  non-RLS-enforcement evidence.
- Cleanup verification is recorded for the disposable local target.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  service-role request-path usage, live repository mode, and public Notes API
  behavior remain out of scope.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, or automatic RLS validation execution is introduced.

## Risks

- A manual run could be mistaken for hosted or production permission unless the
  approved local-only scope is re-checked immediately before execution.
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
4. Do not automatically continue to hosted staging planning after rendering the
   report.
5. Wait for external ChatGPT review feedback before proceeding further.
