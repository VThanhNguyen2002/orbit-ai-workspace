# Next Action

## Objective

Start Slice 6D — Notes persistence/auth integration plan. The shared Notes CRUD
contracts, Slice 6B FastAPI route skeleton, and Slice 6C API client methods are
in place. The next step should plan durable persistence and auth integration
before implementation.

## Expected Files To Change

- docs for persistence/auth planning
- future migration/RLS/auth boundary notes only if needed

Do not add database migrations, Supabase clients, provider secrets, frontend
screens, Expo initialization, API client methods, or sync engine implementation
in this planning slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm --filter @synapse/shared contracts:check
```

## Definition Of Done

- Persistence/auth boundaries for Notes are documented before code changes.
- Supabase table/RLS/auth dependency expectations are clear.
- In-memory backend limitations and replacement path are explicit.
- No provider secrets, live Supabase calls, UI, or sync engine code is added.

## Risks

- Persistence planning can drift into implementation too early.
- Auth placeholder replacement must preserve non-enumerating 404 behavior.
- RLS and application-level user scoping need to stay aligned.

## Rollback Notes

Revert only Slice 6D planning docs if route sequencing changes. Keep completed
shared contracts, backend skeleton, and API client methods intact.
