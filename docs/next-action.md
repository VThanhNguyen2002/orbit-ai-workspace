# Next Action

## Objective

Recommended next task: **Slice 7L-C — Grant or deny local-only live harness
approval with evidence**.

Slice 7L-B is complete as a docs-only prerequisite packet. The
[OpenAI live harness prerequisites](openai-live-harness-prerequisites.md)
document prepares checklists and an evidence template for a future local-only
approval decision, while keeping live harness approval **NOT GRANTED**.

The prerequisite packet now covers:

- Security/privacy checklist.
- Placeholder-only cost/budget checklist.
- Credential-mode decision checklist.
- Redacted evidence template.
- Rollback/disable checklist.
- No-default-CI proof checklist.
- Local-only execution boundary.
- Remaining blockers.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7L-C Scope

Grant or deny local-only live harness approval with evidence, without
implementing or running the harness.

Include:

- Clear grant or denial decision.
- Link to approval record commit.
- Security/privacy evidence.
- Cost/budget evidence.
- Credential-mode evidence.
- Approved or rejected evidence format.
- Rollback/disable evidence.
- No-default-CI evidence.
- External review sign-off or explicit denial.

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
- Local-only approval remains not granted unless a later evidence-backed record
  grants it.

## Risks

- A future approval decision can be mistaken for permission to implement or run
  live provider calls before harness code exists.
- Credential-mode decisions must avoid normalizing long-lived keys or default
  CI network calls.
- Cost and retry guardrails must remain precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L-C:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
