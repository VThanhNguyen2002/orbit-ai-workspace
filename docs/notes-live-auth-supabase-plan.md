# Notes Live Auth And Supabase Plan

## Status

Slice 6H is planning/design only. It does not add a JWT library, live Supabase
client wiring, migration execution, credentials, frontend UI, sync engine, or AI
integration.

## Objective

Define a safe, ordered path from the Slice 6E/6G Notes boundaries to live
Supabase Auth and RLS-backed Notes persistence. The path must preserve
deterministic local/test/CI behavior until live integration is deliberately
enabled and validated.

## Non-Goals

- No runtime code, dependencies, Supabase client, or JWT verifier is added in
  this slice.
- No database migration is executed or treated as production-ready.
- No real key, token, password, URL, or `.env` file is added.
- No frontend auth, Expo, offline sync, AI, Storage, Realtime, or background
  cleanup implementation is added.

## Current Baseline

- Notes CRUD contracts exist in `@synapse/shared`.
- FastAPI Notes routes exist under `/v1/notes`.
- `@synapse/api-client` exposes typed Notes methods.
- `apps/api/app/core/auth.py` has explicit `dev` and `jwt` modes.
- `dev` mode returns a deterministic local/test `AuthContext`.
- `jwt` mode validates only the `Authorization: Bearer <token>` shape and then
  fails closed.
- Unknown auth modes fail closed with `401 UNAUTHORIZED`.
- The memory Notes repository remains the default.
- `apps/api/app/repositories/notes_supabase.py` is scaffold-only and requires an
  injected user-scoped client before use.
- `supabase/migrations/20260522000000_create_notes.sql` is a draft and is not
  executed in CI.
- FastAPI still uses Pydantic models directly; generated shared JSON Schemas are
  not consumed by the backend yet.

## Architectural Decisions

1. Keep `dev` and `jwt` as the only API auth modes.
2. Keep `dev` local/test-only and deterministic.
3. Keep `jwt` fail-closed until a real verifier is wired.
4. Add a dedicated JWT verifier boundary before adding any Supabase request-path
   code.
5. Verify tokens locally using asymmetric Supabase Auth signing keys exposed by
   JWKS as the production default; do not make per-request user lookup the normal
   validation path.
6. Keep legacy HS256 verification with `SUPABASE_JWT_SECRET` as an explicit
   mode for legacy projects only.
7. Prefer Supabase publishable API keys for future Data API clients; allow the
   existing legacy `SUPABASE_ANON_KEY` configuration only as a compatibility
   path.
8. Pass the verified caller access token to a request-scoped Supabase client so
   Supabase Postgres RLS evaluates the same user identity as the API.
9. Keep explicit `user_id` filters in application queries even when RLS is active.
10. Never use `SUPABASE_SERVICE_ROLE_KEY` in normal request-path code.

## JWT Verification Strategy

### Decision

Implement `Slice 6H-1 - JWT verifier interface and tests` before live
persistence wiring. Its production adapter should use `PyJWT[crypto]` to verify
Supabase-issued tokens against an asymmetric JWKS endpoint. Supabase documents
asymmetric signing keys/JWKS verification as the modern local-verification path;
shared-secret verification remains a legacy compatibility mode.

### Verifier Shape

Introduce a small verifier protocol such as:

```python
class JwtVerifier(Protocol):
    def verify(self, token: str) -> VerifiedJwt: ...


class VerifiedJwt(BaseModel):
    user_id: str
    claims: dict[str, Any]
```

`get_auth_context` should keep parsing the Bearer header, then delegate only the
token string to the verifier. The dependency should return:

```python
AuthContext(
    user_id=verified.user_id,
    auth_mode="jwt",
    access_token=token,
)
```

The raw token is retained only long enough to create the caller-scoped Supabase
request client; it must never appear in logs or error bodies.

### JWKS Mode

Use `PyJWT[crypto]` with a bounded in-process JWKS cache:

- Derive the issuer from `SUPABASE_URL` unless overridden:
  `https://<project-ref>.supabase.co/auth/v1`.
- Derive the JWKS URL unless overridden:
  `https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`.
- Verify signature, `exp`, issuer, audience, a configured asymmetric algorithm
  allowlist, and `sub`.
- Require `sub` to be a non-empty UUID string.
- Require audience `authenticated` unless explicitly configured otherwise.
- Require an authenticated user role for Notes access unless a later product
  decision deliberately allows Supabase anonymous users.
- Cache JWKS with a bounded TTL aligned with Supabase's public-key discovery
  caching guidance.
- Refresh JWKS on an unknown `kid` before rejecting.
- Return only coarse `401 UNAUTHORIZED` responses to clients.
- Log only request id and failure category, never token contents or user email.

### Legacy HS256 Mode

Support HS256 only in an explicitly selected legacy deployment mode:

- Require `SUPABASE_JWT_SECRET`.
- Keep HS256 in a mode-specific algorithm allowlist and do not select an
  algorithm based on an unverified token header.
- Do not silently fall back from JWKS mode to a shared secret.
- Do not accept unsigned JWTs or tokens with `alg=none`.

### Tests

Deterministic unit tests should use generated local keys and fake claims, not
live Supabase:

- missing Authorization -> `401`
- malformed Authorization -> `401`
- unsupported auth mode -> `401`
- expired JWT -> `401`
- wrong issuer -> `401`
- wrong audience -> `401`
- missing `sub` -> `401`
- invalid signature -> `401`
- valid local test JWT -> `AuthContext(user_id=<sub>, auth_mode="jwt")`
- fake placeholder token -> `401`

## User-Scoped Supabase Client Strategy

Add a request-scoped Supabase client factory after JWT verification exists:

```python
def get_supabase_user_client(
    auth_context: AuthContext,
    settings: Settings,
) -> SupabaseClient:
    ...
```

Rules:

- Construct the client with `SUPABASE_URL` and a public Data API key:
  `SUPABASE_PUBLISHABLE_KEY` is preferred for future live deployment;
  `SUPABASE_ANON_KEY` is retained only for legacy compatibility.
- Attach the verified caller access token as the authorization token used by
  PostgREST.
- Do not mutate a global Supabase client with per-request credentials.
- Do not use service-role credentials in the request path.
- Keep the memory repository as the default unless
  `SYNAPSE_NOTES_REPOSITORY=supabase`.
- Keep repository protocol methods requiring `user_id`.
- Keep every Supabase query scoped by `user_id` for defense in depth.
- Map Supabase empty-row responses to `NoteNotFoundError`.
- Map version conditional-write misses to `NoteVersionConflictError` only after
  fetching current non-deleted server data for the same user.

The future implementation should validate the exact `supabase-py` API for
injecting the caller token before coding. The repository should keep depending on
a minimal query-builder protocol where possible so tests can remain fake-client
based.

## RLS Validation Strategy

RLS must be verified as defense in depth, not treated as the only protection.

Required validation cases:

- user A can insert, list, get, update, and soft-delete own notes.
- user A cannot select user B notes.
- user A cannot update or soft-delete user B notes.
- insert with mismatched `user_id` is rejected by RLS.
- default list hides soft-deleted notes.
- `include_deleted=true` only returns the caller's deleted notes.
- API still returns `404 NOT_FOUND` for missing/deleted/cross-user notes.
- stale update/delete returns `409 CONFLICT` with full `server_data`.
- physical SQL `DELETE` is not used by Notes request handlers.

Test levels:

- Required CI: unit tests with memory repository and fake verifier/client.
- Optional CI: local Supabase integration tests gated behind an explicit flag.
- Manual/staging: run the migration and RLS tests against a real Supabase
  project before enabling production traffic.

## Migration Execution Plan

The current migration is a draft. Before execution:

1. Confirm a `public.users` table exists and is populated from `auth.users`.
2. Add or verify the trigger/function that creates `public.users` rows from
   Supabase Auth users.
3. Run the Notes migration in a local Supabase stack.
4. Verify indexes and `notes_set_updated_at` trigger behavior.
5. Verify RLS policies with two real Supabase users.
6. Run application-level Notes CRUD smoke tests.
7. Apply to staging.
8. Promote to production only after rollback and cleanup plans are documented.

The migration is not executed in default CI. Optional migration validation can be
added later with Supabase CLI and an explicit integration-test environment.

## Env And Config Plan

Currently implemented settings remain safe because the live path is unwired:

- `SYNAPSE_AUTH_MODE=dev`
- `SYNAPSE_NOTES_REPOSITORY=memory`
- `SYNAPSE_DEV_USER_ID=dev_user`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_SERVICE_ROLE_KEY` (present in settings only; prohibited from the
  Notes request path)

Planned live auth/persistence configuration, to be added only in later
implementation slices:

- `SYNAPSE_AUTH_MODE=jwt`
- `SYNAPSE_JWT_VERIFIER_MODE=jwks` for the recommended deployment or
  `legacy_hs256` only for an identified legacy project
- `SYNAPSE_NOTES_REPOSITORY=supabase`
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY` for the recommended deployment, or the currently
  modeled `SUPABASE_ANON_KEY` only for a legacy-compatible deployment
- `SUPABASE_JWT_AUDIENCE=authenticated`
- `SUPABASE_JWT_ISSUER=https://<project-ref>.supabase.co/auth/v1`
- `SUPABASE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`
- `SUPABASE_JWT_SECRET` only when `SYNAPSE_JWT_VERIFIER_MODE=legacy_hs256`

`SUPABASE_SERVICE_ROLE_KEY` may exist for migration/admin tooling, but the API
request path must not read or inject it into a user request client.

Current `.env.example` is not expanded in this planning slice because the new
configuration is not yet read by runtime code. When implemented, it must contain
placeholders only; files containing real `.env` values remain gitignored.

## Deterministic CI And Test Strategy

Default CI must remain independent of live Supabase:

- `SYNAPSE_AUTH_MODE=dev`
- `SYNAPSE_NOTES_REPOSITORY=memory`
- fake JWT verifier tests use local generated keys
- fake Supabase repository/client tests use deterministic in-memory responses
- no live network calls
- no required Supabase environment variables
- no migration execution

Optional integration tests should require all of:

- `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1`
- a local Supabase URL or disposable staging project URL
- test-only public Data API credentials from environment
- setup/teardown instructions that do not print secrets

## Security Risks And Controls

| Risk | Control |
|------|---------|
| Fake JWT accepted | Keep `jwt` fail-closed until verifier exists; reject invalid signatures and `alg=none`. |
| Token leakage | Never log token values, refresh tokens, email, note title, or note content. |
| Service-role misuse | Do not import or inject service-role credentials into request-path dependencies. |
| RLS bypass via API bug | Keep explicit `user_id` filters in every query. |
| RLS policy drift | Add user A/user B RLS tests before live enablement. |
| Key rotation outage | Prefer JWKS/asymmetric keys and refresh cache on unknown `kid`. |
| Legacy secret exposure | Use `SUPABASE_JWT_SECRET` only for legacy HS256 verification; never commit it. |
| CI flakiness | Keep default tests fake/local; gate live Supabase tests. |

## Future Implementation Slices

1. **Slice 6H-1 - JWT verifier interface and tests (recommended next)**
   Add the injected verifier boundary, selected JWT dependency/config parsing,
   JWKS-mode and explicit legacy-mode adapters, local-key unit tests, and
   route-level JWT success/failure tests. Do not wire Supabase persistence yet.
2. **Slice 6H-2 - User-scoped Supabase client factory**
   Add request-scoped client construction with caller token and fake-client tests.
   Keep memory repository default.
3. **Slice 6H-3 - Supabase Notes repository wiring**
   Wire the scaffold behind config, preserve memory default, and verify
   repository semantics with mocked Supabase responses.
4. **Slice 6H-4 - Local/staging migration and RLS validation**
   Add gated integration tests and migration validation. Default CI remains
   deterministic without Supabase.
5. **Slice 6H-5 - Controlled live rollout**
   Execute migration in staging, validate RLS, verify Notes CRUD with real users,
   then document production rollout steps.
6. **Slice 6H-6 - Contract drift guard between Zod JSON Schema and Pydantic**
   Complete the backend schema-consumption/drift guard independently of live
   authentication. It is important, but it does not unblock authenticated RLS
   evaluation and therefore is not the next task.

## Definition Of Done

Slice 6H planning is done when this document records the verifier, client,
migration, RLS, configuration, testing, and risk decisions; related architecture
docs no longer prescribe HS256 as the default; and the next task is
`Slice 6H-1`.

Later live enablement is done only when:

- `SYNAPSE_AUTH_MODE=jwt` accepts only cryptographically verified Supabase access
  tokens.
- Missing, malformed, expired, wrong-audience, wrong-issuer, missing-`sub`, and
  invalid-signature tokens return `401`.
- `AuthContext.user_id` comes only from verified `sub`.
- `AuthContext.access_token` is available only for request-scoped Supabase client
  construction.
- Supabase request-path clients use a publishable key (or documented legacy
  anon key) plus the caller token.
- Service-role key is absent from request-path code.
- Notes queries still include explicit `user_id` filters.
- RLS integration tests prove user A cannot read or mutate user B notes.
- Default CI passes without Supabase network or credentials.
- Optional integration tests can be enabled explicitly and do not print secrets.
- No real credentials are committed.

## References

- Supabase JWT verification and JWKS:
  https://supabase.com/docs/guides/auth/jwts
- Supabase JWT signing keys:
  https://supabase.com/docs/guides/auth/signing-keys
- Supabase Python verified claims:
  https://supabase.com/docs/reference/python/auth-getclaims
- Supabase RLS:
  https://supabase.com/docs/guides/database/postgres/row-level-security
