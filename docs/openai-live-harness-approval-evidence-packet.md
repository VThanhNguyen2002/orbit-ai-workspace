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

## 3. Final Evidence Decision Matrix

| Evidence item | Reviewer decision | Status | Reason | Next required action |
|---|---|---|---|---|
| Security/privacy approval | `TBD_SECURITY_PRIVACY_REVIEWER` — **NO DECISION RECORDED** | INSUFFICIENT | Guardrails and checklists exist in docs, but no explicit sign-off, named reviewer, or commit-tied approval record exists. | Obtain explicit security/privacy reviewer sign-off and record it in this packet or a linked approval record. |
| Cost/budget approval | `TBD_COST_BUDGET_REVIEWER` — **NO DECISION RECORDED** | MISSING | Only placeholder budget labels exist. No approved request ceiling, token ceiling, timeout, retry count, or spend ceiling has been chosen or recorded. | Reviewer must select and record approved numeric values for all cost/budget placeholders. |
| Credential-mode decision | `TBD_CREDENTIAL_MODE_REVIEWER` — **NO DECISION RECORDED** | MISSING | API-key local-only and WIF candidates are both documented as not approved. No mode has been selected by any reviewer. | Reviewer must explicitly select local-only API-key or WIF candidate, record constraints, and sign off. |
| Synthetic prompt fixture review | `TBD_SYNTHETIC_FIXTURE_REVIEWER` — **NO DECISION RECORDED** | MISSING | No synthetic fixture description, fixture content, or fixture storage decision exists. No reviewer has approved fixture scope. | Reviewer must approve a synthetic fixture description (no real content, no PII) and record it here. |
| Redacted evidence template | `TBD_EVIDENCE_REVIEWER` — template is present in prerequisites doc | PRESENT | Redacted future run report template exists in `docs/openai-live-harness-prerequisites.md` and is reproduced in this packet. | No action required for this item. Template must be used for any future run reports. |
| Rollback/disable plan review | `TBD_ROLLBACK_REVIEWER` — **NO DECISION RECORDED** | INSUFFICIENT | A rollback/disable checklist exists in prerequisites, but no approved plan, named execution owner, or named rollback owner is recorded. | Reviewer must approve and sign a rollback/disable plan with named owner, steps, and disable-flag confirmation. |
| No-default-CI proof review | `TBD_CI_REVIEWER` — **NO DECISION RECORDED** | INSUFFICIENT | Policy language exists stating live tests are skipped by default, but no explicit proof artifact (workflow inspection result, CI log excerpt, or reviewer confirmation) is recorded. | Reviewer must provide explicit confirmation or proof artifact that normal push CI has no live flags and live tests are skipped. |
| Fail-closed config proof | `TBD_CONFIG_REVIEWER` — existing config and tests confirm fail-closed posture | PRESENT | `apps/api/app/core/config.py` rejects OpenAI `api_key` and `workload_identity` modes at runtime. `FakeSummarizationProvider` remains the only runtime-enabled default. | No action required for this item. This is evidence of current fail-closed posture, not live approval. |
| Local-only boundary evidence | `TBD_LOCAL_BOUNDARY_REVIEWER` — **NO DECISION RECORDED** | INSUFFICIENT | A local-only boundary checklist and requirements exist in prerequisites, but no approved runbook, no named boundary enforcer, and no commit-tied sign-off exists. | Reviewer must approve a local-only boundary runbook and record explicit consent here. |
| External review sign-off | `TBD_EXTERNAL_REVIEWER` — **NO SIGN-OFF RECORDED** | MISSING | No external reviewer has signed off on any aspect of the live harness plan. No review comment, issue, PR review, or explicit record of external sign-off exists in the repository. | External reviewer must provide explicit sign-off (PR review, issue comment, or approval record) before approval can be reconsidered. |

**Summary:** 2 of 10 evidence items are PRESENT. 4 are MISSING. 4 are
INSUFFICIENT. 0 have been explicitly approved by a named reviewer.

Any `MISSING` or `INSUFFICIENT` item keeps approval **DENIED / NOT GRANTED**.

## 4. Reviewer Decision Sections

### 4.1 Security/Privacy Reviewer Decision

**Reviewer placeholder:** `TBD_SECURITY_PRIVACY_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** INSUFFICIENT

Required before recording a positive decision:

- Explicit confirmation that the proposed harness uses synthetic-only prompts
  with no real note content, no user PII, no production data.
- Explicit confirmation that no raw prompt, note content, auth header, API key,
  OIDC token, JWT, or provider response body will be logged.
- Explicit confirmation that redacted diagnostics only are acceptable.
- Explicit confirmation that external review is required before any execution.
- Named reviewer and date of review.
- Reference to specific commit or PR comment providing the sign-off.

Absence of all the above keeps security/privacy status INSUFFICIENT and
approval blocked.

### 4.2 Cost/Budget Reviewer Decision

**Reviewer placeholder:** `TBD_COST_BUDGET_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** MISSING

Required before recording a positive decision:

- Explicit numeric or bounded value for each placeholder:

  | Future limit | Placeholder label | Approved value |
  |---|---|---|
  | Max requests per run | `TO_BE_APPROVED_MAX_REQUESTS_PER_RUN` | NOT APPROVED |
  | Max prompt length | `TO_BE_APPROVED_MAX_PROMPT_LENGTH` | NOT APPROVED |
  | Max output tokens | `TO_BE_APPROVED_MAX_OUTPUT_TOKENS` | NOT APPROVED |
  | Max retries | `TO_BE_APPROVED_MAX_RETRIES` | NOT APPROVED |
  | Max timeout | `TO_BE_APPROVED_MAX_TIMEOUT` | NOT APPROVED |
  | Max spend ceiling | `TO_BE_APPROVED_MAX_SPEND_CEILING` | NOT APPROVED |

- Named reviewer and date of review.
- Reference to commit or PR sign-off.

Absence of all the above keeps cost/budget status MISSING and approval blocked.

### 4.3 Credential-Mode Reviewer Decision

**Reviewer placeholder:** `TBD_CREDENTIAL_MODE_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** MISSING

Both candidate modes remain not approved:

| Future choice | Current status | Required evidence |
|---|---|---|
| Local-only API-key candidate | NOT APPROVED | Local-only storage boundary, git exclusion, redaction proof, cleanup step, and reviewer decision. |
| WIF candidate | NOT APPROVED | Separate WIF approval for issuer, audience, subject, repository/ref/workflow, environment, trust policy, redaction, rollback, and permissions. |

Required before recording a positive credential-mode decision:

- Selection of exactly one candidate mode.
- Explicit constraints for that mode (storage, exclusion, redaction, cleanup).
- Confirmation that no production API-key fallback is approved.
- Confirmation that credentials stay outside git.
- Named reviewer and date of review.
- Reference to commit or PR sign-off.

Absence of all the above keeps credential-mode status MISSING and approval
blocked.

### 4.4 Synthetic Prompt Fixture Reviewer Decision

**Reviewer placeholder:** `TBD_SYNTHETIC_FIXTURE_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** MISSING

Required before recording a positive fixture decision:

- Approved fixture description (not prompt text) confirming:
  - Synthetic text only.
  - No real note content.
  - No names, emails, or PII.
  - Short enough for the approved (future) budget.
  - Cannot be mistaken for production data.
- Storage and review decision for the fixture (if a future fixture file is committed).
- Named reviewer and date of review.
- Reference to commit or PR sign-off.

Do not add actual fixture text to this packet. Adding fixture text without
explicit budget and fixture review would be mistaken as execution permission.

Absence of all the above keeps fixture status MISSING and approval blocked.

### 4.5 Rollback/Disable Plan Reviewer Decision

**Reviewer placeholder:** `TBD_ROLLBACK_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** INSUFFICIENT

The rollback/disable checklist from `docs/openai-live-harness-prerequisites.md`
exists but is not an approved plan. An approved plan requires:

- Named execution owner responsible for disable if a run goes wrong.
- Named rollback owner responsible for ensuring fake-provider default is
  restored.
- Explicit confirmation that the live flag can be unset without a code change.
- Explicit confirmation that any local environment value is cleared after the
  run.
- Explicit confirmation that no route or provider default switch is approved.
- Explicit confirmation that no default CI live test is approved.
- Explicit confirmation that no live provider output is persisted.
- Reference to commit or PR sign-off.

Absence of all the above keeps rollback/disable status INSUFFICIENT and
approval blocked.

### 4.6 No-Default-CI Proof Reviewer Decision

**Reviewer placeholder:** `TBD_CI_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** INSUFFICIENT

Policy language states live tests are skipped by default, but no explicit proof
artifact is recorded. Required before recording a positive no-default-CI
decision:

- Reviewer confirmation (issue comment, PR review, or entry here) that:
  - Normal push CI workflow (`ci.yml`) has no `SYNAPSE_OPENAI_LIVE_TESTS`,
    `SYNAPSE_AI_PROVIDER=openai`, or other live-enabling environment variables.
  - Live tests are skipped or absent in the default test run.
  - No `workflow_dispatch` live provider job exists.
- Named reviewer and date of review.
- Reference to commit, workflow file line range, or CI run inspected.

Absence of all the above keeps no-default-CI status INSUFFICIENT and approval
blocked.

### 4.7 Local-Only Boundary Reviewer Decision

**Reviewer placeholder:** `TBD_LOCAL_BOUNDARY_REVIEWER`
**Current decision:** NOT RECORDED
**Status:** INSUFFICIENT

The local-only boundary checklist exists in prerequisites but no approved
boundary runbook, named enforcer, or commit-tied sign-off exists. Required
before recording a positive local-only boundary decision:

- Approved runbook confirming:
  - Local developer machine only.
  - Explicit opt-in flag required.
  - Synthetic prompt only.
  - No background summarization.
  - No shared credentials.
  - No committed live evidence containing secrets.
  - No committed prompt text or raw provider body.
  - No route behavior switch.
  - No provider default switch.
- Named reviewer and date of review.
- Reference to commit or PR sign-off.

Absence of all the above keeps local-only boundary status INSUFFICIENT and
approval blocked.

### 4.8 External Review Sign-Off

**Reviewer placeholder:** `TBD_EXTERNAL_REVIEWER`
**Current decision:** NOT RECORDED — NO SIGN-OFF EXISTS
**Status:** MISSING

No external reviewer has provided any sign-off on any aspect of the live
harness plan in this repository. No PR review comment, issue approval, or out-
of-band approval record exists.

Required before a future approval can be considered:

- Explicit external reviewer sign-off in the form of:
  - A PR review approval on a slice that adds live harness evidence, or
  - An issue comment from a named reviewer explicitly approving scope, or
  - An explicit approval record committed to docs with a named reviewer, date,
    and scope.
- The sign-off must cover at minimum: synthetic-only data, no PII, no live
  production call, budget ceiling, rollback plan, and local-only boundary.
- The sign-off must be tied to a specific commit or PR so it is auditable.

Absence of all the above keeps external review status MISSING and approval
blocked.

## 5. Redacted Evidence Format

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

## 6. Decision Rule

If any required reviewer decision is:

- Missing (not recorded at all), or
- Placeholder-only (no named reviewer, no date, no specific scope), or
- Insufficient (checklist exists but no sign-off), or
- Not explicitly approved by a named reviewer,

then:

- Approval remains **DENIED / NOT GRANTED**.
- Live harness execution remains blocked.
- Credential use remains blocked.
- OpenAI API calls remain blocked.
- OpenAI SDK, runtime, WIF runtime, and live harness skeleton remain blocked.

This decision rule applies to each evidence item independently. A subset of
items being present or partially approved does not unlock execution.

## 7. Security/Privacy Evidence Requirements

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

## 8. Future Approval Path

Recommended follow-up slices:

- **Slice 7L-F — Resolve missing OpenAI live harness approval evidence.**
  Required next step given that approval remains DENIED / NOT GRANTED and
  multiple evidence items are MISSING or INSUFFICIENT. Slice 7L-F must collect
  or explicitly deny each required reviewer decision. If all evidence is
  provided and explicitly approved, a later record may grant approval. If any
  item remains missing, approval must remain DENIED / NOT GRANTED.
- **Slice 7N — Opt-in live provider harness skeleton.**
  Only reachable after all evidence items are explicitly PRESENT and approved.
  Do not proceed to Slice 7N from this packet.

Do not proceed to Slice 7L-F automatically from this packet.
