# Notes Migration/RLS Validation Plan

## Status

Slice 6H-3B-4 defines the approval and validation plan for a future Notes
migration/RLS artifact. This document is security-first planning only. It does
not add executable SQL, migrations, generated Supabase state, credentials, live
SDK wiring, local Supabase execution, hosted Supabase access, or RLS tests.

Slice 6H-3B-4A adds the documentation-only draft review packet in
[notes-migration-rls-draft-review-packet.md](notes-migration-rls-draft-review-packet.md),
and Slice 6H-3B-4A-R records acceptance in
[notes-migration-rls-approval-record.md](notes-migration-rls-approval-record.md).
Slice 6H-3B-4B adds the local-only Markdown artifact in
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
Slice 6H-3B-4C adds skipped-by-default Notes RLS validation case scaffolding in
`apps/api/tests/integration/test_notes_rls_validation.py`. It defines the
validation cases and safety gates only; it does not execute the local artifact
or validate RLS. Slice 6H-3B-4C-R records the local execution approval gate in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md)
and kept local RLS execution approval pending at that time. Slice 6H-3B-4C-L
adds the local-only dry-run preparation checklist in
[notes-local-rls-dry-run-preparation.md](notes-local-rls-dry-run-preparation.md)
without executing the artifact. Slice 6H-3B-4C-LA records constrained approval
for a future local-only RLS dry-run attempt without executing it. Slice
6H-3B-4C-DR adds the local-only execution runbook in
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
without executing the artifact, running Supabase locally, or validating RLS.
The next recommended action is to follow that runbook only for an approved
disposable local attempt and produce redacted evidence, or explicitly defer
local execution before hosted staging planning.

## 1. Objective

Define the review process, approval criteria, artifact policy, and validation
matrix required before a future Notes migration/RLS artifact may be committed
or tested against Supabase.

The plan must make future reviewers able to answer:

- whether the proposed Notes table behavior matches the existing public Notes
  API and repository contract;
- whether RLS enforces owner isolation independently of application-level
  `user_id` predicates;
- whether the migration artifact is minimal, environment-independent, and free
  of secrets or real data;
- whether validation uses only synthetic users and data in local or approved
  non-production targets; and
- whether default CI remains credential-free and disabled for live/local
  Supabase tests.

## 2. Non-Goals

- Do not add executable SQL, migrations, policies, seeds, database dumps, or
  generated Supabase state.
- Do not run Supabase locally or connect to hosted Supabase.
- Do not add real project URLs, public keys, service-role keys, JWT secrets,
  access tokens, refresh tokens, passwords, `.env` files, or other credentials.
- Do not execute RLS validation tests.
- Do not add a live Supabase SDK adapter or enable live Notes repository mode.
- Do not add service-role use to the Notes request path.
- Do not change public Notes API behavior, shared contracts, frontend/UI, Expo,
  AI, or offline sync behavior.
- Do not treat this plan as approval to commit a migration.

## 3. Current Baseline

- Memory Notes persistence is the default for normal local, test, and CI runs.
- `SupabaseNotesRepository` is scaffolded behind an injected user-scoped client
  protocol and is not wired into request handling.
- Fake repository and fake SDK transport tests prove query shape, owner
  predicates, caller-token propagation assumptions, redaction, no-network
  behavior, and service-role exclusion without importing the Supabase SDK.
- The live/local harness skeleton is skipped by default and requires explicit
  opt-in, explicit `local` or `staging` mode, required placeholder environment
  names, synthetic user token placeholders, and absence of
  `SUPABASE_SERVICE_ROLE_KEY`.
- The local Supabase setup guide documents placeholder-only preparation and
  reiterates that RLS coverage is blocked until an approved migration/RLS
  artifact exists.
- The draft review packet describes the proposed future Notes table/RLS design
  in sanitized prose and records review questions, approval gates, and risks
  before any SQL artifact exists.
- The local-only artifact is a Markdown review document outside
  `supabase/migrations/`; it is not a Supabase migration file and has not been
  executed.
- The RLS validation test skeleton defines the required user A/user B cases
  behind the existing opt-in live harness. Default CI verifies case inventory,
  missing-env gating, required synthetic token placeholders, service-role
  rejection, and no-network behavior only.
- The local execution approval record now approves a future local-only RLS
  dry-run attempt under strict constraints. It does not approve automatic
  execution, hosted Supabase, staging, production, default CI, committed SQL,
  migrations, real data, credentials, service-role request-path usage, live
  repository mode, or public Notes API behavior changes.
- The local dry-run preparation document records the disposable local target
  assumptions, preflight checklist, manual dry-run sequence, evidence format,
  redaction expectations, and rollback/cleanup checklist.
- The local dry-run execution runbook records the exact local-only preflight
  commands, stop conditions, opt-in harness command boundary, redacted evidence
  template, cleanup sequence, and acceptance criteria.
- No `.sql` Notes migration or auto-applied RLS artifact is approved or
  committed.
- No RLS behavior has been validated against local or hosted Supabase.

## 4. Why Committed Executable SQL Remains Prohibited For Now

Committed executable SQL remains prohibited because the repository does not yet
have an approved migration file, hosted execution path, or completed synthetic
RLS validation evidence. Slice 6H-3B-4C-LA approves only a future local-only
dry-run attempt that manually materializes the reviewed Markdown artifact in a
disposable local target under the documented constraints.

Specific reasons:

- Git history is durable. A private repository can later become broader in
  access or public, so operational database artifacts need review before they
  enter history.
- A migration can change privilege boundaries, grants, ownership behavior,
  timestamps, soft-delete semantics, and RLS outcomes. Those effects must be
  reviewed before commit.
- Service-role/admin execution and request-path validation have different
  security properties. Planning must keep those boundaries separate before any
  artifact is introduced.
- A migration without an RLS validation matrix can create false confidence.
- Generated Supabase state, dumps, local database files, and environment-bound
  metadata are not portable review artifacts.

Until a separate migration-file approval is explicit,
`supabase/migrations/*.sql` remains ignored and no SQL file should be
committed. Fenced SQL-like draft content in Markdown may be manually
materialized only for the approved local-only dry-run attempt, after the
runbook and pre-execution checks are satisfied.

## 5. Approval Criteria For Future Migration/RLS Artifacts

A future artifact may be proposed only after a review packet shows all of the
following:

- The artifact is minimal and limited to the Notes table/RLS behavior under
  review.
- It is environment-independent and contains no project identifiers, connection
  strings, credentials, tokens, real user identifiers, real emails, or real note
  content.
- It preserves the current Notes public API behavior: owner-scoped CRUD,
  optimistic version checks, soft deletion, non-disclosing not-found behavior,
  and no request-path physical delete.
- It enables or requires RLS for Notes before live request-path persistence is
  considered.
- It binds read, insert, update, and soft-delete behavior to the authenticated
  caller identity.
- It avoids broad grants and avoids widening access for anonymous, public,
  service-role, or cross-user paths.
- It does not introduce unsafe privileged functions. Any privileged function
  requires explicit justification, narrowed scope, and separate review.
- It includes rollback and cleanup considerations for non-production trials.
- It includes a synthetic validation matrix and expected evidence format.
- It passes secret/data scanning before commit.

Approval must be specific to the artifact being committed. Approval for this
plan, a future review packet, or local setup instructions is not approval to
commit arbitrary SQL.

## 6. Required Security Review Checklist

Reviewers must confirm:

- The artifact contains no production data, seed data, dumps, backups,
  credentials, tokens, connection strings, project identifiers, or real user
  content.
- RLS is enabled for every Notes user-data path before live Notes persistence is
  enabled.
- Read behavior returns only rows owned by the authenticated caller.
- Insert behavior prevents the caller from creating a row for another owner.
- Update and soft-delete behavior are limited to owned rows.
- Physical delete is not part of public Notes CRUD.
- Application-level `user_id` predicates remain required after RLS exists.
- Service-role credentials are absent from request-path code, harness inputs,
  logs, tests, and docs examples.
- Grants are narrow and do not provide broad table access beyond the intended
  public-key plus caller-JWT request path.
- Any trigger, default, generated value, or helper function is minimal and does
  not bypass owner checks.
- Any privileged function is absent, or explicitly justified and reviewed for
  search path, caller influence, write scope, and data exposure.
- Rollback and non-production cleanup are documented.
- Validation evidence uses synthetic users/data only and redacts keys, tokens,
  Auth payloads, URLs with secrets, and note content.

## 7. Proposed Notes Table/RLS Behavior

This section is sanitized prose only. It is not a migration and must not be
copied into an executable SQL file.

The future Notes persistence target is a user-owned table with a stable note
identifier, an authenticated owner identifier, editable title/content fields,
content type, archive state, soft-delete state, creation/update timestamps,
optional deletion timestamp, and monotonically increasing version.

Expected behavior:

- Each Notes row belongs to exactly one authenticated user.
- Normal reads return only rows owned by the authenticated caller.
- Default reads hide soft-deleted rows through application predicates; RLS still
  limits any include-deleted path to the owner.
- Inserts must create rows for the authenticated caller only.
- Updates must affect only rows owned by the authenticated caller.
- The public Notes delete operation remains a soft-delete update owned by the
  caller.
- Physical deletion is reserved for separately approved administrative cleanup,
  not request-path CRUD.
- RLS and application-level owner predicates are complementary; neither replaces
  the other.

## 8. RLS Validation Matrix

The future opt-in harness must validate RLS with synthetic user A and synthetic
user B after the approved artifact is applied in local or approved
non-production Supabase.

| Case | Actor | Target data | Expected outcome |
|---|---|---|---|
| Select own notes | User A | User A synthetic notes | User A can select visible own notes |
| Block cross-user select | User A | User B synthetic notes | User A cannot select or infer User B notes |
| Block cross-user update | User A | User B synthetic note | Update is rejected or returns the same non-disclosing not-found outcome as the API contract |
| Block cross-user soft delete | User A | User B synthetic note | Soft-delete update is rejected or returns the same non-disclosing not-found outcome as the API contract |
| Bind insert owner | User A | Insert payload attempting User B ownership | Insert is rejected; no User B-owned row is created by User A |
| Allow own insert | User A | Insert payload for User A ownership | Insert succeeds only for User A ownership |
| Owner-scoped soft delete | User A | User A synthetic note | Soft delete succeeds as an owner-scoped update and hides the note from default reads |
| Include deleted remains owner-scoped | User A | User A deleted note and User B deleted note | User A can inspect only own deleted note when an owner-scoped include-deleted path is explicitly tested |
| No physical delete in CRUD | User A | User A synthetic note | Public Notes delete path performs only soft-delete behavior |

Slice 6H-3B-4C maps this matrix into skipped pytest case functions. Those case
functions continue to skip after the base live-harness gate because no live
client, local artifact execution approval, or applied RLS target exists in this
slice.

Validation evidence must distinguish RLS enforcement from adapter behavior.
Adapter validation proves request construction and caller-token propagation.
RLS validation proves database policy behavior after the approved artifact is
applied.

## 9. Migration Review Checklist

Before any migration file is approved for commit, reviewers must verify:

- No production data, production schema dump, backup, snapshot, or seed with
  real data is included.
- No credentials, passwords, JWT secrets, service-role keys, access tokens,
  refresh tokens, private keys, connection strings, or project identifiers are
  included.
- No service-role key is required for request-path Notes behavior or harness
  validation.
- No broad grants are introduced.
- No unsafe privileged function is introduced. Any privileged function must be
  explicitly justified, narrowly scoped, and reviewed before commit.
- Rollback and cleanup considerations are documented, including how to remove
  synthetic rows from local or approved non-production environments.
- The artifact is minimal and environment-independent.
- Secret/data scans pass before commit.
- The artifact remains uncommitted until approval is recorded.

## 10. Test Harness Prerequisites

RLS tests may be added or enabled only after all prerequisites are true:

- A specific Notes migration/RLS artifact has been approved.
- The approved artifact has been applied in a disposable local project or an
  approved non-production staging project.
- The target contains only synthetic users and synthetic Notes data for the
  harness.
- The harness uses explicit opt-in configuration, including
  `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1`.
- `SYNAPSE_SUPABASE_TEST_MODE` is explicitly set to `local` or `staging`.
- The harness uses `SUPABASE_PUBLISHABLE_KEY`, or a reviewed legacy
  `SUPABASE_ANON_KEY`, plus synthetic user access-token sources.
- `SUPABASE_SERVICE_ROLE_KEY` is absent from request-path harness inputs.
- Default CI remains disabled for live/local Supabase tests.
- Logs and failures redact keys, tokens, authorization headers, Auth payloads,
  URLs with secrets, user emails, and note content.

## 11. Artifact Policy

- No `.sql` file or auto-applied migration is committed until explicit approval
  is granted for that specific executable artifact.
- The migration file must be minimal, environment-independent, and scoped to the
  reviewed Notes behavior.
- Generated Supabase state remains ignored and uncommitted.
- `.env` files, dumps, backups, SQLite/db files, local metadata, and generated
  runtime directories remain uncommitted.
- A future approved migration change must update ignore rules only as part of
  that explicit review, not as a convenience during planning.
- Review packets and local-only artifacts may describe intended behavior in
  prose, checklists, or clearly labeled fenced SQL-like drafts. They must state
  when draft content is not approved for default execution.

## 12. Security Risks

| Risk | Required control |
|---|---|
| RLS bypass | Require public-key plus caller-JWT request path, approved RLS, and user A/B validation before live enablement |
| Cross-user leakage | Keep application `user_id` predicates and validate RLS blocks cross-user select, update, and soft-delete attempts |
| Service-role misuse | Keep service-role credentials out of request-path code, adapter construction, harness inputs, and validation evidence |
| Token leakage | Use short-lived synthetic access tokens and redact tokens, authorization headers, Auth payloads, and env values |
| Cleanup failure | Use deterministic synthetic prefixes, owner-scoped cleanup, and coarse cleanup reports without note content |
| Accidental live CI execution | Keep default CI unset for live flags; require explicit env opt-in, mode, markers, and reviewed manual workflow separation |
| False RLS confidence | Do not infer database enforcement from fake tests, adapter tests, or setup docs |
| Unsafe migration scope | Require artifact-specific review for grants, functions, rollback, and environment independence |

## 13. Future Implementation Slices

1. **Slice 6H-3B-4A - Migration/RLS draft review packet (completed)**
   Prepare a documentation-only packet with the proposed artifact scope,
   sanitized behavior summary, reviewer checklist, validation evidence plan, and
   rollback/cleanup notes. Do not commit executable SQL.
2. **Slice 6H-3B-4A-R - Record Migration/RLS review packet approval (completed)**
   Record external review acceptance and the remaining non-approval boundaries.
3. **Slice 6H-3B-4B - Approved local-only migration artifact (completed)**
   Add the minimal environment-independent Markdown artifact for local-only
   validation review. Keep it outside `supabase/migrations/`, do not execute it,
   and keep generated Supabase state, credentials, and real data out of git.
4. **Slice 6H-3B-4C - RLS validation tests behind opt-in harness (completed)**
   Add skipped-by-default tests that validate the approved artifact with
   synthetic users and explicit local env gates only after separate execution
   approval is recorded.
5. **Slice 6H-3B-4C-R - Record explicit local RLS execution approval
   (completed)**
   Record that local RLS execution approval remains pending, define the local
   approval conditions, and keep staging, production, hosted Supabase, default
   CI, real data, credentials, and service-role request-path usage not approved.
6. **Slice 6H-3B-4C-L - Local-only RLS execution dry-run preparation
   (completed)**
   Document the disposable local target assumptions, exact manual command
   boundary, rollback/cleanup procedure, evidence format, redaction checklist,
   and reviewer sign-off format needed before local execution approval can be
   granted. Do not execute the artifact.
7. **Slice 6H-3B-4C-LA - Grant local-only RLS dry-run approval
   (completed)**
   Record constrained approval for a future local-only dry-run attempt using
   the preparation document as the review boundary. Do not execute the dry-run.
8. **Slice 6H-3B-4C-DR - Local-only RLS dry-run execution runbook
   (completed)**
   Prepare the careful runbook for the approved local-only attempt, including
   pre-execution checks, stop conditions, redacted evidence capture, and cleanup
   verification. Do not automatically execute merely because approval is
   recorded.
9. **Future approved local-only dry-run execution report**
   Follow the runbook only in a disposable local target, record redacted
   evidence, verify cleanup, and avoid claiming RLS enforcement from
   scaffold-only skips.
10. **Slice 6H-3B-4D - Hosted staging validation plan**
   Document controlled hosted non-production validation, secret-store handling,
   workflow separation, redaction, rollback, and evidence requirements after
   local-only evidence is accepted or local execution is explicitly deferred.

## 14. Definition Of Done

Slice 6H-3B-4 is complete when:

- This plan defines the migration/RLS approval process, security checklist,
  sanitized Notes behavior, validation matrix, artifact policy, risks, and
  future implementation slices.
- The plan explains why executable SQL remains prohibited until explicit
  approval.
- Related Supabase planning docs point to this plan.
- This plan led to **Slice 6H-3B-4A - Migration/RLS draft review packet** as
  the required review-packet step before any executable artifact.
- No runtime code, tests, executable SQL, migrations, `.env` files, credentials,
  generated Supabase state, live Supabase execution, live SDK adapter, live
  repository mode, service-role request-path usage, frontend/UI, Expo, AI,
  offline sync, or public Notes API behavior change is introduced.

Slice 6H-3B-4A is complete when:

- A draft review packet documents current Notes contract sources, proposed
  future table/RLS behavior in sanitized prose, review checklist, risk analysis,
  review questions, and approval gates.
- The next recommended task is Slice 6H-3B-4B, but only after the review packet
  is accepted and approvals are recorded.
- No runtime code, tests, executable SQL, migrations, `.env` files, credentials,
  generated Supabase state, live Supabase execution, live SDK adapter, live
  repository mode, service-role request-path usage, frontend/UI, Expo, AI,
  offline sync, or public Notes API behavior change is introduced.

Slice 6H-3B-4B is complete when:

- A local-only Markdown artifact documents the Notes table/RLS draft outside
  `supabase/migrations/`.
- The artifact includes status warnings, source references, fenced SQL-like
  draft content, owner-spoofing notes, soft-delete/version behavior,
  rollback/cleanup notes, validation checklist, and open questions.
- The next recommended task is Slice 6H-3B-4C, but only after separate approval
  exists to execute the local artifact.
- No runtime code, tests, `.sql` files, Supabase migrations, `.env` files,
  credentials, generated Supabase state, Supabase execution, live repository
  mode, service-role request-path usage, frontend/UI, Expo, AI, offline sync,
  or public Notes API behavior change is introduced.

Slice 6H-3B-4C is complete when:

- `apps/api/tests/integration/test_notes_rls_validation.py` defines the user
  A/user B RLS validation cases behind the existing opt-in live harness.
- Default CI verifies only scaffold inventory and safety gates.
- The tests remain skipped by default and do not import a Supabase client,
  execute SQL, apply the local artifact, connect to local or hosted Supabase,
  use service-role request-path credentials, or change public Notes API
  behavior.
- The next recommended task is Slice 6H-3B-4C-R because explicit local RLS
  execution approval remains absent.

Slice 6H-3B-4C-R is complete when:

- `docs/notes-local-rls-execution-approval-record.md` records local RLS
  execution approval as pending.
- The record documents the required conditions for a later local-only approval:
  disposable local Supabase, synthetic users/data only, no credentials in git,
  local artifact policy review, rollback/cleanup documentation, RLS test matrix
  mapping, no service-role request-path usage, and explicit reviewer approval.
- Staging, production, hosted Supabase, default CI, real data, credentials,
  SQL files, migrations, and live RLS validation remain not approved.
- That completed slice led to Slice 6H-3B-4C-L.

Slice 6H-3B-4C-L is complete when:

- `docs/notes-local-rls-dry-run-preparation.md` documents the objective,
  non-goals, current status, preconditions, preflight checklist, manual
  dry-run sequence, evidence format, rollback/cleanup checklist, approval
  decision point, and definition of done for a future local-only dry-run.
- Local execution approval remained pending until Slice 6H-3B-4C-LA granted
  it explicitly under constraints.
- That completed slice led to Slice 6H-3B-4C-LA.
- No runtime code, tests, executable SQL, migrations, `.env` files,
  credentials, generated Supabase state, local Supabase run, hosted Supabase
  connection, live RLS validation, live repository mode, service-role
  request-path usage, frontend/UI, Expo, AI, offline sync, or public Notes API
  behavior change is introduced.

Slice 6H-3B-4C-LA is complete when:

- `docs/notes-local-rls-execution-approval-record.md` records that the
  local-only RLS dry-run attempt is approved under constraints.
- The approved scope is limited to a disposable local Supabase target, the
  local-only Markdown artifact, opt-in local harness, synthetic users,
  synthetic Notes rows, redacted evidence, and cleanup verification.
- Staging, production, hosted Supabase, default CI, real data, credentials,
  committed `.env` files, committed `.sql` files, committed
  `supabase/migrations/*`, generated Supabase state, live repository mode,
  service-role request-path usage, and public Notes API behavior changes remain
  not approved.
- Required pre-execution conditions and dry-run stop conditions are documented.
- That completed slice led to Slice 6H-3B-4C-DR.
- No runtime code, tests, executable SQL files, migrations, `.env` files,
  credentials, generated Supabase state, local Supabase run, hosted Supabase
  connection, live RLS validation, live repository mode, service-role
  request-path usage, frontend/UI, Expo, AI, offline sync, or public Notes API
  behavior change is introduced.

Slice 6H-3B-4C-DR is complete when:

- `docs/notes-local-rls-dry-run-execution-runbook.md` documents the local-only
  source-of-truth references, required inputs, pre-execution checks, stop
  conditions, execution sequence, redacted evidence template, cleanup sequence,
  and acceptance criteria.
- Related approval, preparation, validation, harness, and policy docs point to
  the runbook.
- The runbook states that current scaffold-only skips are safety-gate evidence
  only and not RLS enforcement evidence.
- No runtime code, tests, executable SQL files, migrations, `.env` files,
  credentials, generated Supabase state, local Supabase run, hosted Supabase
  connection, live RLS validation, live repository mode, service-role
  request-path usage, frontend/UI, Expo, AI, offline sync, or public Notes API
  behavior change is introduced.
