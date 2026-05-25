# Next Action

## Objective

Start **Slice 6H-1 - JWT verifier interface and tests**. Slice 6H planning is
captured in
[notes-live-auth-supabase-plan.md](notes-live-auth-supabase-plan.md): use
asymmetric Supabase signing keys and JWKS verification as the default live auth
path, retain HS256 only as an explicit legacy mode, and do not wire live
Supabase persistence until authenticated identity is verified.

Security gate: no executable Supabase migration is committed. Notes/RLS design
remains sanitized documentation only, and any future migration artifact requires
explicit approval and security review under
[database-migration-policy.md](security/database-migration-policy.md).

## Expected Files To Change

- API auth/config modules, dependency metadata, and deterministic auth tests
  needed for the verifier interface and its selected adapters.
- Documentation/config placeholders only when required by implemented settings.
- Do not add the user-scoped Supabase client factory or create/execute an RLS
  migration in this slice.

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

- A verifier interface is injected behind `get_auth_context`; production JWT
  mode never accepts a token based on header shape alone.
- JWKS mode verifies signature, expiry, issuer, audience, and UUID `sub` with an
  explicit asymmetric algorithm allowlist; legacy HS256 is opt-in only.
- Tests use generated local keys/fakes and cover invalid and valid token paths
  without requiring Supabase or network calls.
- A verified `sub` is the only source for `AuthContext.user_id`, and errors/logs
  never expose bearer-token values.
- Memory persistence remains the default; no live Supabase client or executable
  migration is introduced.
- No real credentials, UI, Expo, AI, or sync engine work is added.

## Risks

- The Supabase repository remains scaffolded only; live client injection still
  needs its later implementation slice.
- Until Slice 6H-1 is completed, auth rejects all `jwt` requests after
  Bearer-shape checks because no verifier is wired yet.
- JWKS cache and key-rotation handling require careful deterministic tests before
  production enablement.
- The Notes/RLS design has no executable migration artifact. Any later migration
  and user-scoped validation must pass explicit security approval first.
- Contract drift can still appear between shared Zod schemas and FastAPI
  Pydantic models until the separate `Slice 6H-6` drift guard is completed.

## Rollback Notes

If Slice 6H-1 implementation is unsuitable, revert only that implementation.
Keep completed shared contracts, backend skeleton, API client methods, Slice
6E/6G auth/repository boundaries, Slice 6H plan, and the database artifact
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
