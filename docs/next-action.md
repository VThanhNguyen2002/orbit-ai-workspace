# Next Action

## Objective

Recommended next task: **Slice 7J — Mocked WIF token exchange boundary tests**.

Slice 7I is complete. The docs-only
[OpenAI Workload Identity approval record](openai-workload-identity-approval-record.md)
now defines:

- Candidate WIF environments for GitHub Actions, future cloud runtime, and local
  fake-provider default.
- Approval requirements before any WIF implementation.
- Future GitHub Actions checklist for minimal permissions, branch/environment
  restrictions, fail-closed token exchange, and no live provider tests in
  default CI.
- Security risks for broad trust policy, token logging, accidental live cost,
  confused-deputy behavior, over-permissive workflows, and unreviewed API-key
  fallback.
- Fake-only testing strategy and current decision status.

No WIF runtime, token exchange, OpenAI SDK, provider credential, live provider
call, route behavior change, frontend work, SSE, SQL, migration, Supabase
generated state, or API client change has been added.

## Slice 7J Scope

Add mocked WIF token exchange boundary tests without implementing live token
exchange or provider runtime.

Include:

- A small token-exchange boundary/interface shape, if needed for tests.
- Fake or mocked token exchange only.
- Fail-closed tests for wrong issuer, audience, subject, repository/ref/workflow,
  denied exchange, malformed exchange response, and unavailable exchange.
- Redaction tests proving OIDC/JWT/access-token-shaped values do not appear in
  reprs, errors, logs, safe diagnostics, or public surfaces.
- Documentation that live WIF remains deferred.

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

- Live WIF runtime remains unimplemented.
- Token exchange is fake or mocked only.
- No provider SDK, credential, `.env`, SQL, migration, Supabase state, frontend,
  API client behavior, or public route behavior is introduced.
- Token, OIDC, JWT, API-key, auth-header, prompt, note-content, and raw payload
  logging remain prohibited.
- Default CI remains fake-only and network-free.

## Risks

- A mocked boundary could be mistaken for approved WIF runtime.
- Token-shaped fixtures can trigger secret scanners if they resemble real
  credentials.
- Claim validation tests must stay precise without embedding real issuer,
  subject, or token values.

## External Review Gate

Before proceeding beyond Slice 7J:

1. Include changed files, non-goals, deferred runtime behavior, verification
   evidence, CI status if checked, security observations, and unresolved risks.
2. Be explicit about anything scaffold-only, mocked/faked, intentionally
   deferred, or unresolved.
3. Do not automatically continue to live provider harness planning, GitHub
   Actions WIF setup, or WIF runtime work.
