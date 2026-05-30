# Database Migration And Artifact Policy

## Status

This is an interim security gate. No executable Supabase migration is currently
approved for commit. Until an explicit policy change is reviewed and approved,
`supabase/migrations/*.sql` remains ignored.

## Current Posture

- Architecture documents may describe intended tables, ownership boundaries, and
  RLS outcomes as sanitized, non-deployable summaries.
- Planning work must not add executable migrations, generated database state, or
  environment-specific database artifacts.
- Local Supabase setup documentation may describe future disposable local
  preparation with placeholders only; it must not commit generated Supabase
  state, local database files, credentials, or executable SQL.
- The repository being private does not make operational database artifacts safe
  to commit casually. Git history is durable and access can change over time.

## Prohibited Artifacts

Do not commit:

- live database dumps, production schema dumps, backups, snapshots, or exports;
- generated Supabase state, temporary runtime directories, or local metadata;
- `.env` files, connection strings, credentials, passwords, JWT secrets,
  service-role keys, refresh tokens, or access tokens;
- seed files containing real user, production, or otherwise sensitive data; or
- executable migration files before the approval gate below is completed.

## Future Migration Approval Gate

An executable migration may be introduced only after explicit approval for the
specific database change. Before commit, it must:

1. Be minimal and environment-independent, with no project identifiers,
   credentials, real data, or deployment-specific values.
2. Receive security review for privilege scope, RLS effects, data exposure,
   rollback considerations, and secret/data scanning.
3. Be accompanied by a clear execution and validation plan using synthetic data
   and an approved non-production environment first.
4. Change the ignore rule only as part of the explicitly approved migration
   review, not as a convenience during planning.

For Notes specifically,
[notes-migration-rls-validation-plan.md](../notes-migration-rls-validation-plan.md)
defines the review process, security checklist, validation matrix, and future
review-packet step that must precede any executable Notes migration/RLS
artifact. The draft review packet is recorded in
[notes-migration-rls-draft-review-packet.md](../notes-migration-rls-draft-review-packet.md);
the acceptance record is documented in
[notes-migration-rls-approval-record.md](../notes-migration-rls-approval-record.md).
That record allows the next local-only artifact preparation slice under the
documented constraints, but it does not approve production/staging execution,
live RLS tests, or service-role request-path usage.

The Slice 6H-3B-4B local artifact is recorded as Markdown at
[notes-local-migration-rls-artifact.md](../database/notes/notes-local-migration-rls-artifact.md).
It is not a Supabase migration file, is not stored under `supabase/migrations/`,
and must not be executed without a separate execution approval record.

The local execution approval gate is recorded in
[notes-local-rls-execution-approval-record.md](../notes-local-rls-execution-approval-record.md).
That record now approves a future local-only RLS dry-run attempt under strict
constraints. It does not approve creating or committing SQL files, adding
Supabase migrations, running hosted Supabase, staging or production execution,
default CI execution, committing credentials, using service-role credentials in
request-path code, enabling live repository mode, or changing public Notes API
behavior.

The local dry-run preparation checklist is recorded in
[notes-local-rls-dry-run-preparation.md](../notes-local-rls-dry-run-preparation.md).
It documents the preflight checks, manual local-only sequence, evidence format,
redaction expectations, and rollback/cleanup checklist for a future approval
decision. It remains non-executable documentation. The later approval remains
local-only and does not grant hosted, staging, production, or CI execution
approval.

The local-only dry-run execution runbook is recorded in
[notes-local-rls-dry-run-execution-runbook.md](../notes-local-rls-dry-run-execution-runbook.md).
It documents the pre-execution checks, stop conditions, opt-in local harness
boundary, redacted evidence template, cleanup sequence, and acceptance
criteria for the approved local-only attempt. It does not approve committed SQL
files, Supabase migrations, hosted Supabase, staging, production, default CI,
credentials in git, service-role request-path usage, or public Notes API
behavior changes.

The local dry-run blocker-resolution checklist is recorded in
[notes-local-rls-dry-run-blocker-resolution.md](../notes-local-rls-dry-run-blocker-resolution.md).
It documents the missing local-only prerequisites, placeholder-only environment
rules, disposable target requirements, synthetic data requirements, cleanup
proof expectations, stop conditions, and definition of ready before another
dry-run attempt. It does not execute SQL, create SQL files, add migrations, run
Supabase locally, connect to hosted Supabase, run RLS validation, or authorize
staging/production execution.

## Notes Design Handling

The intended Notes ownership and RLS behavior is documented in architecture
plans and the local-only Markdown artifact only. Those summaries are not an
auto-applied migration, have not been executed, and do not authorize staging or
production deployment.

## Git History Posture

- Removed migration artifacts must not remain in `HEAD`.
- The removed Notes SQL draft contained no secrets, credentials, or production
  data; therefore this project will not rewrite Git history at this time.
- Historical removal requires explicit approval and coordination because it
  changes repository history for all collaborators.
- Reserve history rewriting for discovered secrets, credentials, production
  data, other sensitive exposure, or a reviewed cleanup before public release.
- Private repository status is not a substitute for review discipline or future
  public-release preparation.
