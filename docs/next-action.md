# Next Action

## Objective

Recommended next task: **Slice 7L — OpenAI live harness approval record**.

Slice 7K is complete as a docs-only planning slice. The
[OpenAI live provider harness plan](openai-live-provider-harness-plan.md)
documents a future optional live OpenAI provider validation harness without
implementing the harness, adding an SDK, adding credentials, exchanging tokens,
calling OpenAI, changing CI defaults, or wiring the OpenAI adapter into runtime
selection.

The plan now defines:

- Harness modes for default CI, local opt-in, future GitHub Actions opt-in, and
  hosted/staging.
- Required opt-in variables for any future live harness.
- Credential handling rules that keep fake provider and default CI
  credential-free.
- Synthetic-prompt-only live test boundaries.
- Redaction and logging rules for note content, prompt text, provider response
  bodies, auth headers, API keys, OIDC/JWT values, access tokens, and raw user
  payloads.
- Safety stop conditions for missing credentials, unsupported auth mode, real
  data, token logging risk, budget overrun, unsafe/malformed output,
  out-of-harness network calls, and unredactable evidence.
- Cost, timeout, retry, request-count, and token guardrails.
- Approval requirements before any live harness implementation.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, or route behavior change has been added.

## Slice 7L Scope

Create an approval record for the future OpenAI live provider harness without
implementing the harness.

Include:

- Security approval status.
- Cost approval status.
- Credential-mode decision status.
- Redaction evidence format.
- Rollback and disable plan.
- Explicit confirmation that live provider tests remain out of default CI.
- External review gate.
- Decision status for local opt-in, GitHub Actions opt-in, and hosted/staging
  modes.

Do not add OpenAI SDKs, provider credentials, `.env` files, real provider calls,
live harness code, WIF runtime, token exchange, GitHub Actions WIF wiring,
frontend work, SSE streaming, SQL, migrations, Supabase generated state, API
client changes, or route behavior changes unless a later slice explicitly
approves them.

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

- Live provider harness approval remains documentation-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Approval status is explicit enough to prevent accidental live provider tests.

## Risks

- An approval record can be mistaken for permission to implement or run live
  provider calls.
- Credential-mode approval must avoid normalizing long-lived keys or default CI
  network calls.
- Cost and retry guardrails must remain precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
