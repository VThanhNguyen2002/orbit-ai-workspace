# Notes Local Migration/RLS Artifact

## Status Banner

This is a local-only draft artifact for future Notes table/RLS review and local
validation planning.

- Not executed.
- Not a Supabase migration file.
- Not placed under `supabase/migrations/`.
- Not approved for staging or production.
- Not approved for automatic CI execution.
- Not approved for live Supabase execution.
- Requires separate approval before becoming executable SQL or being run
  anywhere.

Do not copy this artifact into an SQL runner, Supabase CLI command, hosted
database console, CI job, or migration directory without a separate execution
approval record.

## Source-Of-Truth References

- Approval record commit:
  `db87ad83892ea9c532b9e34a164ce6778b4412b0`
- Accepted review packet commit:
  `a8b435aee7f31b4e4f414b4ae8165baa062fb414`
- Approval record:
  [notes-migration-rls-approval-record.md](../../notes-migration-rls-approval-record.md)
- Review packet:
  [notes-migration-rls-draft-review-packet.md](../../notes-migration-rls-draft-review-packet.md)
- Validation plan:
  [notes-migration-rls-validation-plan.md](../../notes-migration-rls-validation-plan.md)
- Database artifact policy:
  [database-migration-policy.md](../../security/database-migration-policy.md)
- API contract:
  [api-contract.md](../../architecture/api-contract.md)
- Data model:
  [data-model.md](../../architecture/data-model.md)
- Auth/RLS architecture:
  [auth-and-rls.md](../../architecture/auth-and-rls.md)
- Backend Notes schema:
  `apps/api/app/schemas/notes.py`
- Shared Notes contract:
  `packages/shared/src/domain/index.ts`

Shared/backend contract drift guard status: current CI checks the stable Notes
wire surface across shared Zod and backend Pydantic/routes. It intentionally
does not prove full UUID/date-time type equivalence and currently treats shared
`sync_metadata` as optional and not emitted by backend Notes routes.

## Proposed Local Table Artifact

The following is a sanitized SQL-like draft inside Markdown only. It is not a
Supabase migration file and must not be executed by default.

```sql
-- REVIEW DRAFT ONLY. DO NOT EXECUTE BY DEFAULT.
-- Local-only Notes table/RLS artifact candidate.
-- No real data, credentials, project identifiers, seeds, dumps, or generated
-- Supabase state are included.

create table if not exists public.notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id),
  title text not null,
  content text not null default '',
  content_type text not null default 'plain',
  is_archived boolean not null default false,
  is_deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz null,
  version bigint not null default 0,
  sync_metadata jsonb null,

  constraint notes_title_length check (
    char_length(title) between 1 and 500
  ),
  constraint notes_content_length check (
    char_length(content) <= 50000
  ),
  constraint notes_content_type_allowed check (
    content_type in ('plain', 'markdown')
  ),
  constraint notes_version_non_negative check (
    version >= 0
  ),
  constraint notes_deleted_timestamp_consistency check (
    (is_deleted = false and deleted_at is null)
    or
    (is_deleted = true and deleted_at is not null)
  ),
  constraint notes_sync_metadata_object check (
    sync_metadata is null
    or jsonb_typeof(sync_metadata) = 'object'
  )
);

create index if not exists notes_owner_visible_updated_idx
  on public.notes (user_id, is_deleted, updated_at desc, id);

create index if not exists notes_owner_archive_updated_idx
  on public.notes (user_id, is_archived, is_deleted, updated_at desc, id);

create index if not exists notes_owner_title_idx
  on public.notes (user_id, is_deleted, lower(title), id);

create index if not exists notes_owner_version_idx
  on public.notes (user_id, id, version);
```

Table design notes:

- `public.users(id)` is the assumed owner foreign-key target from the current
  architecture docs. If the local validation schema uses a different profile
  table or direct `auth.users` reference, that change needs review before
  execution.
- `is_deleted` is included because both current shared and backend Notes models
  expose it.
- `sync_metadata` is included as optional JSON because the shared contract
  allows it, while the backend currently does not emit it. Additional shape
  constraints remain an open question.
- No triggers or `SECURITY DEFINER` functions are included in this draft.
  Timestamp and version mutation remain application/repository behavior unless a
  later reviewed artifact adds narrowly scoped helpers.

## Proposed RLS Artifact

The following is a sanitized SQL-like draft inside Markdown only. It is not a
Supabase migration file and must not be executed by default.

```sql
-- REVIEW DRAFT ONLY. DO NOT EXECUTE BY DEFAULT.
-- RLS intent: authenticated callers can access only their own Notes rows.
-- No public read policy, service-role path, broad grant, DELETE policy, or
-- SECURITY DEFINER helper is included.

alter table public.notes enable row level security;

alter table public.notes force row level security;

create policy notes_select_own
  on public.notes
  for select
  to authenticated
  using (
    user_id = auth.uid()
  );

create policy notes_insert_own
  on public.notes
  for insert
  to authenticated
  with check (
    user_id = auth.uid()
  );

create policy notes_update_own
  on public.notes
  for update
  to authenticated
  using (
    user_id = auth.uid()
  )
  with check (
    user_id = auth.uid()
  );

-- Intentionally absent:
-- No FOR DELETE policy is defined for request-path CRUD.
-- Public Notes DELETE remains a soft-delete UPDATE through notes_update_own.
```

RLS design notes:

- The policies are scoped to authenticated callers and owner rows only.
- Insert and update checks reject rows whose `user_id` does not match
  `auth.uid()`.
- Application-level `user_id` predicates remain required after RLS exists.
- No service-role behavior is part of this request-path artifact.
- No grant statements are included. Any later grant needed for local PostgREST
  validation must be reviewed for least privilege before execution.

## Owner-Spoofing Prevention Notes

Client create/update DTOs do not contain `user_id`; request-path ownership must
come from the verified auth context. The future repository path should continue
to set or constrain `user_id` from the authenticated caller, not from client
input.

The RLS insert `with check` condition is the database boundary that rejects a
row whose owner differs from the authenticated user. The update policy uses both
`using` and `with check` so an owner cannot move a row to another user and a
caller cannot update another user's row.

Local validation must include a synthetic user A/user B spoofing attempt before
any RLS coverage is claimed.

## Soft-Delete And Version Semantics

- Update and delete paths remain version-gated at the application/repository
  layer with the expected `version` value.
- Successful mutable operations increment `version` and update `updated_at`.
- Public Notes delete remains a soft-delete update that sets `is_deleted=true`
  and `deleted_at` to the deletion timestamp.
- No request-path CRUD operation physically deletes a Notes row.
- Default reads hide deleted rows through application predicates, while any
  `include_deleted` path remains owner-scoped by both application predicates and
  RLS.
- Physical cleanup remains separately approved administrative work and is not
  part of this artifact.

## Rollback And Cleanup Notes

This artifact is not executed in this slice, so no rollback command is provided
or approved.

Before any future local execution, reviewers must document:

- the disposable local target;
- how synthetic users and rows are identified;
- how local-only test rows are cleaned up without exposing note content;
- how failed local setup is reset without touching staging or production; and
- how to confirm no generated Supabase state, dumps, backups, database files,
  credentials, or `.env` files enter git.

No production rollback commands belong in this artifact.

## Validation Checklist For Later Local Execution

- [ ] Separate approval exists to execute this local artifact.
- [ ] Execution target is disposable local Supabase only.
- [ ] Synthetic users only.
- [ ] Synthetic Notes data only.
- [ ] No real data, real emails, real note content, dumps, backups, or snapshots.
- [ ] No credentials, tokens, service-role keys, project identifiers, or `.env`
  files in git.
- [ ] RLS is enabled on `public.notes`.
- [ ] User A can create, list, get, update, and soft-delete User A notes.
- [ ] User A cannot see User B notes.
- [ ] User A cannot mutate or soft-delete User B notes.
- [ ] Insert owner spoofing is rejected.
- [ ] `include_deleted` remains owner-scoped.
- [ ] Public Notes delete performs soft-delete update only.
- [ ] No service-role credential is used in request-path validation.
- [ ] Cleanup succeeds and reports only coarse synthetic row counts.
- [ ] Validation evidence redacts tokens, Auth payloads, emails, and note
  content.

## Known Open Questions

- Exact `auth.uid()` behavior in the local Supabase test environment must be
  confirmed before execution.
- `is_deleted` is kept in the table as a backend/shared contract field; a future
  review may decide whether it should be derived from `deleted_at` instead.
- `sync_metadata` JSON shape may need stricter database constraints if the
  backend starts emitting or mutating it.
- Index shape should be revisited after real usage patterns and query plans are
  available.
- The correct owner foreign-key target for local validation must be confirmed
  against the approved local schema.

## Definition Of Done

Slice 6H-3B-4B is complete when:

- This Markdown artifact exists outside `supabase/migrations/`.
- No `.sql` file, Supabase migration file, `.env` file, credential, generated
  Supabase state, seed, dump, backup, or database file is added.
- No SQL or RLS test is executed.
- No live Supabase connection is made.
- The proposed table and RLS behavior are documented for local-only review.
- Owner-spoofing, soft-delete/version behavior, rollback/cleanup notes,
  validation checklist, and open questions are documented.
- The next recommended task is Slice 6H-3B-4C, but execution of this artifact
  remains blocked until separate approval is recorded.
- Verification and CI pass.
