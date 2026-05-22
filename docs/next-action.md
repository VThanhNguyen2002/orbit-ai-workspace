# Next Action

## Objective

Start Slice 6E — Notes Supabase persistence/auth implementation. The shared
Notes CRUD contracts, FastAPI route skeleton, API client methods, and Slice 6D
persistence/auth integration plan are in place. The next step should implement
the planned migration, auth dependency, RLS-aware repository, and tests.

## Expected Files To Change

- `apps/api/pyproject.toml` for explicit auth/Supabase dependencies if needed
- `apps/api/app/core/config.py`
- `apps/api/app/core/deps.py` or equivalent auth dependency module
- `apps/api/app/repositories/notes.py`
- `apps/api/app/services/notes.py` only if the repository contract needs a small
  adjustment
- `apps/api/app/routers/notes.py` to replace `dev_user`
- migration files for `public.notes` and RLS
- API tests for auth, persistence, and cross-user isolation

Do not add provider secrets, frontend screens, Expo initialization, API client
methods, sync engine implementation, AI behavior, or service-role usage in
request handlers.

## Commands To Run

```bash
cd apps/api
python -m ruff check .
python -m pytest
cd ../..

pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm --filter @synapse/shared contracts:check
```

## Definition Of Done

- Notes routes no longer use `dev_user`.
- Notes routes require bearer auth except public health/version routes.
- `public.notes` migration includes columns, checks, indexes, and RLS from the
  Slice 6D plan.
- Request-path Supabase access is user-scoped and does not use service role.
- Update/delete remain version-gated and soft-delete only.
- Missing/deleted/cross-user notes return `404`; stale versions return `409`.
- Tests cover unauthenticated access, cross-user isolation, conflicts, and soft
  delete behavior.
- No provider secrets, UI, sync engine, or AI code is added.

## Risks

- Supabase integration can make tests environment-dependent if fakes are not
  preserved for baseline CI.
- RLS mistakes can either block valid own-user access or expose cross-user data.
- Auth placeholder replacement must preserve non-enumerating `404` behavior.
- Service-role credentials must not enter request-handling code.

## Rollback Notes

Revert only Slice 6E persistence/auth implementation files if route sequencing
changes. Keep completed shared contracts, backend skeleton, API client methods,
and Slice 6D plan intact.
