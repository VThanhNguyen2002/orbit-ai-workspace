# Next Action

## Objective

Recommended next task: **Slice 7K — OpenAI provider live harness planning**.

Slice 7J is complete. The mocked WIF token exchange boundary now defines:

- Typed WIF subject metadata, exchange request/result objects, an exchanger
  protocol, a fake exchanger, and safe exchange errors.
- Deterministic fake exchange behavior with a synthetic short-lived access-token
  placeholder object.
- Fail-closed checks for unsupported issuer, audience, subject, repository,
  ref, workflow, unavailable exchange, and malformed exchange result cases.
- Redaction behavior that keeps raw identity assertion and fake access-token
  placeholder values out of reprs, error strings, and safe diagnostics.
- Tests proving no network socket use, no OpenAI SDK import requirement, no
  environment credential reads, no real-looking compact JWT fixtures, and
  exact-fingerprint-only `.gitleaksignore`.

No real WIF runtime, live token exchange, GitHub OIDC request, OpenAI SDK,
provider credential, live provider call, route behavior change, frontend work,
SSE, SQL, migration, Supabase generated state, or API client change has been
added.

## Slice 7K Scope

Plan an optional live OpenAI provider harness without implementing the harness
or enabling live provider calls by default.

Include:

- Harness objective, non-goals, and approval gates.
- Required opt-in controls for any future live provider test.
- Credential handling rules that keep fake provider and default CI
  credential-free.
- Cost, timeout, retry, and budget guardrails.
- Redaction and logging requirements for prompts, note content, provider
  responses, auth headers, tokens, API keys, and raw payloads.
- Clear separation between mocked tests, optional live harness planning, and any
  future runtime provider implementation.

Do not add OpenAI SDKs, provider credentials, `.env` files, real provider calls,
default live network behavior, WIF runtime, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migrations, Supabase generated state, API client
changes, or route behavior changes unless a future slice explicitly approves
them.

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

- Live provider harness remains planning-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Approval gates are explicit enough to prevent accidental live provider tests.

## Risks

- A live harness plan can be mistaken for permission to run live provider calls.
- Opt-in controls must avoid normalizing long-lived keys or default CI network
  calls.
- Cost and retry guardrails must be precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7K:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything planning-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to live harness implementation, GitHub Actions
   WIF setup, WIF runtime work, or live provider runtime wiring.
