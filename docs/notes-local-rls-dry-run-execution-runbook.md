# Notes Local RLS Dry-Run Execution Runbook

## 1. Status

Slice 6H-3B-4C-DR prepares the local-only execution runbook for the approved
Notes RLS dry-run attempt.

This runbook is documentation-only until an operator deliberately follows it in
a disposable local Supabase target. Adding this document does not execute SQL,
create a SQL file, create a migration, run Supabase locally, connect to hosted
Supabase, run live RLS validation, add credentials, enable live Notes
persistence, use a service-role request path, or change public Notes API
behavior.

The local-only dry-run attempt is approved under constraints in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).
Execution must still stop if any preflight check or stop condition below fails.

Current repository note: the pytest RLS case functions remain scaffolded and
skip after the base harness gate. A scaffold-only skip run can verify this
runbook's local safety gates, but it is not RLS enforcement evidence.

Slice 6H-3B-4C-E attempted preflight and stopped before execution because the
required disposable local target configuration and synthetic user token inputs
were absent. See
[notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md).

## 2. Source-Of-Truth References

- Approval record:
  [notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md)
- Dry-run preparation:
  [notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
- Local-only Markdown artifact:
  [notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md)
- Database artifact policy:
  [database-migration-policy.md](security/database-migration-policy.md)
- Validation plan:
  [notes-migration-rls-validation-plan.md](notes-migration-rls-validation-plan.md)
- Live/local harness plan:
  [notes-supabase-live-test-harness-plan.md](notes-supabase-live-test-harness-plan.md)
- Local setup guide:
  [notes-local-supabase-setup-guide.md](notes-local-supabase-setup-guide.md)
- Harness gate:
  `apps/api/tests/integration/supabase_live_harness.py`
- RLS validation cases:
  `apps/api/tests/integration/test_notes_rls_validation.py`

## 3. Scope

This runbook is limited to:

- a disposable local Supabase target only;
- the reviewed Markdown artifact only;
- synthetic users only;
- synthetic Notes rows only;
- public-key plus synthetic caller-token request-path validation only;
- opt-in local harness mode only;
- redacted evidence only; and
- cleanup verification after every attempted run, including failed or partial
  runs.

This runbook does not approve:

- hosted Supabase execution;
- staging or production execution;
- default CI execution;
- committed `.env` files;
- committed `.sql` files;
- committed `supabase/migrations/*` files;
- generated Supabase state, dumps, backups, snapshots, or database files;
- real users, real emails, real Notes content, imported data, or production
  data;
- service-role credentials in request-path code, harness configuration, or
  validation evidence;
- live Notes repository mode; or
- public Notes API behavior changes.

## 4. Required Local Inputs

Prepare these inputs outside git before execution:

- disposable local Supabase target URL;
- reviewed artifact commit or blob identity;
- synthetic user A and synthetic user B;
- short-lived synthetic access tokens for user A and user B;
- local public publishable key, or a deliberately reviewed legacy anon-key
  fallback;
- synthetic run id or prefix that contains no secret or personal value;
- redacted evidence destination; and
- cleanup owner and cleanup method for the disposable local target.

Do not print, paste into docs, screenshot, commit, or share raw URLs with
embedded secrets, keys, access tokens, authorization headers, Auth payloads,
emails, user ids, note ids, or note content.

## 5. Pre-Execution Checks

Run these checks immediately before any local-only dry-run attempt.

### Approval And Target

- [ ] Approval record still grants local-only execution under constraints.
- [ ] Target is disposable local Supabase only.
- [ ] Target contains no real users, real Notes rows, staging data, production
      data, imports, dumps, backups, snapshots, or realistic personal content.
- [ ] Synthetic user A and user B are ready.
- [ ] Cleanup can be completed by row/user cleanup or by disposing/resetting the
      entire local project.

### Git Hygiene

Use commands that print only filenames or status, not secret values.

```bash
git status --short
git diff --cached --name-only
git diff --cached --name-only -- '.env' '.env.*' '*.sql' 'supabase/migrations/*'
git diff --cached --name-only -- 'supabase/**'
git ls-files -- '.env' '.env.*'
```

Expected result:

- working tree is clean before preparing local-only evidence;
- no `.env` or `.env.*` file is tracked or staged;
- no `.sql` file is staged;
- no `supabase/migrations/*` file is staged; and
- no generated Supabase state, dump, backup, snapshot, database file, or local
  runtime file is staged.

Stop if any output shows a prohibited artifact that would be committed.

### Artifact Identity

Record identities in evidence before materializing anything in the local
target.

```bash
git rev-parse HEAD
git rev-parse HEAD:docs/database/notes/notes-local-migration-rls-artifact.md
git rev-parse HEAD:docs/notes-local-rls-dry-run-execution-runbook.md
```

If the artifact content has changed from the reviewed local-only Markdown
artifact, stop and obtain separate approval.

### Harness Environment Shape

Set values only in a local shell, gitignored local environment file, or approved
secret store. Do not commit the file or values.

```bash
export SYNAPSE_SUPABASE_INTEGRATION_TESTS=1
export SYNAPSE_SUPABASE_TEST_MODE=local
export SUPABASE_URL='<disposable-local-supabase-url>'
export SUPABASE_PUBLISHABLE_KEY='<local-public-publishable-key>'
export SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN='<synthetic-user-a-token>'
export SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN='<synthetic-user-b-token>'
unset SUPABASE_SERVICE_ROLE_KEY
```

Use this presence check instead of printing raw values:

```bash
python - <<'PY'
import os

required = (
    "SYNAPSE_SUPABASE_INTEGRATION_TESTS",
    "SYNAPSE_SUPABASE_TEST_MODE",
    "SUPABASE_URL",
    "SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN",
    "SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN",
)
public_key_names = ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY")

for name in required:
    print(f"{name}: {'set' if os.getenv(name) else 'missing'}")

print(
    "public key:",
    "set" if any(os.getenv(name) for name in public_key_names) else "missing",
)
print(
    "SUPABASE_SERVICE_ROLE_KEY:",
    "set - STOP" if os.getenv("SUPABASE_SERVICE_ROLE_KEY") else "absent",
)
PY
```

Expected result:

- opt-in flag is set to `1`;
- mode is `local`;
- URL, public key source, user A token, and user B token are present;
- service-role key is absent; and
- no raw value is printed.

Stop if a service-role key is present or if local values cannot be supplied
without entering git.

## 6. Stop Conditions

Stop immediately and do not continue the dry-run if any of these occur:

- target is not disposable local Supabase;
- real users, real emails, real Notes content, production data, staging data,
  dumps, backups, snapshots, or realistic personal content are involved;
- cleanup cannot be guaranteed;
- the local schema differs from the reviewed artifact in a way that changes
  owner, grant, RLS, soft-delete, version, trigger, or function behavior;
- the artifact must be changed before execution;
- a service-role key is needed for request-path behavior;
- the harness would need to print or capture raw secrets, tokens, Auth
  payloads, URLs with secrets, emails, user identifiers, or note content;
- any cross-user visibility or mutation is observed;
- physical delete is required for public Notes CRUD validation;
- any `.env`, `.sql`, migration, generated Supabase state, dump, backup,
  snapshot, database file, credential, or sensitive evidence artifact would be
  staged or committed; or
- default CI would need to set live/local harness values.

## 7. Execution Sequence

### 7.1 Baseline Local Safety Check

Run the default local scaffold check before any Supabase target is prepared.

```bash
pytest apps/api/tests/integration/test_notes_rls_validation.py -q -rs
```

Expected current result for this slice:

- local harness guard tests pass; and
- live RLS case functions skip.

This confirms default local behavior only. It does not validate RLS.

### 7.2 Prepare Disposable Local Target

Prepare the local Supabase target outside git:

1. Start or reset a disposable local Supabase project.
2. Confirm the target contains no real users or real Notes rows.
3. Create or identify synthetic user A and synthetic user B.
4. Obtain short-lived synthetic caller access tokens outside git.
5. Record only pseudonyms for users in evidence.

If user creation tooling requires administrative capability, keep that setup
outside request-path validation and outside evidence. Do not place admin or
service-role credentials in harness inputs. Stop if setup cannot be separated
from the request-path dry-run.

### 7.3 Review And Materialize Artifact Locally

Review the local-only Markdown artifact and database policy one final time.

Materialize only the reviewed artifact content into the disposable local target.
Do not create a repository `.sql` file, migration file, generated state file, or
committed copy. Do not run the artifact in hosted, staging, production, or CI.

Stop if the target lacks the expected owner table or if the reviewed
`public.users(id)` ownership assumption would need to change. That requires
separate review before execution.

### 7.4 Run The Opt-In Local Harness

Run the Notes RLS validation file from the prepared local shell.

```bash
pytest apps/api/tests/integration/test_notes_rls_validation.py -q -rs
```

Evidence handling:

- capture pass/fail/skip summaries only;
- redact failures before sharing;
- do not paste raw response bodies if they contain tokens, Auth payloads,
  emails, user ids, note ids, or note content; and
- do not claim RLS coverage from scaffold-only skips.

For this slice's current scaffold, the expected opt-in result remains pass plus
skip, not executed RLS validation. A future implementation may replace the
scaffold skips with live local assertions, but it must keep this runbook's
preflight, stop, redaction, and cleanup rules.

## 8. Evidence Template

Use this format for any future local execution report.

```text
Environment type: local only
Approval record: docs/notes-local-rls-execution-approval-record.md
Runbook: docs/notes-local-rls-dry-run-execution-runbook.md
Artifact: docs/database/notes/notes-local-migration-rls-artifact.md
Source commit: <commit sha>
Artifact blob: <blob sha>
Harness mode: local
Public key source: <publishable or reviewed legacy anon fallback, value redacted>
Synthetic run id or prefix: <non-sensitive id, redacted if needed>
Synthetic users: user A and user B, raw identifiers redacted
Service-role request path used: no

Matrix:
- user A can select own notes: <pass/fail/skip, redacted detail>
- user A cannot select user B notes: <pass/fail/skip, redacted detail>
- user A cannot update user B notes: <pass/fail/skip, redacted detail>
- user A cannot soft-delete user B notes: <pass/fail/skip, redacted detail>
- insert owner spoofing is rejected: <pass/fail/skip, redacted detail>
- include_deleted remains owner-scoped: <pass/fail/skip, redacted detail>
- request-path CRUD performs no physical delete: <pass/fail/skip, redacted detail>

Cleanup:
- synthetic Notes rows cleaned up or local project disposed: <yes/no>
- synthetic users removed or local project disposed: <yes/no>
- coarse cleanup counts only: <counts, no content>

Git hygiene after run:
- no .env, SQL, migration, generated Supabase state, credential, or sensitive
  evidence staged: <yes/no>
```

Skip-only matrix entries are acceptable only as scaffold evidence. They are not
accepted RLS enforcement evidence.

## 9. Cleanup Sequence

Complete cleanup after every attempt, including stopped or failed attempts.

1. Delete synthetic Notes rows created by the dry-run, or dispose/reset the
   entire local project.
2. Remove synthetic Auth users, or dispose/reset the entire local project.
3. Reset local containers, volumes, generated runtime files, and temporary
   database state according to the local setup method.
4. Clear local shell values.

```bash
unset SYNAPSE_SUPABASE_INTEGRATION_TESTS
unset SYNAPSE_SUPABASE_TEST_MODE
unset SUPABASE_URL
unset SUPABASE_PUBLISHABLE_KEY
unset SUPABASE_ANON_KEY
unset SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN
unset SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN
unset SUPABASE_SERVICE_ROLE_KEY
```

5. Delete or scrub temporary gitignored local env files when no longer needed.
6. Keep cleanup evidence to local environment type, synthetic run id or prefix,
   and coarse row/user counts only.
7. Confirm final git hygiene.

```bash
git status --short
git diff --cached --name-only
```

Stop and treat the run as failed if cleanup cannot be verified.

## 10. Acceptance Criteria

A future local-only dry-run report is acceptable only when:

- the target was disposable local Supabase;
- the reviewed artifact identity is recorded;
- all preflight checks passed before execution;
- no service-role request path was used;
- only synthetic users and synthetic Notes rows were involved;
- matrix results are recorded without raw identifiers, tokens, Auth payloads,
  emails, or note content;
- cleanup verification is recorded;
- no prohibited artifact or sensitive evidence is staged or committed; and
- any skip-only scaffold result is labeled as scaffold evidence, not RLS
  enforcement evidence.

Hosted staging planning remains deferred until local-only dry-run evidence is
accepted or local execution is explicitly deferred.

## 11. Definition Of Done

Slice 6H-3B-4C-DR is complete when:

- this runbook documents local-only scope, source-of-truth references,
  pre-execution checks, stop conditions, execution sequence, redacted evidence
  capture, cleanup verification, and acceptance criteria;
- related approval, preparation, validation, harness, and policy docs point to
  this runbook;
- no SQL file, migration, `.env` file, credential, generated Supabase state,
  local Supabase run, hosted Supabase connection, live RLS validation, runtime
  code, test code, live repository mode, service-role request-path usage,
  frontend/UI, Expo, AI, offline sync, or public Notes API behavior change is
  introduced; and
- focused verification passes.
