# Notes Local RLS Execution Approval Record

## Status

Slice 6H-3B-4C-R recorded the approval gate for a future local-only Notes RLS
execution attempt. Slice 6H-3B-4C-L added
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
with the disposable local target assumptions, preflight checks,
rollback/cleanup expectations, evidence format, stop boundaries, and manual
dry-run sequence.

Slice 6H-3B-4C-LA records the explicit approval decision:

**Local-only RLS dry-run attempt: approved under constraints.**

This is documentation-only. It does not execute SQL, create a migration, run
Supabase locally, connect to hosted Supabase, run live RLS tests, add
credentials, enable live repository mode, or change public Notes API behavior.

This approval does not authorize automatic execution after this commit. The
next slice must prepare the local-only dry-run execution runbook and still stop
at any pre-execution failure or stop condition documented below.

## Approval Decision

Current decision:

- Local-only RLS dry-run attempt: approved under constraints.
- Production execution approval: not granted.
- Staging execution approval: not granted.
- Hosted Supabase execution approval: not granted.
- Default CI execution: prohibited.
- Service-role request-path usage: prohibited.
- Real user data: prohibited.
- Real production data: prohibited.
- Live repository mode: not granted.
- Public Notes API behavior changes: not granted.

## Approved Local-Only Scope

This approval is limited to:

- Target: disposable local Supabase environment only.
- Allowed artifact:
  [notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
- Artifact form: local-only Markdown artifact only. This approval does not
  approve committing a `.sql` file or `supabase/migrations/*` file.
- Allowed validation: opt-in local harness only, using
  `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` and
  `SYNAPSE_SUPABASE_TEST_MODE=local`.
- Allowed users: synthetic users only.
- Allowed data: synthetic Notes rows only.
- Allowed credentials: local-only public key and synthetic caller-token values
  supplied from a gitignored local file, local shell, or approved secret store.
- Allowed evidence: redacted evidence collection only.
- Required cleanup: cleanup verification is required after any attempted
  local-only dry-run, including failed or partial attempts.

The approved local-only scope is bound by
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
and [database-migration-policy.md](security/database-migration-policy.md).

## Explicitly Not Approved

This record does not approve:

- staging execution;
- production execution;
- hosted Supabase execution;
- default CI execution;
- service-role request-path usage;
- real user data;
- real production data;
- committed `.env` files;
- committed `.sql` files;
- committed `supabase/migrations/*`;
- generated Supabase state;
- live Notes repository mode;
- public Notes API behavior changes;
- connecting to hosted Supabase;
- using real credentials, real emails, real note content, dumps, backups, or
  snapshots; or
- broadening the local artifact beyond the reviewed Markdown content without
  separate approval.

## Required Before Actual Dry-Run Execution

Before any approved local-only dry-run attempt begins, all of the following
must be true:

- Working tree is clean.
- No `.env` or `.env.*` file is staged.
- No `.sql` file is staged.
- No `supabase/migrations/*` file is staged.
- No generated Supabase state, dump, backup, snapshot, database file, or local
  runtime file is staged.
- Local environment values come only from a gitignored local file or local
  shell.
- No credential, project identifier, access token, refresh token, service-role
  key, JWT secret, password, client secret, connection string, authorization
  header, Auth payload, or `.env` file enters git.
- `SUPABASE_SERVICE_ROLE_KEY` is absent from request-path harness
  configuration.
- Request-path harness behavior uses a public key plus synthetic caller access
  tokens, never service role.
- Synthetic user A and user B access tokens are available locally only through
  `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` and
  `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN`.
- The dry-run evidence template is ready and configured for redaction.
- The rollback/cleanup checklist is ready for the disposable local target.
- The RLS validation matrix is understood and mapped to
  `apps/api/tests/integration/test_notes_rls_validation.py`.
- The local artifact is reviewed against
  [database-migration-policy.md](security/database-migration-policy.md) before
  it is manually materialized in the disposable local target.

## Dry-Run Stop Conditions

Stop immediately and do not continue the local-only dry-run if any of the
following occur:

- A service-role key is required for request-path behavior.
- Real data, real users, real emails, real Notes content, production data,
  staging data, dumps, backups, or snapshots are involved.
- Cleanup cannot be guaranteed or the disposable local target cannot be reset
  or disposed.
- RLS policy behavior allows cross-user visibility.
- SQL differs from the reviewed Markdown artifact without separate approval.
- Secrets, tokens, authorization headers, Auth payloads, URLs with secrets,
  emails, raw user identifiers, or note content would be printed, shared, or
  committed.
- Any `.env`, `.sql`, `supabase/migrations/*`, generated Supabase state, dump,
  backup, snapshot, database file, credential, or sensitive evidence artifact
  would be staged or committed.

## Evidence And Cleanup Requirements

A future local-only dry-run execution report must use the evidence format in
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md).
It must include:

- environment type: local only;
- approval record and artifact version or commit;
- pseudonymized synthetic user A/B identifiers;
- local RLS validation matrix results;
- confirmation that no service-role request path was used;
- redacted failure logs if failures occur; and
- cleanup verification with coarse synthetic counts only.

Cleanup verification is required even when the dry-run stops early.

## Next Approval Step

Recommended next task: **Slice 6H-3B-4C-DR - Local-only RLS dry-run execution
runbook**.

That slice should prepare the careful runbook for the approved local-only
attempt. It must not automatically execute the dry-run merely because approval
is recorded here.

Hosted staging planning remains deferred until the local-only dry-run is either
completed with accepted evidence or explicitly deferred.

## Definition Of Done

Slice 6H-3B-4C-LA is complete when:

- This approval record states that the local-only RLS dry-run attempt is
  approved under constraints.
- The approved local-only scope is explicit: disposable local Supabase,
  Markdown artifact only, opt-in local harness only, synthetic users, synthetic
  Notes rows, redacted evidence, and cleanup verification.
- Staging, production, hosted Supabase, default CI, real data, credentials,
  committed `.env` files, committed `.sql` files, committed
  `supabase/migrations/*`, generated Supabase state, live repository mode,
  service-role request-path usage, and public Notes API behavior changes remain
  not approved.
- Required pre-execution conditions and stop conditions are documented.
- The next recommended task is Slice 6H-3B-4C-DR.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  local Supabase run, hosted Supabase connection, live RLS test, runtime code,
  test code, or public Notes API behavior change is introduced.
