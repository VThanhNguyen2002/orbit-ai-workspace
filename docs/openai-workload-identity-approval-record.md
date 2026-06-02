# OpenAI Workload Identity Approval Record

## Objective

Document the approval requirements for a future Workload Identity Federation
(WIF) authentication path for OpenAI provider access. This record is a planning
and security gate only. It does not implement token exchange, provider runtime
authentication, live OpenAI calls, or CI/cloud identity wiring.

## Non-Goals

This record explicitly excludes:

- WIF runtime implementation.
- Token exchange implementation.
- OpenAI SDK or provider dependency installation.
- Live OpenAI API calls.
- Provider credentials.
- `.env` files.
- Long-lived provider key setup.
- GitHub Actions WIF configuration changes.
- Cloud runtime identity configuration changes.
- Backend route behavior changes.
- API client changes.
- SSE streaming.
- SQL, migrations, or Supabase/RLS work.
- Production deployment.

## Current Baseline

The backend still uses `FakeSummarizationProvider` for the summarization route:

```text
POST /v1/ai/notes/{note_id}/summarize
```

Slice 7G added a network-free OpenAI provider adapter boundary with an injected
transport protocol and fake transport tests. The adapter is not wired into the
runtime route.

Slice 7H added future OpenAI config shape and fail-closed validation. Defaults
remain fake-only, disabled, credential-free, and network-free. The `api_key` and
`workload_identity` auth modes are accepted as future configuration names but
are rejected by runtime validation because neither credential path is
implemented.

Slice 7J adds a mocked, internal token exchange boundary with fake exchanger
tests only. It is not wired into provider selection, routes, GitHub Actions, or
any live credential flow.

No OpenAI SDK, provider credentials, live token exchange, WIF runtime, live
provider calls, or route behavior changes exist.

## WIF Concept Summary

Workload Identity Federation lets a workload exchange a short-lived,
trusted-issuer identity assertion for short-lived credentials scoped to a target
provider or cloud identity. The intended benefit is avoiding long-lived provider
keys in CI and cloud environments.

For Synapse, WIF remains a preferred future direction only where the chosen
provider and deployment environment support a narrowly scoped, auditable
exchange. Any implementation must fail closed, redact token-exchange
diagnostics, and avoid printing or storing raw identity assertions or exchanged
credentials.

## Candidate Environments

### GitHub Actions

GitHub Actions may be considered for future WIF-based opt-in provider tests or
deployment workflows. It must not be used for live provider tests in default CI.
Any future workflow must use minimal permissions and request identity tokens only
in jobs that need the exchange.

### Future Cloud Runtime

A future cloud runtime may use workload identity if the deployment platform and
provider support scoped identity exchange. Runtime identity configuration must
be reviewed separately from GitHub Actions because issuer, audience, subject,
service account mapping, and network boundaries differ.

### Local Development

Local development remains fake-provider-first. WIF is not required for local
tests. Any local provider fallback must remain explicitly opt-in, gitignored,
and excluded from default test and CI paths.

## Approval Requirements Before Implementation

Before any WIF runtime work starts, all of the following must be approved:

- The target provider and environment are selected.
- Issuer constraints are documented.
- Audience constraints are documented.
- Subject constraints are documented.
- Repository, branch/ref, workflow, and environment constraints are documented
  where GitHub Actions is involved.
- Service account or provider identity mapping is reviewed.
- Trust policy is narrow and contains no broad repository, organization, branch,
  wildcard, or unconstrained subject access.
- No raw OIDC or JWT values may be logged.
- No short-lived access token values may be logged.
- No long-lived provider API key may be committed.
- Rollback and disable plan is documented.
- Threat model is updated for token exchange and confused-deputy risk.
- CI permissions are reviewed before workflow changes.
- Cost, rate, and live-test opt-in controls are reviewed.
- Public errors and diagnostics remain redacted.

Implementation must not begin until the approval record is updated with the
chosen environment, exact constraints, and reviewer acceptance.

## GitHub Actions Future Checklist

Any future GitHub Actions WIF workflow must satisfy this checklist:

- Use minimal repository permissions.
- Grant identity-token permission only on jobs that perform token exchange.
- Restrict workflow execution by branch, tag/ref, environment, or manual approval
  as appropriate for the selected use case.
- Avoid broad subject patterns.
- Avoid broad audience values.
- Never print raw identity assertions.
- Never print exchanged access credentials.
- Never write identity assertions or exchanged credentials to artifacts.
- Never upload artifacts containing provider request headers or credentials.
- Fail closed if token exchange fails.
- Keep live provider tests out of default CI.
- Keep live provider tests behind an explicit opt-in flag and review gate.
- Redact token-exchange diagnostics before logging.

## Security Risks

| Risk | Concern | Required Mitigation |
|---|---|---|
| Broad subject or audience | A trusted issuer could mint credentials for unintended jobs or branches. | Strict issuer, audience, subject, repository, ref, workflow, and environment constraints. |
| Token logging | Raw identity assertions or exchanged credentials could leak through logs. | No raw token logging; redacted diagnostics only. |
| Accidental live cost usage | CI could run live provider calls unexpectedly. | No live provider tests in default CI; explicit opt-in only. |
| Confused deputy | A workflow could obtain credentials for a target it should not access. | Narrow trust policy and service account mapping review. |
| Over-permissive workflow | Excessive GitHub permissions can widen blast radius. | Minimal permissions and job-scoped identity-token access. |
| Unreviewed API-key fallback | Long-lived key fallback could become the de facto production path. | Explicit fallback review; no production API-key approval in this record. |

## Testing Strategy

Future WIF tests must remain fake by default:

- Fake WIF exchange tests only in normal CI.
- Mocked token exchange only.
- No live token exchange in default tests.
- No live OpenAI tests in default tests.
- Redaction tests for OIDC/JWT/access-token-shaped values.
- Failure tests for missing issuer, wrong audience, wrong subject, wrong
  repository/ref/workflow, denied exchange, and malformed exchange response.
- Tests must prove raw identity assertions and exchanged credentials do not
  appear in reprs, stringified errors, public errors, logs, or artifacts.

## Decision Status

- WIF is preferred for future CI/cloud provider authentication where supported.
- WIF runtime is not approved for implementation yet.
- API-key fallback is not approved for production.
- API-key fallback may only be considered in a later explicitly reviewed local or
  cloud fallback slice.
- Any implementation requires a later approval slice with exact provider,
  environment, issuer, audience, subject, service account mapping, rollback, and
  test plan.

## Future Slices

- **Slice 7K — OpenAI provider live harness planning.**
- **Slice 7L — OpenAI live harness approval record.**
- **Slice 7L-A — Grant or deny local-only live harness approval constraints.**
- **Slice 7O — Optional workflow_dispatch live provider validation planning.**

Do not proceed from this approval record to WIF runtime implementation without a
separate explicit approval.

## Slice 7J Update — 2026-06-01

Slice 7J adds `apps/api/app/services/openai_workload_identity.py` as a mocked,
network-free WIF token exchange boundary. The module defines typed request,
subject, result, protocol, fake exchanger, and safe error objects. Raw identity
assertions and fake access-token placeholders are excluded from reprs, error
strings, and safe diagnostics.

Tests cover deterministic fake exchange, required issuer/audience/subject
metadata, unsupported claim fail-closed behavior, unavailable exchange,
malformed exchange result handling, no-network behavior, no OpenAI SDK import
requirement, no environment credential reads, synthetic token shape hygiene, and
exact-fingerprint-only `.gitleaksignore` entries.

This remains scaffold-only. No real token exchange, WIF runtime, GitHub OIDC
request, provider SDK, credential, API call, route wiring, GitHub Actions
workflow, SQL, migration, Supabase state, SSE, frontend, or API client change is
approved or implemented.

## Slice 7K Update — 2026-06-02

Slice 7K adds the docs-only
[OpenAI live provider harness plan](openai-live-provider-harness-plan.md). The
plan keeps WIF preferred for any future CI/cloud credential path where supported
but does not approve WIF runtime, GitHub OIDC token requests, token exchange, or
workflow wiring.

Any future live harness using WIF still requires explicit security, cost,
credential-mode, redaction evidence, rollback/disable, and no-default-CI
approval before implementation.

## Slice 7L Update — 2026-06-02

Slice 7L adds the docs-only
[OpenAI live harness approval record](openai-live-harness-approval-record.md).
That record keeps live harness execution pending/not granted and does not approve
WIF runtime, GitHub Actions OIDC wiring, real OIDC/JWT exchange, token exchange,
or exchanged credential use.

WIF approval remains separate from live harness execution approval. Any WIF
candidate still requires a future approval record with exact constraints before
implementation.

## Definition of Done

This slice is complete when:

- The WIF approval record exists.
- Existing provider/security planning docs link to the record.
- `docs/next-action.md` points to the next approved planning task.
- Verification passes without runtime code changes.
- No SDK, credential, live token exchange, WIF runtime, API call, `.env` file,
  SQL, migration, Supabase state, SSE, frontend, route behavior, or API client
  change is introduced.
- `.gitleaksignore` remains exact-fingerprint only.
