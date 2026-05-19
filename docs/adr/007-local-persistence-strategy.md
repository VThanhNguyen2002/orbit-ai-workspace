# ADR-007: Local Persistence Strategy

**Status:** Accepted
**Date:** 2026-05-19
**Author:** Viet Thanh Nguyen

## Context

Synapse must support offline reads and writes across mobile and web. Local persistence needs relational queries, durable sync state, migrations, and observable reads for UI updates.

ADR-005 established the offline-first strategy. This ADR selects the concrete local persistence implementation for that strategy.

## Decision

Use **WatermelonDB backed by SQLite on mobile** and a **WatermelonDB web adapter with browser storage underneath** for web.

Local persistence stores:

- user content metadata and text entities
- sync operation queue
- conflict records
- last successful sync timestamp

It does not store voice memo audio binaries as database blobs.

## Rationale

- WatermelonDB is designed for React Native offline-first applications.
- Observable queries fit the UI model without custom subscription plumbing.
- SQLite gives mobile durable structured storage with migration support.
- The same conceptual data model can run on web through WatermelonDB's web adapter.
- Keeping sync state near the entities reduces mismatch between local records and pending operations.

## Consequences

### Positive

- Local-first reads and writes are fast and durable.
- Sync can map directly from local mutations to API operations.
- Migration strategy is explicit from the first implementation phase.
- UI can subscribe to local data instead of waiting on network state.

### Negative

- Adds a client storage dependency that must work across Expo/web constraints.
- Web behavior may differ from native SQLite performance.
- WatermelonDB has its own schema and migration conventions.

### Mitigations

- Keep the adapter boundary inside `apps/mobile`.
- Keep validation and domain rules in `@synapse/shared`.
- Add persistence tests for queue durability, migrations, logout cleanup, and server id backfill.
- Use full reset plus pull sync as the last-resort migration recovery path, while preserving unsynced operations when possible.

## Implementation Notes

See [local-persistence.md](../architecture/local-persistence.md).

The first implementation should create only the tables required for Phase 1 entities and sync metadata. Avoid prebuilding speculative local tables.
