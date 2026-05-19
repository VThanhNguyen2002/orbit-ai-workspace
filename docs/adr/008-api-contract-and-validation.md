# ADR-008: API Contract And Validation

**Status:** Accepted
**Date:** 2026-05-19
**Author:** Viet Thanh Nguyen

## Context

Synapse has a TypeScript client, shared TypeScript packages, and a Python FastAPI backend. The API contract must stay stable across offline sync, AI streaming, and generated validation artifacts.

## Decision

Use a **resource-oriented `/v1` REST API** with:

- consistent success and error envelopes
- Supabase JWT bearer auth
- optimistic concurrency via `version`
- SSE for long-running AI operations
- Zod schemas in `@synapse/shared` as the source validation contract
- generated JSON Schema/Pydantic-compatible validation for FastAPI

## Rationale

- REST is simple to debug and maps cleanly to notes, tasks, voice memos, sync, and search.
- A standard envelope gives the client one path for `data`, `error`, and `request_id`.
- Version checks prevent lost updates during offline sync.
- SSE gives AI feedback without requiring WebSocket state management.
- Shared schema generation reduces frontend/backend validation drift.

## Consequences

### Positive

- API behavior is predictable for normal CRUD and queued sync operations.
- Client code can centralize response parsing and error classification.
- Validation can be tested once at the schema level and again at API boundaries.
- Streaming endpoints remain compatible with normal HTTP infrastructure.

### Negative

- Zod to JSON Schema conversion adds a build step.
- Pydantic parity must be tested for complex schema features.
- SSE requires explicit client handling for terminal `done` and `error` events.

### Mitigations

- Keep shared schemas simple and avoid conversion-hostile constructs.
- Add contract tests for each request/response model.
- Include `request_id` in every response and error.
- Treat sync push as idempotent by operation id.

## Implementation Notes

See [api-contract.md](../architecture/api-contract.md).

Do not introduce GraphQL, tRPC, or provider-specific AI payloads unless a later ADR supersedes this decision.
