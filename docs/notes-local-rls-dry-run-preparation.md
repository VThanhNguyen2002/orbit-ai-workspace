# Notes Local RLS Dry-Run Preparation

## 1. Objective

Slice 6H-3B-4C-L prepares the process for a future local-only Notes RLS
execution dry-run.

This document is a checklist and evidence plan only. It does not approve,
execute, apply, or validate the local Markdown artifact in
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
Local execution remains blocked until a later approval record explicitly grants
local-only dry-run execution.

The intended future dry-run is limited to a disposable local Supabase target,
synthetic users, synthetic Notes rows, a public-key plus caller-token request
path, and redacted evidence.

## 2. Non-Goals

This preparation does not:

- execute SQL;
- create SQL files;
- create migration files;
- add anything under `supabase/migrations/`;
- start Supabase locally;
- connect to live, hosted, staging, or production Supabase;
- add real credentials, real user data, real emails, or real Notes content;
- run RLS validation;
- run the opt-in live/local harness;
- use service-role credentials in request-path code or tests;
- enable live Notes repository mode; or
- change runtime code, tests, public Notes API behavior, frontend/UI, Expo, AI,
  or offline sync behavior.

## 3. Current Status

- Local RLS execution approval is pending in
  [notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
- The local Notes table/RLS artifact is Markdown-only and remains outside
  `supabase/migrations/`.
- Live/local Notes RLS tests are skipped by default.
- No executable Notes SQL is committed.
- No Supabase local run, hosted Supabase connection, or RLS validation has been
  performed.
- No Supabase environment is required by CI.
- Default CI remains credential-free and must not set live harness opt-in
  values.

## 4. Preconditions Before Local Execution Approval

A reviewer may consider local-only dry-run execution approval only after all of
the following are true:

- The target is a disposable local Supabase project.
- The target contains no real user data, imported production data, staging data,
  dumps, backups, snapshots, or realistic personal content.
- Synthetic users only are used.
- Synthetic Notes rows only are used.
- Real local values are supplied only from a gitignored local environment file,
  a local shell, or an approved secret store.
- No credentials, project identifiers, tokens, JWT secrets, passwords, client
  secrets, connection strings, authorization headers, Auth payloads, or `.env`
  files enter git.
- No service-role credential is used by request-path code, adapter
  construction, harness configuration, or validation evidence.
- The local Markdown artifact is reviewed against
  [database-migration-policy.md](security/database-migration-policy.md) before
  execution.
- The rollback and cleanup checklist in this document is ready for the exact
  disposable local target.
- The evidence redaction plan in this document is ready before any test output
  is captured.
- The RLS validation matrix is mapped to the opt-in cases in
  `apps/api/tests/integration/test_notes_rls_validation.py`.
- An explicit approval record identifies the artifact version, local-only
  target assumptions, evidence owner, and cleanup owner before execution.

## 5. Dry-Run Preflight Checklist

Run these checks before local execution approval is granted and repeat them
immediately before any approved local dry-run:

- [ ] Working tree is clean before preparing local-only evidence.
- [ ] No `.env` or `.env.*` file is staged or tracked.
- [ ] No `.sql` file is staged.
- [ ] No `supabase/migrations/*` file is staged.
- [ ] No generated Supabase state, dump, backup, snapshot, database file, or
      local runtime file is staged.
- [ ] Local environment values exist only outside git.
- [ ] `SYNAPSE_SUPABASE_INTEGRATION_TESTS` is not set in default CI.
- [ ] `SYNAPSE_SUPABASE_TEST_MODE` is planned as `local` only for the dry-run.
- [ ] `SUPABASE_URL` points only to the disposable local target and is not
      committed.
- [ ] A public key placeholder is mapped through `SUPABASE_PUBLISHABLE_KEY`, or
      a reviewed legacy `SUPABASE_ANON_KEY` fallback, outside git.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is absent from request-path harness
      configuration.
- [ ] Service-role credentials are not used to construct Notes request-path
      clients.
- [ ] Synthetic user A and user B access-token placeholders are mapped outside
      git through
      `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` and
      `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN`.
- [ ] No refresh tokens, passwords, client secrets, or real user tokens are
      harness inputs.
- [ ] The local artifact version and source commit are identified before it is
      materialized in the disposable local target.
- [ ] The RLS validation matrix is understood before execution:
      own select, cross-user select block, cross-user update block,
      cross-user soft-delete block, insert owner binding, include-deleted owner
      scoping, and no request-path physical delete.
- [ ] Evidence capture is configured to redact keys, tokens, authorization
      headers, Auth payloads, URLs with embedded secrets, emails, user ids, and
      note content.
- [ ] Cleanup ownership, synthetic prefixes, and cleanup evidence expectations
      are documented for the local target.

## 6. Manual Dry-Run Sequence

The future sequence is deliberately prose/pseudocode only. It is not executable
instruction, and it must not be followed until explicit local-only execution
approval is recorded.

1. If local-only dry-run execution approval is not explicitly granted, stop.
2. Confirm the working tree and preflight checklist are clean.
3. Prepare a disposable local Supabase project outside git.
4. Confirm the local project contains no real users, no real Notes rows, no
   imported dumps, and no production or staging data.
5. Create or identify synthetic user A and synthetic user B in the disposable
   local project.
6. Map short-lived synthetic user A/B access-token placeholders outside git.
7. Review the Markdown artifact and policy record one final time against the
   approved artifact commit.
8. Materialize the reviewed artifact manually only in the disposable local
   target after approval. Do not create a repository `.sql` file, migration
   file, generated state artifact, or committed copy.
9. Run the opt-in local harness only from a deliberate local shell or
   gitignored local environment, with local mode and public-key plus
   caller-token request-path inputs.
10. Capture the RLS validation matrix results using the evidence format below.
11. Redact keys, tokens, Auth payloads, URLs with secrets, user identifiers,
    emails, and note content before sharing evidence.
12. Clean up synthetic Notes rows and synthetic users, or dispose of/reset the
    entire local project.
13. Clear local-only environment values from the shell or temporary local file.
14. Confirm no SQL, migration, `.env`, credential, generated Supabase state, or
    evidence artifact with sensitive data is staged.

## 7. Evidence Format

A future local execution report must include:

- Environment type: local only.
- Approval slice or record that granted local-only execution.
- Artifact path and artifact version or commit.
- Harness mode: local.
- Public-key source: publishable key or reviewed legacy anon-key fallback,
  value redacted.
- Synthetic user identifiers pseudonymized as user A and user B, with raw ids,
  emails, and tokens redacted.
- Synthetic run identifier or prefix, redacted if it contains any sensitive
  value.
- Test matrix results for:
  - user A can select own notes;
  - user A cannot select user B notes;
  - user A cannot update user B notes;
  - user A cannot soft-delete user B notes;
  - insert owner spoofing is rejected;
  - include-deleted remains owner-scoped; and
  - request-path CRUD performs no physical delete.
- Cleanup result with coarse counts only.
- Failure logs, if any, with keys, tokens, authorization headers, Auth
  payloads, URLs with secrets, emails, raw user identifiers, and note content
  redacted.
- Confirmation that no service-role credential was used in the request path.
- Confirmation that no `.env`, SQL, migration, generated Supabase state, real
  data, or credential artifact was staged or committed.

## 8. Rollback/Cleanup Checklist

Complete this checklist after any future approved local dry-run, including
failed or partial attempts:

- [ ] Synthetic Notes rows created by the dry-run are deleted or made
      unreachable by disposing of the local project.
- [ ] Synthetic Auth users are removed, or the disposable local project is
      reset/disposed.
- [ ] Local project containers, volumes, generated runtime files, and temporary
      database state are reset or disposed according to the local setup method.
- [ ] Local shell variables containing Supabase URLs, public keys, or synthetic
      access tokens are cleared.
- [ ] Temporary gitignored local env files are deleted or scrubbed when no
      longer needed.
- [ ] No credentials persist in logs, shell transcripts, test reports,
      screenshots, issue comments, or committed docs.
- [ ] No `.env`, `.sql`, migration, generated Supabase state, dump, backup,
      snapshot, or database file is staged.
- [ ] Cleanup evidence reports only local environment type, synthetic run id or
      prefix, and coarse row/user counts.

## 9. Approval Decision Point

After this preparation document is accepted, the next approval slice may either:

- grant local-only RLS dry-run execution approval; or
- keep execution blocked.

Recommended next task: **Slice 6H-3B-4C-LA - Grant local-only RLS dry-run
approval**.

This recommendation is local-only. It does not imply hosted staging,
production, default CI, live repository mode, service-role request-path usage,
or public Notes API behavior approval.

## 10. Definition Of Done

Slice 6H-3B-4C-L is complete when:

- This dry-run preparation document exists.
- The preflight checklist is documented.
- The manual dry-run sequence is documented without executable SQL commands.
- The future evidence format is documented.
- The rollback/cleanup checklist is documented.
- Existing approval, validation, harness, policy, and next-action docs point to
  this preparation and the next approval decision.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  local Supabase run, hosted Supabase connection, live RLS validation, runtime
  code, tests, or public Notes API behavior change is introduced.
- Verification passes.
- CI passes.
