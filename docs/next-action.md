# Next Action

## Objective

Prepare **Slice 6H-3B-4A - Migration/RLS draft review packet**. Slice 6H-3B-4
adds the security-first migration/RLS validation plan, but no executable Notes
migration/RLS artifact is approved or committed yet.

The next bounded step is still documentation-first. Create a review packet that
describes the proposed migration/RLS artifact scope, sanitized Notes behavior,
review evidence, validation expectations, rollback/cleanup considerations, and
open questions. The packet should make a later approval decision possible
without adding SQL in this step.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md) and
[notes-migration-rls-validation-plan.md](notes-migration-rls-validation-plan.md).

## Expected Files To Change

- A documentation-only Migration/RLS draft review packet, or a clearly scoped
  update to the validation plan that captures the review packet contents.
- Minimal documentation updates that keep the next step review-first.
- Do not add SQL, migrations, Supabase generated state, live SDK transport,
  credentials, `.env` files, live repository wiring, or RLS execution.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, or service-role usage in
request handlers.

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

- The review packet describes proposed Notes table/RLS behavior in sanitized
  prose only.
- The packet identifies reviewers, approval evidence, open questions, rollback
  considerations, cleanup expectations, and synthetic validation evidence.
- The packet confirms no production data, credentials, service-role request-path
  usage, broad grants, unsafe privileged functions, or generated Supabase state
  are proposed.
- The packet keeps default CI disabled for live/local Supabase tests.
- No service-role credential is introduced into the request path or default
  tests.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- A review packet still does not prove real RLS enforcement; an approved
  artifact and opt-in execution remain later work.
- A future migration could expose data if RLS or ownership predicates are
  incomplete; security review must happen before commit or execution.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Slice 6H-6 guard covers stable Notes field/envelope/default/version/status
  behavior, not complete type-format equivalence or runtime schema validation.

## Rollback Notes

If Slice 6H-3B-4A review-packet work is unsuitable, revert only that work. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H-3 and Slice 6H-3B plans, Slice 6H-3A fake-client
repository tests, Slice 6H-6 contract drift guard, Slice 6H-3B-1 adapter
interface/tests, Slice 6H-3B-2 fake SDK transport tests, Slice 6H-3B-3 harness
plan, Slice 6H-3B-3A skipped harness skeleton, Slice 6H-3B-3B local setup
guide, Slice 6H-3B-4 migration/RLS validation plan, and the database artifact
security policy intact.

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
