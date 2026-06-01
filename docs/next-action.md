# Next Action

## Objective

Recommended next task: **Slice 7F — OpenAI provider integration planning**.

Slice 7E is complete. The backend now has:

- `apps/api/app/services/ai_prompting.py` prompt assembly for note
  summarization.
- Diagnostic redaction coverage for note title/content, prompt text, bearer/JWT
  values, provider API keys, Supabase key names, auth headers, and raw payload
  fields.
- Service wiring that builds a provider-facing prompt before invoking the fake
  provider.
- Route compatibility for `POST /v1/ai/notes/{note_id}/summarize` with the same
  snake_case fake-provider response shape.

## Slice 7F Scope

Plan OpenAI provider integration without enabling live runtime behavior by
default.

Include:

- Provider interface review for an eventual OpenAI implementation.
- Workload Identity Federation strategy and local fallback policy.
- Explicit opt-in gate for any live provider tests.
- Cost/usage tracking design.
- Failure-mode mapping for provider unavailable, timeout, rate limit, and
  malformed response.

Do not add OpenAI SDKs, provider credentials, `.env` files, default live network
  calls, frontend work, SSE streaming, SQL, migrations, Supabase generated state,
  or API client changes unless a future slice explicitly approves them.

## Commands To Run

For the next planning slice, prefer docs-focused verification plus existing
suite checks affected by any code changes:

```bash
python3 -m ruff check apps/api
python3 -m pytest apps/api/tests/test_ai_prompting.py apps/api/tests/test_ai_summarization.py
pnpm --filter @synapse/shared contracts:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
gitleaks detect --source=. --redact
```

## Definition Of Done

- OpenAI provider runtime remains deferred and disabled by default.
- No provider SDK, credential, `.env`, SQL, migration, Supabase state, frontend,
  or API client behavior is introduced without explicit approval.
- Credential strategy documents WIF first and local API-key fallback only for
  explicitly opted-in development.
- Live provider tests, if planned, are opt-in and skipped in default CI.
- Public errors and diagnostics continue to exclude note content, prompt text,
  token values, API keys, auth headers, and raw user payloads.

## Risks

- Provider planning could accidentally drift into runtime implementation.
- Local API-key fallback language must not normalize committed credentials.
- Usage/cost metadata can be useful, but raw prompt, note content, and response
  text must remain excluded from logs.
- SSE streaming and persisted summaries are still deferred; planning should not
  imply they are available.

## External Review Gate

Before proceeding beyond Slice 7F planning:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status, security observations, and unresolved risks.
2. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to OpenAI runtime implementation.
