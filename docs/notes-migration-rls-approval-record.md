# Notes Migration/RLS Approval Record

## Status

Slice 6H-3B-4A-R records acceptance of the Notes migration/RLS draft review
packet by external ChatGPT engineering/security review. This record approves
only the sanitized table/RLS design review scope described below.

This is documentation-only. It does not add, approve, or execute SQL.

## Accepted Review

- Accepted review packet commit:
  `a8b435aee7f31b4e4f414b4ae8165baa062fb414`
- Accepted scope: sanitized Notes table/RLS design review only.
- External ChatGPT engineering/security review: accepted.

The accepted packet covers proposed Notes table shape, owner-scoped RLS
behavior, current shared/backend contract differences, risk analysis, review
questions, and security checklist expectations. It remains non-executable
documentation.

## Not Approved

This record does not approve:

- executable SQL execution;
- Supabase migration execution;
- production migration;
- staging migration;
- live RLS tests;
- live Supabase execution;
- service-role request-path usage;
- real data, real credentials, `.env` files, dumps, backups, generated
  Supabase state, or environment-bound artifacts; or
- runtime code, public Notes API behavior, frontend/UI, Expo, AI, or offline
  sync changes.

SQL artifact approval is not yet granted by this record. Production/staging
execution approval is not granted. Live Supabase execution approval is not
granted. Service-role request-path usage remains prohibited.

## Allowed Next Slice

The next allowed slice is **Slice 6H-3B-4B - Approved local-only migration
artifact**.

Slice 6H-3B-4B may prepare the local-only Notes migration/RLS artifact under the
documented policy constraints, but it must still not execute the artifact by
default and must not broaden runtime behavior.

## Constraints For Slice 6H-3B-4B

The next slice must remain:

- local-only;
- synthetic-only;
- free of real data, production/staging dumps, backups, and snapshots;
- free of credentials, tokens, service-role keys, project identifiers, and
  `.env` files;
- environment-independent;
- disabled for execution by default;
- scoped to the accepted Notes table/RLS design;
- compatible with current public Notes API behavior; and
- subject to security review before commit or execution of any executable
  artifact.

Any later local or hosted execution remains blocked until a separate execution
plan and approval are recorded.

## Local Artifact Record

Slice 6H-3B-4B creates a non-auto-executable local-only review artifact at
[notes-local-migration-rls-artifact.md](database/notes/notes-local-migration-rls-artifact.md).
The artifact is a Markdown review document, not a Supabase migration file, and
it is not placed under `supabase/migrations/`.

This record allows the artifact to be reviewed as a local-only draft. It still
does not approve:

- executing the artifact;
- copying fenced SQL-like draft content into a runnable `.sql` file;
- applying the artifact to local, staging, production, or hosted Supabase;
- enabling RLS tests; or
- using service-role credentials in request-path behavior.

## Local Execution Approval Gate

Slice 6H-3B-4C-R records the local execution approval gate in
[notes-local-rls-execution-approval-record.md](notes-local-rls-execution-approval-record.md).

That record keeps local RLS execution approval pending. It does not approve
executing the local artifact, running opt-in RLS validation, creating SQL files,
adding Supabase migrations, connecting to hosted Supabase, running default CI
live tests, committing credentials, or using service-role credentials in the
request path.

The next recommended task is **Slice 6H-3B-4C-L - Local-only RLS execution
dry-run preparation**. That task must still be documentation/preparation only
unless a later approval record explicitly grants local execution.
