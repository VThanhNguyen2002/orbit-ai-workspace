# OpenAI Live Harness Approval Record

## 1. Objective

Record the approval gate for a future opt-in OpenAI live provider harness. This
record defines approval status, candidate scope, required evidence,
pre-execution constraints, credential handling, stop conditions, and future
decision points.

This record does not implement a live harness, install an OpenAI SDK, add
credentials, exchange tokens, call OpenAI, wire WIF runtime, add CI workflow
jobs, change route behavior, or approve live execution.

## 2. Current Approval Status

Status: **PENDING / NOT GRANTED - live harness execution is not approved yet.**

The following remain explicitly unapproved:

- No live OpenAI API call is approved.
- No SDK implementation is approved.
- No credential use is approved.
- No WIF runtime is approved.
- No default CI live test is approved.

No explicit approval evidence exists in the current repository. Any later
approval must update this record or a successor approval record before live
execution begins.

## 3. Candidate Approved Scope, Not Yet Granted

The only candidate scope currently under consideration is a future local opt-in
live smoke test with strict limits:

- Local opt-in live smoke test only.
- Synthetic prompt only.
- No real notes.
- No user PII.
- No production data.
- Redacted evidence only.
- Strict cost ceiling.
- Strict request ceiling.
- Fake provider remains default.

This candidate scope is not granted by this record.

## 4. Explicitly Not Approved

The following are not approved:

- Production live provider execution.
- Staging or hosted live provider execution.
- Default CI live tests.
- GitHub Actions WIF wiring.
- Real OIDC or JWT exchange.
- Committed API keys.
- Committed `.env` files.
- Route behavior switch to OpenAI.
- Background summarization.
- Persisted live provider outputs.
- OpenAI SDK dependency installation.
- Provider credentials in source, docs, logs, artifacts, or client bundles.

## 5. Required Approvals Before Execution

Before any live harness execution or implementation begins, the project must
record all of the following:

- Security/privacy approval.
- Cost/budget approval.
- Credential-mode approval.
- Local-only or CI-opt-in mode decision.
- Redaction evidence format.
- Rollback and disable plan.
- External review gate.
- No-default-CI confirmation.

Approval must be explicit, reviewable, and tied to a commit. Absence of an
approval entry means execution remains denied.

## 6. Required Pre-Execution Checklist

A future live harness run must not start until this checklist is complete:

- Git state is clean.
- No `.env` file is staged.
- No SDK dependency change is present unless separately approved.
- No workflow change is present unless separately approved.
- No live data is used.
- Synthetic prompt is prepared.
- Credential source is outside git.
- Request budget is configured.
- Cost budget is configured.
- Evidence output is redacted.
- Fail-closed behavior is confirmed.

## 7. Credential Handling Constraints

- No committed credentials.
- No real values in docs.
- No raw key output.
- No raw token output.
- No raw OIDC or JWT output.
- API-key fallback is local-only unless separately approved.
- WIF is preferred for future CI/cloud auth where supported, but is not
  implemented.
- Fake provider remains default for local development, tests, and normal CI.
- Future credentials must stay outside source files, public config dumps, reprs,
  errors, logs, screenshots, artifacts, and client bundles.

## 8. Stop Conditions

Future execution must stop if:

- Credentials are missing.
- Credentials would be printed.
- Real user data appears.
- Note content would be logged.
- Prompt text would be logged.
- Cost budget is missing.
- Request budget is exceeded.
- Provider output is unsafe or malformed.
- Cleanup or evidence cannot be redacted.
- The live test would run in default CI.
- Route behavior would switch to OpenAI without approval.
- WIF runtime, OIDC exchange, or token exchange would occur without separate
  approval.

## 9. Evidence Requirements

A future live harness report must include:

- Run mode.
- Approval record commit.
- Redacted credential mode.
- Synthetic prompt description, not prompt text.
- Coarse provider result only.
- Cost count or cost bucket only.
- Request count only.
- No raw provider body.
- No token, key, OIDC, or JWT value.
- Cleanup and no-artifact confirmation.

Evidence must be safe to include in repository docs or issue/PR comments. If the
evidence cannot be redacted, the run must stop and report only the stop reason.

## 10. Relationship To WIF

WIF is preferred for future CI/cloud authentication where the provider and
environment support a secure, narrowly scoped exchange.

This record does not approve WIF runtime. It does not approve GitHub Actions
OIDC wiring, identity-token permission changes, real OIDC/JWT exchange, token
exchange implementation, or exchanged credential use.

WIF approval remains separate from live harness execution approval. A future WIF
record must still approve issuer, audience, subject, repository, ref, workflow,
environment, trust policy, redaction behavior, rollback, and CI permissions
before any WIF-based live harness can run.

## 11. Future Slices

Recommended follow-up slices:

- **Slice 7L-A — Grant or deny local-only live harness approval constraints.**
- **Slice 7M — OpenAI SDK adapter planning.**
- **Slice 7N — Opt-in live provider harness skeleton.**
- **Slice 7O — Optional workflow_dispatch live provider validation planning.**

Do not proceed to Slice 7L-A automatically from this record.

## 12. Definition Of Done

This slice is complete when:

- `docs/openai-live-harness-approval-record.md` exists.
- Approval status is unambiguous and remains pending unless explicit approval
  evidence exists.
- Related OpenAI provider, WIF, privacy, AI summarization, and next-action docs
  reference this record where useful.
- No runtime code, tests, SDK, credential, `.env` file, API call, token
  exchange, WIF runtime, backend route, API client method, SSE/frontend,
  Supabase, SQL, migration, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- Verification passes or any blocked verification is explicitly reported.
