# Next Action

## Objective

Recommended next task: **Slice 7L-B — Resolve live harness approval
prerequisites**.

Slice 7L-A is complete as a docs-only denial slice. The
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
now records that local-only live harness approval is **NOT GRANTED** until
required prerequisites exist.

The denial reason is missing explicit evidence for:

- Security/privacy approval.
- Cost/budget approval.
- Credential-mode approval.
- Redaction evidence format.
- Rollback and disable plan.
- Local-only execution checklist evidence.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7L-B Scope

Resolve the live harness approval prerequisites without implementing or running
the harness.

Include:

- Security/privacy approval evidence.
- Cost/budget ceiling.
- Credential mode decision: API-key local-only or WIF future.
- Synthetic prompt fixture.
- Redacted evidence template.
- No-default-CI proof.
- Fail-closed config proof.
- Local-only execution boundary.
- Rollback and disable plan.
- External review gate.

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

- Live harness prerequisite resolution remains documentation-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Local-only approval remains not granted unless a later evidence-backed record
  grants it.

## Risks

- Prerequisite work can be mistaken for permission to implement or run live
  provider calls.
- Credential-mode resolution must avoid normalizing long-lived keys or default
  CI network calls.
- Cost and retry guardrails must be precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L-B:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
