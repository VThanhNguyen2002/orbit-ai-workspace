# Next Action

## Objective

Recommended next task: **Slice 8C — Summary history UI/API consumption planning
or backend summary history persistence planning**.

Slice 8B is complete. Do not proceed to OpenAI live provider work, Supabase
live runtime, Docker, RLS, WIF runtime, SDK dependency installation, credential
use, frontend implementation, or persistence work unless those paths are
explicitly reopened or selected for the next approved slice.

## Slice 8B Result

Slice 8B adds summary history API client integration:

- `client.ai.listNoteSummaries(note_id)` calls
  `GET /v1/ai/notes/{note_id}/summaries`.
- the note id is URL-encoded consistently with the existing summarize method.
- successful responses return `{ data: { items }, meta }` through the existing
  success envelope style.
- the list payload is validated with the shared snake_case summary list
  contract.
- 404/error responses keep the existing `ApiClientError` behavior.
- focused API client tests cover path construction, valid list parsing, 404
  mapping, and camelCase rejection.

No shared contract shape change, backend route behavior change, SDK install,
dependency manifest change, lockfile change, credential, `.env` file, live API
call, WIF runtime, token exchange, live harness, route/client live OpenAI
behavior, SSE/frontend work, SQL, migration, Supabase work, `.gitleaksignore`
broadening, or generated Supabase state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Slice 8C Options

Choose one direction for Slice 8C:

- Summary history UI/API consumption planning: decide where the client method
  should be consumed and define UI/data-loading boundaries without implementing
  frontend UI yet.
- Backend summary history persistence planning: define storage, ownership,
  privacy, retention, and migration requirements before any persistence work.

## Live Provider And Supabase Status

- Fake provider remains the default.
- OpenAI live harness remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.
- Supabase/Docker/live RLS work remains out of scope unless explicitly
  approved.

## Definition Of Done

- Pick the 8C direction before implementation.
- Keep fake-provider-only backend behavior unchanged unless persistence planning
  explicitly changes the next approved scope.
- No live provider, SDK dependency, credential, `.env`, SQL/migration,
  Supabase generated state, Docker, or SSE/frontend implementation is
  introduced without approval.
- Verification and security checks pass for any approved changes.
