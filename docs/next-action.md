# Next Action

## Objective

Prepare **Slice 6H-3B-4C - RLS validation tests behind opt-in harness**. Slice
6H-3B-4B adds the local-only Markdown artifact in
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md),
but that artifact has not been executed and is not approved for automatic
execution.

The next bounded step is to add skipped-by-default RLS validation tests behind
the existing opt-in harness shape. That work must follow
[database-migration-policy.md](security/database-migration-policy.md),
[notes-migration-rls-validation-plan.md](notes-migration-rls-validation-plan.md),
[notes-migration-rls-approval-record.md](notes-migration-rls-approval-record.md),
and the local artifact.

Security gate: Slice 6H-3B-4C may add tests that remain skipped by default, but
it must not execute the local artifact or run RLS validation until a separate
execution approval is recorded.

## Expected Files To Change

- Skipped-by-default RLS validation test scaffolding behind explicit opt-in
  harness controls, only after confirming it cannot execute without approval.
- Minimal documentation updates that identify the test execution gate.
- No local or hosted Supabase execution.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, generated Supabase state, `.env` files, or RLS test execution.

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

- RLS validation tests are present only as skipped-by-default or explicitly
  gated scaffolding.
- Tests require explicit local execution approval before they can apply or
  validate the local artifact.
- Default CI remains credential-free and does not run Supabase.
- No service-role credential is introduced into request-path code, test inputs,
  or default tests.
- No real data, credentials, generated Supabase state, dumps, backups, SQLite/db
  files, `.env` files, or hosted resources are used.
- Memory persistence remains the default; live repository wiring remains
  deferred.

## Risks

- Tests could create false confidence if they run without applying the reviewed
  artifact in an approved local target.
- Harness gating mistakes could accidentally attempt live/local Supabase access
  in default CI.
- Service-role values must remain rejected from request-path validation.
- The local-only artifact still does not prove hosted staging readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## Rollback Notes

If Slice 6H-3B-4C work is unsuitable, revert only that work. Keep completed
shared contracts, backend skeleton, API client methods, Slice 6E/6G boundaries,
Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor factory/tests, the
Slice 6H-3 and Slice 6H-3B plans, Slice 6H-3A fake-client repository tests,
Slice 6H-6 contract drift guard, Slice 6H-3B-1 adapter interface/tests, Slice
6H-3B-2 fake SDK transport tests, Slice 6H-3B-3 harness plan, Slice 6H-3B-3A
skipped harness skeleton, Slice 6H-3B-3B local setup guide, Slice 6H-3B-4
migration/RLS validation plan, Slice 6H-3B-4A draft review packet, Slice
6H-3B-4A-R approval record, Slice 6H-3B-4B local artifact, and the database
artifact security policy intact.

## External Review Gate

Before considering the slice complete:

1. Render the full final report clearly and structurally.
2. Include:
   - architectural decisions
   - tradeoffs
   - risks
   - shortcuts/deferred items
   - verification evidence
   - CI status
   - security observations
3. Assume the rendered output will be reviewed externally by ChatGPT as an
   extended engineering review gate.
4. Be explicit about:
   - anything intentionally deferred
   - anything scaffold-only
   - anything mocked/faked
   - any remaining inconsistencies
   - any temporary implementations
5. Do not hide weak points or unresolved risks.
6. Do not automatically continue to the next slice after rendering the report.
7. Wait for external ChatGPT review feedback before proceeding further.

The rendered report must be detailed enough for:

- architecture review
- consistency review
- security review
- CI/reliability review
- implementation-scope review

Treat the final report as a handoff artifact for external engineering audit.
