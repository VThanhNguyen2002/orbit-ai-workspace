# Next Action

## Objective

Start Slice 6H — Notes live auth/Supabase integration planning. The shared
Notes CRUD contracts, FastAPI route skeleton, API client methods, auth context
boundary, explicit `dev`/`jwt` auth modes, fail-closed JWT branch, repository
interface, memory default, Supabase repository scaffold, and draft Notes
migration/RLS file are in place. The next step should plan live JWT verification
and user-scoped Supabase client wiring without breaking deterministic CI.

## Expected Files To Change

- Planning docs and small deterministic tests only if gaps are discovered.
- Avoid frontend UI, Expo initialization, sync engine work, AI/provider work, and
  live Supabase client wiring unless Slice 6H explicitly expands scope.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, or service-role usage in
request handlers.

## Commands To Run

```bash
cd apps/api
python -m ruff check .
python -m pytest
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

- Planning identifies the JWT library/verifier approach and exact config needed
  without committing secrets.
- Planning identifies how request-path Supabase clients will be user-scoped and
  avoid service-role use.
- Memory repo remains the default and does not require Supabase environment
  variables.
- Notes auth still derives `user_id` from the auth context and never from client
  payloads.
- Missing/deleted/cross-user Notes still return `404`; stale versions return
  `409` with `server_data`.
- No secrets, provider integration, frontend UI, Expo initialization, or sync
  engine work is added.

## Risks

- The Supabase repository is scaffolded only; live client injection and full JWT
  verification still need dedicated implementation.
- Auth currently rejects all `jwt` requests after Bearer-shape checks because no
  verifier is wired yet.
- The SQL RLS draft still needs execution against a real Supabase project and
  integration tests using user-scoped tokens.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the JSON Schema bridge is completed.

## Rollback Notes

Revert only Slice 6H planning changes if they introduce noise. Keep completed
shared contracts, backend skeleton, API client methods, Slice 6E/6G
auth/repository boundaries, and migration/RLS draft intact.

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
