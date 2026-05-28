# Notes Local Supabase Setup Guide

## Status

Slice 6H-3B-3B documents a future local-only Supabase setup path for the
skipped Notes harness. This guide is documentation only. It does not add a
Supabase SDK adapter, start Supabase, connect to a live service, commit
credentials, commit `.env` files, add SQL, add migrations, execute RLS tests, or
enable live Notes persistence.

The local harness can be prepared safely, but it cannot claim RLS coverage until
a specific Notes migration/RLS artifact is approved under
[database-migration-policy.md](security/database-migration-policy.md) and
applied in a disposable local or approved non-production environment.

## 1. Objective

Provide a safe reference for how a later engineer should prepare local
Supabase configuration for the opt-in Notes harness without committing database
artifacts, credentials, generated Supabase state, executable migrations, or
real user data.

The guide supports future adapter and RLS validation work by documenting:

- local-only prerequisites and environment boundaries;
- placeholder environment variable names;
- synthetic user and synthetic Notes data rules;
- cleanup expectations;
- default-CI exclusion; and
- the migration/RLS approval gate that must be completed before RLS behavior is
  asserted.

## 2. Non-Goals

- Do not run Supabase locally as part of this slice.
- Do not connect to hosted Supabase or production Supabase.
- Do not add `supabase-py`, a live SDK adapter, or live repository wiring.
- Do not set `SYNAPSE_NOTES_REPOSITORY=supabase` for normal local, test, or CI
  execution.
- Do not add `.env` files, real URLs, keys, passwords, access tokens, refresh
  tokens, JWT secrets, or service-role credentials.
- Do not add SQL, migrations, seeds, dumps, backups, generated Supabase state,
  or executable database artifacts.
- Do not execute RLS tests or claim RLS coverage.
- Do not use a service-role key in the Notes request path or as a harness input.
- Do not change public Notes API behavior, frontend/UI, Expo, AI, or offline
  sync behavior.

## 3. Current Baseline

- Normal local/test/CI runs use `SYNAPSE_NOTES_REPOSITORY=memory`.
- The public Notes API behavior is unchanged and remains backed by the memory
  repository by default.
- `apps/api/tests/integration/supabase_live_harness.py` contains test-only
  gating helpers. The harness is skipped unless
  `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` and
  `SYNAPSE_SUPABASE_TEST_MODE` is `local` or `staging`.
- The harness requires `SUPABASE_URL`, a public key
  (`SUPABASE_PUBLISHABLE_KEY`, or legacy `SUPABASE_ANON_KEY`), and synthetic
  user A/B access-token placeholders.
- The harness rejects `SUPABASE_SERVICE_ROLE_KEY` because request-path tests
  must use a public key plus the verified caller token.
- The placeholder live test still skips because no live SDK adapter, approved
  migration/RLS artifact, or RLS validation target exists.
- `supabase/migrations/*.sql` and generated local Supabase state remain ignored
  by policy and must not be committed during planning.

## 4. Prerequisites

Future local setup should use only a disposable, non-production Supabase target.
Local setup is optional until a later slice implements and approves the actual
adapter/RLS validation path.

- Supabase CLI is optional. If used later, install and run it outside this docs
  slice and keep any generated state out of git.
- Docker is optional. If local Supabase uses Docker later, keep containers,
  volumes, and generated files local to the developer machine.
- Use a local-only or otherwise non-production project. Never point the local
  harness at production.
- Do not import, clone, restore, or seed production data.
- Use only synthetic Supabase Auth users and synthetic Notes data.
- Apply no Notes migration unless the exact artifact has passed the database
  migration approval gate.

## 5. Local Environment File Policy

`.env` files are ignored and are the only acceptable place for real local
values on a developer machine. They must never be added to git.

Rules:

- Commit placeholders only, such as values in `.env.example` or docs.
- Keep real credentials in a gitignored `.env` file, a local shell, or an
  approved secret store.
- Do not paste real values into Markdown, test snapshots, issue comments, CI
  logs, command history that will be shared, or generated artifacts.
- Do not create committed per-developer config files for Supabase URLs, keys,
  tokens, or auth credentials.
- Treat public Supabase keys as environment-specific operational values even
  when they are not service-role secrets.

## 6. Required Placeholder Variables

The future local harness should use these names with placeholder values in docs
and real values only in a gitignored local environment.

```text
SUPABASE_URL=http://127.0.0.1:<local-supabase-api-port>
SUPABASE_PUBLISHABLE_KEY=replace-with-local-publishable-key
SYNAPSE_SUPABASE_INTEGRATION_TESTS=1
SYNAPSE_SUPABASE_TEST_MODE=local
SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN=replace-with-short-lived-synthetic-user-a-token
SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN=replace-with-short-lived-synthetic-user-b-token
```

Optional legacy public-key fallback only when a later reviewed setup explicitly
targets a legacy project:

```text
SUPABASE_ANON_KEY=replace-with-legacy-local-anon-key
```

Synthetic user token source placeholders:

- User A token source: short-lived access token for
  `synapse-live-harness-user-a`.
- User B token source: short-lived access token for
  `synapse-live-harness-user-b`.

These access-token placeholders describe future local synthetic Auth users.
Refresh tokens, passwords, client secrets, and service-role keys are not harness
inputs.

## 7. What Must Not Be Committed

Do not commit any of the following:

- generated Supabase state such as `supabase/.branches/`, `supabase/.temp/`,
  `supabase/.cache/`, local metadata, runtime files, containers, or volumes;
- `supabase/migrations/*.sql` or any executable `migrations/*.sql` file before
  explicit migration approval;
- database dumps, backups, exports, snapshots, `.sql.gz`, `.psql`, `.sqlite`,
  `.db`, or equivalent local database files;
- `.env`, `.env.*`, `supabase/.env`, or `supabase/.env.*`;
- service-role keys, JWT secrets, private keys, passwords, client secrets, or
  connection strings;
- real access tokens, refresh tokens, authorization headers, session payloads,
  or Supabase Auth response bodies; or
- seed data containing real emails, names, note content, production rows, or
  personal data.

## 8. How The Future Harness Should Be Run

The harness must remain skipped by default. Normal CI must not set
`SYNAPSE_SUPABASE_INTEGRATION_TESTS=1`, must not provide Supabase credentials,
and must not depend on a local CLI, Docker, hosted project, or network service.

Future local execution should be an explicit, manual, env-gated flow only:

1. Prepare a disposable local/non-production Supabase project outside git.
2. Create or obtain synthetic user A/B access tokens from the local-only test
   project.
3. Confirm no service-role key is present in the harness environment.
4. Export only the placeholder variable names listed above, with real values
   supplied from a gitignored local environment.
5. Run only the marked Supabase harness tests from a deliberate local shell.
6. Review redacted output only; do not print tokens, keys, URLs with embedded
   secrets, user emails, or note content.

Command shape for a later approved local run:

```bash
SYNAPSE_SUPABASE_INTEGRATION_TESTS=1 \
SYNAPSE_SUPABASE_TEST_MODE=local \
SUPABASE_URL=http://127.0.0.1:<local-supabase-api-port> \
SUPABASE_PUBLISHABLE_KEY=replace-with-local-publishable-key \
SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN=replace-with-short-lived-synthetic-user-a-token \
SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN=replace-with-short-lived-synthetic-user-b-token \
python3 -m pytest -m supabase_live
```

That command is illustrative only for a later approved slice. In the current
baseline it still cannot perform live Notes validation because no live adapter
or approved migration/RLS artifact exists.

## 9. Synthetic Data Rules

Synthetic data must be deterministic, non-personal, and easy to clean up.

- Use the deterministic prefix root `synapse-live-harness`.
- Use safe labels such as `synapse-live-harness-user-a` and
  `synapse-live-harness-user-b`.
- Do not use real emails, real names, real account identifiers, real note
  titles, real note content, or imported user data.
- Include a run id in synthetic Notes content or metadata only after the
  approved schema supports a safe field for it.
- Keep cleanup owner-scoped and targeted to synthetic rows.
- Prefer cleanup through the same user-scoped request path being validated.
- If administrative cleanup is later required, document it as a separate
  approved utility outside request-path validation.
- Cleanup failures should report coarse counts and run ids only, never tokens,
  user emails, Auth payloads, or note content.

## 10. RLS/Migration Prerequisite

No RLS claim may be made from this guide or from the current harness skeleton.
Fake repository tests and fake SDK transport tests prove code boundaries, not
database enforcement.

Before any local harness run claims RLS coverage:

1. A specific Notes migration/RLS artifact must be approved under
   [database-migration-policy.md](security/database-migration-policy.md).
2. The artifact must receive security review for privilege scope, RLS effects,
   rollback, cleanup, and absence of secrets or real data.
3. The artifact must be applied only in a disposable local or approved
   non-production environment.
4. The harness must validate synthetic user A/user B isolation against that
   applied artifact.
5. Results must distinguish adapter validation from RLS validation.

Until those steps are complete, the safe next engineering task is migration/RLS
validation planning, not live execution.

## 11. Troubleshooting

Missing env flag:

- If `SYNAPSE_SUPABASE_INTEGRATION_TESTS` is absent or not `1`, the harness is
  skipped by design.

Invalid mode:

- `SYNAPSE_SUPABASE_TEST_MODE` must be `local` or `staging`. Local setup uses
  `local`.

Service-role key present:

- Remove `SUPABASE_SERVICE_ROLE_KEY` from the harness environment. Request-path
  tests reject it because service-role credentials bypass RLS.

Harness skipped by design:

- The current placeholder live test still skips even with opt-in variables
  because no live SDK adapter or approved migration/RLS artifact exists.

Missing public key:

- Provide `SUPABASE_PUBLISHABLE_KEY` for the future local harness. Use
  `SUPABASE_ANON_KEY` only for a reviewed legacy fallback.

Missing synthetic user tokens:

- Provide short-lived synthetic user A/B access-token placeholders from the
  local-only project. Do not use refresh tokens, passwords, or real user tokens.

## 12. Security Checklist

- Confirm the target is local-only or otherwise non-production.
- Confirm no production data is imported, restored, seeded, or copied.
- Confirm `.env` files remain ignored and untracked.
- Confirm no real URL, key, token, password, JWT secret, client secret,
  service-role credential, or authorization header appears in git.
- Confirm `SUPABASE_SERVICE_ROLE_KEY` is absent from request-path harness input.
- Confirm no `supabase/migrations/*.sql` file or other executable SQL artifact
  is introduced without explicit approval.
- Confirm generated Supabase state, dumps, backups, SQLite files, and database
  files remain untracked.
- Confirm synthetic users and Notes data use deterministic prefixes and no real
  personal data.
- Confirm cleanup is scoped to synthetic rows and reports only coarse details.
- Confirm default CI remains credential-free and does not run live/local
  Supabase tests.
- Confirm RLS coverage is not claimed until an approved migration is applied
  and user A/user B outcomes are validated.

## 13. Definition Of Done

Slice 6H-3B-3B is complete when:

- This guide documents local-only setup expectations without running Supabase.
- Placeholder environment variables and synthetic user token sources are named
  without real values.
- `.env`, credential, token, service-role, generated state, dump, database file,
  SQL, and migration commit restrictions are explicit.
- The guide explains the env-gated future harness flow while preserving default
  CI disablement.
- Synthetic data, cleanup, troubleshooting, and security checklist expectations
  are documented.
- The migration/RLS approval prerequisite is recorded as the blocker for RLS
  claims and meaningful local validation.
- Related planning docs and the API README point to this guide.
- The next recommended task is **Slice 6H-3B-4 - Approved migration/RLS
  validation planning**.
- No runtime code, tests, SDK dependency, frontend/UI, Expo, AI, offline sync,
  SQL, migration, `.env`, generated Supabase state, live repository mode, or
  public Notes API behavior change is introduced.
