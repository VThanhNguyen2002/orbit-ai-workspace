# Next Action

## Objective

Prepare **Slice 6H-3B-4B - Approved local-only migration artifact**, but do not
start until the Slice 6H-3B-4A draft review packet is accepted and the required
approvals are recorded.

The next bounded step, after acceptance, is to add the minimal
environment-independent Notes migration/RLS artifact for local-only validation.
That work must follow
[database-migration-policy.md](security/database-migration-policy.md),
[notes-migration-rls-validation-plan.md](notes-migration-rls-validation-plan.md),
and
[notes-migration-rls-draft-review-packet.md](notes-migration-rls-draft-review-packet.md).

Security gate: this repository still has no approved executable Supabase
migration at the time of this handoff. Slice 6H-3B-4B may create an artifact
only if the review packet has been accepted and the artifact-specific policy
exception is explicit.

## Expected Files To Change

- The approved local-only Notes migration/RLS artifact, only after acceptance
  and recorded approval.
- Minimal documentation updates that identify the artifact as approved for
  local-only validation.
- A clear note that generated Supabase state, real data, credentials, dumps,
  backups, and `.env` files remain prohibited.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, or RLS test execution.

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

- The review packet acceptance and artifact-specific approval are recorded
  before any executable SQL is added.
- The migration artifact is minimal, environment-independent, and local-only at
  this stage.
- The artifact contains no production data, credentials, project identifiers,
  service-role keys, broad grants, or unsafe privileged functions.
- Generated Supabase state, dumps, backups, SQLite/db files, and `.env` files
  remain untracked.
- The artifact preserves current Notes API behavior and owner-scoped soft
  deletion/version semantics.
- No service-role credential is introduced into the request path or default
  tests.
- Memory persistence remains the default; live repository wiring and RLS tests
  remain deferred.

## Risks

- Adding a migration artifact changes the repository's database artifact
  posture, so review evidence must be explicit.
- A faulty RLS artifact could expose cross-user data if later applied.
- A local-only artifact still does not prove hosted staging readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## Rollback Notes

If Slice 6H-3B-4B work is unsuitable, revert only that work. Keep completed
shared contracts, backend skeleton, API client methods, Slice 6E/6G boundaries,
Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor factory/tests, the
Slice 6H-3 and Slice 6H-3B plans, Slice 6H-3A fake-client repository tests,
Slice 6H-6 contract drift guard, Slice 6H-3B-1 adapter interface/tests, Slice
6H-3B-2 fake SDK transport tests, Slice 6H-3B-3 harness plan, Slice 6H-3B-3A
skipped harness skeleton, Slice 6H-3B-3B local setup guide, Slice 6H-3B-4
migration/RLS validation plan, Slice 6H-3B-4A draft review packet, and the
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
