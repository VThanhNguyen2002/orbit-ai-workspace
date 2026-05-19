# Next Action

## Objective

Start Slice 2 — Shared contracts foundation. The goal is to define the first platform-agnostic TypeScript contracts that the API, client, and future app implementation can share safely.

## Expected Files To Change

- `packages/shared/src/**`
- `packages/shared/package.json` if test scripts or lightweight validation tooling are added
- package tests for shared contracts if introduced
- documentation only if contract decisions need clarification

No app features, Expo initialization, FastAPI business endpoints, UI screens, or real sync/AI implementation should be added in this slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- `@synapse/shared` exports initial domain/API contract types without platform imports.
- API envelope, error envelope, pagination, and sync DTO placeholders are represented.
- runtime validation approach is chosen only if it stays lightweight.
- package boundary linting remains green.
- no product flow is implemented.

## Risks

- Contracts can become too broad before feature code proves the shape.
- Runtime validation dependencies can add weight too early.
- Shared contracts may accidentally encode platform/runtime assumptions.

## Rollback Notes

Revert only the shared contract files and any Slice 2 validation/test additions. Keep Slice 1 ESLint and boundary enforcement intact.
