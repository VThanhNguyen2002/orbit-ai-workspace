# OpenAI Live Provider Harness Plan

## Status

Slice 7K is a documentation-only planning slice for a future opt-in live OpenAI
provider validation harness. Slice 7L adds the
[OpenAI live harness approval record](openai-live-harness-approval-record.md)
with approval status still pending, and Slice 7L-A records that local-only live
harness approval is not granted until prerequisites exist. Slice 7L-B adds the
[OpenAI live harness prerequisites](openai-live-harness-prerequisites.md)
packet without granting approval. These docs do not implement the harness,
install an OpenAI SDK, add credentials, exchange tokens, call OpenAI, change CI
defaults, wire the OpenAI adapter into runtime selection, or alter public API
behavior.

## 1. Objective

Plan how a future opt-in live OpenAI provider validation harness could prove
smoke-level compatibility with a live provider while keeping the current Synapse
runtime fake-provider-first, credential-free by default, and network-free in
normal local tests and CI.

The future harness would be a narrow validation tool only. It would not be the
runtime provider implementation, a production readiness gate, a CI default, or
approval to send user data to OpenAI.

## 2. Non-Goals

This plan explicitly excludes:

- OpenAI SDK dependency installation.
- Real OpenAI API calls.
- Provider credentials.
- `.env` files.
- WIF runtime implementation.
- Token exchange implementation.
- GitHub Actions WIF wiring.
- Default CI live tests.
- Backend route changes.
- API client changes.
- SSE, frontend, or Supabase work.
- SQL, migrations, or generated Supabase state.
- Production deployment.

## 3. Current Baseline

The backend already exposes a note summarization route backed by
`FakeSummarizationProvider`. The fake provider is deterministic, network-free,
credential-free, and remains the default provider for local development, tests,
and CI.

The prompt builder and diagnostic redaction boundary exists in
`apps/api/app/services/ai_prompting.py`. It builds provider-facing prompt
objects from explicit note title/content inputs and keeps raw prompt text, note
content, note title, tokens, API-key-shaped values, auth headers, and Supabase
key names out of safe diagnostic surfaces.

The API client already exposes `client.ai.summarizeNote(note_id)` against the
existing backend route. No new client method is needed for this planning slice.

`apps/api/app/services/openai_provider.py` defines a network-free OpenAI adapter
boundary with injected transport and fake transport tests. It reads no
credentials, imports no OpenAI SDK, creates no HTTP client, and is not wired
into runtime provider selection.

`apps/api/app/services/openai_workload_identity.py` defines a mocked WIF token
exchange boundary with fake exchanger tests only. It performs no real token
exchange, reads no environment credentials, requests no GitHub OIDC token, and
is not wired into OpenAI provider auth.

`apps/api/app/core/config.py` accepts future OpenAI provider and auth-mode names
but fails closed for live runtime paths. Fake provider mode remains the only
runtime-enabled default. The live OpenAI provider remains unimplemented.

## 4. Harness Modes

### Default CI

Default CI remains fake-only, network-free, and credential-free. It may run
mocked transport, prompt redaction, config validation, and fake-provider tests.
It must not run live OpenAI tests, request credentials, exchange tokens, or make
provider network calls.

### Local Opt-In

A future local live harness may run only when an engineer explicitly sets the
live harness flag, live mode, provider, and auth mode. Local mode may use a
gitignored shell environment or local secret manager only after a separately
approved implementation slice. It must use synthetic prompt content and must
not read real notes or production data.

### GitHub Actions Opt-In

A future GitHub Actions live harness is not approved by this plan. If approved
later, it must be manual, protected, and separate from normal push CI. It must
use minimal permissions, protected environments where credentials are involved,
and no artifact/log output that contains tokens, provider request headers,
prompt text, note content, or raw provider bodies.

### Hosted Or Staging

Hosted or staging live-provider validation is not approved yet. Any hosted mode
requires a separate approval record covering environment, credentials, network
egress, data boundaries, cost controls, retention policy, rollback, and disable
plan.

## 5. Required Opt-In Gating

A future live harness must fail closed unless all required opt-in controls are
present and valid. Placeholder variable names for a later implementation:

| Variable | Required placeholder value |
|---|---|
| `SYNAPSE_OPENAI_LIVE_TESTS` | `1` |
| `SYNAPSE_OPENAI_LIVE_MODE` | `local` or `ci_opt_in` |
| `SYNAPSE_AI_PROVIDER` | `openai` |
| `SYNAPSE_OPENAI_AUTH_MODE` | `api_key` or `workload_identity` |

These names are placeholders for future planning only. This slice does not add
environment reads, real values, defaults, secrets, or test harness code.

The future harness must reject unsupported modes, missing budget configuration,
missing timeout configuration, missing credential configuration, and any attempt
to run in normal default CI.

## 6. Credential Handling Rules

- Commit no credentials.
- Put no real credential values in docs.
- Do not commit `.env` files.
- Do not print raw token, key, header, identity assertion, or access-token
  values.
- Keep API-key fallback local-only unless separately approved.
- Prefer WIF for future CI/cloud auth where supported, but do not implement WIF
  in this slice.
- Keep fake provider as the default local, test, and CI provider.
- Store future approved credentials only in an appropriate local shell,
  gitignored local file, local secret manager, CI protected environment, or
  deployment secret manager.
- Keep provider credentials out of public config dumps, reprs, errors, logs,
  screenshots, artifacts, and client bundles.

## 7. Live Test Boundaries

A future live test may prove only smoke-level provider compatibility. It must
use a small synthetic prompt with no real note content, no user PII, no
production data, and no hidden or background summarization.

Required boundaries:

- Use synthetic content created for the harness.
- Never read from the Notes repository for live provider input.
- Never include user email, display name, auth token, internal IDs, or Supabase
  credentials in the prompt.
- Enforce strict request timeout.
- Enforce strict retry count.
- Enforce strict max prompt length.
- Enforce strict max output tokens.
- Enforce a per-run cost/request budget.
- Fail before the provider call if the budget cannot be evaluated.
- Clean up or redact any local evidence artifacts.
- Never execute in default CI.

## 8. Redaction And Logging Rules

Future live harness diagnostics must be redacted by default:

- No note content logs.
- No prompt text logs.
- No OpenAI raw response body logs if it may include prompt or content.
- No auth headers.
- No API key values.
- No OIDC, JWT, or access-token values.
- No raw user payloads.
- Redacted diagnostics only.

Allowed diagnostics are coarse metadata such as provider name, model name,
operation name, configured mode name, timeout category, retry count, coarse token
counts, estimated cost bucket, request budget pass/fail, and redacted failure
code. Raw request and response bodies must stay out of logs and artifacts.

## 9. Safety Stop Conditions

A future live harness must stop before or during execution if:

- Credentials are missing.
- Auth mode is unsupported.
- Required explicit opt-in gates are absent.
- Real note content, user PII, or production data appears in the candidate
  prompt.
- Tokens, keys, auth headers, identity assertions, access tokens, prompts, note
  content, raw provider bodies, or raw payloads would be logged.
- Request budget is missing or exceeded.
- Timeout or retry bounds are missing.
- The provider returns unsafe, empty, malformed, or unvalidated output.
- Any network call is attempted outside the opt-in harness.
- Cleanup or evidence cannot be redacted.
- The harness is running under normal push CI.

## 10. Testing Strategy

Existing fake tests remain the default test path. Mocked transport tests
continue to prove adapter behavior without network access, credentials, SDK
imports, or environment reads.

Future live harness tests must be skipped by default and must require explicit
opt-in. They may prove only smoke-level compatibility with the selected provider
and auth mode. They must not become release gates, normal CI checks, or required
local developer checks without a separate approval.

Default coverage should continue to prove:

- Fake provider remains the runtime default.
- OpenAI adapter behavior is verified with injected fake transport.
- WIF exchange behavior is verified with fake exchange only.
- Redaction excludes prompt text, note content, auth headers, API keys, OIDC/JWT
  values, access-token values, and raw payloads.
- Runtime config fails closed for unimplemented live modes.

## 11. CI And GitHub Actions Considerations

Normal push CI must not run live OpenAI tests.

A future approved GitHub Actions option should use `workflow_dispatch` only,
environment protection before credentials or WIF are available, minimal
permissions, no broad OIDC trust, and no artifact upload containing tokens,
provider headers, prompts, raw provider responses, or raw payloads.

Any future OIDC/WIF workflow must constrain issuer, audience, subject,
repository, ref, workflow, and environment. Identity-token permission must be
job-scoped and present only where token exchange is needed. Broad repository,
organization, branch, wildcard, or unconstrained subject trust is not allowed.

## 12. Cost And Token Strategy

A future live harness must define all budget settings before any provider call:

- Maximum prompt length.
- Maximum output tokens.
- Maximum retries.
- Maximum timeout.
- Per-run request count ceiling.
- Per-run cost ceiling.
- Fail-closed behavior when budget config is missing.
- Coarse usage metadata only.

Usage evidence may record provider, model, operation, coarse input/output token
counts, request count, elapsed duration bucket, and estimated cost bucket. It
must not include note content, prompt text, raw response body, credentials,
provider headers, auth headers, identity assertions, access tokens, or raw
payloads.

## 13. Approval Requirements Before Implementation

Before any live harness implementation starts, the following must be approved:

- Security approval.
- Cost approval.
- Credential-mode approval.
- Redaction evidence format.
- Rollback and disable plan.
- Confirmation that live tests remain out of default CI.
- External engineering/security review gate.
- Synthetic prompt content and output validation criteria.
- CI or local execution mode boundaries.

Approval must not be inferred from this plan. The next slice must record the
approval decision before skeleton or runtime work begins.

Slice 7L records the approval gate and keeps status as pending/not granted. Any
future local-only live harness run still requires a later grant or denial record
with explicit constraints.

Slice 7L-A denies local-only live harness approval until the repository contains
security/privacy approval, cost/budget ceiling, credential-mode decision,
synthetic prompt fixture, redacted evidence template, no-default-CI proof,
fail-closed config proof, local-only execution boundary, rollback/disable plan,
and external review gate evidence.

Slice 7L-B prepares those prerequisite checklists and a redacted evidence
template. It does not approve execution, credentials, SDK/runtime work, WIF, or
live API calls.

Slice 7L-C reviews the available evidence and denies local-only live harness
approval. The evidence packet lacks explicit security/privacy approval,
cost/budget approval values, credential-mode decision, synthetic prompt fixture,
approved rollback/disable plan, no-default-CI proof, local-only boundary
evidence, and external review sign-off.

## 14. Future Slices

Recommended follow-up slices:

- **Slice 7L — OpenAI live harness approval record.**
- **Slice 7L-A — Deny local-only live harness approval until prerequisites exist.**
- **Slice 7L-B — Resolve live harness approval prerequisites.**
- **Slice 7L-C — Grant or deny local-only live harness approval with evidence.**
- **Slice 7L-D — Prepare OpenAI live harness approval evidence packet.**
- **Slice 7L-E — Grant or deny local-only live harness approval with evidence.**
- **Slice 7M — OpenAI SDK adapter planning, still no credentials.**
- **Slice 7N — Opt-in live provider harness skeleton.**
- **Slice 7O — Optional workflow_dispatch live provider validation planning.**

Do not proceed to Slice 7L automatically from this planning slice.

## 15. Definition Of Done

This slice is complete when:

- `docs/openai-live-provider-harness-plan.md` exists.
- Existing OpenAI provider, WIF, privacy, AI summarization, and next-action docs
  reference the plan where useful.
- No runtime code, tests, SDK, credential, `.env` file, API call, token
  exchange, WIF runtime, backend route, API client method, SSE/frontend,
  Supabase, SQL, migration, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- Verification passes or any blocked verification is explicitly reported.
