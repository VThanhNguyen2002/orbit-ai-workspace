# Next Action

## Objective

Start **Slice 6H-3 - Supabase repository live implementation planning**. Slice
6H-2 now provides an inert, redacted user-scoped client descriptor boundary
which accepts the verified caller token and selects only public Data API
configuration. The repository remains scaffold-only, so the next bounded step
is to plan how a reviewed SDK adapter would be injected without enabling live
access or migrations.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- Documentation and, only where needed for deterministic planning validation,
  minimal fake-client/repository-boundary tests.
- Specify how the descriptor feeds a later SDK adapter and how the adapter is
  injected into the existing repository scaffold.
- Do not connect to live Supabase, enable live Notes persistence, add JWKS
  network retrieval, or create/execute an RLS migration in this slice.

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

- The SDK-adapter and repository injection plan preserves verified caller-token
  pass-through, explicit user scoping, and public-key-only request handling.
- Any new validation remains fake/local and makes no live Supabase request.
- No service-role credential is introduced into the request path.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- The Supabase repository remains scaffold-only; implementation and RLS
  validation still require separately reviewed later slices.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the separate `Slice 6H-6` drift guard is completed.

## Rollback Notes

If Slice 6H-3 planning is unsuitable, revert only that planning work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H plan, and the database artifact security policy
intact.

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
