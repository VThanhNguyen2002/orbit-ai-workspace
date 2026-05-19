# ADR-001: Monorepo with Turborepo + pnpm

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

Synapse has a React Native frontend (web + mobile), a FastAPI backend, and shared TypeScript packages. Code sharing between apps is a core architecture requirement — types, validation, and business logic must be defined once and consumed everywhere.

We need a monorepo tool to manage the workspace, orchestrate builds, and enforce package boundaries.

## Decision

Use **Turborepo** as the monorepo orchestrator and **pnpm** as the package manager.

## Rationale

### Why Turborepo

- **Remote caching** — skips unchanged builds (significant for CI)
- **Minimal configuration** — single `turbo.json` vs Nx's project.json per package
- **Task graph aware** — `dependsOn: ["^build"]` ensures correct build order
- **No lock-in** — standard npm workspaces under the hood, Turborepo is optional orchestration

### Why pnpm over yarn or npm

- **Strict dependency resolution** — packages can only import declared dependencies (no phantom deps)
- **Disk efficient** — content-addressable store deduplicates packages globally
- **`workspace:*` protocol** — internal packages always resolve to local versions without publishing
- **Speed** — consistently fastest package manager in benchmarks

### Why not Nx

- Nx requires more configuration (project.json per package, plugins, generators)
- Synapse has 4–6 packages — Nx's power is overkill and adds cognitive overhead
- Turborepo's simpler model is sufficient for this scale
- Nx's code generation is not needed (we scaffold manually)

## Consequences

### Positive
- Single `pnpm install` sets up the entire workspace
- `turbo run build` parallelizes builds respecting dependency order
- Adding a new package requires only a directory + `package.json`
- CI benefits from Turborepo's cache (unchanged packages skip entirely)

### Negative
- Python backend lives outside the Turborepo build graph (requires separate tooling)
- TypeScript ↔ Python bridge (Zod → JSON Schema) is an extra build step
- Turborepo doesn't manage Python dependencies (uses pyproject.toml + pip/uv separately)

### Mitigations
- Python backend has its own `Makefile` / scripts for development
- Root `package.json` scripts orchestrate both ecosystems: `pnpm dev` starts Turborepo + uvicorn
- The Zod → JSON Schema step is a Turborepo task (`generate-schemas`) that runs before the Python API starts

## Implementation Notes

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```jsonc
// turbo.json
{
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "dev": { "cache": false, "persistent": true },
    "test": { "dependsOn": ["build"] },
    "lint": {},
    "typecheck": { "dependsOn": ["^build"] },
    "generate-schemas": { "dependsOn": ["^build"], "outputs": ["dist/schemas/**"] }
  }
}
```
