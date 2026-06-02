# OpenAI Live Harness Approval Evidence Packet

## 1. Objective

Prepare evidence for a future local-only OpenAI live harness approval decision
without granting approval, implementing a harness, adding credentials,
installing runtime dependencies, wiring WIF, exchanging tokens, or calling
OpenAI.

This packet is evidence preparation only. It is not execution permission.

## 2. Current Decision Status

Approval remains **DENIED / NOT GRANTED**.

This packet does not approve:

- Live harness execution.
- Provider credentials.
- OpenAI API calls.
- OpenAI SDK or runtime work.
- WIF runtime.
- Token exchange.
- GitHub OIDC token requests.
- GitHub Actions live provider validation.
- Backend route changes.
- API client changes.
- SSE or frontend work.
- SQL, migrations, Supabase/RLS work, or generated Supabase state.

Fake provider remains the default for local development, tests, and normal CI.

## 3. Evidence Matrix

| Evidence item | Current status | Required artifact | Owner/reviewer placeholder | Notes |
|---|---|---|---|---|
| Security/privacy approval | INSUFFICIENT | Reviewer decision covering synthetic-only data, no PII, redacted diagnostics, no sensitive logging, and external review before execution. | `TBD_SECURITY_PRIVACY_REVIEWER` | Existing docs define guardrails, but no explicit approval or sign-off exists. |
| Cost/budget approval | MISSING | Reviewer decision for request, prompt, output-token, retry, timeout, and spend ceilings. | `TBD_COST_BUDGET_REVIEWER` | Only placeholder labels are prepared in this packet. |
| Credential-mode decision | MISSING | Reviewer decision selecting or rejecting a future local-only API-key candidate and WIF candidate. | `TBD_CREDENTIAL_MODE_REVIEWER` | No credential mode is approved by this packet. |
| Synthetic prompt fixture | MISSING | Reviewed synthetic fixture description and storage decision. | `TBD_SYNTHETIC_FIXTURE_REVIEWER` | Do not add executable fixture content in this slice. |
| Redacted evidence template | PRESENT | Redacted future run report template. | `TBD_EVIDENCE_REVIEWER` | Present in prerequisite docs and repeated below for packet completeness. |
| Rollback/disable plan | INSUFFICIENT | Reviewer-approved disable plan with owner and confirmation steps. | `TBD_ROLLBACK_REVIEWER` | Existing checklist is not an approved plan. |
| No-default-CI proof | INSUFFICIENT | Proof that normal push CI has no live flags and live validation is skipped by default. | `TBD_CI_REVIEWER` | No workflow change is approved here. |
| Fail-closed config proof | PRESENT | Existing config and tests showing live modes fail closed until future approved runtime slices. | `TBD_CONFIG_REVIEWER` | This is evidence of current fail-closed posture, not live approval. |
| Local-only boundary evidence | INSUFFICIENT | Reviewer-approved local-only boundary record and runbook. | `TBD_LOCAL_BOUNDARY_REVIEWER` | Existing boundary checklist is not approved execution evidence. |
| External review sign-off | MISSING | Explicit external reviewer sign-off or explicit denial entry. | `TBD_EXTERNAL_REVIEWER` | Missing sign-off keeps approval denied. |

Any `MISSING` or `INSUFFICIENT` item keeps approval **DENIED / NOT GRANTED**.

## 4. Security/Privacy Evidence

A future approval packet must show that the proposed local-only live harness
would be reviewed for all of the following:

- No real notes.
- No user PII.
- No prompt or note-content logging.
- No raw provider response logging.
- No auth, token, or key logging.
- Redacted diagnostics only.
- Fake provider remains default.
- External review before execution.

The reviewer decision must be explicit, tied to a commit, and safe to store in
repo docs or review comments. Absence of that decision keeps live execution
blocked.

## 5. Cost/Budget Evidence

Future limits must stay placeholder-only until a later reviewer decision chooses
approved values:

| Future limit | Placeholder label |
|---|---|
| Max requests per run | `TO_BE_APPROVED_MAX_REQUESTS_PER_RUN` |
| Max prompt length | `TO_BE_APPROVED_MAX_PROMPT_LENGTH` |
| Max output tokens | `TO_BE_APPROVED_MAX_OUTPUT_TOKENS` |
| Max retries | `TO_BE_APPROVED_MAX_RETRIES` |
| Max timeout | `TO_BE_APPROVED_MAX_TIMEOUT` |
| Max spend ceiling | `TO_BE_APPROVED_MAX_SPEND_CEILING` |

A future harness must fail closed if any required budget configuration is
missing, invalid, or not tied to an approved evidence record.

This packet does not add provider config, credentials, defaults, environment
reads, retry behavior, timeout behavior, or cost-bearing execution.

## 6. Credential-Mode Evidence

Future credential-mode review must compare these choices without approving
either in this packet:

| Future choice | Current status | Required evidence |
|---|---|---|
| Local-only API-key candidate | Still not approved. | Local-only storage boundary, git exclusion, redaction proof, cleanup step, and reviewer decision. |
| WIF candidate | Preferred for CI/cloud where supported, still not approved. | Separate WIF approval for issuer, audience, subject, repository/ref/workflow, environment, trust policy, redaction, rollback, and permissions. |

Credential rules for any future decision:

- No production API-key fallback is approved.
- Credential source must stay outside git.
- No committed `.env` file is allowed.
- No tokens, keys, OIDC values, JWT values, auth headers, or provider headers may
  appear in logs, docs, screenshots, artifacts, or client bundles.
- Fake provider remains default until a later approved runtime slice changes
  only the explicitly approved path.

## 7. Synthetic Prompt Fixture

A future synthetic prompt fixture must satisfy all of the following before use:

- Synthetic text only.
- No real note content.
- No names, emails, or PII.
- Short enough for the approved budget.
- Stored only if it contains no secrets and cannot be mistaken for production
  data.
- Reviewed before any live run uses it.

This slice does not add the actual live fixture because fixture text could be
mistaken as executable approval. A later slice may add a reviewed fixture
description or fixture only if the approval boundary remains explicit.

## 8. Redacted Evidence Format

A future live harness report should use this template with labels and coarse
metadata only:

```text
Run mode:
Approval record commit:
Credential mode label only:
Synthetic prompt description, not prompt text:
Coarse provider result:
Request count:
Cost estimate bucket:
Cleanup/no-artifact confirmation:
Redaction confirmation:
Stop condition if failed:
```

Future report rules:

- Describe the synthetic prompt; do not include prompt text.
- Record a credential mode label only; do not include credential values.
- Record coarse provider results only; do not include raw provider response
  bodies.
- Record request count and cost estimate bucket only.
- Confirm cleanup and no-artifact state.
- Confirm redaction.
- If execution stops, record only the stop condition.

## 9. Rollback/Disable Plan

A future reviewer-approved rollback and disable plan must document that:

- Fake provider remains default.
- The future live flag can be unset.
- Any local environment value can be cleared after the run.
- No route or provider default switch is approved.
- No default CI live test is approved.
- No live provider output is persisted.
- No evidence containing secrets is committed.

This packet does not approve an execution owner or rollback owner. Those fields
must be filled by a later reviewer-decision slice.

## 10. No-Default-CI Proof

A future evidence packet must include proof that:

- Normal push CI has no live environment flags.
- Live tests are skipped by default.
- Workflow changes require separate approval.
- `workflow_dispatch` live validation remains unapproved.
- Default CI remains fake-only, credential-free, and network-free.

This packet does not add workflow changes, identity-token permissions, protected
environments, live provider jobs, or manual live validation.

## 11. Local-Only Boundary Evidence

A future local-only boundary record must document:

- Local developer machine only.
- Explicit opt-in flag.
- Synthetic prompt only.
- No background summarization.
- No shared credentials.
- No committed live evidence containing secrets.
- No committed prompt text or raw provider body.
- No route behavior switch.
- No provider default switch.

The boundary must be reviewed before any local-only execution is reconsidered.

## 12. Future Approval Path

Recommended follow-up slices:

- **Slice 7L-E — Fill approval evidence packet with reviewer decisions.**
- **Slice 7L-F — Grant or deny local-only live harness approval with completed evidence.**
- **Slice 7M — OpenAI SDK adapter planning only after the approval path is clear.**

Do not proceed to Slice 7L-E automatically from this packet.
