# Next Action

## Objective

Recommended next task: **Slice 7H — OpenAI config and credential-mode
validation**.

Slice 7G is complete. The backend now has:

- `apps/api/app/services/openai_provider.py` as a network-free provider adapter
  boundary.
- Internal OpenAI request/response DTOs with prompt/content hidden from reprs.
- An injected transport protocol with no SDK, HTTP client, environment lookup,
  credential input, or network behavior.
- Safe provider errors and redacted diagnostics for timeout, unavailable, and
  malformed-response paths.
- Fake transport tests proving request construction, synthetic success mapping,
  no-network behavior, no SDK import requirement, and diagnostic redaction.

The adapter is not wired into the API route. `FakeSummarizationProvider` remains
the default runtime provider for local development, tests, and CI.

## Slice 7H Scope

Add future OpenAI configuration and credential-mode validation without enabling
live provider runtime behavior.

Include:

- Typed settings for future OpenAI model, timeout, retry budget, request budget,
  and auth mode.
- Validation that defaults remain fake-only and credential-free.
- Credential-mode parsing for `fake`, `api_key`, and `workload_identity` as
  configuration shape only.
- Tests proving invalid config fails closed and no secrets are required for the
  fake/default path.
- Docs clarifying that live provider calls and WIF runtime remain deferred.

Do not add OpenAI SDKs, provider credentials, `.env` files, real provider calls,
default live network behavior, WIF runtime, frontend work, SSE streaming, SQL,
migrations, Supabase generated state, API client changes, or route behavior
changes unless a future slice explicitly approves them.

## Commands To Run

Use bounded commands for anything that may hang:

```bash
pnpm install --frozen-lockfile

cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/shared contracts:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build

gitleaks detect --source=. --redact
pnpm dlx node-actionlint .github/workflows/ci.yml
```

## Definition Of Done

- Defaults remain fake-only, credential-free, and network-free.
- Future OpenAI settings are typed and validated without reading provider
  credentials in the adapter.
- Invalid provider/auth-mode config fails closed.
- No provider SDK, credential, `.env`, SQL, migration, Supabase state, frontend,
  API client behavior, or public route behavior is introduced.
- Public errors and diagnostics continue to exclude note content, prompt text,
  token values, API keys, auth headers, and raw user payloads.

## Risks

- Config scaffolding could accidentally become runtime provider selection.
- Auth-mode names can imply readiness; docs and tests must keep `api_key` and
  `workload_identity` non-runtime until explicitly approved.
- Default CI must not require provider secrets or live network access.

## External Review Gate

Before proceeding beyond Slice 7H:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to WIF planning, mocked OpenAI runtime, or live
   provider harness work.
