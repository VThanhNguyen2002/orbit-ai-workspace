# Notes Supabase Live Test Harness Plan

## Status

Slice 6H-3B-3 established the plan for a future opt-in live/local Supabase test
harness. It follows the implemented descriptor boundary, adapter protocol,
fake SDK transport tests, and Supabase-shaped Notes repository coverage. Slice
6H-3B-3A adds skipped-by-default pytest scaffolding and gating helpers under
`apps/api/tests/integration/`. Slice 6H-3B-3B adds the documentation-only local
setup guide in
[notes-local-supabase-setup-guide.md](notes-local-supabase-setup-guide.md).
Slice 6H-3B-4 adds the security-first migration/RLS validation plan in
[notes-migration-rls-validation-plan.md](notes-migration-rls-validation-plan.md),
and Slice 6H-3B-4B adds the local-only Markdown artifact in
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
Slice 6H-3B-4C now adds skipped-by-default Notes RLS validation case
scaffolding in `apps/api/tests/integration/test_notes_rls_validation.py`.
Slice 6H-3B-4C-R records the local execution approval gate in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md)
and kept local RLS execution approval pending at that time. Slice 6H-3B-4C-L
adds
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
with the local preflight checklist, evidence format, and cleanup expectations,
but it does not execute the artifact or run RLS validation. Slice 6H-3B-4C-LA
records constrained approval for a future local-only RLS dry-run attempt
without executing it. Slice 6H-3B-4C-DR adds the local-only dry-run execution
runbook in
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
without executing the artifact, running Supabase locally, or validating RLS.
These slices do not add a live Supabase SDK adapter, connect to Supabase,
introduce credentials, add `.env` files, add migrations or SQL, execute RLS
tests, or enable live Notes persistence.

The next bounded action is to follow the runbook only for an approved
disposable local attempt and produce redacted evidence, or explicitly defer
local execution before hosted staging planning. That still avoids automatic
execution, staging, production, hosted Supabase, default CI, real data,
credential, service-role request-path, and public Notes API behavior approval.

## 1. Objective

Define the future harness that can validate the Notes Supabase adapter, RLS
behavior, and user-scoped request path only when an engineer explicitly opts
in with synthetic data and test-only configuration. The harness must keep
default local, test, and CI execution credential-free, deterministic, and
network-free.

The harness eventually needs to prove:

- the API verifies a caller token before constructing Supabase client inputs;
- the live adapter propagates the verified caller token to Supabase Data API
  requests;
- the adapter uses only a public publishable key, or documented legacy anon
  key, as public API metadata;
- Notes queries and writes remain explicitly scoped by authenticated `user_id`;
- RLS independently prevents cross-user reads and writes; and
- soft delete remains an owner-scoped update, not a physical delete.

## 2. Non-Goals

- Do not add or import the real Supabase Python SDK.
- Do not implement the live adapter or repository wiring.
- Do not connect to local or hosted Supabase from default tests.
- Do not add real project URLs, keys, passwords, JWTs, refresh tokens, access
  tokens, `.env` files, or deployment secrets.
- Do not add SQL, migrations, seed files, database dumps, RLS policies, or
  executable database artifacts.
- Do not execute RLS tests in this planning slice.
- Do not use a service-role key in the Notes request path or to make RLS tests
  pass.
- Do not change public Notes API behavior, frontend/UI, Expo, AI, or offline
  sync behavior.

## 3. Current Baseline

- Memory Notes persistence is the default and remains active in normal CI.
- `get_supabase_user_client()` returns an inert,
  `UserScopedSupabaseClientDescriptor` only after JWT auth context has a
  verified caller access token.
- `UserScopedSupabaseClientAdapter`, `UserScopedSupabaseClient`, and
  `UserScopedSupabaseQuery` are implementation-neutral protocols; no SDK is
  imported.
- `SupabaseNotesRepository` requires an injected user-scoped client and is not
  wired into normal request handling.
- Fake-client repository tests prove query shaping, owner predicates,
  version-conflict handling, soft deletion, no-network behavior, and
  service-role non-propagation.
- Fake SDK transport tests prove the candidate adapter shape for caller-token
  authorization metadata, public-key metadata, request isolation, no
  session/refresh calls, redaction, and no network.
- `apps/api/tests/integration/supabase_live_harness.py` provides test-only
  decision/config helpers that require explicit opt-in, explicit mode,
  required environment names, no service-role key, and redacted config
  rendering.
- `apps/api/tests/integration/test_supabase_live_harness.py` verifies the
  default skip path, missing/invalid configuration, service-role rejection,
  synthetic naming rules, redaction, and no-network default behavior. Its
  placeholder live test is marked `supabase_live` and `integration`, and skips
  until later slices add a live adapter and approved migration/RLS artifact.
- `apps/api/tests/integration/test_notes_rls_validation.py` defines the Notes
  RLS validation cases behind the same opt-in harness. Default CI verifies case
  inventory, required synthetic user-token placeholders, service-role
  rejection, and no-network gating only. The case tests remain skipped even when
  the base live harness is configured because no live client, artifact
  execution approval, or applied RLS target exists in this slice.
- `docs/notes-local-rls-execution-approval-record.md` records the local
  execution approval gate and now approves a future local-only RLS dry-run
  attempt under strict constraints.
- `docs/notes-local-rls-dry-run-preparation.md` records the future local-only
  preflight checklist, manual sequence, evidence format, redaction plan, and
  cleanup checklist.
- `docs/notes-local-rls-dry-run-execution-runbook.md` records the local-only
  pre-execution checks, stop conditions, opt-in harness command boundary,
  redacted evidence template, cleanup sequence, and acceptance criteria.
- No executable Notes migration exists. RLS intent is documentation only until
  the database artifact policy approves a specific migration.
- `docs/notes-local-supabase-setup-guide.md` documents the future local-only
  setup posture, placeholder variables, synthetic data rules, cleanup
  expectations, troubleshooting, and artifact/credential restrictions.
- `docs/notes-migration-rls-validation-plan.md` documents the future
  migration/RLS approval criteria, security review checklist, RLS validation
  matrix, artifact policy, and review-packet-first implementation sequence.

## 4. Default CI Must Remain Credential-Free

Normal push CI must not depend on Supabase because live credentials and network
state would make the default pipeline unsafe and flaky. Default CI must remain:

- deterministic and runnable by any contributor with no external account;
- safe for forks, logs, caches, and artifact retention;
- independent of Supabase project availability, rate limits, auth settings, or
  local CLI state;
- free of live tokens, public keys, service-role keys, refresh tokens, and test
  user credentials; and
- unable to apply migrations, seed data, or mutate hosted resources.

Default CI may continue to run fake repository, descriptor, fake SDK transport,
contract, lint, typecheck, and build checks. It must not run the future live
harness unless an explicitly separate, reviewed workflow or manual command opts
in with test-only configuration.

## 5. Opt-In Test Modes

### Local Supabase Mode

Local mode targets a disposable Supabase instance controlled by the developer.
It is useful for proving adapter mechanics and RLS outcomes before any hosted
environment is touched.

Required properties:

- Runs only when the explicit harness flag and `local` mode are set.
- Uses a local project URL such as `http://127.0.0.1:<port>` supplied by the
  developer environment, never committed.
- Uses synthetic Supabase Auth users and synthetic Notes data only.
- Requires a reviewed migration to be applied locally before RLS tests may
  claim RLS coverage.
- Must provide cleanup steps that remove synthetic Notes rows created by the
  harness.
- Must not require a service-role key in the API request path. Any local setup
  convenience that needs admin privileges is outside request-path tests and
  must be documented separately.

### Hosted Staging Supabase Mode

Hosted staging mode targets an approved non-production Supabase project. It is
for final validation of the request path and RLS behavior after local
confidence exists.

Required properties:

- Runs only when the explicit harness flag and `staging` mode are set.
- Uses a disposable or dedicated non-production project, never production.
- Uses synthetic test users and deterministic test Notes content.
- Requires the approved migration/RLS artifact to be applied in that staging
  project before RLS assertions are enabled.
- Must run from a controlled manual environment or explicitly reviewed
  integration workflow, not normal push CI.
- Must redact URLs, keys, authorization headers, user emails, and note content
  from logs and test diagnostics.

## 6. Required Environment Variables

The future harness may document placeholders like the following. Real values
belong only in a gitignored local `.env` file, a local shell, or an approved
secret store.

```text
SYNAPSE_SUPABASE_INTEGRATION_TESTS=0
SYNAPSE_SUPABASE_TEST_MODE=local
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=replace-with-public-publishable-key
SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN=replace-with-short-lived-user-a-token
SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN=replace-with-short-lived-user-b-token
```

Optional legacy public-key fallback only when deliberately testing a legacy
project:

```text
SUPABASE_ANON_KEY=replace-with-legacy-public-anon-key
```

Explicit non-requirements:

- `SUPABASE_SERVICE_ROLE_KEY` is not an input to request-path harness tests.
- Refresh tokens are not harness inputs for the backend adapter boundary.
- Passwords and client secrets are not harness inputs.
- Test user access tokens must be short-lived, synthetic, and never committed.

If later setup tooling needs to create local/staging synthetic users, that setup
must be separately reviewed. It must not blur the request-path rule that Notes
operations run with a public key plus the verified caller token, not service
role.

## 7. Test Gating Strategy

Future live/local tests must be skipped by default. A safe pytest skeleton
now requires all of:

- an explicit flag, for example `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1`;
- an explicit mode, for example `SYNAPSE_SUPABASE_TEST_MODE=local` or
  `SYNAPSE_SUPABASE_TEST_MODE=staging`;
- `SUPABASE_URL`;
- `SUPABASE_PUBLISHABLE_KEY` or an explicitly accepted legacy `SUPABASE_ANON_KEY`;
- synthetic user A and user B access-token sources; and
- markers `@pytest.mark.supabase_live` and `@pytest.mark.integration` so normal
  test selection can identify the harness.

The skeleton should fail closed:

- Missing flag means skip, not fail.
- Missing required live values after the flag is set means a coarse
  configuration failure that redacts variable values.
- Normal push CI must not set the flag.
- A later manual workflow, if added, must be separate from `ci.yml` or gated so
  it cannot run on ordinary pushes.
- Even with all opt-in variables present, the current placeholder live test
  skips because no live adapter, approved migration, or RLS validation target
  exists yet.
- The Notes RLS validation skeleton also skips its live case functions after
  the base harness gate because Slice 6H-3B-4C defines the validation matrix and
  safety checks only. It does not execute the local artifact, create SQL, or
  connect to local or hosted Supabase.

## 8. Synthetic Data Rules

The harness must never use real users or real Notes content.

Synthetic user rules:

- Use deterministic labels such as `synapse-live-harness-user-a` and
  `synapse-live-harness-user-b`.
- Do not log emails, access tokens, or Supabase Auth response bodies.
- Use disposable users where possible; otherwise use dedicated staging-only
  users that contain no real personal data.

Synthetic Notes rules:

- Use deterministic titles/content such as `Harness note A` and
  `Harness note B`.
- Include a unique run identifier in a non-sensitive field where the approved
  schema supports it, or use deterministic cleanup predicates scoped to the
  synthetic users.
- Do not print full note content in assertion messages or logs.
- Keep all cleanup owner-scoped and targeted to synthetic rows.

Cleanup strategy:

- Prefer API-level or repository-level cleanup using the same user-scoped path
  where possible.
- If administrative cleanup is later required, it must be a separate approved
  utility outside request-path validation and must never be used to justify RLS
  behavior.
- Cleanup failures should be reported with coarse row counts and run ids only,
  never credentials or note content.

## 9. RLS Validation Strategy

RLS validation must be explicit and cannot be inferred from fake tests. After
an approved migration exists and is applied in the target environment, the
harness should validate at least:

- User A can create, list, get, update, and soft-delete notes owned by user A.
- User A cannot list or get notes owned by user B.
- User A cannot update or soft-delete user B notes.
- Insert attempts whose `user_id` differs from the verified caller are
  rejected by RLS.
- Update attempts that target another owner are rejected or produce the same
  non-disclosing not-found behavior as the API contract.
- Soft-deleted user A notes are hidden by default and visible only to user A
  when an owner-scoped include-deleted path is explicitly tested.
- Cross-user and deleted item responses do not reveal existence.
- No Notes request performs physical deletion.

Slice 6H-3B-4C defines these cases in pytest without implementing live
Supabase client logic. The executable assertions remain deferred until the
approved local-only runbook is followed and the approved artifact is applied in
the selected disposable local target.

The harness should distinguish:

- adapter validation, which proves request construction and caller token
  propagation; and
- RLS validation, which proves database policy behavior after an approved
  migration has been applied.

## 10. Migration Prerequisite

No executable Notes migration is committed or approved today. The future
harness cannot claim RLS coverage until:

1. A specific migration/RLS artifact is explicitly approved under
   [database-migration-policy.md](security/database-migration-policy.md).
2. The artifact is security-reviewed for RLS effects, privilege scope,
   rollback, and absence of secrets or real data.
3. The artifact is applied in a disposable local or approved non-production
   environment.
4. The harness validates synthetic user A/user B outcomes against that applied
   artifact.

Until then, live/local harness skeleton tests may exist only as skipped
scaffolding or adapter-smoke tests that clearly do not claim RLS enforcement.

## 11. Adapter Validation

Before RLS assertions run, the harness should validate that the live adapter
matches the fake transport contract:

- It consumes `UserScopedSupabaseClientDescriptor`.
- It creates a fresh request-scoped client per caller.
- It sends `Authorization: Bearer <verified caller access token>` as request
  authorization metadata.
- It uses `SUPABASE_PUBLISHABLE_KEY`, or documented legacy `SUPABASE_ANON_KEY`,
  as public API key metadata.
- It never selects or propagates `SUPABASE_SERVICE_ROLE_KEY`.
- It does not mutate global client auth state.
- It does not call refresh-token APIs, set persistent sessions, or require
  refresh tokens.
- It redacts URL/key/token/header values in failures, logs, snapshots, and
  assertion messages.

Adapter validation must not broaden public Notes API behavior. It should drive
the same `SupabaseNotesRepository` query flow that the fake tests already
exercise.

## 12. Security Risks

| Risk | Required control |
|---|---|
| Token leakage | Use short-lived synthetic tokens only; redact authorization headers, env values, logs, errors, and test ids |
| Service-role misuse | Keep service-role credentials out of request-path harness inputs and adapter construction |
| Cross-user leak | Preserve explicit `user_id` predicates and require user A/user B RLS assertions before live enablement |
| Cleanup failure | Use deterministic synthetic rows, owner-scoped cleanup, and coarse failure reporting without content |
| Accidental default CI execution | Require explicit env flag, explicit mode, marker opt-in, and no normal push workflow activation |
| False RLS confidence | Do not claim RLS coverage until an approved migration is applied in the target environment |
| Hosted staging drift | Validate against an approved non-production project only and document migration/version state |
| Flaky network dependency | Keep default CI fake/local; isolate live runs in manual opt-in commands or workflows |

## 13. Future Implementation Slices

1. **Slice 6H-3B-3A - Opt-in live test harness skeleton (completed)**
   Skipped-by-default pytest markers, redacted configuration guards, synthetic
   naming helpers, and placeholder tests now prove the harness cannot run
   without explicit opt-in. No SDK transport, credentials, migrations, or RLS
   execution were added.
2. **Slice 6H-3B-3B - Local Supabase setup guide (completed)**
   Document local-only setup steps, synthetic test users, placeholder
   configuration, cleanup expectations, and how the skipped skeleton would be
   enabled manually after approved prerequisites exist.
3. **Slice 6H-3B-3C - Hosted staging opt-in test plan**
   Document the controlled staging workflow, secret-store expectations,
   CI/manual workflow separation, redaction requirements, and rollback
   expectations for non-production hosted validation.
4. **Slice 6H-3B-4 - Approved migration/RLS validation planning (completed)**
   Plan the explicit database-artifact approval, security review, non-production
   application path, and synthetic owner-isolation validation before any
   executable migration or RLS test is added.
5. **Slice 6H-3B-4A - Migration/RLS draft review packet (completed)**
   Prepare the documentation-only review packet for a future artifact. Do not
   add executable SQL.
6. **Slice 6H-3B-4B - Approved local-only migration artifact (completed)**
   Add the local-only Markdown artifact outside `supabase/migrations/`. Do not
   execute it by default.
7. **Slice 6H-3B-4C - RLS validation tests behind opt-in harness (completed)**
   Add skipped-by-default Notes RLS validation case scaffolding behind the
   existing live harness, with default CI limited to gating and inventory
   checks.
8. **Slice 6H-3B-4C-R - Record explicit local RLS execution approval
   (completed)**
   Record local execution approval as pending, define the conditions required
   before approval can be granted, and keep hosted/staging/production/default CI
   execution not approved.
9. **Slice 6H-3B-4C-L - Local-only RLS execution dry-run preparation
   (completed)**
   Document the disposable local target assumptions, exact manual command
   boundary, rollback/cleanup procedure, evidence format, redaction checklist,
   and reviewer sign-off format without executing the artifact.
10. **Slice 6H-3B-4C-LA - Grant local-only RLS dry-run approval
    (completed)**
    Record constrained approval for a future local-only dry-run attempt. Do not
    execute the dry-run.
11. **Slice 6H-3B-4C-DR - Local-only RLS dry-run execution runbook
    (completed)**
    Prepare the careful runbook for the approved local-only attempt, including
    pre-execution checks, stop conditions, redacted evidence capture, and
    cleanup verification. Do not automatically execute merely because approval
    is recorded.
12. **Future approved local-only dry-run execution report**
    Follow the runbook only in a disposable local target, record redacted
    evidence, verify cleanup, and avoid claiming RLS enforcement from
    scaffold-only skips.
13. **Slice 6H-3B-4D - Hosted staging validation plan**
   Document controlled hosted non-production validation after local-only
   evidence is accepted or local execution is explicitly deferred.

## 14. Definition Of Done

Slice 6H-3B-3 is complete when:

- This document defines local and hosted staging harness modes.
- It specifies placeholder-only environment variables, explicit opt-in gates,
  default-CI exclusion, and no service-role request-path use.
- It defines synthetic data, cleanup, adapter validation, and RLS validation
  expectations without executing them.
- It records the migration/RLS approval prerequisite before any RLS coverage can
  be claimed.
- Existing Supabase planning docs point to this harness plan.
- The next recommended task is Slice 6H-3B-3A.
- No SDK implementation, live network behavior, credential, `.env` file,
  migration, SQL artifact, RLS execution, UI, AI, sync work, or public Notes API
  behavior change is introduced.

Slice 6H-3B-3A is complete when:

- Test-only integration scaffolding defines the `supabase_live` and
  `integration` markers and keeps the placeholder live test skipped by default.
- Gating helpers require the explicit opt-in flag, explicit local/staging mode,
  required placeholder environment names, and reject service-role request-path
  inputs.
- Tests prove default skip behavior, missing/invalid configuration handling,
  service-role rejection, redacted config/error rendering, synthetic naming
  rules, and no network access in the default path.
- The next recommended task is Slice 6H-3B-3B; no live SDK adapter, network
  behavior, credential, `.env` file, migration, SQL artifact, or RLS execution
  has been introduced.

Slice 6H-3B-3B is complete when:

- A local setup guide documents local-only/non-production prerequisites,
  placeholder environment names, synthetic user/token source expectations,
  cleanup rules, troubleshooting, and security checklist items.
- The guide states that `.env` files, real credentials, generated Supabase
  state, dumps/backups/database files, service-role keys, access tokens, SQL,
  and migrations must not be committed.
- The guide keeps the future harness env-gated and default CI disabled.
- The next recommended task is Slice 6H-3B-4 migration/RLS validation planning;
  no live SDK adapter, network behavior, credential, `.env` file, migration,
  SQL artifact, or RLS execution has been introduced.

Slice 6H-3B-4 is complete when:

- A migration/RLS validation plan defines artifact approval criteria, security
  review requirements, sanitized Notes behavior, a synthetic user A/B RLS
  validation matrix, migration review checklist, harness prerequisites,
  artifact policy, risks, and future implementation slices.
- It keeps executable SQL prohibited until explicit approval and sets the next
  recommended task to Slice 6H-3B-4A review-packet documentation.
- No live SDK adapter, network behavior, credential, `.env` file, migration,
  SQL artifact, or RLS execution has been introduced.

Slice 6H-3B-4C is complete when:

- Notes RLS validation cases are defined in pytest behind the existing opt-in
  harness.
- Default pytest/CI runs verify only case inventory, missing-env gating,
  synthetic user-token requirements, service-role rejection, and no-network
  default behavior.
- The live case functions remain skipped without executing a Supabase client,
  SQL, migrations, local artifact, or RLS validation.
- The next recommended task is Slice 6H-3B-4C-R because explicit local
  execution approval remains absent.

Slice 6H-3B-4C-R is complete when:

- The local RLS execution approval record exists and keeps local execution
  approval pending.
- The record explicitly blocks hosted Supabase, staging, production, default CI,
  real data, credentials, and service-role request-path usage.
- The record defines the local-only conditions required before any future
  execution approval can be granted.
- That completed slice led to Slice 6H-3B-4C-L.

Slice 6H-3B-4C-L is complete when:

- `docs/notes-local-rls-dry-run-preparation.md` documents the local-only
  objective, non-goals, current status, preconditions, preflight checklist,
  manual sequence, evidence format, cleanup checklist, approval decision point,
  and definition of done.
- Local execution approval remained pending until Slice 6H-3B-4C-LA granted
  it explicitly under constraints.
- That completed slice led to Slice 6H-3B-4C-LA.
- No live SDK adapter, network behavior, credential, `.env` file, migration,
  SQL artifact, local Supabase run, hosted Supabase connection, RLS execution,
  service-role request-path usage, or public Notes API behavior change has
  been introduced.

Slice 6H-3B-4C-LA is complete when:

- The local RLS execution approval record states that the local-only RLS
  dry-run attempt is approved under constraints.
- The approved scope is limited to a disposable local Supabase target, the
  local-only Markdown artifact, opt-in local harness, synthetic users,
  synthetic Notes rows, redacted evidence, and cleanup verification.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  committed `.env` files, committed `.sql` files, committed
  `supabase/migrations/*`, generated Supabase state, live repository mode,
  service-role request-path usage, and public Notes API behavior changes remain
  not approved.
- Required pre-execution conditions and dry-run stop conditions are documented.
- That completed slice led to Slice 6H-3B-4C-DR.
- No live SDK adapter, network behavior, credential, `.env` file, migration,
  SQL artifact, local Supabase run, hosted Supabase connection, RLS execution,
  service-role request-path usage, or public Notes API behavior change has
  been introduced.

Slice 6H-3B-4C-DR is complete when:

- `docs/notes-local-rls-dry-run-execution-runbook.md` documents the local-only
  pre-execution checks, stop conditions, execution sequence, redacted evidence
  capture, cleanup verification, and acceptance criteria.
- Related approval, preparation, validation, harness, and policy docs point to
  the runbook.
- The runbook keeps current scaffold-only skips separate from accepted RLS
  enforcement evidence.
- No live SDK adapter, network behavior, credential, `.env` file, migration,
  SQL artifact, local Supabase run, hosted Supabase connection, RLS execution,
  service-role request-path usage, or public Notes API behavior change has
  been introduced.
