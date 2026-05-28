# Next Action

## Objective

Prepare **Slice 6H-3B-3A - Opt-in live test harness skeleton**. Slice 6H-3B-3
now adds the concrete opt-in live/local harness plan in
[notes-supabase-live-test-harness-plan.md](notes-supabase-live-test-harness-plan.md),
covering local and hosted staging modes, placeholder-only configuration,
default-CI exclusion, synthetic data rules, adapter/RLS validation
expectations, cleanup, risks, and migration prerequisites.

The next bounded step is to add skipped-by-default test scaffolding and
fail-closed configuration guards only. Keep live transport, RLS execution,
migrations, credentials, and live enablement deferred to separately reviewed
slices.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- Skipped-by-default API test scaffolding for the future live/local harness,
  including markers and configuration guards that prove the harness cannot run
  without explicit opt-in.
- Minimal documentation updates reflecting the skeleton and preserving the
  planning constraints.
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

- The skeleton is skipped by default in normal pytest and normal push CI.
- Running live/local tests requires an explicit flag, explicit mode, and
  placeholder-only required environment configuration.
- Missing opt-in configuration produces skip or redacted configuration failure,
  not accidental network execution.
- No service-role credential is introduced into the request path, skeleton, or
  default tests.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- A skipped skeleton still does not prove real SDK compatibility or RLS
  enforcement; implementation and approved RLS validation remain later slices.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- The Slice 6H-6 guard covers stable Notes field/envelope/default/version/status
  behavior, not complete type-format equivalence or runtime schema validation.

## Rollback Notes

If Slice 6H-3B-3A harness skeleton work is unsuitable, revert only that work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H-3 and Slice 6H-3B plans, Slice 6H-3A fake-client
repository tests, Slice 6H-6 contract drift guard, Slice 6H-3B-1 adapter
interface/tests, Slice 6H-3B-2 fake SDK transport tests, Slice 6H-3B-3 harness
plan, and the database artifact security policy intact.

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
