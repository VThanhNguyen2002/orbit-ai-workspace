# Notes Local RLS Execution Approval Record

## Status

Slice 6H-3B-4C-R records the approval gate for a future local-only Notes RLS
execution attempt.

Local RLS execution approval is **pending**. This record does not grant approval
to execute the local artifact or run opt-in RLS validation tests yet, because
the disposable local target, exact rollback/cleanup steps, execution evidence
format, and explicit reviewer approval for execution are not fully recorded.

This is documentation-only. It does not execute SQL, create a migration, run
Supabase locally, connect to hosted Supabase, run live RLS tests, add
credentials, enable live repository mode, or change public Notes API behavior.

## Approval Decision

Local-only execution may be explicitly granted later only if every condition in
this record is satisfied and a reviewer records that approval before execution.

Current decision:

- Local RLS execution approval: pending.
- Production execution approval: not granted.
- Staging execution approval: not granted.
- Hosted Supabase execution approval: not granted.
- Default CI execution: prohibited.
- Live tests: opt-in only and still skipped by default.
- Service-role request-path usage: prohibited.
- Real user data: prohibited.
- Real production data: prohibited.

## Pending Local-Only Scope

If all conditions are later satisfied and approval is recorded, the only
candidate scope is:

- Target: disposable local Supabase environment only.
- Allowed artifact:
  [notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
- Allowed validation: opt-in local harness using
  `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` and
  `SYNAPSE_SUPABASE_TEST_MODE=local`.
- Allowed data: synthetic users and synthetic Notes rows only.
- Allowed credentials: local-only synthetic public key/token values supplied
  from a gitignored local file, local shell, or approved secret store.

This pending scope does not approve staging, production, hosted Supabase,
default CI, migration files, `.env` commits, generated Supabase state, real
data, or service-role request-path behavior.

## Required Conditions Before Approval

All of the following must be true before local execution can be approved:

- The execution target is a disposable local-only Supabase environment.
- Synthetic users only are used.
- Synthetic Notes data only is used.
- No real user data, real emails, real note content, production data, staging
  data, dumps, backups, snapshots, or generated database files enter git.
- No real credentials, project identifiers, access tokens, refresh tokens,
  service-role keys, JWT secrets, passwords, client secrets, connection
  strings, or `.env` files enter git.
- Environment values come only from a gitignored local file, a local shell, or
  an approved secret store.
- The local artifact is reviewed against
  [database-migration-policy.md](security/database-migration-policy.md) before
  execution.
- Rollback and cleanup steps are documented for the disposable local target,
  including how synthetic rows/users are identified and removed without logging
  note content.
- Cleanup evidence reports only coarse synthetic counts and run identifiers.
- The RLS validation matrix is mapped to opt-in tests in
  `apps/api/tests/integration/test_notes_rls_validation.py`.
- The request-path harness uses a public key plus synthetic caller access
  tokens, never a service-role credential.
- `SUPABASE_SERVICE_ROLE_KEY` remains rejected by the request-path harness.
- Default CI does not set live Supabase env flags and does not run live RLS
  validation.
- Validation evidence redacts keys, tokens, authorization headers, Auth
  payloads, URLs with secrets, emails, and note content.
- An explicit reviewer approval entry is recorded before any local artifact
  execution or opt-in RLS validation run.

## Explicitly Not Approved

This record does not approve:

- executing the local Markdown artifact;
- copying fenced draft content into a runnable SQL file;
- creating `.sql` files;
- adding anything under `supabase/migrations/`;
- running Supabase locally;
- connecting to hosted Supabase;
- running live RLS tests;
- committing `.env` files or credentials;
- using service-role credentials in request-path code or tests;
- enabling live Notes repository mode;
- staging or production execution;
- hosted Supabase execution;
- default CI execution; or
- public Notes API behavior changes.

## Next Approval Step

Recommended next task: **Slice 6H-3B-4C-L - Local-only RLS execution dry-run
preparation**.

That slice should still avoid execution. It should document the disposable
local target assumptions, exact manual command boundary, rollback/cleanup
procedure, evidence format, redaction checklist, and reviewer sign-off format
needed before this approval can move from pending to granted.

Hosted staging planning remains deferred until local-only execution approval is
granted or explicitly deferred.

## Definition Of Done

Slice 6H-3B-4C-R is complete when:

- This approval record exists and records local RLS execution approval as
  pending.
- Production, staging, hosted Supabase, default CI, real data, credentials, and
  service-role request-path usage remain explicitly not approved.
- Conditions for a future local-only approval are documented.
- The next recommended task is Slice 6H-3B-4C-L.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  local Supabase run, hosted Supabase connection, live RLS test, runtime code,
  or public Notes API behavior change is introduced.
