# Notes Supabase Repository Implementation Plan

## Status

Slice 6H-3 defines the bounded path from the existing Supabase-shaped Notes
repository scaffold and inert user-scoped client descriptor to a future
reviewed implementation. Slice 6H-3A adds deterministic fake-client tests for
the scaffold's query shaping, owner scoping, version conflict, and soft-delete
behavior. Slice 6H-6 adds a lightweight contract drift guard between exported
shared Notes JSON Schemas and backend expectations. Slice 6H-3B records the
future live adapter contract in
[notes-supabase-live-adapter-plan.md](notes-supabase-live-adapter-plan.md).
Slice 6H-3B-1 adds the implementation-neutral adapter protocol boundary and
fake-adapter proof. Slice 6H-3B-2 adds deterministic fake SDK transport tests
for caller authorization metadata, public-key metadata, request isolation,
redaction, and no session/refresh calls. None of these slices adds an SDK
client, live network transport, executable migration, RLS execution, or live
test.

## Objective

Plan a future live Supabase Notes repository implementation that preserves the
existing `NotesRepository` contract, uses the verified caller identity and
access token for request-scoped Data API access, keeps application-level
`user_id` filtering, and relies on RLS as an additional isolation boundary once
an approved schema exists.

## Non-Goals

- Do not add or instantiate a Supabase SDK client.
- Do not connect to Supabase or require live configuration in default CI.
- Do not add SQL, migrations, database artifacts, or execute RLS validation.
- Do not add service-role use to any request-handling path.
- Do not add credentials, `.env` files, frontend/UI/Expo work, AI behavior, or
  offline sync behavior.
- Do not broadly refactor Notes CRUD, route envelopes, or shared contracts.

## Current Baseline

- `apps/api/app/repositories/notes.py` defines `NotesRepository`, including
  `user_id` on every operation; its factory defaults to the memory repository.
- `apps/api/app/services/notes.py` is a thin forwarding boundary: it passes the
  authenticated `user_id` and validated request objects to the repository.
- `apps/api/app/repositories/notes_supabase.py` already describes Supabase query
  intent for list, create, get, update, and soft delete, but requires an
  injected user-scoped client and therefore remains scaffold-only.
- `apps/api/app/core/supabase_client.py` accepts verified JWT auth context,
  returns an inert `UserScopedSupabaseClientDescriptor`, and now defines the
  minimal application-owned query/client/adapter protocols. It stores caller
  token and public key values redacted and constructs no transport.
- Request-path public configuration prefers `SUPABASE_PUBLISHABLE_KEY`, with
  `SUPABASE_ANON_KEY` as a legacy public fallback. The factory does not select
  `SUPABASE_SERVICE_ROLE_KEY`.
- No executable Notes migration is committed, and no RLS behavior has been run
  or validated against Supabase.

## Repository Interface Mapping

| Protocol method | Current scaffold responsibility | Future live implementation constraint |
|---|---|---|
| `list_notes` | Build owner-scoped filtered, sorted, paginated selection | Execute through a request-scoped user client only |
| `create_note` | Build a row payload with server-controlled initial state | Write `user_id` from authenticated context; RLS must reject mismatch |
| `get_note` | Select one visible non-deleted owner row | Return no distinction between absent, deleted, or cross-user row |
| `update_note` | Conditional update on owner, visibility, and version | Keep atomic version guard and map misses after scoped lookup |
| `delete_note` | Conditional soft-delete update on owner and version | Never issue a physical delete for the Notes API path |

The implemented `UserScopedSupabaseQuery` and `UserScopedSupabaseClient`
protocols now express only the client/query behavior needed by
`SupabaseNotesRepository`. A future SDK adapter must implement that surface
without changing service or route ownership of API concerns.

## User-Scoped Client Usage

Future live wiring must follow this request-local sequence:

1. The auth boundary verifies the bearer JWT and creates `AuthContext` with
   verified `user_id` and retained redacted `access_token`.
2. `get_supabase_user_client` validates JWT mode and public Supabase
   configuration, returning the existing redacted descriptor.
3. A future reviewed SDK adapter consumes that descriptor to construct a fresh
   user-scoped Data API client for the request.
4. The adapter sends the verified caller access token as the authorization
   context used by Supabase/PostgREST so RLS evaluates the same caller.
5. The request-scoped client is injected into `SupabaseNotesRepository`.

The adapter must not mutate a global client's auth state, render token values
in diagnostics, or be constructed in default unit tests. The Slice 6H-3B plan
requires request-local access-token-only authorization, disables session
refresh/persistence assumptions, and now includes fake transport tests for the
candidate request-local SDK shape before any live enablement.

## No Service-Role Request-Path Policy

Normal Notes requests must use a public Data API key plus the verified caller
JWT. `SUPABASE_SERVICE_ROLE_KEY` is not a valid factory input for request
clients, must not be used as a fallback, and must not be injected into the
repository or adapter path.

Any later administrative or migration use of a service-role credential is a
separate reviewed concern outside Notes request handling. It cannot justify
weakening caller-scoped queries or RLS expectations.

## CRUD Operation Mapping

### `list_notes`

- Query `notes` with an explicit `user_id = auth_context.user_id` predicate.
- Unless `include_deleted` is true, require `is_deleted = false`.
- Apply `is_archived` only when requested.
- Preserve deterministic sort plus `id` tie-breaking and page range behavior.
- Convert returned rows and count metadata into `ListNotesData`.

### `create_note`

- Insert only repository-produced fields, including the authenticated
  `user_id`, editable note fields, and initial non-archived/non-deleted state.
- Do not accept client-controlled owner, timestamp, deletion, or version state.
- Require a returned row that validates as a `Note`.

### `get_note`

- Select by `id`, authenticated `user_id`, and `is_deleted = false`.
- Return the validated row when present.
- Treat missing, deleted, and inaccessible cross-user records uniformly as not
  found.

### `update_note`

- Update only editable fields plus repository-generated `updated_at` and the
  incremented version.
- Match `id`, authenticated `user_id`, `is_deleted = false`, and the requested
  current version in one conditional write.
- On an empty result, apply the conflict lookup behavior below.

### `delete_note`

- Implement API deletion as an update setting `is_deleted`, `deleted_at`,
  `updated_at`, and incremented version.
- Match `id`, authenticated `user_id`, `is_deleted = false`, and expected
  version in the conditional write.
- On an empty result, apply the same conflict lookup behavior as update.
- Never use physical `DELETE` for this request path.

## Version Conflict Behavior

Updates and soft deletes remain optimistic, version-gated operations. If a
conditional write returns no row, the repository performs one owner-scoped,
non-deleted lookup for the same note:

- No visible row: raise `NoteNotFoundError`, producing `404` at the API
  boundary.
- Visible row exists: raise `NoteVersionConflictError` with the expected
  version and validated current server note, producing `409` with
  `server_data`.

The follow-up lookup must remain scoped to the authenticated `user_id` so it
cannot reveal another user's note or deleted data.

## Soft Delete Behavior

Deletion is a state transition, not row removal. Default list and item reads
hide deleted Notes. `include_deleted=true` may expose deleted rows only for the
authenticated owner, still constrained by application predicates and eventual
RLS. Any physical retention cleanup is an administrative feature requiring a
separate design and security review.

## RLS Expectations

RLS is required before a live Notes table is enabled, but it is not implemented
or exercised by this plan.

| Operation | Expected eventual RLS outcome |
|---|---|
| List/get | An authenticated caller can read only owned rows |
| Create | Insert succeeds only when row `user_id` matches `auth.uid()` |
| Update/soft delete | An authenticated caller can mutate only owned rows |
| Cross-user access | Reads and mutations do not expose another user's record |
| Physical delete | Not exposed by the Notes request path |

Application queries must keep explicit `user_id` predicates after RLS is
enabled. RLS and API filtering are complementary controls.

## Error Mapping

| Scenario | HTTP response | Boundary behavior |
|---|---:|---|
| Missing, malformed, or rejected authentication | `401` | Auth boundary rejects before constructing a user-scoped client |
| Missing, deleted, or cross-user note | `404` | Repository returns not found without confirming existence |
| Stale update or soft-delete version | `409` | Repository supplies current owner-visible `server_data` |
| Invalid request DTO or query parameter | `400` | Existing Notes validation contract rejects input before repository execution |
| Configuration, transport, SDK, or unexpected persistence failure | `500` | Return a coarse server error; never expose tokens, keys, queries, or note content |

The implemented Notes route tests establish `400 VALIDATION_ERROR` for
request-schema failures, including rejected server-controlled fields and
missing required versions. Malformed request syntax is a distinct bad-request
case and must be specified and tested before custom handling is introduced. A
stale but otherwise valid `version` is a business conflict and remains `409`.

## Test Strategy

### Slice 6H-3A Unit Tests With Fake Client (Implemented)

- Tests inject a deterministic fake client/query builder into the existing
  `SupabaseNotesRepository`; do not construct a real SDK client.
- Tests prove each operation adds the authenticated `user_id` predicate or
  payload.
- Coverage includes pagination/filter ordering, row conversion, non-deleted visibility,
  version-gated update/delete, follow-up not-found/conflict classification, and
  soft-delete payload behavior.
- Empty fake responses model invisible/missing records only to prove repository
  scoping and
  non-disclosing error mapping; these are not RLS tests.
- A fake-client construction test blocks socket connections, and service-role
  placeholder configuration is verified not to reach injected client
  operations.

### Slice 6H-6 Notes Contract Drift Guard (Implemented)

- `apps/api/tests/test_contract_drift.py` loads the ten stable exported Notes
  JSON Schemas after `@synapse/shared contracts:export`.
- It compares snake_case field presence and effective required status against
  Pydantic Notes models; `ListNotesRequest` is compared to the implemented
  route query signature because no backend DTO exists for query parameters.
- It verifies create defaults and server-controlled-field exclusion,
  update/delete `version`, response envelopes, `data.items` and
  `data.pagination`, and the existing `400 VALIDATION_ERROR` versus
  `409 CONFLICT` behavior.
- It deliberately does not claim complete type equivalence: exported Zod
  defaulted fields are treated as omittable inputs, optional shared
  `sync_metadata` and response metadata `pagination` are not backend-emitted
  fields, and UUID/date-time precision remains outside this lightweight test.
- CI exports the generated schemas before API tests; FastAPI runtime code does
  not depend on Node or load these files.

### Slice 6H-3B-1 SDK Adapter Interface (Implemented)

- `UserScopedSupabaseQuery` specifies only the chainable query methods already
  used by Notes; `UserScopedSupabaseClient` specifies only `table()`.
- `UserScopedSupabaseClientAdapter` models future construction from the
  existing redacted descriptor without importing an SDK or opening a network
  connection.
- Deterministic fake-adapter tests prove the protocol can drive the current
  Notes query flow, create distinct fake clients for separate descriptor
  builds, and avoid rendering caller tokens or service-role configuration.

### Slice 6H-3B-2 Fake SDK Transport Tests (Implemented)

- Test-only fake SDK objects model candidate client construction, outgoing
  request metadata, auth/session boundaries, sanitized transport failure, and
  repository-compatible query execution without importing a real SDK.
- Tests prove the adapter receives `UserScopedSupabaseClientDescriptor`, unwraps
  the caller token only for request authorization metadata, and uses
  publishable or legacy anon key metadata as the public Data API key.
- Tests prove service-role values are not accepted or propagated, clients are
  request-scoped, shared auth headers are not globally mutated, token/session
  refresh and persistence are not called, representations/errors are redacted,
  and no socket network call occurs.

### Default CI

- Keep `SYNAPSE_NOTES_REPOSITORY=memory` as the active default.
- Keep factory and repository coverage fake/local and deterministic.
- Require no Supabase URL, API key, caller token, database, migration, or
  network connection.

### Optional Live Or Local Tests

Only after explicit approval, an approved migration, and reviewed adapter
wiring may opt-in local or non-production Supabase tests validate RLS behavior.
They must use synthetic users and test-only configuration, remain disabled by
default, and avoid printing credentials, tokens, or note content.

## Migration Policy

There is no executable Notes migration committed or approved. This plan is a
non-deployable description of expected repository and RLS behavior. Per
[database-migration-policy.md](security/database-migration-policy.md), any
future migration requires explicit approval and security review before commit,
must be environment-independent and free of credentials or real data, and must
be validated first in an approved non-production environment.

## Security Risks

| Risk | Required control |
|---|---|
| Token leakage | Preserve redacted token handling; never log or render caller JWTs |
| Service-role misuse | Reject service-role credentials from normal request-path client creation and injection |
| RLS bypass | Use caller JWT for live Data API calls and require reviewed RLS before enablement |
| Cross-user leakage | Keep `user_id` predicates and return `404` for invisible records |
| Logging note content | Log only safe operational categories/request identifiers, not titles or content |
| Premature database artifact | Do not add or execute migrations until the policy gate is satisfied |

## Implementation Slices

1. **Slice 6H-3A - Supabase repository fake-client tests (completed)**
   Deterministic injected-fake tests now cover query shaping, user filters,
   version/conflict handling, soft deletion, no-network behavior, and
   service-role avoidance without contacting Supabase.
2. **Slice 6H-6 - Contract drift guard between Zod JSON Schema and Pydantic (completed)**
   Deterministic backend tests now compare the stable exported Notes schema
   shapes and status contract to Pydantic/route expectations without runtime
   code generation or network access.
3. **Slice 6H-3B - Supabase live SDK adapter planning (completed)**
   The new live adapter plan defines request-scoped construction, caller-token
   propagation, public-key/service-role policy, SDK assumptions, and gated test
   and RLS work without adding transport.
4. **Slice 6H-3B-1 - Supabase SDK adapter interface (completed)**
   Minimal application-owned query/client/adapter protocols and deterministic
   fake-adapter tests now exist without any live SDK dependency.
5. **Slice 6H-3B-2 - Supabase fake SDK transport tests (completed)**
   Deterministic fake transport tests now prove request authorization metadata,
   public-key metadata, redaction, isolation, no session/refresh handling, and
   repository compatibility without Supabase credentials or network access.
6. **Slice 6H-3B-3 - Opt-in live Supabase test harness planning (recommended next)**
   Plan live/local coverage as separately enabled, synthetic, and outside
   default CI before any live infrastructure work.
7. **Slice 6H-3B-4 - Approved migration/RLS validation**
   Add and validate a minimum reviewed artifact only after explicit security
   approval.

## Definition Of Done

Slice 6H-3 planning is complete when:

- This document describes the existing repository/client boundaries and the
  future injection sequence without implementing them.
- CRUD, version-conflict, soft-delete, RLS, error, test, migration, and security
  decisions are explicit.
- At completion of the original planning slice, the next implementation step
  was restricted to fake-client repository tests.
- No SDK wiring, network access, migration, RLS execution, credential, UI, AI,
  or sync implementation is introduced.
- Memory repository behavior remains the default for local/test/CI.

Slice 6H-3A is complete when deterministic fake-client tests lock down existing
repository query, visibility, conflict, and soft-delete behavior without
constructing a live SDK client or testing RLS.

Slice 6H-6 is complete when exported shared Notes artifacts are compared during
backend verification for stable field/envelope/default/version/status behavior,
with the comparison limitations documented and without adding runtime Node,
live Supabase wiring, or database artifacts.

Slice 6H-3B is complete when the adapter plan fixes the future interface,
caller-token, public-key, SDK-assumption, error, RLS, test, and security
constraints without adding a live client, credential, or database artifact.

Slice 6H-3B-1 is complete when the application-owned protocols represent only
the existing Notes query surface, injected fake-adapter tests preserve
request-local/redacted/no-network guarantees, and no live SDK, activation,
credential, migration, or RLS execution is introduced.

Slice 6H-3B-2 is complete when test-only fake SDK transport coverage proves
descriptor consumption, caller authorization metadata, publishable/anon
public-key metadata, service-role exclusion, per-request client isolation,
redacted representations/errors, no session or refresh handling, no network
access, and compatibility with the current Notes repository query flow without
adding a live SDK, credential, migration, or RLS execution.
