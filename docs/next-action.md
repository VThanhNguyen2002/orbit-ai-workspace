# Next Action

## Objective

Prepare **Slice 6H-3B-2 - Supabase fake SDK transport tests**. Slice 6H-3B-1
now adds the minimal application-owned query/client/adapter protocol boundary
and deterministic fake-adapter proof described in
[notes-supabase-live-adapter-plan.md](notes-supabase-live-adapter-plan.md).

The next bounded step is to pin/review the candidate SDK construction shape and
prove with fake transport only that caller authorization, public key use,
redaction, and per-request isolation meet the plan. Keep live transport, RLS
execution, and live enablement deferred to separately reviewed slices.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- Focused fake SDK transport tests and only the minimum test support needed to
  represent candidate SDK construction and outgoing authorization safely.
- Documentation updates only where required to reflect the reviewed interface.
- Do not add the live SDK transport/dependency, connect to Supabase, enable
  live Notes persistence, add JWKS retrieval, or create/execute an RLS
  migration.

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

- Fake transport tests prove the selected candidate SDK shape would attach only
  the verified caller token and publishable/anon key to request-scoped
  operations.
- Tests prove no session persistence, refresh-token handling, shared client
  authorization state, secret rendering, or network access is introduced.
- No service-role credential is introduced into the request path.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- Fake SDK transport tests still do not prove real SDK compatibility or RLS
  enforcement; opt-in integration and approved RLS validation remain later
  slices.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- The Slice 6H-6 guard covers stable Notes field/envelope/default/version/status
  behavior, not complete type-format equivalence or runtime schema validation.

## Rollback Notes

If Slice 6H-3B-2 fake transport work is unsuitable, revert only that work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H-3 and Slice 6H-3B plans, Slice 6H-3A fake-client
repository tests, Slice 6H-6 contract drift guard, Slice 6H-3B-1 adapter
interface/tests, and the database artifact security policy intact.

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
