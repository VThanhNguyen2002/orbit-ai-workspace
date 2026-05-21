# Next Action

## Objective

Start Slice 6B — Notes backend route skeleton. The shared Notes CRUD contracts
exist; the next step should add route signatures and mocked-service route tests
without database or auth provider integration.

## Expected Files To Change

- `apps/api/app/routers/notes.py`
- `apps/api/app/models/notes.py` if route request/response models are needed
- `apps/api/app/services/note_service.py` as an interface or fake boundary only
- `apps/api/tests/test_notes.py`
- docs only for route skeleton clarifications

No database integration, Supabase/auth provider wiring, frontend screens, API
client note methods, or sync engine implementation should be added in this
slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- Notes route signatures exist for list, create, get, update, and delete.
- Route tests use mocked dependencies and do not touch a real database.
- Routes use the standard success/error envelope shapes.
- Auth/database dependencies remain placeholders or fakes.
- Stale-version and not-found behavior is represented in tests through mocked
  service errors.
- No product feature code is implemented.

## Risks

- Route skeletons can drift into persistence or auth implementation too early.
- Mocked service errors must match the standard API error envelope.
- Route models must stay aligned with exported shared schemas.
- Tests can miss 404/409 behavior if service fakes are too shallow.

## Rollback Notes

Revert only Slice 6B API route skeleton files and tests if route sequencing
changes. Keep completed shared contracts and planning docs intact.
