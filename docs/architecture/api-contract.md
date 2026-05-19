# API Contract

## Design Principles

1. **Resource-oriented** — endpoints map to entities, not UI actions
2. **Consistent error format** — every error returns the same JSON shape
3. **Streaming for AI** — SSE for long-running AI operations
4. **Shared validation** — Zod schemas (frontend) ↔ JSON Schema (backend)
5. **Auth via Supabase JWT** — every request carries `Authorization: Bearer <jwt>`

## Base URL

```
Production:  https://api.synapse.app/v1
Development: http://localhost:8000/v1
```

All endpoints are prefixed with `/v1`. Version bumps only on breaking changes.

## Authentication

Every request (except `/v1/health`) requires a valid Supabase JWT in the `Authorization` header.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The backend validates the JWT against Supabase's JWT secret. The `sub` claim becomes `user_id` for all downstream operations. No session cookies, no API keys for clients.

## Endpoint Map

### Notes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/notes` | List notes (paginated) |
| POST | `/v1/notes` | Create note |
| GET | `/v1/notes/:id` | Get single note |
| PATCH | `/v1/notes/:id` | Update note (partial) |
| DELETE | `/v1/notes/:id` | Soft delete note |
| POST | `/v1/notes/:id/summarize` | Trigger AI summarization (SSE) |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/tasks` | List tasks (paginated, filterable) |
| POST | `/v1/tasks` | Create task |
| GET | `/v1/tasks/:id` | Get single task |
| PATCH | `/v1/tasks/:id` | Update task (partial) |
| DELETE | `/v1/tasks/:id` | Soft delete task |

### Voice Memos

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/voice-memos` | List voice memos |
| POST | `/v1/voice-memos` | Create metadata record |
| GET | `/v1/voice-memos/:id` | Get single memo |
| DELETE | `/v1/voice-memos/:id` | Soft delete memo |
| POST | `/v1/voice-memos/:id/transcribe` | Trigger Whisper transcription |
| GET | `/v1/voice-memos/:id/transcript` | Get transcript |

### Search

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/search` | Semantic search across all user content |
| POST | `/v1/search/ask` | Natural language Q&A over user content (Phase 2, RAG) |

### Sync

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/sync/push` | Push batch of offline operations |
| GET | `/v1/sync/pull` | Pull changes since timestamp |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/health` | Health check (no auth) |

## Request/Response Formats

### Successful Response

```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### Paginated Response

```json
{
  "data": [ ... ],
  "meta": {
    "request_id": "req_abc123",
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 142,
      "has_next": true
    }
  }
}
```

Pagination uses `page` + `per_page` query parameters. Default `per_page: 20`, max `100`.

### Error Response

Every error follows this shape — no exceptions:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      {
        "field": "title",
        "message": "Must be between 1 and 500 characters"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### Error Codes

| HTTP | Code | Meaning |
|------|------|---------|
| 400 | `VALIDATION_ERROR` | Request body/params failed validation |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | Valid JWT but insufficient permissions |
| 404 | `NOT_FOUND` | Entity doesn't exist or belongs to another user |
| 409 | `CONFLICT` | Version mismatch (optimistic concurrency) |
| 422 | `UNPROCESSABLE` | Valid format but semantically wrong |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server fault |

### Conflict Response (409)

Returned when an update targets a stale version:

```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Entity has been modified",
    "details": [
      {
        "field": "version",
        "expected": 3,
        "actual": 5,
        "server_data": {
          "id": "note-uuid",
          "title": "Updated title",
          "content": "Full current content from server",
          "version": 5,
          "updated_at": "2025-05-18T10:30:00Z"
        }
      }
    ]
  }
}
```

`server_data` contains the **full current entity** — not just changed fields. The client uses this to:
1. Auto-resolve if changes are to different fields (merge non-overlapping)
2. Surface to user if same field was edited on both sides

See [offline-sync.md](offline-sync.md) for conflict resolution strategy.

## Streaming Responses (SSE)

AI operations (summarization, transcription) return streaming responses via Server-Sent Events.

**Request:** Standard POST to the action endpoint.

**Response:** `Content-Type: text/event-stream`

```
event: token
data: {"text": "The meeting "}

event: token
data: {"text": "covered three "}

event: token
data: {"text": "main topics..."}

event: action_items
data: {"items": [{"text": "Schedule follow-up", "priority": "high"}]}

event: done
data: {"summary_id": "uuid-here"}

event: error
data: {"code": "PROVIDER_ERROR", "message": "LLM request failed"}
```

Event types:
- `token` — incremental text chunk
- `action_items` — extracted tasks (sent once, after full text)
- `done` — operation complete, includes ID of persisted result
- `error` — operation failed

The client renders tokens as they arrive. The final `done` event signals that the summary has been persisted to the database and will appear via Realtime subscription.

## Validation Strategy

### Shared Schema Approach

```
Zod schema (@synapse/shared)
    ↓ build step
JSON Schema file
    ↓ loaded by FastAPI
Pydantic model validation
```

Example — Note creation schema:

```typescript
// @synapse/shared/src/validation/note.ts
import { z } from 'zod';

export const CreateNoteSchema = z.object({
  title: z.string().min(1).max(500),
  content: z.string().max(50_000).default(''),
  content_type: z.enum(['plain', 'markdown']).default('plain'),
});

export const UpdateNoteSchema = z.object({
  title: z.string().min(1).max(500).optional(),
  content: z.string().max(50_000).optional(),
  content_type: z.enum(['plain', 'markdown']).optional(),
  is_archived: z.boolean().optional(),
  version: z.number().int().positive(),  // Required for optimistic concurrency
});
```

The frontend validates before sending. The backend validates again using the equivalent JSON Schema. Two validation passes, identical rules, zero divergence.

## Partial Updates (PATCH)

Updates use PATCH semantics — only included fields are modified. The `version` field is always required to enable conflict detection.

```json
PATCH /v1/notes/abc-123
{
  "title": "New title",
  "version": 3
}
```

Omitted fields are not touched. Explicitly setting a field to `null` clears it (where the schema allows nullable).

## Sync Endpoints

### POST /v1/sync/push

Accepts a batch of offline operations:

```json
{
  "operations": [
    {
      "id": "op-uuid",
      "entity_type": "note",
      "entity_id": "note-uuid",
      "operation": "update",
      "payload": { "title": "New title", "version": 3 },
      "created_at": 1700000000000
    }
  ]
}
```

Response:

```json
{
  "data": {
    "results": [
      { "operation_id": "op-uuid", "status": "applied" },
      { "operation_id": "op-uuid-2", "status": "conflict", "server_data": { ... } }
    ]
  }
}
```

### GET /v1/sync/pull?since=1700000000000

Returns all entities modified after the given timestamp for the current user. Used to hydrate local state after being offline.

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `since` | integer (epoch ms) | Yes | Timestamp of last successful sync |
| `entity_types` | string (comma-separated) | No | Filter: `note,task,voice_memo`. Default: all types |

**Response:**

```json
{
  "data": {
    "notes": [
      {
        "id": "note-uuid",
        "title": "Updated note",
        "content": "...",
        "content_type": "markdown",
        "is_archived": false,
        "is_deleted": false,
        "version": 5,
        "created_at": "2025-05-18T09:00:00Z",
        "updated_at": "2025-05-18T10:30:00Z"
      }
    ],
    "tasks": [
      {
        "id": "task-uuid",
        "title": "Follow up with team",
        "status": "todo",
        "priority": "high",
        "is_deleted": false,
        "version": 2,
        "note_id": "note-uuid",
        "created_at": "2025-05-18T09:15:00Z",
        "updated_at": "2025-05-18T10:45:00Z"
      }
    ],
    "voice_memos": [],
    "summaries": [],
    "transcripts": []
  },
  "meta": {
    "request_id": "req_abc123",
    "sync_timestamp": 1700003400000,
    "has_more": false
  }
}
```

**Key behaviors:**
- Includes soft-deleted entities (`is_deleted: true`) so the client can remove them locally
- `sync_timestamp` in the response becomes the client's next `since` value
- `has_more: true` indicates more changes exist — client should call again with returned `sync_timestamp`
- Maximum 500 entities per response; if exceeded, `has_more` is set to `true`

### POST /v1/sync/push — Conflict Detail

When a push operation conflicts, the `server_data` in the result contains the full current entity:

```json
{
  "data": {
    "results": [
      {
        "operation_id": "op-uuid-1",
        "status": "applied",
        "entity": { "id": "note-uuid", "version": 4 }
      },
      {
        "operation_id": "op-uuid-2",
        "status": "conflict",
        "server_data": {
          "id": "note-uuid-2",
          "title": "Server version of title",
          "content": "Server content",
          "version": 7,
          "updated_at": "2025-05-18T10:30:00Z"
        }
      },
      {
        "operation_id": "op-uuid-3",
        "status": "rejected",
        "reason": "Entity not found (may have been permanently deleted)"
      }
    ]
  }
}
```

Possible `status` values: `applied`, `conflict`, `rejected`.

## Semantic Search

### POST /v1/search

**Request:**

```json
{
  "query": "meeting about Q3 roadmap",
  "limit": 10,
  "threshold": 0.7,
  "source_types": ["note", "transcript"]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | — | Natural language search query |
| `limit` | integer | No | 10 | Max results (1–50) |
| `threshold` | float | No | 0.7 | Minimum cosine similarity (0.0–1.0) |
| `source_types` | string[] | No | all | Filter by entity type: `note`, `transcript` |

**Response:**

```json
{
  "data": {
    "results": [
      {
        "source_type": "note",
        "source_id": "note-uuid",
        "title": "Q3 Planning Meeting",
        "snippet": "...discussed Q3 roadmap priorities and resource allocation...",
        "similarity": 0.92,
        "chunk_index": 0,
        "updated_at": "2025-05-15T14:00:00Z"
      },
      {
        "source_type": "transcript",
        "source_id": "memo-uuid",
        "title": "Voice memo — May 10",
        "snippet": "...talked about the Q3 roadmap with the product team...",
        "similarity": 0.85,
        "chunk_index": 2,
        "updated_at": "2025-05-10T09:30:00Z"
      }
    ]
  },
  "meta": {
    "request_id": "req_def456",
    "query_embedding_ms": 45,
    "search_ms": 12
  }
}
```

**Notes:**
- `snippet` is the matching text chunk (not the full content)
- `chunk_index` identifies which chunk of the source document matched
- `meta` includes timing for performance monitoring
- Results are ordered by `similarity` descending
- Queries shorter than 3 characters return empty results

## Rate Limiting

- Standard endpoints: 100 req/min per user
- AI endpoints (summarize, transcribe): 10 req/min per user
- Sync push: 30 req/min per user

429 responses include `Retry-After` header.

## Pagination Assumptions

| Parameter | Type | Default | Max | Notes |
|-----------|------|---------|-----|-------|
| `page` | integer | 1 | — | 1-indexed |
| `per_page` | integer | 20 | 100 | Values > 100 are clamped to 100 |
| `sort` | string | `updated_at` | — | Allowed: `created_at`, `updated_at`, `title` |
| `order` | string | `desc` | — | `asc` or `desc` |

- Pagination applies to: `GET /v1/notes`, `GET /v1/tasks`, `GET /v1/voice-memos`
- Sync endpoints do NOT use pagination — they use `since` timestamp with `has_more` flag
- Search results use `limit` (not `per_page`) and are not paginated beyond the limit

## Validation Assumptions

1. **Request body validation** runs on every POST/PATCH. Invalid requests return 400 before any DB operation.
2. **Path parameters** (`id`) are validated as UUID v4. Non-UUID strings return 400.
3. **Query parameters** are validated for type and range. Out-of-range values are clamped (not rejected).
4. **Empty strings** are treated as `null` for optional string fields. Required string fields reject empty strings.
5. **Timestamps** in request bodies use ISO 8601 format. Epoch milliseconds are used only in sync endpoints.
6. **Content size limits:** note content max 50,000 chars, task title max 500 chars, task description max 5,000 chars.
7. **Idempotency:** `POST /v1/sync/push` is idempotent — replaying the same `operation_id` returns `applied` without re-processing.

## FastAPI Implementation Notes

- All routes use `Depends(get_current_user)` for auth
- Request models are Pydantic v2 models generated from or equivalent to JSON Schema
- Response models use `response_model` parameter for automatic serialization
- SSE uses `StreamingResponse` with `text/event-stream` content type
- Middleware adds `request_id` to every response via UUID generation
