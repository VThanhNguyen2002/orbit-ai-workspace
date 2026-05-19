# ADR-005: Offline-First Sync Strategy

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

Synapse targets mobile users who may lose connectivity (commuting, traveling, poor signal). The app must remain fully functional offline — reads and writes must work without network. Changes made offline must sync when connectivity resumes without data loss.

This is also a key portfolio differentiator: most productivity apps treat offline as an afterthought.

## Decision

Implement **offline-first architecture** with:

1. **Local-first writes** — all mutations write to local persistence immediately
2. **Sync queue** — offline operations queued and replayed on reconnect
3. **Optimistic concurrency** — version-based conflict detection
4. **Last-write-wins default** — auto-resolve most conflicts by timestamp
5. **Pull-based hydration** — `/v1/sync/pull?since=` endpoint for delta sync

## Rationale

### Why not sync frameworks (WatermelonDB, PowerSync)

**WatermelonDB:**
- Good fit for React Native offline, but adds SQLite dependency
- Custom sync protocol — harder to debug and maintain
- Opinionated about data model (requires `_status` and `_changed` columns)

**PowerSync:**
- Cloud service with sync built in — adds vendor dependency
- Requires their specific client SDK
- Free tier limitations may constrain development

**Custom approach chosen because:**
- Full control over conflict resolution strategy
- Simpler mental model (queue + version + timestamp)
- Portfolio value: demonstrates sync engineering, not framework usage
- Fewer moving parts to debug

### Why version-based, not CRDT

CRDTs (Conflict-free Replicated Data Types) are powerful but:
- Complex to implement correctly for arbitrary data structures
- Overkill for a single-user app where conflicts are rare
- Add significant bundle size (Yjs, Automerge)
- Better suited for collaborative editing (Google Docs-style)

Version-based optimistic concurrency is simpler, well-understood, and sufficient for Synapse's single-user multi-device model.

### Why last-write-wins over manual resolution

For a single user on multiple devices:
- Conflicts are rare (< 1% of operations)
- When they occur, the latest edit is usually the intended one
- Manual resolution adds friction to a productivity app
- Complex conflicts (same field edited on both sides) are surfaced to user — only the common case auto-resolves

## Consequences

### Positive
- App works identically offline and online — no degraded state
- User never waits for network to complete a write
- Sync is transparent — user doesn't need to understand it
- Demonstrates real engineering capability in portfolio

### Negative
- More complex client architecture (stores, queues, connectivity detection)
- Version field on every mutable entity adds schema complexity
- Edge cases around app crash during sync require careful handling
- Testing offline behavior requires connectivity simulation

### Mitigations
- Sync logic lives in `@synapse/shared` — tested independently of UI
- Queue persistence uses the selected WatermelonDB local persistence layer
- Integration tests mock connectivity toggling
- ConflictRecord tracks all resolutions for debugging

## Technical Details

See [offline-sync.md](../architecture/offline-sync.md) for full implementation details including:

- Sync queue interface and processing rules
- Retry strategy with exponential backoff
- Pull sync and delta hydration
- Conflict detection and resolution flow
- Local persistence abstraction
- Connectivity detection
- Edge cases and handling
