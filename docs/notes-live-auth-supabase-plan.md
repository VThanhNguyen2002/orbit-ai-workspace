# Notes Live Auth And Supabase Plan

## Status

Slice 6H-3 records the future Supabase Notes repository implementation path in
[notes-supabase-repository-implementation-plan.md](notes-supabase-repository-implementation-plan.md).
Slice 6H-2 adds a user-scoped Supabase client factory boundary represented by
an inert, redacted descriptor, and Slice 6H-1 added the API JWT verifier
boundary and deterministic local-key tests. None of these slices adds live
Supabase SDK transport, JWKS discovery, migration execution, credentials,
frontend UI, sync engine, or AI integration. A prior security patch removed
the executable Notes SQL draft; no executable Supabase migration is currently
committed.

## Objective

Define a safe, ordered path from the Slice 6E/6G Notes boundaries to live
Supabase Auth and RLS-backed Notes persistence. The path must preserve
deterministic local/test/CI behavior until live integration is deliberately
enabled and validated.

## Non-Goals

- No live Supabase SDK client or transport, network-backed JWKS retrieval, or
  legacy shared-secret JWT adapter is added in this slice.
- No executable database migration is committed, executed, or treated as
  production-ready without explicit approval and security review.
- No real key, token, password, URL, or `.env` file is added.
- No frontend auth, Expo, offline sync, AI, Storage, Realtime, or background
  cleanup implementation is added.

## Current Baseline

- Notes CRUD contracts exist in `@synapse/shared`.
- FastAPI Notes routes exist under `/v1/notes`.
- `@synapse/api-client` exposes typed Notes methods.
- `apps/api/app/core/auth.py` has explicit `dev` and `jwt` modes.
- `dev` mode returns a deterministic local/test `AuthContext`.
- `jwt` mode delegates bearer tokens to an injected verifier. The implemented
  RS256 adapter requires configured issuer, audience, and public key values and
  verifies signature, expiry, UUID `sub`, and authenticated role.
- If JWT verifier configuration is absent or token verification fails, `jwt`
  mode fails closed with `401 UNAUTHORIZED`.
- `apps/api/app/core/supabase_client.py` accepts verified JWT auth context and
  returns only redacted request-scoped client inputs; it creates no live client.
- Unknown auth modes fail closed with `401 UNAUTHORIZED`.
- The memory Notes repository remains the default.
- `apps/api/app/repositories/notes_supabase.py` is scaffold-only, recognizes a
  publishable or legacy anon public key, and still requires an injected
  user-scoped client before use.
- Notes table and RLS intent now exist only as sanitized architecture
  documentation; no executable Supabase migration is tracked.
- FastAPI still uses Pydantic models directly; generated shared JSON Schemas are
  not consumed by the backend yet.

## Architectural Decisions

1. Keep `dev` and `jwt` as the only API auth modes.
2. Keep `dev` local/test-only and deterministic.
3. Keep `jwt` fail-closed unless a configured verifier successfully verifies the
   bearer token.
4. Use the dedicated JWT verifier boundary before adding any Supabase
   request-path code.
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
11. Keep the Slice 6H-2 factory inert until a reviewed SDK adapter and
    repository integration are deliberately implemented.

## JWT Verification Strategy

### Decision

Slice 6H-1 implements `JwtVerifier` and `VerifiedJwtClaims`, plus a
`PyJWT[crypto]` RS256 adapter configured with `SYNAPSE_JWT_PUBLIC_KEY`,
`SYNAPSE_JWT_ISSUER`, and `SYNAPSE_JWT_AUDIENCE`. This provides a real
verification boundary without a network dependency. Live Supabase deployments
still require a later JWKS adapter; shared-secret verification remains a
deferred legacy compatibility option only.

### Verifier Shape

Introduce a small verifier protocol such as:

```python
class JwtVerifier(Protocol):
    def verify(self, token: str) -> VerifiedJwtClaims: ...


class VerifiedJwtClaims(BaseModel):
    sub: str
    role: Literal["authenticated"]
```

`get_auth_context` should keep parsing the Bearer header, then delegate only the
token string to the verifier. The dependency should return:

```python
AuthContext(
    user_id=verified.sub,
    auth_mode="jwt",
    access_token=token,
)
```

The raw token is retained only long enough to create the caller-scoped Supabase
request client; it must never appear in logs or error bodies.

### Implemented Configured RS256 Mode

`PyJwtRsaVerifier` uses an explicit `RS256` allowlist and a configured public
key. It validates signature, `exp`, issuer, audience, UUID `sub`, and
`role="authenticated"`. It rejects unsigned tokens, invalid signatures, and
all invalid claims with a coarse `401 UNAUTHORIZED` response. It does not log
or return token values.

### Deferred JWKS Mode

For live Supabase integration, extend the verifier boundary with
`PyJWT[crypto]` and a bounded in-process JWKS cache:

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

### Deferred Legacy HS256 Mode

If an identified legacy deployment later requires HS256, support it only in an
explicitly selected compatibility mode:

- Require `SUPABASE_JWT_SECRET`.
- Keep HS256 in a mode-specific algorithm allowlist and do not select an
  algorithm based on an unverified token header.
- Do not silently fall back from JWKS mode to a shared secret.
- Do not accept unsigned JWTs or tokens with `alg=none`.

### Tests

Implemented tests generate ephemeral local RSA keys and fake claims, not live
Supabase:

- missing Authorization -> `401`
- malformed Authorization -> `401`
- unsupported auth mode -> `401`
- expired JWT -> `401`
- wrong issuer -> `401`
- wrong audience -> `401`
- missing `sub` -> `401`
- malformed UUID `sub` -> `401`
- invalid signature -> `401`
- unsupported role and unsigned token -> `401`
- valid local test JWT -> `AuthContext(user_id=<sub>, auth_mode="jwt")`
- fake placeholder token -> `401`

## User-Scoped Supabase Client Strategy

Slice 6H-2 adds this request-scoped factory boundary after JWT verification:

```python
def get_supabase_user_client(
    auth_context: AuthContext,
    settings: Settings,
) -> UserScopedSupabaseClientDescriptor:
    ...
```

Implemented behavior:

- Reject `dev` auth contexts and JWT contexts without an access token.
- Require `SUPABASE_URL` and a public Data API key;
  `SUPABASE_PUBLISHABLE_KEY` is preferred and `SUPABASE_ANON_KEY` is a legacy
  fallback.
- Store retained auth-context tokens and descriptor token/public-key inputs as
  redacted `SecretStr` values for a future SDK adapter.
- Never select `SUPABASE_SERVICE_ROLE_KEY`.
- Build no live Supabase SDK object and make no network request.

Deferred adapter/repository rules:

- Attach the verified caller access token as the authorization token used by
  PostgREST when the live adapter is explicitly implemented.
- Do not mutate a global Supabase client with per-request credentials.
- Do not use service-role credentials in the request path.
- Keep the memory repository as the default unless
  `SYNAPSE_NOTES_REPOSITORY=supabase`.
- Keep repository protocol methods requiring `user_id`.
- Keep every Supabase query scoped by `user_id` for defense in depth.
- Map Supabase empty-row responses to `NoteNotFoundError`.
- Map version conditional-write misses to `NoteVersionConflictError` only after
  fetching current non-deleted server data for the same user.

The future adapter implementation should validate the exact `supabase-py` API
for injecting the caller token before coding. The repository should keep
depending on a minimal query-builder protocol where possible so tests remain
fake-client based.

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
- Manual/staging: after a future migration is explicitly approved and reviewed,
  validate its RLS outcomes against an approved non-production Supabase
  environment before enabling production traffic.

## Future Migration Approval And Execution Plan

There is no committed executable migration. The Notes table/RLS descriptions in
these documents are non-deployable architecture summaries. Before a future
migration may be created, committed, or executed:

1. Obtain explicit approval to introduce a minimal, environment-independent
   migration under the database migration policy.
2. Security-review the proposed artifact before commit; it must contain no
   credentials, real data, dumps, or environment-specific identifiers.
3. Confirm any required user identity/table dependency in an approved
   non-production environment.
4. Validate indexes, timestamp/version behavior, and RLS outcomes with synthetic
   users only after the migration artifact is approved.
5. Run application-level Notes CRUD smoke tests in that approved environment.
6. Apply to staging and production only under separately reviewed rollout and
   rollback instructions.

Default CI does not run database migrations. See
[database-migration-policy.md](security/database-migration-policy.md) for the
artifact and approval gate.

## Env And Config Plan

Currently implemented settings remain safe because the live path is unwired:

- `SYNAPSE_AUTH_MODE=dev`
- `SYNAPSE_NOTES_REPOSITORY=memory`
- `SYNAPSE_DEV_USER_ID=dev_user`
- `SYNAPSE_JWT_ISSUER`
- `SYNAPSE_JWT_AUDIENCE`
- `SYNAPSE_JWT_PUBLIC_KEY` (RS256 verification key; optional in default mode)
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY` (preferred public Data API key)
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
- `SYNAPSE_JWT_AUDIENCE=authenticated`
- `SYNAPSE_JWT_ISSUER=https://<project-ref>.supabase.co/auth/v1`
- `SYNAPSE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`
- `SUPABASE_JWT_SECRET` only when `SYNAPSE_JWT_VERIFIER_MODE=legacy_hs256`

`SUPABASE_SERVICE_ROLE_KEY` may exist for migration/admin tooling, but the API
request path must not read or inject it into a user request client.

`.env.example` contains placeholders for the configured local RS256 verifier and
public Data API key selection only. Files containing real environment values
remain gitignored, and no test or runtime credential is committed.

## Deterministic CI And Test Strategy

Default CI must remain independent of live Supabase:

- `SYNAPSE_AUTH_MODE=dev`
- `SYNAPSE_NOTES_REPOSITORY=memory`
- JWT verifier tests generate local RSA keys in test fixtures
- client-factory tests build redacted descriptors and block network construction
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
| Fake JWT accepted | `jwt` requires successful RS256 verification; tests reject invalid signatures and `alg=none`. |
| Token leakage | Never log token values, refresh tokens, email, note title, or note content. |
| Service-role misuse | Do not import or inject service-role credentials into request-path dependencies. |
| Accidental token rendering | Store retained auth and descriptor key/token values as `SecretStr` and test redacted `repr`/`str`. |
| RLS bypass via API bug | Keep explicit `user_id` filters in every query. |
| RLS policy drift | Add user A/user B RLS tests before live enablement. |
| Premature operational schema artifact | Ignore Supabase migration SQL and require explicit security review before any exception. |
| Key rotation outage | Configured-key mode is not suitable for live rotation; add JWKS caching/refresh before live Supabase auth. |
| Legacy secret exposure | Use `SUPABASE_JWT_SECRET` only for legacy HS256 verification; never commit it. |
| CI flakiness | Keep default tests fake/local; gate live Supabase tests. |

## Future Implementation Slices

1. **Slice 6H-1 - JWT verifier interface and tests (completed)**
   The injected boundary, configured RS256 adapter, placeholder configuration,
   generated-local-key tests, and route-level success/failure coverage exist.
   JWKS and legacy shared-secret adapters remain intentionally deferred.
2. **Slice 6H-2 - User-scoped Supabase client factory (completed)**
   The inert redacted descriptor factory accepts verified JWT context, prefers a
   publishable public key, rejects service-role-only configuration, and makes no
   network call. Memory remains the default.
3. **Slice 6H-3 - Supabase repository live implementation planning (completed)**
   The repository implementation plan records future adapter injection, CRUD
   mapping, RLS expectations, security controls, and the approval gate without
   adding live code or migrations.
4. **Slice 6H-3A - Supabase repository fake-client tests (completed)**
   Deterministic injected fakes verify scaffold query shaping, explicit owner
   scoping, conflict classification, and soft-delete behavior without network
   access.
5. **Slice 6H-6 - Contract drift guard between Zod JSON Schema and Pydantic (recommended next)**
   Fake repository response rows are validated through backend Pydantic models,
   while shared Zod schemas remain separately generated. Add the drift guard
   before introducing live transport.
6. **Slice 6H-3B - Live SDK adapter behind feature flag**
   After review, add the caller-scoped transport gated off by default.
7. **Slice 6H-3C - Approved migration and RLS validation**
   Only after explicit security approval, introduce and validate the minimum
   reviewed schema/RLS artifact.
8. **Slice 6H-3D - Opt-in live integration tests**
   Add non-production/local integration coverage only after adapter and RLS
   approval, disabled by default.

## Definition Of Done

Slice 6H-3 is complete when the new repository implementation plan specifies
caller-scoped injection, CRUD/conflict/delete semantics, RLS expectations,
security controls, and staged test/live work without adding runtime transport
or a database artifact. No executable database migration is part of this
planning slice.

Later live enablement is done only when:

- a network-backed Supabase JWKS verifier is added and reviewed for key rotation;
- `SYNAPSE_AUTH_MODE=jwt` accepts only cryptographically verified Supabase access
  tokens in live configuration;
- Missing, malformed, expired, wrong-audience, wrong-issuer, missing-`sub`, and
  invalid-signature tokens return `401`.
- `AuthContext.user_id` comes only from verified `sub`.
- `AuthContext.access_token` is available only for request-scoped Supabase client
  construction; the implemented descriptor is not yet an SDK transport.
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
