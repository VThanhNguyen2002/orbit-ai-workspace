# Next Action

## Objective

Recommended next task: **Slice 7L-A — Grant or deny local-only live harness
approval constraints**.

Slice 7L is complete as a docs-only approval-record slice. The
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
sets approval status to pending/not granted and records that live harness
execution is not approved yet.

The record now defines:

- Current approval status: pending/not granted.
- Candidate local-only synthetic smoke-test scope, not yet granted.
- Explicitly not approved items, including production/staging execution,
  default CI live tests, GitHub Actions WIF wiring, real OIDC/JWT exchange,
  committed keys, committed `.env` files, route switch to OpenAI, background
  summarization, and persisted live provider outputs.
- Required approvals before execution.
- Required pre-execution checklist.
- Credential handling constraints.
- Stop conditions.
- Evidence requirements.
- Relationship to WIF.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7L-A Scope

Grant or deny local-only live harness approval constraints without implementing
the harness.

Include:

- A clear grant or denial decision for local-only live smoke testing.
- Security/privacy decision.
- Cost/budget decision.
- Credential-mode decision.
- Redaction evidence format decision.
- Rollback and disable plan decision.
- No-default-CI confirmation.
- External review gate decision.
- Remaining conditions that must be satisfied before any harness skeleton can
  be implemented.

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

- Local-only live harness approval decision remains documentation-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Grant or denial status is explicit enough to prevent accidental live provider
  tests.

## Risks

- A grant/deny record can be mistaken for permission to implement or run live
  provider calls without satisfying every condition.
- Credential-mode decisions must avoid normalizing long-lived keys or default CI
  network calls.
- Cost and retry guardrails must remain precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L-A:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
