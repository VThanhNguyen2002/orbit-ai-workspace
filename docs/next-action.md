# Next Action

## Objective

Start Slice 1 — Tooling and package boundary enforcement. The goal is to make package boundaries executable before any product logic is added.

## Expected Files To Change

- root ESLint/config files as needed
- root `package.json` scripts if boundary commands are added
- package-level config only where required
- CI workflow only if a new verification command is introduced
- documentation only for boundary rule clarifications

No app features, Expo initialization, API routes, or product schemas should be added in this slice.

## Commands To Run

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

If a boundary-specific command is added, run it locally and add it to CI.

## Definition Of Done

- `packages/shared` is protected from React, React Native, Expo, DOM/browser APIs, Node-only APIs, app imports, UI imports, and API client imports.
- packages cannot import from `apps/*`.
- lint/typecheck/test/build pass.
- CI runs the same baseline checks.
- no product logic is introduced.

## Risks

- ESLint config can become too broad and block valid package internals.
- TypeScript path aliases can mask invalid dependency edges if lint rules are weak.
- Adding too much tooling at once can slow the repo before implementation starts.

## Rollback Notes

Revert only the boundary tooling/config changes from Slice 1. Do not alter the Wave 1/Wave 2 architecture docs or the monorepo scaffold unless the config change directly requires it.
