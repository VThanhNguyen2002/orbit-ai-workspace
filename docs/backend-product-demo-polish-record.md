# Backend Product Demo Polish Record

Date: 2026-06-04

## Decision Status

Slice 8E is **COMPLETE** as a dependency-free backend/product demo polish slice.
Slice 8F is **COMPLETE** as a docs-only API-level demo runbook slice.
Slice 8G is **COMPLETE** as a docs-only rendered mobile demo unblock decision packet. Decision: **DEFER** rendered mobile UI. See [`docs/rendered-mobile-demo-unblock-decision-packet.md`](rendered-mobile-demo-unblock-decision-packet.md).

## Scope Completed

- Summary history now lists generated fake-provider summaries newest first for note detail consumption.
- The dependency-free mobile API boundary can request summary generation through `summarizeForNote(noteId)` and still validates responses with shared contracts.
- The dependency-free mobile view-state layer now models `summarizing`, append, dedupe, newest-first sorting, and safe error states without rendering React Native or Expo UI.
- Backend tests cover the demo endpoint sequence: get note detail, list empty summary history, generate two fake summaries, and list generated summaries newest first.
- Backend tests also assert that AI summary/history surfaces and captured logs do not expose prompt text, raw diagnostics, note content, placeholder key names, bearer-like values, or `sk-` token-like strings.

## Explicit Non-Changes

- No package manifests, lockfiles, or dependency installs.
- No Expo, React Native runtime, rendered mobile UI, router, or native files.
- No OpenAI SDK, live provider, credential, `.env`, WIF runtime, SSE streaming, SQL, migration, Supabase state, Docker, or generated state.
- No durable summary persistence; summary history remains memory-only for fake-provider demos and resets with the backend process.

## Verification

- `pytest tests/test_ai_summarization.py -q`
- `pytest -q`
- `ruff check .`
- `pnpm --filter mobile lint`
- `pnpm --filter mobile exec tsc --noEmit -p tsconfig.json`
- `git diff --check`
- `git ls-files -- ".env" ".env.*" "*.sql" "supabase/migrations/*"`
- `gitleaks detect --source=. --redact -v`

## Slice 8F API-Level Demo Runbook

Date: 2026-06-06

### Demo Purpose

Show the current note-detail AI summary flow at API/code level using only the
existing fake provider, memory repositories, and shared response contracts. This
is suitable for local development and CI-style verification while rendered
mobile UI, production persistence, live provider wiring, Supabase, Docker, and
new dependencies remain out of scope.

### Prerequisites

- Run with `SYNAPSE_AI_SUMMARIZATION_ENABLED=true`.
- Keep the default fake provider selected.
- Use the default memory-backed demo/test state.
- Do not create `.env` files for this flow.
- Do not provide provider credentials or call a live provider.
- Do not run SQL, migrations, Supabase, or Docker for this flow.
- Do not initialize Expo or React Native UI runtime for this flow.

### Demo Fixture

Create a demo note through the existing notes API in local dev/test context:

```http
POST /v1/notes
```

```json
{
  "title": "Demo planning note",
  "content": "Demo-only planning notes with decisions and follow-up items.",
  "content_type": "plain"
}
```

Expected result: a standard success envelope with a note in `data`. Keep
`data.id` as `note_id` for the remaining calls. The note is memory-backed in the
current demo/test setup.

### API Demo Sequence

1. Load note detail.

```http
GET /v1/notes/{note_id}
```

Expected result: `200` success envelope with the created note in `data`.
Authorized note detail responses include the note content by design.

2. List initial summary history.

```http
GET /v1/ai/notes/{note_id}/summaries
```

Expected result:

```json
{
  "items": []
}
```

3. Generate the first fake summary.

```http
POST /v1/ai/notes/{note_id}/summarize
```

Expected result: `200` success envelope with a `Summary` in `data`:

- `source_id` equals `note_id`.
- `source_type` is `note`.
- `provider` is `fake`.
- `model` is `fake-model-v1`.
- `content` is the deterministic fake summary text.
- `action_items` is a non-empty list of safe generated action items.
- `id` and `created_at` are generated for this summary result.

4. Generate a second fake summary by repeating the summarize call.

Expected result: the second summary has the same deterministic generated
content/action-item shape, but a different generated `id` and `created_at`.

5. List summary history again.

```http
GET /v1/ai/notes/{note_id}/summaries
```

Expected result: `data.items` contains the second summary first and the first
summary second. This newest-first ordering is intentional for note-detail demo
consumption.

### Demo Safety Checks

For the summarize and summary-history responses, plus captured backend logs,
verify that the API surfaces do not expose:

- raw note content or title
- prompt text
- raw provider diagnostics or raw provider payload keys
- provider credential key names
- bearer-like values
- token-like substrings

The existing backend test
`test_note_detail_demo_flow_lists_fake_summaries_without_sensitive_ai_leaks`
already verifies the API demo sequence, newest-first history, and leak checks.

### Memory-Only Limitation

Summary history is intentionally memory-only for the fake-provider demo. It is
cleared when the backend process or test fixture resets, is not persisted to a
database, and is not production storage. This limitation must be named during
any demo that shows summary history.

### Verification Commands

Focused API/code-level verification:

```bash
cd apps/api
python3 -m pytest tests/test_ai_summarization.py -q
```

Broader safe verification for this slice:

```bash
cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..
pnpm --filter @synapse/api-client test
pnpm --filter mobile lint
pnpm --filter mobile exec tsc --noEmit -p tsconfig.json
```

Security posture checks:

```bash
git ls-files -- ".env" ".env.*" "*.sql" "supabase/migrations/*"
gitleaks detect --source=. --redact
```

Expected security posture for Slice 8F:

- no package manifests or lockfiles changed
- no dependency installed
- no OpenAI SDK dependency approved or added
- no provider credentials or `.env` files added
- no live provider runtime or network behavior introduced
- no Supabase, Docker, SQL, migrations, or generated state added
- no rendered mobile UI, Expo runtime, router, or native files added
- `.gitleaksignore` remains exact-fingerprint only
