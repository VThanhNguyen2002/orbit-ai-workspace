# Next Action

## Objective

Prepare **Slice 6H-3B - Supabase live SDK adapter planning**. Slice 6H-6 now
adds a deterministic backend guard for the ten stable Notes JSON Schema
artifacts exported from `@synapse/shared`. The guard compares bounded
Pydantic/route expectations without changing public Notes behavior or loading
Node-generated artifacts in FastAPI runtime code.

The next bounded step is planning and review only: determine the exact
request-scoped SDK adapter API, caller JWT injection mechanism, disabled-by-
default feature flag, failure mapping, and test/security gates before any live
transport implementation is approved.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- Sanitized adapter planning documentation only, unless a separate reviewed
  implementation task is later approved.
- Specify public-key plus verified caller-token usage, feature-flag behavior,
  test strategy, and RLS/migration approval dependencies.
- Do not add an SDK dependency or adapter, connect to Supabase, enable live
  Notes persistence, add JWKS retrieval, or create/execute an RLS migration.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, live Notes Supabase repository
wiring, or service-role usage in request handlers.

## Commands To Run

```bash
pnpm --filter @synapse/shared contracts:export
pnpm --filter @synapse/shared contracts:check

cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/shared test
pnpm --filter @synapse/api-client test
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- A reviewable adapter plan identifies how a future client would be
  request-scoped and use only the publishable/anon key plus verified caller
  token.
- Feature-flag, error, testing, security, RLS, and migration approval gates are
  explicit before any implementation.
- No service-role credential is introduced into the request path.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- The fake-client repository tests do not prove SDK compatibility or RLS
  enforcement; those remain separately reviewed later slices.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- The Slice 6H-6 guard covers stable Notes field/envelope/default/version/status
  behavior, not complete type-format equivalence or runtime schema validation.

## Rollback Notes

If Slice 6H-3B planning work is unsuitable, revert only that work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H-3 repository implementation plan, the Slice 6H
plan, Slice 6H-3A fake-client repository tests, Slice 6H-6 contract drift
guard, and the database artifact security policy intact.

## External Review Gate

Before considering the slice complete:

1. Render the full final report clearly and structurally.
2. Include:
   - architectural decisions
   - tradeoffs
   - risks
   - shortcuts/deferred items
   - verification evidence
   - CI status
   - security observations
3. Assume the rendered output will be reviewed externally by ChatGPT as an
   extended engineering review gate.
4. Be explicit about:
   - anything intentionally deferred
   - anything scaffold-only
   - anything mocked/faked
   - any remaining inconsistencies
   - any temporary implementations
5. Do not hide weak points or unresolved risks.
6. Do not automatically continue to the next slice after rendering the report.
7. Wait for external ChatGPT review feedback before proceeding further.

The rendered report must be detailed enough for:

- architecture review
- consistency review
- security review
- CI/reliability review
- implementation-scope review

Treat the final report as a handoff artifact for external engineering audit.
