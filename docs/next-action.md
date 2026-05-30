# Next Action

## Objective

Recommended next task: **Slice 6H-3B-4C-B4-R — Resolve Docker disk space
blocker manually**.

Slice 6H-3B-4C-B4 identified the root cause of the `supabase start` failure:
**disk exhausted (ENOSPC)**. Supabase images (~4.9 GB) were pulled successfully
but container layer writes consumed all remaining space on `/`. The startup
failed with `error running container: exit 1` and `supabase stop` also failed
with `ENOSPC`.

Cleanup: all Supabase images removed via `docker rmi` (~4.9 GB reclaimed).
Disk is now ~3.9 GB free (86% used) — still insufficient. At least 8–10 GB
free is needed before retrying.

See section 13 of
[notes-local-rls-dry-run-blocker-resolution.md](notes-local-rls-dry-run-blocker-resolution.md)
for exact disk cleanup steps.

Do not run Slice 6H-3B-4C-E3 until `supabase start` succeeds locally and the
full blocker-resolution checklist (section 11) is satisfied.



## Why This Is Next

RLS behavior has not been validated. B2 is complete. The only remaining blocker
is a human operator running the manual setup sequence in
[notes-local-rls-dry-run-blocker-resolution.md](notes-local-rls-dry-run-blocker-resolution.md)
sections 3–8. Until that setup is done outside git, E3 must not be attempted.

Hosted staging planning remains deferred until the local-only dry-run is either
completed with accepted evidence or explicitly deferred.

## Expected Files To Change

- A redacted local-only dry-run execution report, if the checklist is satisfied
  and the runbook is followed.
- A refreshed blocked report, if the checklist is still not satisfied.
- Minimal references from planning docs, if the re-attempt outcome changes
  status.

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, hosted staging workflow
execution, live Notes Supabase repository wiring, service-role request-path
usage, generated Supabase state, `.env` files, SQL files, migrations, or RLS
test execution outside the approved manual local-only runbook flow.

## Commands To Run

Before attempting E3, complete the manual setup sequence in
[notes-local-rls-dry-run-blocker-resolution.md](notes-local-rls-dry-run-blocker-resolution.md)
sections 3–8 outside git. Then satisfy the preflight checklist in section 11
before running any harness command.

Fast verification for docs-only slices:

```bash
git diff --check
python3 -m ruff check apps/api
python3 -m pytest apps/api/tests/integration/test_notes_rls_validation.py -q
pnpm dlx node-actionlint .github/workflows/ci.yml
gitleaks detect --source=. --redact
```

## Definition Of Done

- Missing local-only prerequisites are prepared outside git before execution,
  or execution remains explicitly blocked.
- No real URL, key, token, user identifier, note identifier, or note content is
  committed.
- The operator can prove that cleanup is actionable before retrying the dry-run.
- Hosted Supabase, staging, production, default CI, real data, credentials,
  service-role request-path usage, live repository mode, and public Notes API
  behavior remain out of scope.
- No SQL file, migration, `.env` file, credential, generated Supabase state,
  hosted resource access, or automatic RLS validation execution is introduced.

## Risks

- A retry could be mistaken for hosted or production permission unless the
  approved local-only scope is re-checked immediately before execution.
- Cleanup remains unproven until an actual disposable local target exists.
- Service-role values must remain outside request-path validation.
- The local-only dry-run remains blocked until local target and synthetic token
  inputs exist.
- A future successful local-only dry-run still will not prove hosted staging
  readiness.
- JWKS cache and key-rotation handling remain required before production
  Supabase authentication is enabled.

## External Review Gate

Before considering the next slice complete:

1. Render the full final report clearly and structurally.
2. Include runbook scope, non-goals, risks, deferred work, verification
   evidence, CI status, and security observations.
3. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
4. Do not automatically continue to hosted staging planning after rendering the
   report.
5. Wait for external ChatGPT review feedback before proceeding further.
