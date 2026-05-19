# Local Persistence

## Overview

Synapse uses a local persistence layer to enable offline-first behavior. All user content (notes, tasks, voice memo metadata, transcripts, summaries) is stored locally so the app is fully functional without network access. This document defines the storage engine, schema design, data lifecycle, and integration with the sync system.

## Storage Engine

### Decision: WatermelonDB on SQLite

| Option Considered | Verdict | Reason |
|-------------------|---------|--------|
| WatermelonDB | **Selected** | Built for React Native offline-first apps; lazy-loading, observable queries, built-in sync primitives |
| Raw SQLite (expo-sqlite) | Rejected | Too low-level; would need to build observable queries and sync layer from scratch |
| MMKV | Rejected | Key-value only; no relational queries, no schema enforcement |
| Realm | Rejected | Heavy runtime, proprietary sync protocol conflicts with Supabase |
| PouchDB | Rejected | CouchDB-oriented sync; doesn't align with Supabase PostgreSQL backend |

**Rationale:** WatermelonDB wraps SQLite and provides:
- Lazy-loading for large datasets (notes don't load content until accessed)
- Observable queries that integrate with React re-rendering
- Schema definition with migrations
- Built-in sync protocol (`synchronize()`) that can be adapted to our push/pull endpoints
- Runs on both React Native (native SQLite) and web (LokiJS adapter or wa-sqlite)

### Web Adapter

- **Mobile:** Native SQLite via `@nozbe/watermelondb/adapters/sqlite`
- **Web:** `@nozbe/watermelondb/adapters/lokijs` (LokiJS in-memory with IndexedDB persistence)

This means web users also get offline support, though with slightly different performance characteristics (IndexedDB is slower than native SQLite for large datasets).

## Local Schema

The local schema mirrors the server-side data model but with additional sync-specific fields managed by WatermelonDB.

```typescript
// packages/shared/src/local-schema/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'notes',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true },       // null until synced
        { name: 'title', type: 'string' },
        { name: 'content', type: 'string' },
        { name: 'content_type', type: 'string' },                      // 'plain' | 'markdown'
        { name: 'is_archived', type: 'boolean' },
        { name: 'is_deleted', type: 'boolean' },
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'tasks',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true },
        { name: 'note_id', type: 'string' },                           // local WatermelonDB ID
        { name: 'title', type: 'string' },
        { name: 'description', type: 'string', isOptional: true },
        { name: 'status', type: 'string' },                            // 'todo' | 'in_progress' | 'done'
        { name: 'priority', type: 'string' },                          // 'low' | 'medium' | 'high'
        { name: 'due_date', type: 'number', isOptional: true },
        { name: 'is_deleted', type: 'boolean' },
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'voice_memos',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true },
        { name: 'title', type: 'string', isOptional: true },
        { name: 'duration_seconds', type: 'number' },
        { name: 'status', type: 'string' },                            // 'recording' | 'uploaded' | 'transcribing' | 'transcribed' | 'failed'
        { name: 'is_deleted', type: 'boolean' },
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
      // NOTE: Audio binary NOT stored in DB — held in temp file cache only
    }),
    tableSchema({
      name: 'transcripts',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true },
        { name: 'voice_memo_id', type: 'string' },
        { name: 'content', type: 'string' },
        { name: 'language', type: 'string' },
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
    tableSchema({
      name: 'summaries',
      columns: [
        { name: 'server_id', type: 'string', isOptional: true },
        { name: 'source_id', type: 'string' },
        { name: 'source_type', type: 'string' },                       // 'note' | 'transcript'
        { name: 'content', type: 'string' },
        { name: 'model_used', type: 'string' },
        { name: 'action_items', type: 'string' },                      // JSON stringified array
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ],
    }),
  ],
});
```

### Local vs Server ID Mapping

| Field | Purpose |
|-------|---------|
| `id` | WatermelonDB auto-generated local ID (used for all local relations) |
| `server_id` | UUID from the server (null until first sync) |

When an entity is created offline:
1. WatermelonDB assigns a local `id`
2. `server_id` is `null`
3. On sync push, the server creates the entity and returns a server UUID
4. The local `server_id` field is updated
5. All subsequent sync operations use `server_id` for matching

## Sync Integration

WatermelonDB provides a `synchronize()` function that we adapt to our API:

```typescript
// apps/mobile/src/sync/synchronize.ts
import { synchronize } from '@nozbe/watermelondb/sync';
import { database } from '../database';
import { apiClient } from '@synapse/api-client';

export async function syncWithServer(): Promise<void> {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const response = await apiClient.sync.pull(lastPulledAt);
      return {
        changes: mapServerToWatermelon(response.data),
        timestamp: response.meta.sync_timestamp,
      };
    },
    pushChanges: async ({ changes }) => {
      const operations = mapWatermelonToOperations(changes);
      const result = await apiClient.sync.push(operations);
      handleConflicts(result.data.results);
    },
  });
}
```

### Mapping Rules

| WatermelonDB Event | API Operation | Sync Queue Entry |
|--------------------|---------------|-----------------|
| `record.create()` | `POST /v1/{entity}` or included in sync push | `operation: "create"` |
| `record.update()` | `PATCH /v1/{entity}/:id` or included in sync push | `operation: "update"` |
| `record.markAsDeleted()` | `DELETE /v1/{entity}/:id` or included in sync push | `operation: "delete"` (soft) |

## Data Lifecycle

### Creation

```
User creates note → WatermelonDB writes to local SQLite
                   → Sync queue entry created (status: pending)
                   → If online: push immediately
                   → If offline: queue until connectivity
```

### Read

```
UI component subscribes → WatermelonDB observable query
                        → Returns local data immediately (no network wait)
                        → Realtime subscription updates local DB when server changes arrive
```

### Update

```
User edits note → WatermelonDB updates local row (version++)
               → Sync queue entry created
               → If online: push with version for conflict detection
```

### Deletion

```
User deletes note → WatermelonDB marks as deleted (soft delete)
                  → Row hidden from queries but retained for sync
                  → Sync push sends DELETE operation
                  → Server-side: is_deleted=true, retained for 30 days
                  → After 30 days: server purges, next sync pull removes local copy
```

## Storage Limits

| Constraint | Limit | Enforcement |
|------------|-------|-------------|
| Max notes per user | No hard limit (text is small) | Monitor via observability |
| Max note content size | 50,000 characters | Zod schema validation |
| Max tasks per user | No hard limit | Monitor via observability |
| Max voice memo metadata rows | No hard limit | Audio binary not stored locally |
| Total SQLite DB size | ~50MB typical, 200MB upper bound | No enforcement in Phase 1; monitor |
| Sync queue depth | 1,000 operations max | Oldest operations are prioritized; warn user if queue is deep |

### Storage Size Estimation

| Entity | Avg Size | 1,000 Entities |
|--------|----------|----------------|
| Note (title + content) | ~5 KB | ~5 MB |
| Task | ~500 B | ~500 KB |
| Voice memo metadata | ~200 B | ~200 KB |
| Transcript | ~3 KB | ~3 MB |
| Summary | ~2 KB | ~2 MB |

A heavy user with 1,000 notes, 2,000 tasks, 500 transcripts, and 500 summaries would use approximately **12 MB** of local storage. Well within acceptable bounds.

## Schema Migrations

WatermelonDB supports schema migrations. When the local schema changes:

```typescript
// packages/shared/src/local-schema/migrations.ts
import { schemaMigrations, addColumns } from '@nozbe/watermelondb/Schema/migrations';

export const migrations = schemaMigrations({
  migrations: [
    {
      toVersion: 2,
      steps: [
        addColumns({
          table: 'notes',
          columns: [
            { name: 'new_field', type: 'string', isOptional: true },
          ],
        }),
      ],
    },
  ],
});
```

**Migration rules:**
1. Migrations are additive only — never remove columns in a migration
2. New columns must be optional (`isOptional: true`) or have defaults
3. Migrations are tested in CI against a database with synthetic data
4. If migration fails at runtime, the app falls back to a full resync (drop local DB, pull all data)

## Tradeoffs

| Decision | Upside | Downside |
|----------|--------|----------|
| WatermelonDB over raw SQLite | Observable queries, sync primitives, lazy loading | Additional abstraction layer, WatermelonDB-specific patterns |
| Separate local and server IDs | Offline creation without server round-trip | Extra mapping logic in sync layer |
| LokiJS adapter for web | Web offline support | Slower than native SQLite; entire DB in memory |
| No local encryption (Phase 1) | Simpler implementation | Relies on OS-level device security |
| Schema in `@synapse/shared` | Single source of truth for local schema | Must keep in sync with server data model manually |

## Assumptions

1. WatermelonDB's `synchronize()` protocol is adaptable to our custom push/pull endpoints
2. LokiJS performance is acceptable for web users with < 1,000 entities
3. Device storage is sufficient (12 MB for heavy user is well within limits)
4. Schema migrations can be tested in CI with synthetic data
5. Full resync fallback (drop + re-pull) is acceptable for failed migrations
