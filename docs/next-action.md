# Next Action

## Objective

Recommended next task: **Slice 7G — OpenAI provider adapter interface and fake
transport tests**.

Slice 7F is complete. The docs-only
[OpenAI provider integration plan](openai-provider-integration-plan.md) now
defines:

- Future provider adapter boundaries.
- Fake provider default behavior for local/test/CI.
- Credential strategy and Workload Identity Federation requirements.
- Config, request/response, failure-mode, security, testing, and cost plans.
- Future slices 7G through 7K.

## Slice 7G Scope

Add the first implementation-facing provider adapter boundary without live
provider runtime behavior.

Include:

- A concrete adapter interface shape for a future OpenAI summarization provider.
- Fake transport or mocked transport tests only.
- Error/result models needed to test the adapter boundary safely.
- Tests proving no network access, SDK dependency, credentials, raw prompt, note
  content, tokens, API keys, auth headers, or provider raw payloads leak through
  diagnostics.

Do not add OpenAI SDKs, real provider calls, provider credentials, `.env` files,
default live network behavior, WIF runtime, frontend work, SSE streaming, SQL,
migrations, Supabase generated state, or API client changes unless a future
slice explicitly approves them.

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

- Adapter/interface work remains network-free by default.
- Fake provider remains the default local/test/CI path.
- No provider SDK, credential, `.env`, SQL, migration, Supabase state, frontend,
  or API client behavior is introduced without explicit approval.
- Any provider errors or diagnostics are redacted before logging or public
  response handling.
- Public endpoint behavior and shared-contract-compatible response shape remain
  unchanged.

## Risks

- Adapter scaffolding could drift into live provider implementation.
- Fake transport tests must not normalize adding real SDK dependencies.
- Diagnostic coverage must account for provider raw payloads and transport
  errors without preserving sensitive strings.
- WIF and API-key credential modes remain planning/config topics until later
  approved slices.

## External Review Gate

Before proceeding beyond Slice 7G:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to config, WIF, mocked OpenAI runtime, or live
   provider harness work.
