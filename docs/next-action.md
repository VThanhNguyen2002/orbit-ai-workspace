# Next Action

## Objective

Start Slice 6C — Notes API client methods. The shared Notes CRUD contracts exist
and the Slice 6B FastAPI route skeleton is in place with in-memory storage only.
The next step should add typed client methods without frontend UI, sync engine,
database migrations, or provider integration.

## Expected Files To Change

- `packages/api-client/src/index.ts`
- `packages/api-client/src/index.test.ts`
- shared contract imports only if needed

No database integration, Supabase/auth provider wiring, frontend screens, Expo
initialization, or sync engine implementation should be added in this slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm --filter @synapse/shared contracts:check
```

## Definition Of Done

- API client exposes Notes list/create/get/update/delete methods.
- Methods keep snake_case request and response DTOs.
- Methods parse standard success envelopes and preserve error handling behavior.
- Tests cover expected paths, query serialization, payloads, and 404/409 error
  mapping.
- No product UI, sync engine, auth provider, or database code is implemented.

## Risks

- Client methods can drift from the shared snake_case contracts.
- Error mapping should stay compatible with existing `ApiClientError` behavior.
- Notes client work should not pull in sync or UI responsibilities.

## Rollback Notes

Revert only Slice 6C API client changes if route sequencing changes. Keep
completed shared contracts and Slice 6B backend skeleton intact.
