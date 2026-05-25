# Next Action

## Objective

Start **Slice 6H-2 - User-scoped Supabase client factory**. Slice 6H-1 now
provides an injected verifier boundary and a configured RS256 adapter with
local-key tests; it does not perform Supabase JWKS discovery or contact a live
service. The next factory should propagate the already verified caller token
through a narrowly scoped client boundary using fakes in tests.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- API client-factory/repository-boundary modules and deterministic fake-client
  tests required to model caller-scoped data access.
- Documentation/config placeholders only when required by implemented settings.
- Do not connect to live Supabase, wire live Notes persistence, add JWKS network
  retrieval, or create/execute an RLS migration in this slice.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, live Notes Supabase repository
wiring, or service-role usage in request handlers.

## Commands To Run

```bash
cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/shared test
pnpm --filter @synapse/shared contracts:check
pnpm --filter @synapse/api-client test
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Definition Of Done

- A request-scoped factory consumes the verified caller access token without
  mutating global authentication state.
- Tests use fake client construction only and demonstrate that caller identity
  and token handoff stay scoped to the request.
- No service-role credential is read or used in the request path.
- Memory persistence remains the default; no live Supabase client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- The Supabase repository remains scaffolded only; live client injection still
  needs its later implementation slice.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the separate `Slice 6H-6` drift guard is completed.

## Rollback Notes

If Slice 6H-2 implementation is unsuitable, revert only that factory work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, the Slice 6H plan, and the
database artifact security policy intact.

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
