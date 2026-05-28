# Synapse API

FastAPI backend for the Synapse service.

## Baseline Routes

The API is mounted under `/v1`.

- `GET /v1/health` returns the service health payload.
- `GET /v1/version` returns service, app, and API version metadata.
- `GET /v1/notes` lists non-deleted notes from the configured Notes repository.
- `POST /v1/notes` creates a note in the configured Notes repository.
- `GET /v1/notes/{note_id}` returns one non-deleted note.
- `PATCH /v1/notes/{note_id}` updates a note when the request `version` matches.
- `DELETE /v1/notes/{note_id}` soft deletes a note when the request `version`
  matches.

All routes use the shared success envelope shape:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_abc123"
  }
}
```

Errors use the shared error envelope shape and include the same `request_id` in
`meta.request_id`. The request id is also returned as the `X-Request-ID` header.

The Notes routes now use a narrow auth context dependency and repository
interface. Local and test runs default to `SYNAPSE_AUTH_MODE=dev` and
`SYNAPSE_NOTES_REPOSITORY=memory`, which still uses the safe `dev_user` identity
and process-local storage. Dev auth is deterministic and local/test-only; do not
use it in production. That default keeps CI deterministic and requires no
Supabase project or secrets.

Slice 6E adds a Supabase-ready repository scaffold. Notes/RLS persistence intent
is maintained as sanitized architecture documentation only; no executable
Supabase migration is currently committed. Live Supabase client wiring remains
deferred; request-path code does not use the service role key.

Slice 6G hardens auth mode handling. Supported modes are `dev` and `jwt`.
Unknown modes fail closed with `401 UNAUTHORIZED`; `jwt` mode requires a Bearer
header shape and rejects missing or malformed headers.

Slice 6H-1 adds an injected JWT verifier interface and a configured RS256
`PyJWT[crypto]` adapter. In `jwt` mode it verifies signature, expiry, issuer,
audience, authenticated role, and UUID `sub`, which becomes
`AuthContext.user_id`; invalid or unconfigured requests return `401
UNAUTHORIZED`. Tests generate local RSA keys at runtime and make no Supabase
network calls. Live Supabase JWKS discovery and the user-scoped repository
client remain deferred.

Slice 6H-2 adds a user-scoped Supabase client factory boundary. It accepts only
a JWT `AuthContext` with a verified caller access token, selects a publishable
public Data API key (or legacy anon fallback), and returns an inert redacted
descriptor for a future SDK adapter. It performs no network calls and does not
use service-role credentials. Retained bearer values are represented as
redacted secrets in auth/client objects. Notes still run against memory by
default; live Supabase repository wiring remains deferred.

Slice 6H-3A adds deterministic fake-client coverage for the scaffolded
Supabase Notes repository. Tests assert explicit user scoping, version-gated
updates and soft deletes, conflict lookup behavior, service-role avoidance, and
no-network execution. The tests do not construct an SDK client or validate
RLS; memory persistence remains the default.

Slice 6H-6 adds a deterministic Notes contract drift guard. Backend tests read
the JSON Schema artifacts exported from `@synapse/shared` and compare stable
Notes fields, effectively required request fields, response envelope shape,
version requirements, and validation/conflict status behavior with the
existing Pydantic and route surface. The guard is deliberately not generated
Python code or runtime JSON Schema validation.

Slice 6H-3B-3A adds a skipped-by-default Supabase live/local harness skeleton
under `tests/integration/`. The skeleton defines pytest markers and fail-closed
configuration guards only. It does not import the Supabase SDK, connect to
Supabase, execute migrations or RLS tests, enable live Notes persistence, or
require credentials in normal CI.

Slice 6H-3B-3B adds a documentation-only local Supabase setup guide for that
future harness. The guide keeps local setup placeholder-only, prohibits
committed `.env` files, generated Supabase state, SQL/migrations, service-role
keys, and real tokens, and records approved migration/RLS validation planning
as the blocker before local RLS coverage can be claimed.

## Configuration

Supported local placeholders:

```bash
SYNAPSE_AUTH_MODE=dev
SYNAPSE_NOTES_REPOSITORY=memory
SYNAPSE_DEV_USER_ID=dev_user
SYNAPSE_JWT_ISSUER=https://issuer.example.invalid/auth/v1
SYNAPSE_JWT_AUDIENCE=authenticated
SYNAPSE_JWT_PUBLIC_KEY=replace-with-rs256-public-key-pem
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=replace-with-supabase-publishable-key
SUPABASE_ANON_KEY=replace-with-supabase-anon-key
SUPABASE_JWT_SECRET=replace-with-legacy-jwt-secret
SUPABASE_SERVICE_ROLE_KEY=replace-with-service-role-key
```

Use `.env` for real local values; it is gitignored. Commit only `.env.example`
placeholders. The `SYNAPSE_JWT_*` values are optional in default `dev` mode and
must all be configured before `jwt` mode will accept an RS256 token.
`SUPABASE_PUBLISHABLE_KEY` is preferred for the deferred user-scoped data path;
`SUPABASE_ANON_KEY` is a legacy public-key fallback only.

Optional live/local harness placeholders are documented in
`docs/notes-supabase-live-test-harness-plan.md` and the local-only setup posture
is documented in `docs/notes-local-supabase-setup-guide.md`. The harness is
skipped unless `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` and
`SYNAPSE_SUPABASE_TEST_MODE` is `local` or `staging`. Even then, the current
skeleton contains no live adapter or approved RLS validation and remains
placeholder-only. Request-path harness tests must not use
`SUPABASE_SERVICE_ROLE_KEY`.

## Local Checks

Export shared contracts from the repository root before running API tests:

```bash
pnpm --filter @synapse/shared contracts:export
```

Then, from this directory:

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
```

## Contract Bridge

Backend validation should consume JSON Schema artifacts generated by
`@synapse/shared`, not duplicate Zod rules by hand.

Generate the artifacts from the repository root:

```bash
pnpm --filter @synapse/shared build
```

The generated files live under `packages/shared/dist/schemas/`. Future FastAPI
routes should load schemas by the stable entries in `manifest.json` and use them
for request/response validation before business endpoint logic is added.

`tests/test_contract_drift.py` currently consumes the generated Notes artifacts
only during verification. It checks field names and effective required/optional
status, treating Zod fields with defaults as omittable inputs. Shared optional
`sync_metadata` and response metadata `pagination` are documented extensions
not emitted by the current Notes routes. Exact type/format equivalence and
runtime JSON Schema validation are deferred.

No secrets, environment values, Supabase clients, auth providers, or AI providers
belong in this bridge.
