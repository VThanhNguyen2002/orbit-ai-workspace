# Monorepo Architecture

## Structure

```
synapse/
├── apps/
│   ├── mobile/                # Expo app — web, iOS, Android
│   │   ├── app/               # Expo Router file-based routing
│   │   ├── components/        # App-specific composed components
│   │   ├── hooks/             # App-specific hooks (useAuth, useSync)
│   │   ├── services/          # Platform-specific service wiring
│   │   ├── stores/            # Zustand stores (local state + sync)
│   │   ├── app.json
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── api/                   # FastAPI backend
│       ├── app/
│       │   ├── routers/       # Route handlers
│       │   ├── services/      # Business logic (AI, sync, search)
│       │   ├── models/        # SQLAlchemy / Pydantic models
│       │   ├── core/          # Config, dependencies, middleware
│       │   └── main.py
│       ├── tests/
│       ├── pyproject.toml
│       └── Dockerfile
├── packages/
│   ├── shared/                # Cross-platform business logic
│   │   ├── src/
│   │   │   ├── types/         # Entity types, API types, enum maps
│   │   │   ├── validation/    # Zod schemas
│   │   │   ├── utils/         # Pure functions (date, text, sync logic)
│   │   │   └── constants/     # Shared constants, feature flags
│   │   ├── tsconfig.json
│   │   └── package.json
│   ├── ui/                    # Cross-platform UI components
│   │   ├── src/
│   │   │   ├── primitives/    # Button, Input, Text, Icon
│   │   │   ├── composites/    # NoteCard, TaskRow, VoicePlayer
│   │   │   ├── layouts/       # Screen, Modal, BottomSheet
│   │   │   └── tokens/        # Colors, spacing, typography
│   │   ├── tsconfig.json
│   │   └── package.json
│   ├── api-client/            # Typed HTTP + SSE client
│   │   ├── src/
│   │   │   ├── client.ts      # Base HTTP client (fetch-based)
│   │   │   ├── endpoints/     # Per-resource endpoint functions
│   │   │   ├── streaming.ts   # SSE client for AI responses
│   │   │   └── types.ts       # Re-exports from @synapse/shared
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── config/                # Shared configuration
│       ├── src/
│       │   ├── env.ts         # Environment variable schema
│       │   └── constants.ts   # App-wide constants
│       ├── tsconfig.json
│       └── package.json
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
├── tsconfig.base.json
└── .github/
    └── workflows/
```

## Package Boundaries

Each package has a clear ownership contract:

| Area | Owner | Responsibility | Boundary |
|------|-------|----------------|----------|
| `packages/config` (`@synapse/config`) | Platform/infra | Shared constants, environment schema, tooling defaults | No app code, UI code, or runtime-specific side effects |
| `packages/shared` (`@synapse/shared`) | Core/domain | Entity types, Zod schemas, pure utilities, domain constants | Platform-agnostic TypeScript only |
| `packages/api-client` (`@synapse/api-client`) | Frontend/data | Typed HTTP/SSE client and API response helpers | Fetch-based, no rendering or app runtime logic |
| `packages/ui` (`@synapse/ui`) | Frontend/ui | Reusable cross-platform primitives, composites, layouts, tokens | Cross-platform abstractions only; no app services or API calls |
| `apps/mobile` | Mobile app | Expo application shell, navigation, storage, device integrations | Mobile/runtime-specific logic is allowed here |
| `apps/api` | Backend | FastAPI service, backend integrations, persistence, AI orchestration | Backend/runtime-specific logic is allowed here |

### Critical Rule: `@synapse/shared` Must Be Platform-Agnostic

This package is consumed by both the frontend (browser + React Native) and the backend (via generated schemas). It must:

- Use only standard TypeScript
- Avoid React, React Native, Expo, DOM/browser APIs, and Node-only APIs
- Export Zod schemas that can be converted to JSON Schema for Python consumption
- Export pure utility functions with no side effects
- Never depend on `@synapse/ui` or `@synapse/api-client`

### Platform-Agnostic Enforcement Strategy

Import boundaries are enforced at package level:

| Location | Allowed | Forbidden |
|----------|---------|-----------|
| `packages/shared` | Types, schemas, constants, pure utilities | `react`, `react-native`, `expo-*`, DOM/browser APIs such as `window` or `document`, Node-only APIs such as `fs`, `path`, or `process` |
| `packages/ui` | Reusable cross-platform UI abstractions, tokens, props-only components | API clients, app routes, Expo device modules, backend code, Node-only APIs |
| `apps/mobile` | Expo, React Native, storage, navigation, device/runtime services | Backend internals and direct imports from `apps/api` |
| `apps/api` | FastAPI, Python services, persistence, AI providers, generated schema artifacts | React/UI/mobile runtime imports |

ESLint will enforce these boundaries with `no-restricted-imports` plus dependency-boundary rules:

- Allowed: `packages/api-client` imports `@synapse/shared`; `apps/mobile` imports `@synapse/ui`, `@synapse/api-client`, and `@synapse/shared`.
- Forbidden: `packages/shared` imports `react-native` or `fs`; `packages/ui` imports `@synapse/api-client`; any package imports from `apps/*`.
- Package manifests must match the boundary graph so undeclared cross-package imports are caught during install, lint, and typecheck.

Slice 1 implements this with a root `eslint.config.js` flat config and package-level `lint` scripts. The initial enforcement uses restricted imports and globals first; heavier dependency graph tooling can be added later only if the lightweight checks miss real violations.

CI fails on boundary violations. The baseline CI contract is:

- `pnpm lint` runs ESLint restricted-import and dependency-boundary checks.
- `pnpm typecheck` validates TypeScript project references and path aliases.
- `pnpm test` runs package/app tests once they exist.
- `pnpm build` verifies package build outputs.
- Pull requests cannot merge if lint, typecheck, tests, build, or boundary checks fail.

Future implementation should keep this lightweight: ESLint restricted imports, TypeScript project references, CI enforcement, and dependency graph constraints are the source of truth. Add custom scripts only if the standard tooling misses a real violation.

## Build Pipeline

### Turborepo Configuration

```jsonc
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {},
    "typecheck": {
      "dependsOn": ["^build"]
    }
  }
}
```

### Build Order (Enforced by `dependsOn: ["^build"]`)

```
config → shared → api-client → mobile
                → ui         → mobile
```

Backend (`apps/api`) is Python and runs outside the Turborepo build graph. It connects to the TypeScript ecosystem through generated JSON Schema files.

## TypeScript ↔ Python Bridge

The backend needs to validate data using the same rules as the frontend. Instead of maintaining duplicate schemas:

1. `@synapse/shared` defines Zod schemas for all entities
2. A build script converts Zod → JSON Schema and writes `.json` files
3. The Python backend loads these JSON Schema files and validates via `jsonschema` or `pydantic`
4. Both sides are guaranteed to validate identically

```
@synapse/shared/src/validation/note.ts  →  Zod schema
                                        ↓  (zod-to-json-schema)
@synapse/shared/dist/schemas/note.json  →  JSON Schema
                                        ↓  (loaded by Python)
apps/api/app/schemas/note.json          →  Pydantic model validation
```

This is the only cross-language bridge. All other communication is via HTTP/SSE.

## Workspace Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

## Dev Workflow

```bash
# Start everything
pnpm dev                    # Turborepo runs all dev tasks in parallel

# Start specific app
pnpm --filter mobile dev    # Expo dev server
pnpm --filter api dev       # Uvicorn with hot reload (via script)

# Test specific package
pnpm --filter shared test

# Typecheck all
pnpm typecheck
```

## Dependency Rules

1. **No circular dependencies** between packages
2. **Packages never import from `apps/`** — only apps import from packages
3. **`@synapse/ui` never imports `@synapse/api-client`** — UI components receive data via props
4. **`@synapse/api-client` never imports `@synapse/ui`** — data layer is independent of rendering
5. **Internal packages use `workspace:*` protocol** — no published versions

## Boundary Enforcement

The implementation details for boundary checks live in the Platform-Agnostic Enforcement Strategy above. Keep enforcement focused on four layers:

| Mechanism | What It Catches | When |
|-----------|----------------|------|
| ESLint restricted imports | Platform leaks and forbidden package imports | Dev time and CI |
| Package manifest discipline | Workspace dependencies that drift from the allowed graph | Install and review time |
| TypeScript project references | Type-level package boundaries and path alias correctness | `pnpm typecheck` |
| CI lint/typecheck/test/build jobs | Any committed violation of the baseline contract | Every PR |


## Tradeoffs

| Decision | Upside | Downside |
|----------|--------|----------|
| Turborepo over Nx | Simpler config, faster adoption | Less built-in code generation |
| pnpm over yarn | Strict dependency resolution, disk efficient | Slightly less ecosystem familiarity |
| Zod → JSON Schema bridge | Single source of truth for validation | Extra build step, potential schema drift |
| Separate Python backend | Full Python AI ecosystem access | Two runtimes to manage |
| React Native Web over separate web app | Code sharing maximized | Some web-specific patterns harder to implement |
