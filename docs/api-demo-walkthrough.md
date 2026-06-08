# API Demo Walkthrough

Slice: **8H / 8O / 8S / 9C-R**
Date: 2026-06-06; updated 2026-06-08
Status: **Complete — docs plus dependency-free local demo script**

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

## 2. Scripted Local Demo

Slice 8O adds a dependency-free local script for the current fake-provider
flow:

```bash
scripts/demo-api.sh
```

The script defaults to `http://127.0.0.1:8000` and refuses non-local base URLs.
It uses only `bash`, `curl`, and `python3`, sends no auth header, creates no
`.env` file, starts no Docker/Supabase/Expo process, and makes no live provider
call. It expects the backend to be running locally with the default dev auth
mode and AI summarization enabled:

```bash
cd apps/api
SYNAPSE_AI_SUMMARIZATION_ENABLED=true uvicorn app.main:app --reload
```

In a second terminal from the repository root:

```bash
scripts/demo-api.sh
```

Optional local-only override:

```bash
SYNAPSE_DEMO_API_BASE_URL=http://localhost:8000 scripts/demo-api.sh
```

The script performs:

- health check
- synthetic note create
- note list
- note detail
- empty summary history list
- fake summarize
- summary history list
- fake summarize again
- final summary history list with newest-first append verification
- note update (correct version → HTTP 200, version increment)
- note update with stale version (conflict → HTTP 409 assertion)
- note delete (correct version → HTTP 200, soft-delete)
- deleted note GET (→ HTTP 404 isolation assertion)

If the backend is not running, it fails clearly. If AI summarization is disabled
or the backend is not in local dev auth mode, it stops with fixed guidance. The
script prints concise IDs/counts only; it does not print provider diagnostics,
prompt text, auth values, or raw note content.

## 3. Existing Coverage

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

## 4. Evidence Matrix

Slice 8I reviewed the walkthrough against the current backend, shared
contracts, API client, and dependency-free mobile summary-history foundation.
No API or client mismatch was found. The evidence is sufficient for a
portfolio/API demo, so no code or test changes were added.

| Demo claim | Evidence | Status |
|---|---|---|
| Note CRUD walkthrough matches backend behavior | `apps/api/app/routers/notes.py`, `apps/api/tests/test_notes.py`, `apps/api/tests/test_notes_integration_verification.py` | Covered |
| Versioned update/delete and conflict handling are demonstrable | `apps/api/tests/test_notes.py`, `apps/api/tests/test_notes_integration_verification.py`, `packages/api-client/src/notes.test.ts` | Covered |
| Cross-user note access is hidden as safe 404s | `apps/api/tests/test_notes.py`, `apps/api/tests/test_notes_repository.py` | Covered |
| Fake summarize endpoint returns a validated `Summary` envelope | `apps/api/app/routers/ai.py`, `apps/api/tests/test_ai_summarization.py`, `packages/api-client/src/ai.test.ts`, `packages/shared/src/ai-contracts.test.ts` | Covered |
| Empty summary history is available for an owned note | `apps/api/tests/test_ai_summarization.py`, `packages/shared/src/ai-contracts.test.ts` | Covered |
| Repeated fake summaries append and list newest first | `apps/api/app/services/ai_summarization.py`, `apps/api/tests/test_ai_summarization.py` | Covered |
| Summary history cross-user access returns safe 404 | `apps/api/tests/test_ai_summarization.py`, `packages/api-client/src/ai.test.ts` | Covered |
| Shared summary contracts are strict snake_case | `packages/shared/src/ai/index.ts`, `packages/shared/src/schema-registry.ts`, `packages/shared/src/ai-contracts.test.ts` | Covered |
| API client can consume summarize and history endpoints | `packages/api-client/src/index.ts`, `packages/api-client/src/ai.test.ts` | Covered |
| Mobile note list/detail foundation consumes validated Note CRUD data without rendered UI | `apps/mobile/src/features/notes/noteListApi.ts`, `apps/mobile/src/features/notes/noteDetailApi.ts`, `apps/mobile/src/features/notes/noteListViewState.ts`, `apps/mobile/src/features/notes/noteDetailViewState.ts`, `apps/mobile/src/features/notes/noteListPlaceholder.ts`, `apps/mobile/src/features/notes/noteDetailPlaceholder.ts` | Covered by mobile typecheck |
| Mobile foundation consumes shared summary data without rendering UI | `apps/mobile/src/features/notes/summaryHistoryApi.ts`, `apps/mobile/src/features/notes/summaryHistoryViewState.ts`, `apps/mobile/src/features/notes/noteSummaryHistoryPlaceholder.ts` | Covered by typecheck/docs |
| AI summary/history surfaces avoid prompt, raw diagnostic, credential, and note-content leakage | `apps/api/tests/test_ai_summarization.py`, `docs/security/privacy-and-data-handling.md` | Covered |
| Summary history is memory-only demo state | `apps/api/app/services/ai_summarization.py`, this walkthrough, `docs/security/privacy-and-data-handling.md` | Covered |
| Rendered mobile UI and live provider work remain deferred | `docs/rendered-mobile-demo-unblock-decision-packet.md`, `docs/next-action.md` | Covered |

### Gap Review Answers

1. The walkthrough matches actual backend and API-client behavior.
2. All API demo steps are backed by backend, API-client, or shared-contract
   tests.
3. No mismatch was found between backend response shape, shared contracts, API
   client parsing, and mobile view-state input types.
4. Note CRUD, summarize, list history, newest-first order, and cross-user/404
   behavior are covered enough for a dependency-free demo.
5. No new security/logging gap was found; AI surfaces have focused leak tests.
6. No API client gap blocks demo consumption.
7. Additional code would be over-engineering for Slice 8I; the useful hardening
   is this consolidated evidence matrix.

### Slice 8K Mobile Foundation Addendum

Slice 8K adds dependency-free mobile TypeScript view-state foundations for note
list and note detail flows. The adapters wrap the injected `@synapse/api-client`
`notes.list` and `notes.get` methods, validate returned data with shared note
schemas, and keep raw network access out of mobile feature modules.

The list mapper preserves the API/client item ordering exactly as returned. It
maps loading, empty, success, and coarse error states, including a bounded
content preview for future list rows. The detail mapper carries authorized note
content by design for successful owned-note detail views, while not-found,
invalid-response, and unavailable states use UI-safe messages and do not expose
backend diagnostics, auth headers, credentials, prompt text, provider details,
or token-like values.

The placeholder metadata names future note list/detail screen regions only. It
does not add JSX, TSX, Expo, React Native, rendered UI, package changes,
lockfile changes, production persistence, SQL, migrations, Supabase state,
Docker work, OpenAI SDK usage, live provider wiring, credentials, or `.env`
files.

## 5. Note CRUD Sequence

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

## 6. Fake Summary Sequence

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

## 7. Unauthorized and Cross-User Behavior

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

## 8. Safety Checks

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

## 9. Scripted Update / Conflict / Delete Steps (Slice 8S)

The following steps are exercised by `scripts/demo-api.sh` after the summary
history verification and do not require any additional setup.

### Step 10 — Update Note (Correct Version)

```http
PATCH /v1/notes/{note_id}
```

```json
{ "title": "Updated demo planning note", "version": 1 }
```

The script uses the version captured at create time.

Expected result:

- HTTP `200`
- `data.title` reflects the updated value
- `data.version` increments by one
- `data.updated_at` advances

The script captures the new version for use in subsequent steps.

### Step 11 — Update Note (Stale Version → 409 Conflict)

```http
PATCH /v1/notes/{note_id}
```

```json
{ "title": "Stale update attempt", "version": 1 }
```

The script reuses the original (now stale) version intentionally.

Expected result:

- HTTP `409`
- error envelope with `code: "CONFLICT"`
- `details[0].expected` contains the version the client sent
- `details[0].actual` contains the current server version
- `details[0].server_data` contains the current server note

The script asserts that the status is exactly `409`; any other status fails the demo.

### Step 12 — Delete Note (Correct Version)

```http
DELETE /v1/notes/{note_id}
```

```json
{ "version": 2 }
```

The script uses the updated version captured from Step 10.

Expected result:

- HTTP `200`
- `data.is_deleted` is `true`
- `data.deleted_at` is set
- `data.version` increments by one

### Step 13 — Confirm Deleted Note Is Hidden (404)

```http
GET /v1/notes/{note_id}
```

Expected result:

- HTTP `404`
- The soft-deleted note is invisible to subsequent GET requests
- Cross-user and soft-delete isolation uses the same 404 response; no `403` leaks ownership

The script asserts exactly `404`; any other status fails the demo.

---

## 10. API Client Walkthrough Surface

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

## 11. Mobile View-State Surface

The dependency-free mobile export surface now includes:

- **Note List**: `createNoteListApi(client)`, `loadNoteListViewState(api, query)`, `mapNoteListDataToViewState(data)`, `mapNoteListErrorToViewState(error)`, `createNoteListPlaceholder(state)`
- **Note Detail**: `createNoteDetailApi(client)`, `loadNoteDetailViewState(api, noteId)`, `mapNoteDetailDataToViewState(note)`, `mapNoteDetailErrorToViewState(noteId, error)`, `createNoteDetailPlaceholder(noteId, state)`
- **Note Mutation**: `createNoteMutationApi(client)`, `createNoteAndMapMutationViewState(api, payload)`, `updateNoteAndMapMutationViewState(api, noteId, payload)`, `deleteNoteAndMapMutationViewState(api, noteId, payload)`
- **Summary History**: `createSummaryHistoryApi(client)`, `loadSummaryHistoryViewState(api, noteId)`, `mapSummaryHistoryDataToViewState(noteId, data)`, `mapSummaryHistoryErrorToViewState(noteId, error)`, `createNoteSummaryHistoryPlaceholder(noteId, state)`

These modules are plain `.ts` and are intended as future screen-ready state plumbing, not rendered mobile UI.

## 12. Verification

Focused verification for this walkthrough:

```bash
cd apps/api
python3 -m pytest tests/test_notes.py tests/test_notes_integration_verification.py tests/test_ai_summarization.py -q
cd ../..
pnpm --filter @synapse/api-client test
pnpm --filter @synapse/shared contracts:check
```

Script syntax check (Slice 8S extended script):

```bash
bash -n scripts/demo-api.sh
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
