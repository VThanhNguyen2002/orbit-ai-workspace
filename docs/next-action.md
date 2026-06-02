# Next Action

## Objective

Recommended next task: **Slice 7L-F — Resolve missing OpenAI live harness
approval evidence**.

Slice 7L-E is complete as a docs-only evidence fill. The
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
now contains explicit reviewer decision sections for all 8 required evidence
areas and a final decision matrix. Approval remains **DENIED / NOT GRANTED**.

Evidence review result (final, Slice 7L-E):

- PRESENT: redacted evidence template.
- PRESENT: fail-closed config proof.
- MISSING: cost/budget approval (`TBD_COST_BUDGET_REVIEWER` — no numeric values approved).
- MISSING: credential-mode decision (`TBD_CREDENTIAL_MODE_REVIEWER` — no mode selected).
- MISSING: synthetic prompt fixture review (`TBD_SYNTHETIC_FIXTURE_REVIEWER` — no fixture decision).
- MISSING: external review sign-off (`TBD_EXTERNAL_REVIEWER` — no sign-off of any kind exists).
- INSUFFICIENT: security/privacy approval (`TBD_SECURITY_PRIVACY_REVIEWER` — no explicit sign-off).
- INSUFFICIENT: rollback/disable plan review (`TBD_ROLLBACK_REVIEWER` — no named owner or sign-off).
- INSUFFICIENT: no-default-CI proof review (`TBD_CI_REVIEWER` — no explicit proof artifact).
- INSUFFICIENT: local-only boundary review (`TBD_LOCAL_BOUNDARY_REVIEWER` — no approved runbook or sign-off).

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7L-F Scope

Resolve missing or insufficient evidence items required for OpenAI live harness
approval. For each item, obtain an explicit reviewer decision (sign-off,
numeric values, named owner, or explicit denial) or record a permanent denial
entry. Do not grant approval unless all required evidence items are explicitly
PRESENT and approved by a named reviewer.

Include:

- Security/privacy reviewer explicit sign-off or explicit denial entry.
- Cost/budget reviewer explicit numeric approval or explicit denial entry.
- Credential-mode reviewer decision (mode selected or explicitly denied).
- Synthetic prompt fixture reviewer decision (approved description or denial).
- Rollback/disable plan approval with named owner or explicit denial.
- No-default-CI proof artifact or explicit gap acknowledgement.
- Local-only boundary runbook approval with named reviewer or explicit denial.
- External review sign-off or explicit denial entry.

Do not add OpenAI SDKs, provider credentials, `.env` files, real provider
calls, live harness code, WIF runtime, token exchange, GitHub Actions WIF
wiring, frontend work, SSE streaming, SQL, migrations, Supabase generated
state, API client changes, or route behavior changes unless a later slice
explicitly approves them.

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

- Approval evidence remains documentation-only.
- No OpenAI SDK, provider credential, `.env`, SQL, migration, Supabase state,
  frontend, API client behavior, public route behavior, WIF runtime, or live
  token exchange is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, provider
  response, and raw payload logging remain prohibited.
- Default CI remains fake-only and network-free.
- Local-only approval remains denied/not granted unless all required evidence
  items are explicitly PRESENT and approved by a named reviewer.

## Risks

- Reviewer-decision collection can be mistaken for permission to implement or
  run live provider calls.
- Evidence items marked INSUFFICIENT could be prematurely upgraded to PRESENT
  without actual reviewer sign-off.
- Credential-mode decisions must avoid normalizing long-lived keys or default
  CI network calls.
- Cost and retry guardrails must remain precise before any implementation slice.

## External Review Gate

Before proceeding beyond Slice 7L-F:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything unapproved, planning-only, mocked/faked,
   intentionally deferred, or unresolved.
3. Do not automatically continue to SDK adapter planning, live harness
   implementation, GitHub Actions WIF setup, WIF runtime work, or live provider
   runtime wiring.
