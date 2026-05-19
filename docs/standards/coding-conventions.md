# Coding Conventions

## Principles

Synapse code should be boring in the best way: typed, explicit, testable, and easy to move across platforms.

- Prefer small modules with clear ownership over broad shared helpers.
- Keep platform-specific code inside `apps/mobile` or `apps/api`.
- Keep shared packages free of runtime assumptions unless the package contract allows them.
- Validate data at boundaries: UI input, API request bodies, sync payloads, and provider responses.

## TypeScript

| Area | Convention |
|------|------------|
| Strictness | `strict`, `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes` stay enabled |
| Types | Prefer explicit domain types from `@synapse/shared` over inline object shapes |
| Errors | Use typed result/error shapes at package boundaries; avoid throwing for expected validation failures |
| Imports | Use workspace package imports (`@synapse/shared`) instead of relative cross-package paths |
| Async | Always await promises or intentionally return them from the function |

Avoid:

- `any` unless isolated around an untyped third-party boundary with a short explanation
- importing from `apps/*` inside packages
- adding browser, Node, React Native, or Expo APIs to `@synapse/shared`
- duplicating validation rules outside shared schemas

## Python

| Area | Convention |
|------|------------|
| Runtime | Target Python 3.11+ |
| API | FastAPI route handlers stay thin; services own business logic |
| Validation | Pydantic models mirror generated JSON Schema contracts |
| Errors | Raise domain/application errors and convert them once in the global handler |
| Logging | Use structured logs with `request_id`; never log user content |

Route handlers should do only:

1. authenticate and parse request data
2. call a service
3. return the standard response envelope

## Naming

| Thing | Convention |
|-------|------------|
| Packages | `@synapse/<name>` |
| API paths | kebab-case plural resources, e.g. `/v1/voice-memos` |
| TypeScript files | kebab-case for files, PascalCase for components/types |
| Python files | snake_case |
| Database columns | snake_case |
| Error codes | SCREAMING_SNAKE_CASE |

## Package Boundaries

- `packages/shared`: pure TypeScript types, schemas, constants, and utilities only.
- `packages/api-client`: fetch/SSE client logic only; no UI or platform storage.
- `packages/ui`: reusable cross-platform UI abstractions only; no data fetching.
- `packages/config`: shared config contracts and constants only.
- `apps/mobile`: Expo, React Native, persistence adapters, device APIs, navigation.
- `apps/api`: FastAPI, database access, AI providers, RLS-aware backend logic.

## Commits And Reviews

- Use conventional commit messages.
- Keep unrelated refactors out of feature commits.
- A PR is ready when lint, typecheck, tests, and relevant docs pass.
- Security/privacy-sensitive changes must mention what data is stored, logged, or transmitted.
