# @synapse/shared

Platform-agnostic types, validation schemas, constants, and pure utilities for Synapse.

## JSON Schema Export

`@synapse/shared` is the source of truth for API/wire contracts. Its Zod
schemas can be exported to backend-consumable JSON Schema artifacts:

```bash
pnpm --filter @synapse/shared build
```

The build writes deterministic artifacts to `packages/shared/dist/schemas/`:

- `manifest.json` lists every exported contract, stable `$id`, and file path.
- `<group>/<name>.schema.json` contains draft-07 JSON Schema for each contract.

The export includes Notes CRUD contracts such as create/update/delete request
schemas and list/get/create/update/delete response envelopes. Backend routes and
API client note methods are intentionally implemented in later slices.

Use the check command before wiring backend validation to ensure the registry and
generated artifacts are aligned:

```bash
pnpm --filter @synapse/shared check-schemas
pnpm --filter @synapse/shared contracts:check
```

Generated schema files are build artifacts. Do not edit them by hand.
