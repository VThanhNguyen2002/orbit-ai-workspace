# Next Action

## Objective

Recommended next task: **Slice 8B — Summary history API client contract/client
integration**.

Slice 8A is complete. Do not proceed to OpenAI live provider work, Supabase
live runtime, Docker, RLS, WIF runtime, SDK dependency installation, or
credential use unless those paths are explicitly reopened with the required
approvals.

## Slice 8A Result

Slice 8A adds backend-only fake summary history:

- successful fake `POST /v1/ai/notes/{note_id}/summarize` calls are recorded in
  an in-memory history store.
- `GET /v1/ai/notes/{note_id}/summaries` returns recorded summaries for the
  authenticated owner of the note.
- repeated fake summaries append to history.
- missing, deleted, and cross-user notes keep safe 404 behavior.
- history stores only provider-safe summary fields already returned by the API,
  not prompt text, raw provider payloads, diagnostics, credentials, or live
  provider output.
- shared contracts include a snake_case `ListSummariesResponse` envelope.

No SDK install, dependency manifest change, lockfile change, credential, `.env`
file, live API call, WIF runtime, token exchange, live harness, route/client
live OpenAI behavior, SSE/frontend work, SQL, migration, Supabase work,
`.gitleaksignore` broadening, or generated Supabase state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 8B Scope

Summary history API client contract/client integration:

- add API client support for `GET /v1/ai/notes/{note_id}/summaries`.
- reuse the shared `ListSummariesResponse` contract.
- keep fake-provider-only backend behavior unchanged.
- do not add frontend UI, SSE, live provider behavior, credentials, Supabase,
  Docker, SQL, migrations, or OpenAI SDK dependency work.

## Live Provider And Supabase Status

- Fake provider remains the default.
- OpenAI live harness remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- Supabase/Docker/live RLS work remains out of scope for the next slice unless
  explicitly approved.

## Definition Of Done

- API client method and tests cover summary history list behavior.
- Shared contract usage stays snake_case.
- No live provider, SDK dependency, credential, `.env`, SQL/migration,
  Supabase generated state, Docker, or SSE/frontend work is introduced.
- Verification and security checks pass.
