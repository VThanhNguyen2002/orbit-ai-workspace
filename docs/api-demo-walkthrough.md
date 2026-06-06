# API Demo Walkthrough

Slice: **8H**
Date: 2026-06-06
Status: **DOCS-ONLY - Complete**

This walkthrough combines the existing Note CRUD API and fake-provider AI
summary flow into one reviewer-friendly API demo. It uses only the current
backend routes, memory-backed demo/test state, shared contracts, and
dependency-free API client surface.

No package install, package manifest edit, lockfile edit, Expo/React Native
runtime, rendered mobile UI, OpenAI SDK, provider credential, `.env` file, live
provider call, SQL, migration, Supabase state, Docker work, WIF runtime, or
production persistence is required.

## 1. Demo Boundary

Use this walkthrough when the backend is running in local/test mode with:

- `SYNAPSE_AI_SUMMARIZATION_ENABLED=true`
- default fake AI provider
- default memory-backed Notes repository
- no provider credentials
- no `.env` file for this demo
- no SQL, migrations, Supabase, Docker, or live provider setup
- no rendered mobile runtime

Summary history is memory-only demo state. It is cleared when the backend
process or test fixture resets and must not be presented as production
persistence.

## 2. Existing Coverage

The walkthrough is docs-only because the critical demo paths are already
covered:

| Path | Existing coverage |
|---|---|
| Note create/list/get/update/delete | `apps/api/tests/test_notes.py`, `apps/api/tests/test_notes_integration_verification.py` |
| Cross-user note isolation | `apps/api/tests/test_notes.py`, `apps/api/tests/test_notes_repository.py` |
| Fake summary generation | `apps/api/tests/test_ai_summarization.py` |
| Empty and populated summary history | `apps/api/tests/test_ai_summarization.py` |
| Newest-first repeated summaries | `apps/api/tests/test_ai_summarization.py` |
| AI leak checks | `apps/api/tests/test_ai_summarization.py` |
| API client Note CRUD methods | `packages/api-client/src/notes.test.ts` |
| API client summarize/history methods | `packages/api-client/src/ai.test.ts` |
| Shared Note contracts | `packages/shared/src/notes-contracts.test.ts` |

## 3. Note CRUD Sequence

### Create a Note

```http
POST /v1/notes
```

```json
{
  "title": "Demo planning note",
  "content": "Review launch checklist items and assign owners.",
  "content_type": "plain"
}
```

Expected result:

- HTTP `201`
- success envelope with `data.id`, `data.version`, and timestamps
- `data.user_id` belongs to the authenticated demo user
- `data.is_archived` is `false`
- `data.is_deleted` is `false`
- response fields remain snake_case

Save `data.id` as `{note_id}` and `data.version` as `{version}`.

### List Notes

```http
GET /v1/notes?page=1&per_page=20&sort=updated_at&order=desc
```

Expected result:

- HTTP `200`
- success envelope with `data.items` and `data.pagination`
- created note appears for its owner
- cross-user notes do not appear

### Get Note Detail

```http
GET /v1/notes/{note_id}
```

Expected result:

- HTTP `200`
- success envelope with the created note in `data`
- authorized note detail includes note content by design

### Update Note

```http
PATCH /v1/notes/{note_id}
```

```json
{
  "title": "Updated demo planning note",
  "is_archived": true,
  "version": 1
}
```

Use the numeric version returned by create/get/list; `1` is shown only as the
initial create-response example.

Expected result:

- HTTP `200`
- updated fields are reflected in `data`
- `data.version` increments by one
- stale versions return HTTP `409` with a standard conflict envelope and
  server note data

Save the updated `data.version` as `{updated_version}`.

### Delete Note

```http
DELETE /v1/notes/{note_id}
```

```json
{
  "version": 2
}
```

Use the numeric updated version returned by the previous response; `2` is shown
only as the example following a successful first update.

Expected result:

- HTTP `200`
- `data.is_deleted` is `true`
- `data.deleted_at` is set
- `data.version` increments by one
- normal list/get calls hide the deleted note
- `GET /v1/notes/{note_id}` returns HTTP `404` after delete

For the summary demo, use a non-deleted note. Create a second note if this
delete step was already performed.

## 4. Fake Summary Sequence

### List Empty History

```http
GET /v1/ai/notes/{note_id}/summaries
```

Expected result:

```json
{
  "items": []
}
```

### Generate a Fake Summary

```http
POST /v1/ai/notes/{note_id}/summarize
```

Expected result:

- HTTP `200`
- success envelope with a `Summary` in `data`
- `data.source_id` equals `{note_id}`
- `data.source_type` is `note`
- `data.provider` is `fake`
- `data.model` is `fake-model-v1`
- `data.content` is deterministic fake summary text
- `data.action_items` is a non-empty list
- `data.id` and `data.created_at` are generated per summary

### Repeat Summarization

Call the summarize endpoint a second time for the same note.

Expected result:

- content and action-item shape remain deterministic
- the second summary has a distinct `id`
- the second summary has its own `created_at`
- backend history appends the new fake summary rather than replacing the first

### List Newest-First History

```http
GET /v1/ai/notes/{note_id}/summaries
```

Expected result:

- HTTP `200`
- `data.items[0]` is the second summary
- `data.items[1]` is the first summary
- all items have `provider: "fake"` and `model: "fake-model-v1"`

Backend history is append-only for this fake demo. The dependency-free mobile
view-state helper dedupes by summary `id` when merging a generated summary into
an existing local list, then sorts newest first. The API itself should still be
verified as newest-first append behavior.

## 5. Unauthorized and Cross-User Behavior

The demo should show safe ownership behavior without exposing whether another
user's note exists:

- a different user listing notes sees no other user's notes
- `GET /v1/notes/{note_id}` for another user's note returns HTTP `404`
- `PATCH /v1/notes/{note_id}` for another user's note returns HTTP `404`
- `DELETE /v1/notes/{note_id}` for another user's note returns HTTP `404`
- `POST /v1/ai/notes/{note_id}/summarize` for another user's note returns HTTP `404`
- `GET /v1/ai/notes/{note_id}/summaries` for another user's note returns HTTP `404`

Do not use real credential examples in the walkthrough. Use the repository's
test fixtures or local dev auth mode when demonstrating these paths.

## 6. Safety Checks

Summary and summary-history responses, error responses, and captured backend
logs must not expose:

- raw note title or content in AI summary/history surfaces
- prompt text
- raw provider diagnostics
- raw provider payload keys
- provider credential values
- auth header values
- token-like substrings

Authorized note detail responses may include note content because that is the
purpose of `GET /v1/notes/{note_id}`. The non-leak requirement applies to AI
summary/history surfaces and diagnostics.

## 7. API Client Walkthrough Surface

The same flow is available through `@synapse/api-client`:

- `client.notes.create(payload)`
- `client.notes.list(query)`
- `client.notes.get(note_id)`
- `client.notes.update(note_id, payload)`
- `client.notes.delete(note_id, payload)`
- `client.ai.summarizeNote(note_id)`
- `client.ai.listNoteSummaries(note_id)`

The client validates success/error envelopes and shared response contracts. It
preserves snake_case field names and URL-encodes note ids in path segments.

## 8. Verification

Focused verification for this walkthrough:

```bash
cd apps/api
python3 -m pytest tests/test_notes.py tests/test_notes_integration_verification.py tests/test_ai_summarization.py -q
cd ../..
pnpm --filter @synapse/api-client test
pnpm --filter @synapse/shared contracts:check
```

Broader safe verification:

```bash
pnpm install --frozen-lockfile

cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/api-client test
pnpm --filter @synapse/shared contracts:check
pnpm --filter mobile lint
pnpm --filter mobile exec tsc --noEmit -p tsconfig.json

pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Security posture check:

```bash
gitleaks detect --source=. --redact
```

Expected posture:

- no `.env` files
- no OpenAI SDK dependency
- no provider credentials
- no SQL or migrations
- no Supabase generated state
- no live provider runtime changes
- no rendered mobile UI or package changes
- no real credential examples
- `.gitleaksignore` remains exact-fingerprint only
