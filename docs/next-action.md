# Next Action

## Objective

Recommended next task: **Slice 7L-D — Prepare OpenAI live harness approval
evidence packet**.

Slice 7L-C is complete as a docs-only approval decision. The
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
now records the local-only live harness approval decision as **DENIED / NOT
GRANTED**.

Evidence review result:

- PRESENT: redacted evidence template.
- PRESENT: fail-closed config proof.
- MISSING: cost/budget approval evidence.
- MISSING: credential-mode decision evidence.
- MISSING: synthetic prompt fixture.
- MISSING: external review sign-off.
- INSUFFICIENT: security/privacy approval evidence.
- INSUFFICIENT: rollback/disable plan.
- INSUFFICIENT: no-default-CI proof.
- INSUFFICIENT: local-only boundary evidence.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7L-D Scope

Prepare the missing OpenAI live harness approval evidence packet without
granting approval, implementing the harness, or running live calls.

Include:

- Security/privacy approval evidence.
- Cost/budget ceiling proposal.
- Credential-mode decision proposal.
- Synthetic prompt fixture proposal.
- Rollback/disable plan evidence.
- No-default-CI proof.
- Local-only boundary evidence.
- External review sign-off request or denial record.

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

- Approval evidence preparation remains documentation-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Local-only approval remains denied/not granted unless a later evidence-backed
  record grants it.

## Risks

- Evidence preparation can be mistaken for permission to implement or run live
  provider calls.
- Credential-mode decisions must avoid normalizing long-lived keys or default
  CI network calls.
- Cost and retry guardrails must remain precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L-D:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
