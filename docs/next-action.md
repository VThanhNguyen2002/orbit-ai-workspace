# Next Action

## Objective

Start Slice 6F — Notes integration verification. The shared Notes CRUD
contracts, FastAPI route skeleton, API client methods, auth context boundary,
repository interface, memory default, Supabase repository scaffold, and draft
Notes migration/RLS file are in place. The next step should verify the full
contract across packages and document any remaining integration gaps before live
Supabase wiring.

## Expected Files To Change

- Verification docs and small test fixes only if gaps are discovered.
- Avoid frontend UI, Expo initialization, sync engine work, AI/provider work, and
  live Supabase client wiring unless Slice 6F explicitly expands scope.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, or service-role usage in
request handlers.

## Commands To Run

```bash
cd apps/api
python -m ruff check .
python -m pytest
cd ../..

pnpm --filter @synapse/shared test
pnpm --filter @synapse/shared contracts:check
pnpm --filter @synapse/api-client test
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- All requested API, shared, API-client, lint, typecheck, test, and build
  commands pass from a clean checkout.
- Verification confirms memory repo remains the default and does not require
  Supabase environment variables.
- Verification confirms Notes auth derives `user_id` from the auth context and
  never from client payloads.
- Verification confirms missing/deleted/cross-user Notes return `404`; stale
  versions return `409` with `server_data`.
- Verification confirms the migration/RLS draft is present but not executed in
  CI.
- No secrets, provider integration, frontend UI, Expo initialization, or sync
  engine work is added.

## Risks

- The Supabase repository is scaffolded only; live client injection and JWT
  verification still need dedicated implementation.
- The SQL RLS draft still needs execution against a real Supabase project and
  integration tests using user-scoped tokens.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the JSON Schema bridge is completed.

## Rollback Notes

Revert only Slice 6F verification changes if they introduce noise. Keep completed
shared contracts, backend skeleton, API client methods, Slice 6E auth/repository
boundaries, and migration/RLS draft intact.
