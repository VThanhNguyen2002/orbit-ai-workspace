# Next Action

## Objective

Start Slice 6A — Notes contract refinement. The Notes CRUD plan is in place;
the next step should refine shared request/response schemas before route code.

## Expected Files To Change

- `packages/shared/src/**`
- `packages/shared/src/**/*.test.ts`
- `packages/shared/package.json` only if contract tooling needs a small update
- `docs/architecture/api-contract.md` only for contract clarifications

No FastAPI Notes routes, database integration, Supabase/auth wiring, frontend
screens, or sync engine implementation should be added in this slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- Shared contracts include create, update, delete/version, list query, and list
  response schemas for notes.
- Schemas reuse existing Note, pagination, success envelope, and error envelope
  contracts.
- Contract tests cover valid snake_case payloads, invalid payloads, and camelCase
  rejection.
- JSON Schema export/check remains deterministic.
- No product feature code is implemented.

## Risks

- Contract refinement can accidentally encode backend persistence details.
- Direct create id ownership must be settled before backend implementation.
- Delete version semantics need one clear request shape.
- Tests can miss camelCase rejection or conflict envelope expectations.

## Rollback Notes

Revert only Slice 6A shared contract additions and related contract docs if the
shape changes. Keep completed Slices 1-6 planning docs intact.
