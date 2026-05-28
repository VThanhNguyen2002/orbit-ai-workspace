# Notes Supabase Live Adapter Plan

## Status

Slice 6H-3B defines the future live SDK adapter contract constrained by the
implemented user-scoped descriptor and the Supabase-shaped Notes repository
tests. Slice 6H-3B-1 now adds the application-owned query/client/adapter
protocol boundary and deterministic fake-adapter coverage. Slice 6H-3B-2 now
adds deterministic fake SDK transport coverage for caller-token propagation,
public-key metadata, redaction, request isolation, and no session/refresh
handling. Slice 6H-3B-3 now adds a planning document for a disabled-by-default
live/local Supabase harness in
[notes-supabase-live-test-harness-plan.md](notes-supabase-live-test-harness-plan.md).
It does not add `supabase-py`, create a live client, enable Supabase
persistence, introduce credentials, add a migration, or execute RLS validation.

The next bounded task is **Slice 6H-3B-3A - Opt-in live test harness
skeleton**. That task may add skipped-by-default test scaffolding and
fail-closed configuration guards; it must not silently turn on live traffic or
introduce database artifacts.

## 1. Objective

Define how a later FastAPI request may construct a request-scoped Supabase
Python client for Notes using the already verified caller JWT and a public Data
API key. The future adapter must fit the existing repository query-builder
boundary, keep memory persistence as the default, preserve Notes API behavior,
and make Supabase RLS an additional user-isolation boundary rather than a
replacement for application scoping.

## 2. Non-Goals

- Do not add a live Supabase SDK dependency, implementation, or network call.
- Do not enable `SYNAPSE_NOTES_REPOSITORY=supabase` for normal local, test, or
  CI execution.
- Do not add `.env` files, real project URLs, keys, tokens, or other
  credentials.
- Do not add or execute SQL, migrations, RLS policies, seed data, or local
  Supabase setup.
- Do not use a service-role key for any Notes request.
- Do not change Notes routes, response envelopes, CRUD semantics, frontend/UI,
  Expo, AI, offline sync, or public shared contracts.
- Do not implement JWKS retrieval or production live-auth activation here.

## 3. Current Baseline

- `apps/api/app/core/supabase_client.py` defines the redacted
  `UserScopedSupabaseClientDescriptor` plus implementation-neutral
  `UserScopedSupabaseQuery`, `UserScopedSupabaseClient`, and
  `UserScopedSupabaseClientAdapter` protocols. The descriptor accepts only
  JWT-authenticated contexts with a retained verified access token, prefers a
  publishable public key, allows a legacy anon public key fallback, stores
  key/token values as `SecretStr`, and constructs no transport.
- `apps/api/app/repositories/notes_supabase.py` implements the
  `NotesRepository` query shape against an injected
  `UserScopedSupabaseClient`. It does not import or construct a Supabase SDK
  client.
- `SYNAPSE_NOTES_REPOSITORY=memory` is the default. Choosing `supabase` today
  remains unwired and fails closed because no user-scoped client is injected by
  the normal factory.
- Fake-client tests cover owner predicates, pagination and deleted filtering,
  insert ownership, conditional update/delete, conflict lookup, soft deletion,
  adapter protocol compatibility, distinct request client creation, no-network
  behavior, redaction, and service-role non-propagation.
- Fake SDK transport tests cover the candidate request-local construction
  shape: descriptor input, outgoing caller authorization metadata, publishable
  or legacy anon public-key metadata, no session/refresh calls, per-request
  client isolation, redacted representations/errors, no-network execution, and
  compatibility with the existing Notes repository query flow.
- The live test harness plan defines future local and hosted staging modes,
  placeholder-only environment requirements, default-CI exclusion, synthetic
  data rules, adapter validation, RLS validation expectations, cleanup
  expectations, and migration prerequisites.
- The contract drift guard covers stable Notes shared-schema and backend
  behavior boundaries without adding runtime schema loading.
- No approved executable Notes migration or performed RLS validation exists.

## 4. Required Adapter Boundary

The implemented protocol boundary requires any future adapter to consume the
existing inert descriptor and expose only the table-client behavior already
used by `SupabaseNotesRepository`. It does not change the repository protocol
or require routes/services to know about the Supabase SDK.

Implemented application-owned adapter interface:

```python
class UserScopedSupabaseClientAdapter(Protocol):
    def build(
        self,
        descriptor: UserScopedSupabaseClientDescriptor,
    ) -> UserScopedSupabaseClient: ...
```

`UserScopedSupabaseQuery` models only `select`, `insert`, `update`, `eq`,
`order`, `range`, `limit`, and `execute`; `UserScopedSupabaseClient` models
only `table`. No SDK-specific API or transport is represented.

Future construction sequence:

1. Existing authentication verifies the bearer token and supplies
   `AuthContext(user_id=<verified sub>, auth_mode="jwt", access_token=<redacted>)`.
2. Existing `get_supabase_user_client()` produces the redacted descriptor from
   JWT context plus public Supabase configuration.
3. A reviewed adapter implementation builds a new SDK client for this request
   only and returns it as `UserScopedSupabaseClient`.
4. The constructed client is injected into `SupabaseNotesRepository`.
5. The repository continues passing authenticated `user_id` to every operation
   and shaping all filters and payloads.

A future setting should gate any live construction:

```text
SYNAPSE_SUPABASE_LIVE_ADAPTER_ENABLED=false
```

This proposed flag is not implemented by this plan. Its required semantics
are:

- Default `false`; default CI and local/test paths do not construct an SDK
  client.
- Live construction requires the flag to be explicitly enabled together with
  JWT auth mode and Supabase repository selection.
- A selected Supabase repository without enabled/safe adapter configuration
  fails closed; it does not fall back to privileged credentials or implicit
  network behavior.

## 5. User-Scoped Token Propagation Strategy

- The API receives a bearer access token, verifies it before repository work,
  and derives `user_id` only from the verified `sub` claim.
- The existing descriptor retains the verified caller access token as a
  redacted value. The future adapter is the only request-path component allowed
  to unwrap it, solely to set the Data API authorization context.
- Each live Notes request must create a caller-scoped client whose PostgREST
  requests carry `Authorization: Bearer <verified caller access token>`.
- The public API key remains the SDK project key/API key header; it is not a
  substitute identity for the caller JWT.
- The adapter must not receive, store, refresh, or require a refresh token.
- The adapter must not mutate shared/global client authorization state or reuse
  one user's client for another request.
- Tokens must never appear in logs, exceptions, response bodies, metrics
  labels, traces, snapshots, or test diagnostics.

## 6. Public Key Vs Service-Role Policy

Normal Notes request traffic must use:

- `SUPABASE_PUBLISHABLE_KEY` as the preferred public Data API key; or
- `SUPABASE_ANON_KEY` only as the documented legacy public-key fallback; and
- the verified caller access token for RLS identity.

`SUPABASE_SERVICE_ROLE_KEY` must never be:

- selected as a fallback public key;
- passed into the request-scoped descriptor or adapter;
- used by `SupabaseNotesRepository`; or
- used to make any user-requested Notes operation succeed.

A service-role credential may be considered only in separately approved
administrative/migration work outside this request path. Because it bypasses
RLS, it cannot be used to test or justify normal Notes authorization behavior.

## 7. Supabase Python SDK Usage Assumptions

This plan records assumptions to validate before an implementation dependency
is added. As reviewed on 2026-05-26, Supabase's official Python documentation
describes client initialization through `create_client(url, key)`, and states
that authenticated SDK data requests are sent with the user's auth token.

The released `supabase-py` v2.30.0 source also shows a client option for
initial headers and options for token refresh and session persistence. The
candidate future construction pattern is therefore a new request-local client
created with:

- project URL from the descriptor;
- its redacted public Data API key unwrapped only at construction;
- an initial `Authorization` header containing the already verified caller
  access token;
- automatic token refresh disabled; and
- session persistence disabled.

This is an assumption, not implemented code. Slice 6H-3B-2 codifies the
candidate request-local transport shape with fakes only; it still does not add
or pin a real SDK dependency. Before implementation, the exact SDK version and
API names must be re-reviewed. The fake transport tests prove that:

- table requests actually carry the caller bearer authorization header;
- the public API key remains the project key header;
- no authentication refresh or storage call occurs;
- no client state leaks across constructed request clients; and
- failure representations redact key/token material.

The documented Python `auth.set_session(access_token, refresh_token)` method is
not suitable for this boundary because the backend intentionally receives only
the caller access token and must not manage or solicit refresh tokens. If the
chosen pinned SDK cannot support access-token-only Data API authorization
without session mutation or refresh, implementation must stop for review
rather than broaden the auth boundary.

References:

- Supabase Python initialization:
  https://supabase.com/docs/reference/python/initializing
- Supabase Python session setting:
  https://supabase.com/docs/reference/python/auth-setsession
- Supabase Auth and RLS integration:
  https://supabase.com/docs/guides/auth
- Reviewed released SDK source:
  https://github.com/supabase/supabase-py/tree/v2.30.0

## 8. Repository Operation Mapping

The adapter executes the existing repository's query-builder calls; it does
not reinterpret Notes behavior.

### `list_notes`

- Execute a `notes` selection scoped by explicit `user_id`.
- Preserve `is_deleted = false` by default and omit that filter only when
  `include_deleted=true`.
- Preserve optional archived filtering, deterministic requested sorting plus
  `id` tie-breaking, pagination range, and count mapping.
- RLS must independently prevent rows for any other user from being returned.

### `create_note`

- Insert only the repository-produced payload, including the authenticated
  `user_id` and server-selected initial archive/deletion state.
- Never accept a caller-supplied owner, version, deletion state, or timestamp
  through adapter behavior.
- Require the returned row to validate as the existing `Note` model.
- Eventual RLS must reject an inserted owner not matching the caller identity.

### `get_note`

- Select by note id, explicit authenticated `user_id`, and
  `is_deleted = false`, limited to one result.
- Return the validated row when visible.
- Preserve indistinguishable not-found behavior for absent, deleted, or
  cross-user/inaccessible records.

### `update_note`

- Execute the existing conditional update scoped by id, authenticated
  `user_id`, non-deleted visibility, and expected `version`.
- Preserve repository-generated timestamp and incremented version payload.
- If no row is returned, preserve the owner-scoped follow-up lookup used to
  distinguish a stale visible row from not-found without leaking other users.

### `delete_note`

- Execute the existing conditional soft-delete update only.
- Set deleted and updated timestamps together and increment `version`.
- Preserve id, owner, visibility, and expected-version constraints.
- Never issue physical SQL/REST deletion for the public Notes delete method.

## 9. Version Conflict Behavior

Update and delete remain optimistic version-gated writes. An empty conditional
write response triggers one additional lookup scoped by the same authenticated
`user_id` and `is_deleted = false` condition:

- No visible current row maps to `NoteNotFoundError` and the existing `404`
  response.
- A visible current row maps to `NoteVersionConflictError` with validated
  current server data and the existing `409` response.

The adapter must not turn an empty write into an unscoped existence check,
retry a stale write automatically, or expose transport/database details.

## 10. Soft Delete Behavior

- Notes deletion remains an update that marks the row deleted; no live adapter
  may issue a physical delete for the Notes request path.
- Default lists and item reads hide soft-deleted rows.
- `include_deleted=true` remains owner-scoped and eventually RLS-scoped.
- Physical retention/cleanup is administrative work outside this plan and
  would require separate approval and security review.

## 11. Error Mapping

| Condition | Required API-facing behavior | Adapter/repository rule |
|---|---|---|
| Missing or invalid caller authentication | `401 UNAUTHORIZED` | Reject before descriptor/adapter construction |
| Live adapter disabled or unsafely configured when selected | Coarse server/configuration failure | Fail closed; never select service role or silently fall back |
| Missing, deleted, or inaccessible note | `404 NOT_FOUND` | Preserve owner-scoped empty-result mapping |
| Visible row with stale update/delete version | `409 CONFLICT` | Preserve owner-scoped conflict lookup and existing server data contract |
| SDK, transport, PostgREST, or unexpected row failure | Coarse server error | Do not expose URL, headers, key/token values, query details, or note content |

SDK/PostgREST exception classification must be specified and unit tested when
the SDK version is pinned. This plan does not introduce new public error
envelopes or HTTP behavior.

## 12. RLS Expectations

RLS is mandatory before live Notes persistence is approved, and explicit
application-level `user_id` constraints remain mandatory after RLS exists.

Required eventual validation with synthetic user A and user B:

- User A can list, create, get, update, and soft-delete rows owned by user A.
- User A cannot see user B rows in list or get requests.
- User A cannot update or soft-delete user B rows.
- An insert whose `user_id` differs from the verified caller is rejected.
- Soft-deleted user A rows are hidden by default and visible only to user A
  when explicitly included.
- Cross-user and deleted item responses do not reveal existence.
- No Notes request performs physical deletion.

No such RLS test is executed by this planning slice. Any migration/RLS artifact
requires explicit approval under
[database-migration-policy.md](security/database-migration-policy.md) first.

## 13. Test Strategy

### Default Deterministic Coverage

- Existing memory repository behavior remains the local/test/CI default.
- Existing fake-client repository tests remain the primary default coverage
  for CRUD query shaping, owner constraints, conflicts, and soft deletion.
- Existing descriptor tests remain no-network checks for public-key selection,
  redaction, and JWT-only caller inputs.
- Slice 6H-3B-1 tests now prove that an injected fake satisfies the protocol
  boundary, drives the existing Notes query flow without network access, and
  constructs distinct safe fake clients without retaining secret inputs.
- Slice 6H-3B-2 tests now fake SDK client construction and outgoing Data API
  metadata without connecting to Supabase or logging credential values. They
  prove caller bearer propagation, publishable/anon key metadata, no
  service-role propagation, no session/refresh calls, redacted failures, and
  isolated clients per request.
- CI must not require a Supabase URL, API key, JWT, database, migration, or
  network connection.

### Opt-In Live Or Local Supabase Coverage

- A later harness must be disabled by default and require an explicit opt-in
  switch plus test-only environment configuration.
- It must use only synthetic users/content in a disposable local or approved
  non-production environment.
- It must not run in standard CI and must not print URLs containing secrets,
  keys, tokens, authorization headers, or note content.
- It cannot claim RLS coverage until the specific migration/RLS artifact has
  been explicitly approved and applied in that test environment.
- The detailed harness requirements are recorded in
  [notes-supabase-live-test-harness-plan.md](notes-supabase-live-test-harness-plan.md).

## 14. Security Risks

| Risk | Required control |
|---|---|
| Token leakage | Unwrap the caller token only inside request-scoped adapter construction; never log or render it |
| Service-role misuse | Public-key-only adapter inputs; no service-role fallback or request-path import/injection |
| RLS bypass | Propagate verified caller authorization to Data API calls and require approved RLS before live enablement |
| Cross-user leakage | Preserve explicit `user_id` predicates, owner-scoped conflict lookups, and non-disclosing `404` behavior |
| Note content logging | Do not log payloads, returned rows, titles, content, or conflict server data |
| Shared client authorization bleed | Construct per-request clients and test that caller authorization is not reused |
| Refresh-token expansion | Do not accept or manage refresh tokens in the backend adapter boundary |
| Premature database artifact | Keep migration/RLS work gated by explicit security approval |

## 15. Implementation Slices

1. **Slice 6H-3B-1 - Supabase SDK adapter interface (completed)**
   Application-owned query/client/adapter protocols and deterministic
   fake-adapter tests now exist without adding an SDK or enabling transport.
2. **Slice 6H-3B-2 - Supabase fake SDK transport tests (completed)**
   Candidate request-local transport coverage now proves caller authorization
   metadata, public-key metadata, no refresh/session persistence, redaction,
   request isolation, and repository compatibility with fakes only.
3. **Slice 6H-3B-3 - Opt-in live Supabase test harness planning (completed)**
   The harness plan now defines local and hosted staging modes, explicit
   opt-in gates, synthetic data and cleanup rules, adapter/RLS validation
   expectations, and migration prerequisites without adding live execution.
4. **Slice 6H-3B-3A - Opt-in live test harness skeleton (recommended next)**
   Add skipped-by-default markers, configuration guards, and placeholder tests
   that prove the harness cannot run without explicit opt-in.
5. **Slice 6H-3B-3B - Local Supabase setup guide**
   Document local-only setup and cleanup instructions with placeholder values
   and approved prerequisites.
6. **Slice 6H-3B-3C - Hosted staging opt-in test plan**
   Document controlled non-production staging validation, secret-store rules,
   CI/manual workflow separation, and redaction requirements.
7. **Slice 6H-3B-4 - Approved migration/RLS validation**
   Only after explicit database-artifact approval, introduce/review the minimum
   migration and validate owner isolation and soft-delete outcomes in an
   approved environment.

JWKS/live authentication production readiness remains separately gated: an SDK
adapter alone does not make the current configured RS256 verifier suitable for
production key rotation.

## 16. Definition Of Done

Slice 6H-3B planning is complete when:

- A documentation artifact defines the future request-scoped adapter boundary,
  caller-token propagation, public-key-only policy, SDK assumptions, CRUD
  mapping, conflict/delete semantics, error mapping, RLS gates, tests, risks,
  and staged implementation order.
- At completion of the planning slice, related planning documents pointed to
  this plan and recommended Slice 6H-3B-1 next.
- The repository still has no live SDK adapter, live network access, Supabase
  dependency, credential, executable migration, RLS execution, UI, AI, sync
  implementation, or changed public Notes API behavior.
- Memory persistence remains the default and all existing local/CI
  verification continues to pass without live Supabase configuration.

Slice 6H-3B-1 is complete when:

- Application-owned query/client/adapter protocols express only the table
  operations currently required by the Notes repository.
- The repository accepts the protocol boundary while preserving existing API
  behavior and remaining unwired for live data.
- Deterministic fake-adapter tests prove no-network construction/query use,
  per-request fake client isolation, redacted inputs, and no service-role
  propagation.
- The next recommended task is Slice 6H-3B-2; no SDK transport, live
  activation, migration, or RLS execution has been introduced.

Slice 6H-3B-2 is complete when:

- Test-only fake SDK transport coverage proves the future adapter shape
  receives `UserScopedSupabaseClientDescriptor` and sends the verified caller
  token only as request authorization metadata.
- Tests prove publishable or legacy anon key metadata is used as the public
  Data API key, while service-role values are not accepted or propagated.
- Tests prove request-scoped client isolation, no global auth-header mutation,
  no session persistence, no refresh-token handling, redacted representations
  and errors, no network access, and compatibility with the current Notes
  repository query flow.
- The next recommended task is Slice 6H-3B-3 harness planning; no real SDK,
  live activation, credential, migration, or RLS execution has been introduced.

Slice 6H-3B-3 is complete when:

- A harness plan defines local and hosted staging modes, placeholder-only
  environment variables, default-skip behavior, explicit opt-in flags, and
  normal push-CI exclusion.
- The plan defines synthetic user/data rules, cleanup expectations, adapter
  validation checks, user A/user B RLS validation expectations, and migration
  prerequisites.
- The next recommended task is Slice 6H-3B-3A; no live SDK adapter, network
  behavior, credential, `.env` file, migration, SQL artifact, or RLS execution
  has been introduced.
