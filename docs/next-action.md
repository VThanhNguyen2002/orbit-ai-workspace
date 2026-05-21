# Next Action

## Objective

Start Slice 6 — Notes CRUD implementation plan. This is still a planning and
design-first slice, not feature implementation.

## Expected Files To Change

- planning docs for Notes CRUD endpoint shape and sequencing
- docs that identify shared schema/API client changes needed later
- docs that describe sync queue and conflict implications
- docs that define API, shared, and client test expectations

No Notes CRUD code, database integration, Supabase/auth wiring, frontend screens,
or sync implementation should be added in this slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- Notes endpoint list matches the API contract.
- Required shared schemas and future API client methods are identified.
- Optimistic update and sync queue implications are documented.
- API, shared, and client test expectations are explicit.
- No product feature code is implemented.

## Risks

- Planning can drift into implementation before persistence/auth boundaries are ready.
- CRUD endpoints can accidentally bypass offline-first and versioning constraints.
- Shared schemas can grow too broad before the Notes flow proves the shape.
- Tests can miss conflict, validation, and auth-isolation expectations if not planned now.

## Rollback Notes

Revert only Slice 6 planning docs if the CRUD sequence changes. Keep completed
Slices 1-5 intact.
