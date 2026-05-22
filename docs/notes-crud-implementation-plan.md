# Notes CRUD Implementation Plan

## Objective

Track the first Notes CRUD implementation slices. Notes are the first feature to
exercise shared contracts, FastAPI routing, typed API client methods, auth
boundaries, soft deletion, pagination, and future offline-first sync.

Status update: Slice 6B now includes a minimal FastAPI Notes route skeleton with
strict Pydantic DTOs, process-local in-memory storage, soft delete behavior, and
a temporary `dev_user` auth placeholder. Supabase persistence, JWT validation,
RLS, frontend UI, API client methods, and sync remain deferred.

## Non-Goals

- No durable Notes persistence implementation in Slice 6B beyond the in-memory
  route skeleton.
- No database migrations, Supabase clients, auth providers, RLS policies, or
  storage integration.
- No frontend screens, Expo initialization, or local persistence engine.
- No AI summarization, embeddings, search, or sync engine implementation.
- No real secrets or environment values.

## Current Note Model

`@synapse/shared` already defines `NoteSchema` with snake_case wire fields:

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID string | Server entity id in API responses |
| `user_id` | UUID string | Set from authenticated user context, never trusted from client body |
| `title` | string | 1-500 characters |
| `content` | string | up to 50,000 characters |
| `content_type` | `plain` or `markdown` | Phase 1 rich text is out of scope |
| `is_archived` | boolean | Filters list visibility later |
| `is_deleted` | boolean | Soft delete marker |
| `created_at` | ISO timestamp | Server-set |
| `updated_at` | ISO timestamp | Server-set and used for ordering |
| `deleted_at` | ISO timestamp or `null` | Server-set on soft delete |
| `version` | non-negative integer | Optimistic concurrency |
| `sync_metadata` | optional local metadata | Client/local only; not required from backend responses |

Slice 6A added dedicated shared request/response schemas for create, update,
get, list, and delete. Slice 6B added backend skeleton routes; API client note
methods remain deferred.

## API Endpoint Plan

All paths are mounted under the configured `/v1` API prefix.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/notes` | List current user's non-deleted notes with pagination |
| `POST` | `/notes` | Create a note for the current user |
| `GET` | `/notes/{note_id}` | Fetch one note owned by the current user |
| `PATCH` | `/notes/{note_id}` | Partially update a note with `version` required |
| `DELETE` | `/notes/{note_id}` | Soft delete a note with version conflict protection |

### List Notes

Query parameters should reuse `PaginationRequestSchema`:

- `page`
- `per_page`
- `sort`
- `order`

Default behavior:

- exclude `is_deleted = true`
- include archived notes unless an explicit future `is_archived` filter is added
- sort by `updated_at desc`
- return `data.items` and `data.pagination`

### Create Note

Planned request body:

```json
{
  "title": "Planning note",
  "content": "",
  "content_type": "plain"
}
```

Server-owned fields: `id`, `user_id`, `created_at`, `updated_at`, `deleted_at`,
`version`, `is_deleted`. Default `is_archived` should be `false`.

Open contract decision for Slice 6A: decide whether direct `POST /notes` accepts
an optional client-generated `id`, or whether client-generated ids are reserved
for future `/sync/push` create operations.

### Get Note

`GET /notes/{note_id}` returns one `Note`. Missing notes, deleted notes, and
notes owned by another user should all return `404 NOT_FOUND` to avoid entity
enumeration.

### Update Note

Planned request body uses PATCH semantics and requires `version`:

```json
{
  "title": "New title",
  "content": "Updated content",
  "content_type": "markdown",
  "is_archived": false,
  "version": 3
}
```

Allowed mutable fields: `title`, `content`, `content_type`, `is_archived`.
Omitted fields are unchanged. At least one mutable field should be present.

If the current stored version does not match the request `version`, return
`409 CONFLICT` with `server_data` containing the full current note.

### Delete Note

Soft delete should set:

- `is_deleted: true`
- `deleted_at: <server timestamp>`
- `updated_at: <server timestamp>`
- `version: version + 1`

Deletion also requires version conflict protection. Slice 6A chose a request
body shape with `version`.

## Backend Structure Plan

Use the existing FastAPI baseline:

- `apps/api/app/routers/notes.py`: route declarations only, thin handlers
- `apps/api/app/schemas/notes.py`: Pydantic request/response models or generated
  schema-backed equivalents
- `apps/api/app/services/notes.py`: business rules and persistence calls
- `apps/api/app/repositories/notes.py`: in-memory repository only for Slice 6B
- `apps/api/app/core/deps.py`: future `get_current_user` and database dependency
- `apps/api/tests/test_notes.py`: route tests before real database wiring

Routes should return the existing success envelope and raise typed application
errors that the global handler converts to the standard error envelope.

## Shared Contract Impact

Slice 6A added these shared schemas before backend code:

- `CreateNoteRequestSchema`
- `UpdateNoteRequestSchema`
- `DeleteNoteRequestSchema`
- `CreateNoteResponseSchema`
- `UpdateNoteResponseSchema`
- `DeleteNoteResponseSchema`
- `GetNoteResponseSchema`
- `ListNotesRequestSchema`
- `ListNotesResponseSchema`

Rules:

- Keep all wire fields snake_case.
- Keep schemas platform-agnostic.
- Reuse `NoteSchema`, `PaginationRequestSchema`, `PaginationMetaSchema`, and
  error envelope schemas.
- Export JSON Schema artifacts so FastAPI can consume the same contract.
- Add tests for create/update/delete accept/reject cases and camelCase rejection.

## API Client Impact

Future `@synapse/api-client` work should add typed methods after shared schemas
exist:

- `notes.list(query)`
- `notes.create(payload)`
- `notes.get(note_id)`
- `notes.update(note_id, payload)`
- `notes.delete(note_id, payload)`

The client should keep using the generic request wrapper, auth token callback,
and shared success/error envelopes. Tests should cover:

- query serialization for pagination
- success envelope parsing for list and single-note responses
- `ApiClientError` mapping for 400, 401, 404, and 409
- network failure behavior remains unchanged

## Frontend Impact

No UI is implemented yet. Future app work should treat Notes CRUD as local-first:

- screens read from local persistence, not directly from network state
- create/update/delete write locally first
- sync operations are enqueued after local writes
- API client methods are used by the sync layer and online refresh paths
- UI components receive note data via props and do not fetch directly

## Offline-First Implications

Notes must preserve these assumptions:

- optimistic writes update local state immediately
- `version` is required for update/delete conflict detection
- same-entity operations are serialized FIFO
- delete wins over later stale edits through soft deletion rules
- conflicts return full `server_data`
- sync push remains the long-term path for offline-created operations

Before implementation, resolve the create-id ownership question so direct CRUD
and future sync push do not diverge.

## Security And Privacy

- Every Notes endpoint requires authenticated user context.
- `user_id` is derived server-side from the token and ignored/rejected in client
  request bodies.
- Missing, deleted, or cross-user notes return `404 NOT_FOUND`.
- Server logs must not include note `title` or `content`.
- RLS remains required when Supabase persistence is added.
- No service-role key or provider key is exposed to the client.
- Note content is sensitive local data and follows the local storage risk model
  already documented for Phase 1.

## Testing Strategy

Shared package:

- create/update/delete request schema accept/reject tests
- list response envelope with pagination
- conflict error envelope with full `server_data`
- camelCase rejection

API:

- unauthenticated requests return 401 once auth dependency exists
- list returns only current user's non-deleted notes
- create rejects user-supplied `user_id`
- get/update/delete cross-user notes return 404
- patch requires `version`
- stale version returns 409 with `server_data`
- delete is soft and increments version

API client:

- methods call expected paths and methods
- auth header callback is used
- paginated list response parses correctly
- conflict response throws `ApiClientError`

Future app/local persistence:

- create/read/update/delete locally without network
- queue survives restart
- conflict record is created on 409
- no real network/provider calls in tests

## Implementation Sub-Slices

1. **Slice 6A — Notes contract refinement**
   Add create/update/delete/list schemas, tests, and JSON Schema exports.
2. **Slice 6B — Notes backend route skeleton**
   Add FastAPI route signatures, strict DTOs, in-memory repository/service
   boundaries, route tests, and response envelopes. No database yet.
3. **Slice 6C — Notes API client methods**
   Add typed client methods for list, create, get, update, and delete using the
   shared Notes contracts.
4. **Slice 6D — Notes persistence/auth integration plan**
   Plan database migrations, RLS, auth dependency, and local persistence mapping
   before implementation.

## Measurable Definition Of Done

- Notes endpoints match this plan and the API contract.
- Shared request/response schemas are exported and tested.
- API route tests cover success, validation, auth, 404, and 409 paths.
- API client tests cover list/create/get/update/delete success and error cases.
- Soft delete and version conflict behavior are explicit and tested.
- No note content appears in logs, fixtures with secrets, or error messages.
- `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, API lint, and API
  tests pass locally and in CI.
