# Data Flow

## Overview

This document traces how data moves through Synapse for every major operation. It covers the online path, offline path, AI processing pipeline, and real-time update propagation. Each flow references the authoritative docs: [api-contract.md](api-contract.md), [offline-sync.md](offline-sync.md), [ai-integration.md](ai-integration.md).

## Flow 1: Create Note (Online)

```mermaid
sequenceDiagram
    participant U as User
    participant App as React Native App
    participant DB as WatermelonDB (Local)
    participant API as FastAPI Backend
    participant SB as Supabase PostgreSQL
    participant RT as Supabase Realtime

    U->>App: Write note content
    App->>DB: Create local record (server_id=null)
    App->>App: Optimistic UI update (note visible immediately)
    App->>API: POST /v1/notes {title, content}
    API->>API: Validate via JSON Schema
    API->>SB: INSERT INTO notes (RLS enforced)
    SB-->>API: Created row with server UUID
    API-->>App: 201 {data: {id, title, ...}}
    App->>DB: Update server_id on local record
    SB->>RT: Broadcast INSERT event
    RT-->>App: Realtime notification (ignored — already have data)
```

**Key behaviors:**
- Local write happens BEFORE API call (optimistic)
- Realtime event arrives after API response — client deduplicates via `server_id`
- If API call fails, note persists locally and enters sync queue

## Flow 2: Create Note (Offline)

```mermaid
sequenceDiagram
    participant U as User
    participant App as React Native App
    participant DB as WatermelonDB (Local)
    participant Q as Sync Queue

    U->>App: Write note content
    App->>DB: Create local record (server_id=null, version=1)
    App->>Q: Enqueue operation (type=create, entity=note, status=pending)
    App->>App: UI shows note immediately

    Note over App: Device comes online later

    App->>App: Connectivity detected
    App->>App: Refresh auth token if expired
    App->>App: Process sync queue (FIFO)
```

When connectivity resumes, the sync queue is processed via `POST /v1/sync/push`. See offline-sync.md for queue processing rules.

## Flow 3: Edit Note with Conflict

```mermaid
sequenceDiagram
    participant D1 as Device 1
    participant D2 as Device 2
    participant API as FastAPI Backend
    participant SB as Supabase PostgreSQL

    Note over D1,D2: Both devices have note at version=3

    D1->>API: PATCH /v1/notes/:id {title: "A", version: 3}
    API->>SB: UPDATE notes SET title='A', version=4 WHERE id=:id AND version=3
    SB-->>API: Updated (1 row affected)
    API-->>D1: 200 {data: {version: 4}}

    D2->>API: PATCH /v1/notes/:id {content: "B", version: 3}
    API->>SB: UPDATE notes SET content='B', version=4 WHERE id=:id AND version=3
    SB-->>API: 0 rows affected (version mismatch)
    API-->>D2: 409 {error: {code: CONFLICT, server_data: {title: "A", version: 4}}}

    Note over D2: Auto-resolve: D2 changed content, server changed title → merge

    D2->>API: PATCH /v1/notes/:id {content: "B", version: 4}
    API->>SB: UPDATE (success)
    API-->>D2: 200 {data: {version: 5}}
```

**Conflict resolution rules:**
1. Non-overlapping field changes → auto-merge (client retries with server version)
2. Same field changed → surface to user for manual resolution
3. Delete vs. edit → delete wins (consistent with offline-sync.md)

## Flow 4: AI Summarization

```mermaid
sequenceDiagram
    participant App as React Native App
    participant API as FastAPI Backend
    participant LLM as AI Provider (OpenAI/Groq)
    participant SB as Supabase PostgreSQL
    participant RT as Supabase Realtime

    App->>API: POST /v1/notes/:id/summarize
    API->>SB: Fetch note content (RLS enforced)
    SB-->>API: Note content

    API->>API: Chunk content if > context window
    API->>LLM: Stream completion request (system prompt + note content)

    loop Token streaming
        LLM-->>API: Token chunk
        API-->>App: SSE event: token {text: "..."}
        App->>App: Render incremental text
    end

    LLM-->>API: Final response with action items
    API-->>App: SSE event: action_items {items: [...]}
    API->>SB: INSERT INTO summaries (content, action_items, source_id)
    API->>SB: INSERT INTO embeddings (generated from summary)
    API-->>App: SSE event: done {summary_id: "uuid"}

    SB->>RT: Broadcast INSERT event (summaries table)
```

**Key behaviors:**
- Tokens stream to client as they arrive (low latency UX)
- Summary is persisted AFTER full generation (not incremental saves)
- Embedding is generated from the final summary text
- If provider fails mid-stream, `SSE event: error` is sent and no summary is persisted

## Flow 5: Voice Memo → Transcript

```mermaid
sequenceDiagram
    participant App as React Native App
    participant API as FastAPI Backend
    participant Store as Supabase Storage
    participant W as Whisper API
    participant SB as Supabase PostgreSQL

    App->>App: Record audio (local temp file)
    App->>API: POST /v1/voice-memos {title, duration_seconds}
    API->>SB: INSERT INTO voice_memos (status=recording)
    API-->>App: 201 {data: {id: memo_id}}

    App->>Store: Upload audio to voice-memos/{user_id}/{memo_id}.webm
    App->>API: POST /v1/voice-memos/:id/transcribe
    API->>SB: UPDATE status='transcribing'
    API->>Store: Download audio file
    API->>W: Send audio for transcription

    loop Token streaming
        W-->>API: Transcript chunk
        API-->>App: SSE event: token {text: "..."}
    end

    W-->>API: Final transcript
    API->>SB: INSERT INTO transcripts (content, language)
    API->>SB: UPDATE voice_memos SET status='transcribed'
    API->>SB: INSERT INTO embeddings (from transcript)
    API-->>App: SSE event: done {transcript_id: "uuid"}

    App->>App: Delete local temp audio file
```

## Flow 6: Semantic Search

```mermaid
sequenceDiagram
    participant App as React Native App
    participant API as FastAPI Backend
    participant LLM as Embedding Model
    participant SB as Supabase PostgreSQL (pgvector)

    App->>API: POST /v1/search {query: "Q3 roadmap"}
    API->>LLM: Generate embedding for query text
    LLM-->>API: Query embedding vector

    API->>SB: SELECT * FROM embeddings<br/>ORDER BY embedding <=> query_vector<br/>WHERE user_id = auth.uid()<br/>AND similarity > 0.7<br/>LIMIT 10
    SB-->>API: Matching chunks with similarity scores

    API->>SB: Fetch source entities (notes/transcripts) for matched chunks
    SB-->>API: Source entity metadata

    API-->>App: {results: [{source_type, title, snippet, similarity}]}
```

**Key behaviors:**
- Query text is embedded using same model as content embeddings (consistency)
- pgvector `<=>` operator for cosine distance
- RLS enforced — user only sees their own embeddings
- Results include snippet (matched chunk text), not full content

## Flow 7: Sync Pull (Hydrating After Offline)

```mermaid
sequenceDiagram
    participant App as React Native App
    participant API as FastAPI Backend
    participant SB as Supabase PostgreSQL
    participant DB as WatermelonDB (Local)

    App->>App: Connectivity restored
    App->>App: Refresh auth token
    App->>API: GET /v1/sync/pull?since=1700000000000
    API->>SB: SELECT * FROM notes WHERE updated_at > since AND user_id = auth.uid()
    API->>SB: SELECT * FROM tasks WHERE updated_at > since AND user_id = auth.uid()
    API->>SB: (repeat for all entity types)
    SB-->>API: Changed entities (including soft-deleted)
    API-->>App: {data: {notes: [...], tasks: [...]}, meta: {sync_timestamp, has_more}}

    App->>DB: Upsert received entities (match on server_id)
    App->>DB: Mark is_deleted entities for local removal
    App->>App: Update last_synced_at to sync_timestamp

    alt has_more is true
        App->>API: GET /v1/sync/pull?since=<sync_timestamp>
        Note over App,API: Repeat until has_more is false
    end
```

## Data Flow Boundaries

```mermaid
graph TD
    subgraph "Client Layer"
        UI[React Components]
        Store[Zustand Stores]
        WDB[WatermelonDB]
        SQ[Sync Queue]
    end

    subgraph "Network Layer"
        HTTP[REST API Calls]
        SSE[SSE Streaming]
        WS[Realtime WebSocket]
    end

    subgraph "Backend Layer"
        Routes[FastAPI Routes]
        Services[Service Layer]
        AIOrch[AI Orchestrator]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL + pgvector)]
        S3[(Supabase Storage)]
    end

    UI -->|User action| Store
    Store -->|Read/Write| WDB
    Store -->|Queue operation| SQ
    SQ -->|On connectivity| HTTP
    Store -->|API call| HTTP
    HTTP --> Routes
    Routes --> Services
    Services --> PG
    Services --> S3
    Services --> AIOrch
    AIOrch -->|Stream| SSE
    SSE -->|Tokens| UI
    PG -->|Change events| WS
    WS -->|Live updates| Store
```

## Invariants

1. **Local-first:** Every user action writes to WatermelonDB before making any API call
2. **No data loss:** Failed API calls are queued (sync queue), not dropped
3. **Consistency:** `version` field on every mutable entity enables optimistic concurrency
4. **Idempotency:** Sync push operations use `operation_id` to prevent duplicate processing
5. **Privacy:** User content never appears in logs, Sentry events, or error messages
6. **Single authority:** Server is the source of truth; local DB is a cache with write-ahead capability
