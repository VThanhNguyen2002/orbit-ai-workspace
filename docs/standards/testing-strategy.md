# Testing Strategy

## Goals

Tests should protect the behaviors that make Synapse trustworthy: auth isolation, offline durability, sync correctness, API contracts, and AI failure handling.

## Test Layers

| Layer | Scope | Examples |
|-------|-------|----------|
| Unit | Pure functions and schemas | Zod validation, conflict merge helpers, chunking |
| Package integration | Package boundaries | api-client response parsing, UI primitive rendering |
| API integration | FastAPI routes with mocked providers | auth, CRUD, sync push/pull, SSE errors |
| Persistence integration | Local database adapter | offline writes, queue survival, migrations |
| E2E | Critical user journeys | sign in, create note, edit offline, reconnect |

## Required Coverage By Area

| Area | Minimum Tests Before Feature Is Done |
|------|-------------------------------------|
| `@synapse/shared` | schema accept/reject cases, edge values, conflict helpers |
| `@synapse/api-client` | success envelope, error envelope, auth header, SSE parsing |
| `@synapse/ui` | render states, accessibility labels, disabled/loading states |
| `apps/api` | 401/403/404/409 paths, request validation, RLS isolation, provider failures |
| `apps/mobile` | offline write path, sync queue processing, auth session lifecycle |

## Offline And Sync Tests

The sync test suite must cover:

- create offline, reconnect, server id backfill
- update conflict with stale version
- delete vs edit, with delete winning
- queue retry on network/5xx failures
- no retry on validation or auth failures
- queue recovery after app restart or interrupted sync

Use deterministic clocks and fixed operation ids in tests. Avoid real network calls; mock API and provider boundaries.

## Auth And RLS Tests

Every user-owned table needs tests proving:

- unauthenticated requests return 401
- user A cannot read, update, or delete user B records
- inserts cannot spoof another `user_id`
- service-role paths are absent from request handlers

## AI Tests

AI tests use provider fakes. They should verify:

- prompts are not logged
- SSE emits `token`, terminal `done`, and safe `error` events
- provider timeout/rate-limit failures map to documented error codes
- embedding chunking is stable for the same input

## CI Requirements

Baseline CI runs:

```bash
pnpm lint
pnpm typecheck
pnpm test
```

As implementation grows, CI should add API tests, persistence tests, E2E smoke tests, and coverage reporting. Heavy E2E suites can run on PR labels or nightly, but the critical smoke path should run on every PR.

## Fixtures

- Use small, readable fixtures.
- Never commit real user content, real tokens, or production-like secrets.
- Prefer generated UUIDs and timestamps with explicit fixture names.
