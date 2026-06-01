# Next Action

## Objective

Recommended next task: **Slice 7I — Workload Identity Federation
planning/approval record**.

Slice 7H is complete. The backend now has:

- Future OpenAI config fields for provider mode, model, timeout, retry budget,
  request budget, and auth mode.
- Fail-closed parsing for unsupported AI provider and OpenAI auth mode values.
- Runtime validation that rejects OpenAI `api_key` and `workload_identity`
  modes until those credential paths are explicitly implemented.
- Tests proving defaults remain fake-only, disabled, credential-free, and
  network-free.
- Tests proving OpenAI config does not switch the summarization route away from
  `FakeSummarizationProvider`.

No OpenAI SDK, provider credential, live provider call, WIF runtime, route
behavior change, frontend work, SSE, SQL, migration, Supabase generated state,
or API client change has been added.

## Slice 7I Scope

Create a Workload Identity Federation planning and approval record. Keep this
docs-only unless a future slice explicitly approves implementation.

Include:

- Threat model for CI/cloud token exchange.
- Required issuer, audience, subject, repository, branch/ref, and workflow
  constraints.
- Required secret handling and redaction behavior.
- Approval checklist before any WIF runtime work.
- Fallback policy for API-key mode as explicitly reviewed local/cloud fallback.
- Test plan using fake token exchange only.

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

- WIF runtime remains unimplemented.
- No provider SDK, credential, `.env`, SQL, migration, Supabase state, frontend,
  API client behavior, or public route behavior is introduced.
- Approval requirements are explicit enough to block accidental token exchange
  implementation.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, and raw payload
  logging remain prohibited.

## Risks

- WIF planning can sound like runtime readiness; keep approval and non-runtime
  language explicit.
- Claim constraints must be precise enough for future implementation review.
- API-key fallback policy must not normalize long-lived credentials as the
  preferred path.

## External Review Gate

Before proceeding beyond Slice 7I:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to mocked OpenAI runtime, WIF runtime, or live
   provider harness work.
