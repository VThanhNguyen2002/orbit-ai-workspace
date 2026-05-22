# Notes Persistence And Auth Integration Plan

## Status

Slice 6E foundation is now in place. The Notes backend has an auth context
boundary, a repository protocol, the deterministic in-memory repository remains
the default, and a Supabase-ready repository scaffold plus draft migration/RLS
file exist. Live Supabase client wiring, full JWT verification, provider
configuration, secrets, frontend UI, and sync engine behavior remain deferred.

## Current Implemented Surface

- Shared Notes CRUD contracts exist in `@synapse/shared`.
- FastAPI Notes routes exist under `/v1/notes`.
- `@synapse/api-client` exposes `client.notes.list/create/get/update/delete`.
- API route storage defaults to the process-local memory repository and is reset
  on process restart.
- API auth uses `get_auth_context`. Local/test `dev` mode returns the safe
  `dev_user` identity; future `jwt` mode validation is isolated behind the same
  dependency.
- `supabase/migrations/20260522000000_create_notes.sql` drafts `public.notes`,
  indexes, soft-delete/version fields, and own-user RLS policies.
- `apps/api/app/repositories/notes_supabase.py` contains the mapping and
  conditional write scaffold, but requires an injected user-scoped Supabase
  client before it can be used in request paths.

## Target State

Notes CRUD should become a normal authenticated backend path:

1. The client sends `Authorization: Bearer <supabase-access-token>`.
2. FastAPI validates the JWT and maps the `sub` claim to `current_user.user_id`.
3. The Notes service receives `current_user`, not `dev_user`.
4. The repository uses a user-scoped Supabase client with the caller JWT.
5. Supabase Postgres stores Notes rows with RLS enabled.
6. Application queries still filter by `user_id` for defense in depth.
7. Missing, deleted, and cross-user Notes still return `404 NOT_FOUND`.
8. Update/delete conflicts still return `409 CONFLICT` with full `server_data`.

## Remaining Non-Goals

- No database migration is executed in CI.
- No Supabase Python client is added or constructed in request handlers yet.
- No service role key is introduced to request handlers.
- No frontend auth flow, local persistence adapter, Realtime subscription, or sync
  engine is implemented here.
- No Note summarization, embeddings, search, or AI behavior is added.
- No secrets or environment values are written to the repository.

## Database Migration Contract

The Slice 6E draft migration is
`supabase/migrations/20260522000000_create_notes.sql`. Its table contract is:

```sql
CREATE TABLE public.notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title text NOT NULL CHECK (char_length(title) BETWEEN 1 AND 500),
  content text NOT NULL DEFAULT '' CHECK (char_length(content) <= 50000),
  content_type text NOT NULL DEFAULT 'plain'
    CHECK (content_type IN ('plain', 'markdown')),
  is_archived boolean NOT NULL DEFAULT false,
  is_deleted boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz NULL,
  version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  CHECK (
    (is_deleted = false AND deleted_at IS NULL)
    OR (is_deleted = true AND deleted_at IS NOT NULL)
  )
);
```

Expected indexes:

- `notes_user_visible_updated_idx` on `(user_id, is_deleted, updated_at DESC, id)`
  for the default list path.
- `notes_user_archive_visible_updated_idx` on
  `(user_id, is_archived, is_deleted, updated_at DESC, id)` if archived filtering
  is kept on `GET /notes`.
- `notes_user_updated_idx` on `(user_id, updated_at DESC, id)` for future sync
  pull and Realtime catch-up paths.

Timestamp handling:

- `created_at` is set once by the database.
- `updated_at` is set by application updates and may also be protected by a
  simple trigger so direct SQL updates cannot leave stale timestamps.
- Soft delete sets `is_deleted = true`, `deleted_at = now()`, `updated_at = now()`,
  and increments `version`.

Direct CRUD `POST /notes` should keep server-generated ids. Future sync push may
accept a client-generated UUID for offline-created entities after the sync
contract explicitly supports idempotent create operations.

## RLS Policy Contract

Enable RLS in the same migration that creates `public.notes`:

```sql
ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;
```

Policies should use the caller JWT through `auth.uid()`:

```sql
CREATE POLICY "Users can view own notes"
  ON public.notes FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can create own notes"
  ON public.notes FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own notes"
  ON public.notes FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

Do not rely on a user-facing physical `DELETE` path for Notes CRUD. The HTTP
`DELETE /notes/{note_id}` route is a soft delete implemented as an `UPDATE`.
Physical cleanup and account deletion should be separate admin/background paths
with explicit `user_id` scoping.

## Auth Boundary Contract

Slice 6E replaced the route-local placeholder:

```python
dev_user_id = "dev_user"
```

with a shared API dependency that returns a typed current user context:

```python
class AuthContext(BaseModel):
    user_id: str
    auth_mode: str
    access_token: str | None = None
```

Implementation expectations:

- `/v1/health` and `/v1/version` remain public.
- Notes routes depend on `get_auth_context`.
- Missing, malformed, expired, or invalid bearer tokens return `401 UNAUTHORIZED`
  using the existing API error envelope.
- Auth failures log only `request_id` and a reason category, never token contents
  or email addresses.
- `user_id` always comes from the token `sub` claim and is never accepted from
  client request bodies.
- The bearer token will be passed to the Supabase user-scoped client so RLS is
  active once live client wiring is implemented.

Required settings names, with no values committed:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`

Service-role keys must not be used in request-handling code.

## Repository Replacement Plan

Keep the existing route/service shape thin. Slice 6E replaces only the
persistence boundary:

- Keep `apps/api/app/routers/notes.py` responsible for request parsing and
  envelope/error translation.
- Keep `apps/api/app/services/notes.py` responsible for version and soft-delete
  semantics.
- `apps/api/app/repositories/notes.py` defines the protocol and factory.
- `apps/api/app/repositories/notes_memory.py` preserves deterministic local and
  unit-test behavior.
- `apps/api/app/repositories/notes_supabase.py` is a Supabase-shaped scaffold
  that is not live-wired until a user-scoped client is injected.

Repository methods should require authenticated context:

```text
list_notes(user_id, page, per_page, sort, order, is_archived, include_deleted)
create_note(user_id, payload)
get_note(user_id, note_id)
update_note(user_id, note_id, payload)
delete_note(user_id, note_id, payload)
```

All repository queries should include `user_id = current_user.user_id` even though
RLS also enforces ownership.

## Version And Delete Semantics

Update should be a single conditional write:

```sql
UPDATE public.notes
SET
  title = COALESCE(:title, title),
  content = COALESCE(:content, content),
  content_type = COALESCE(:content_type, content_type),
  is_archived = COALESCE(:is_archived, is_archived),
  updated_at = now(),
  version = version + 1
WHERE id = :note_id
  AND user_id = :user_id
  AND is_deleted = false
  AND version = :expected_version
RETURNING *;
```

Delete should also be a conditional write:

```sql
UPDATE public.notes
SET
  is_deleted = true,
  deleted_at = now(),
  updated_at = now(),
  version = version + 1
WHERE id = :note_id
  AND user_id = :user_id
  AND is_deleted = false
  AND version = :expected_version
RETURNING *;
```

If the conditional write returns no rows:

1. Fetch the current non-deleted note for the same `id` and `user_id`.
2. If none exists, return `404 note_not_found`.
3. If a note exists with a different version, return `409 version_conflict` with
   the full current Note in `server_data`.

Deleted notes remain hidden from normal `GET /notes/{note_id}` and default
`GET /notes`.

## Error Envelope Expectations

Use existing envelope codes:

| Scenario | HTTP | Code | Detail message |
|----------|------|------|----------------|
| Missing bearer token | 401 | `UNAUTHORIZED` | `unauthorized` |
| Invalid/expired bearer token | 401 | `UNAUTHORIZED` | `unauthorized` |
| Invalid request DTO | 400 | `VALIDATION_ERROR` | `validation_error` |
| Missing/deleted/cross-user note | 404 | `NOT_FOUND` | `note_not_found` |
| Version mismatch | 409 | `CONFLICT` | `version_conflict` |

Do not return `403` for cross-user Notes access. Use `404` to avoid entity
enumeration.

## Test Plan For Implementation

API unit tests with fakes:

- unauthenticated Notes requests return `401`.
- valid auth injects token `sub` as `current_user.user_id`.
- create ignores/rejects server-controlled fields and stores token-derived
  `user_id`.
- list filters out deleted notes by default.
- get/update/delete for missing, deleted, or cross-user notes return `404`.
- stale update/delete versions return `409` with `server_data`.
- soft delete increments `version` and sets `deleted_at`.
- response DTOs remain snake_case.

Repository and RLS tests:

- user A can insert/select/update own Notes.
- user A cannot select/update user B Notes.
- insert with mismatched `user_id` fails RLS.
- physical delete is not part of the Notes CRUD request path.
- update/delete conditional writes are atomic and version-gated.

CI should keep tests deterministic. If a live or local Supabase service is not
available in default CI, gate integration tests behind explicit environment
configuration and keep unit tests as the required baseline.

## Local Persistence Mapping

No local persistence code is added in the persistence/auth implementation slice.
The server contract should still remain compatible with future local-first sync:

- server `id` maps to local `server_id`.
- direct CRUD creates server ids.
- future `/sync/push` may use client-generated UUIDs for offline-created notes.
- `version`, `updated_at`, `is_deleted`, and `deleted_at` must round-trip exactly.
- conflict responses must include full `server_data` for local merge handling.

## Implementation Order

1. Add API settings for Supabase URL, anon key, and JWT secret without committing
   values.
2. Add an auth dependency and tests for public/private route behavior.
3. Add the Notes migration contract with RLS and indexes.
4. Add a user-scoped Supabase client factory.
5. Implement the Supabase Notes repository behind the existing service boundary.
6. Preserve fake/in-memory repository tests for fast unit coverage.
7. Add optional Supabase integration tests if the environment is configured.
8. Remove the `dev_user` dependency from Notes request handling.

## Security Checklist

- No service role key in request handlers.
- No token, email, title, or content values in logs.
- No real secrets in docs, fixtures, tests, or environment examples.
- All Notes queries include `user_id` filters.
- RLS enabled before any user-owned table is considered production-ready.
- Cross-user access returns `404`, not `403`.
- Soft delete remains an update, not a physical delete.

## Open Decisions

- Whether to include a user-facing physical `DELETE` RLS policy for Notes. The
  recommended Slice 6E default is no policy for request-path physical deletion.
- Whether default CI should start a local Supabase stack or keep Supabase tests
  optional until a later infrastructure slice.
- Whether the JWT validator should use `python-jose`, `PyJWT`, or Supabase JWKS
  helpers. The accepted architecture currently describes HS256 validation with
  `SUPABASE_JWT_SECRET`.
