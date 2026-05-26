# Next Action

## Objective

Start **Slice 6H-3A - Supabase repository fake-client tests**. Slice 6H-3 now
records the future implementation sequence in
[notes-supabase-repository-implementation-plan.md](notes-supabase-repository-implementation-plan.md).
The next bounded step is deterministic test coverage for the existing
Supabase-shaped repository scaffold, without adding an SDK adapter or enabling
live access.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- API repository test files and, only if required for accurate test
  documentation, small planning-document updates.
- Inject deterministic fake client/query objects into the current repository
  scaffold to prove CRUD query shaping, user scoping, soft deletion, and
  conflict classification.
- Do not add a live SDK adapter, connect to Supabase, enable live Notes
  persistence, add JWKS retrieval, or create/execute an RLS migration.

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

- Fake-client tests prove the repository preserves explicit `user_id` scoping,
  soft-delete semantics, and version-conflict/not-found classification.
- Test execution remains fake/local and makes no live Supabase request.
- No service-role credential is introduced into the request path.
- Memory persistence remains the default; no live SDK client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- Fake query-builder tests cannot prove SDK compatibility or RLS enforcement;
  those remain separately reviewed later slices.
- The configured RS256 verifier is suitable for deterministic boundary tests,
  but JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the separate `Slice 6H-6` drift guard is completed.

## Rollback Notes

If Slice 6H-3A fake-client tests are unsuitable, revert only those tests. Keep
completed shared contracts, backend skeleton, API client methods, Slice 6E/6G
boundaries, Slice 6H-1 verifier boundary/tests, Slice 6H-2 descriptor
factory/tests, the Slice 6H-3 repository implementation plan, the Slice 6H
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
