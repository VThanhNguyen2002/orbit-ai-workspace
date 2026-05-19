# Phase 1 Implementation Plan

## 1. Objective

Phase 1 turns the Synapse scaffold into a verified foundation for real product work. The goal is to establish package boundaries, shared contracts, API structure, client utilities, and implementation-ready plans for auth, notes, realtime sync, and AI summarization without overbuilding.

The phase should produce a repo where each next feature can be implemented against stable contracts and validated with repeatable commands.

## 2. Scope

Phase 1 includes:

- monorepo tooling and import boundary enforcement
- functioning shared TypeScript packages
- shared domain contracts and validation schemas
- standard API response, error, pagination, and sync DTO contracts
- FastAPI baseline structure with health/version routes and tests
- API client baseline with typed responses and safe error handling
- mobile/web app foundation planning before Expo initialization
- notes CRUD implementation plan
- realtime sync implementation plan
- AI summarization implementation plan using mock-first streaming
- testing baseline for shared contracts, API routes, and client utilities

## 3. Non-goals

Phase 1 does not include:

- production deployment
- advanced AI orchestration or provider failover
- background jobs
- offline conflict auto-resolution implementation
- push notifications
- analytics dashboards
- Expo initialization unless explicitly requested in a later slice
- full WatermelonDB implementation
- real AI provider integration
- personal RAG
- semantic search UI

## 4. Implementation Slices

### Slice 1 — Tooling And Package Boundary Enforcement

Focus:

- ESLint baseline
- restricted import rules
- dependency boundary checks
- package validation
- TypeScript project references where they add clear value

Acceptance criteria:

- `packages/shared` cannot import React, React Native, Expo, DOM/browser APIs, Node-only APIs, app code, UI, or API client code.
- packages cannot import from `apps/*`.
- root scripts run consistently through pnpm/Turbo.
- lint/typecheck failures clearly identify boundary violations.
- no product logic is added.

### Slice 2 — Shared Contracts Foundation

Focus:

- shared domain types
- API schemas
- validation contracts
- error envelopes
- pagination contracts
- sync DTO placeholders

Acceptance criteria:

- `@synapse/shared` exports initial Note, Task, VoiceMemo, API envelope, error, pagination, and sync DTO types.
- runtime validation is prepared for request/response contracts.
- contracts stay platform-agnostic.
- package tests cover schema accept/reject cases and error envelope shape.

### Slice 3 — FastAPI Baseline

Focus:

- FastAPI app structure
- `/health`
- `/version`
- test baseline
- API router structure

Acceptance criteria:

- API app has explicit router modules and app factory or equivalent startup structure.
- `/health` returns a simple service health payload.
- `/version` returns app/version metadata.
- API tests run without external services.
- route structure is ready for auth, notes, sync, and AI routers.

### Slice 4 — API Client Baseline

Focus:

- fetch wrapper
- typed responses
- error handling
- environment config
- runtime-safe API utilities

Acceptance criteria:

- `@synapse/api-client` exposes a small typed request helper.
- success and error envelopes match the API contract.
- auth header injection is supported without coupling to a specific auth storage implementation.
- tests cover successful response parsing, error parsing, and network failure handling.

### Slice 5 — Mobile/Web App Foundation

Focus:

- Expo initialization planning only
- app structure planning
- platform entrypoints
- shared package integration strategy

Acceptance criteria:

- app folder plan defines future route, component, service, persistence, and state boundaries.
- Expo initialization prerequisites are listed.
- no Expo app is initialized in this slice.
- shared package consumption strategy is documented before UI work starts.

### Slice 6 — Notes CRUD Implementation Plan

Planning only:

- endpoint shape
- package dependencies
- sync implications
- testing expectations

Acceptance criteria:

- notes endpoint list matches the API contract.
- required shared schemas and API client methods are identified.
- optimistic update and sync queue implications are documented.
- API, shared, and client test expectations are explicit.
- no notes feature code is implemented in this planning slice.

### Slice 7 — AI Summarization Implementation Plan

Planning only:

- streaming contract
- mock-first approach
- transcript flow assumptions
- provider abstraction assumptions

Acceptance criteria:

- SSE event sequence is defined for `token`, `action_items`, `done`, and `error`.
- provider interface is planned before real provider integration.
- mock provider testing strategy is defined.
- transcript and summary persistence assumptions are documented.
- no real AI provider integration is implemented in this planning slice.

## 5. Slice Order

The slice order follows dependency order and keeps risk low:

1. Tooling and package boundaries come first so later code cannot drift across package responsibilities.
2. Shared contracts come before API and client work so both sides depend on the same shapes.
3. FastAPI baseline comes before product endpoints so routing, health, and tests are stable.
4. API client baseline comes before app integration so frontend code has one response/error path.
5. Mobile/web foundation planning happens before Expo initialization to avoid premature app structure decisions.
6. Notes CRUD planning comes before implementation because notes exercise shared contracts, API, client, auth, and future sync.
7. AI summarization planning follows CRUD planning because AI depends on authenticated content access, streaming, and persistence decisions.

This sequence favors verification-first development: every slice should leave `lint`, `typecheck`, `test`, and `build` green before the next slice begins.

## 6. Acceptance Criteria

Phase 1 is complete when:

- package boundary enforcement is active and documented
- shared contracts compile and are tested
- FastAPI baseline exposes tested health/version routes
- API client baseline handles typed success/error responses
- mobile/web app initialization plan is ready for execution
- notes CRUD implementation plan is ready to convert into code
- AI summarization implementation plan is mock-first and stream-safe
- CI and local verification commands pass
- no Phase 2 offline persistence or conflict-resolution implementation has been started prematurely

## 7. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sync complexity | Can leak into Phase 1 and slow foundation work | Keep sync DTOs as contracts/placeholders until notes CRUD is stable |
| Expo/Web compatibility risks | Early app decisions may block web or mobile later | Plan app boundaries before Expo initialization; test web early once initialized |
| TypeScript boundary drift | Shared packages could accidentally depend on runtime-specific APIs | Enforce restricted imports and package dependency rules in Slice 1 |
| Supabase lock-in assumptions | Auth/RLS choices shape API and tests | Keep Supabase-specific code behind API/auth boundaries and document assumptions |
| Offline persistence edge cases | WatermelonDB work can grow beyond Phase 1 | Defer full local persistence implementation; only plan DTOs and contracts now |

## 8. Verification Commands

Run after every slice:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Additional checks by slice:

| Slice | Extra Verification |
|-------|--------------------|
| Slice 1 | boundary-violation fixtures or negative lint checks where practical |
| Slice 2 | package tests for shared contracts |
| Slice 3 | API route tests for `/health` and `/version` |
| Slice 4 | API client unit tests for success/error/network paths |
| Slice 5 | no Expo-generated files unless explicitly approved |
| Slice 6 | contract review against `docs/architecture/api-contract.md` |
| Slice 7 | mock SSE stream test plan before provider work |
