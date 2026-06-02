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

## 4. Slice 7L-F Resolution Status

Slice 7L-F converts each MISSING or INSUFFICIENT evidence item into a concrete
required-action record. No items are upgraded to APPROVED because no named
reviewer has provided explicit sign-off.

| Evidence item | Previous status | Resolution added in 7L-F | New status | Why approval still denied | Next required action |
|---|---|---|---|---|---|
| Security/privacy approval | INSUFFICIENT | Required reviewer scope, required approval wording, and blockers documented in section 5.1 | PREPARED / STILL NOT APPROVED | No named reviewer has signed off. Checklists are not approvals. | Named security/privacy reviewer must sign off explicitly. |
| Cost/budget approval | MISSING | Required placeholder table with all six limit fields and block wording documented in section 5.2 | PREPARED / STILL NOT APPROVED | No numeric values have been approved. Placeholders are not values. | Named cost/budget reviewer must approve actual numeric limits. |
| Credential-mode decision | MISSING | Candidate comparison table with required evidence per mode documented in section 5.3 | PREPARED / STILL NOT APPROVED | No mode has been selected. Candidates are not decisions. | Named credential-mode reviewer must select and record a mode. |
| Synthetic prompt fixture | MISSING | Required fixture criteria and storage decision scope documented in section 5.4 | PREPARED / STILL NOT APPROVED | No fixture description or storage decision has been approved. Criteria are not a fixture. | Named fixture reviewer must approve a fixture description. |
| Redacted evidence template | PRESENT | No change required | PRESENT | — | No action required. |
| Rollback/disable plan | INSUFFICIENT | Named-owner requirements, required plan elements, and required sign-off format documented in section 5.5 | PREPARED / STILL NOT APPROVED | No named owner or approved plan exists. Checklists are not plans. | Named rollback reviewer must approve a plan with named owner. |
| No-default-CI proof | INSUFFICIENT | Proof artifact requirements and workflow inspection scope documented in section 5.6 | PREPARED / STILL NOT APPROVED | No explicit proof artifact has been recorded. Policy language is not proof. | Named CI reviewer must provide or record an explicit proof artifact. |
| Fail-closed config proof | PRESENT | No change required | PRESENT | — | No action required. |
| Local-only boundary | INSUFFICIENT | Runbook elements, named-enforcer requirement, and sign-off format documented in section 5.7 | PREPARED / STILL NOT APPROVED | No approved runbook or named enforcer exists. Checklists are not runbooks. | Named boundary reviewer must approve a runbook with explicit sign-off. |
| External review sign-off | MISSING | Required sign-off format and scope documented in section 5.8 | PREPARED / STILL NOT APPROVED | No sign-off of any kind exists. Required-action record is not a sign-off. | External reviewer must provide explicit sign-off against a specific commit or PR. |

**Post 7L-F summary:** 2 PRESENT, 0 MISSING, 0 INSUFFICIENT, 8 PREPARED / STILL NOT APPROVED.
Approval remains **DENIED / NOT GRANTED**. `PREPARED / STILL NOT APPROVED` is not an approval state.

## 5. Required-Action Records

### 5.1 Security/Privacy Approval: Required-Action Record

**Reviewer placeholder:** `TBD_SECURITY_PRIVACY_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required review scope.** The reviewer must confirm in writing that the
proposed local-only live harness enforces all of the following:

- Synthetic prompt only — no real note content.
- No user PII in prompts or logged output.
- No production data.
- No raw prompt text in logs.
- No raw provider response body in logs.
- No auth header, API key, OIDC token, or JWT value in logs.
- Redacted diagnostics only.
- Fake provider remains default in CI and local development.
- External review is required before any live execution begins.

**Required approval wording** (or equivalent in reviewer's own form):

> I, [reviewer name], confirm that the proposed local-only OpenAI live harness
> satisfies the security and privacy requirements listed in
> `docs/openai-live-harness-approval-evidence-packet.md` section 5.1 as of
> commit [commit SHA]. This confirmation is not live execution approval.

**Blockers.** Until this statement or equivalent is recorded in a PR review,
issue comment, or committed approval record:

- Security/privacy approval status remains NOT APPROVED.
- Live harness execution remains blocked.
- Credential use remains blocked.
- OpenAI API calls remain blocked.

### 5.2 Cost/Budget Approval: Required-Action Record

**Reviewer placeholder:** `TBD_COST_BUDGET_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required approval table.** The reviewer must choose actual numeric or bounded
values to replace each placeholder:

| Future limit | Placeholder label | Required approved value |
|---|---|---|
| Max requests per run | `TO_BE_APPROVED_MAX_REQUESTS_PER_RUN` | **NOT APPROVED — reviewer must fill** |
| Max prompt length | `TO_BE_APPROVED_MAX_PROMPT_LENGTH` | **NOT APPROVED — reviewer must fill** |
| Max output tokens | `TO_BE_APPROVED_MAX_OUTPUT_TOKENS` | **NOT APPROVED — reviewer must fill** |
| Max retries | `TO_BE_APPROVED_MAX_RETRIES` | **NOT APPROVED — reviewer must fill** |
| Max timeout | `TO_BE_APPROVED_MAX_TIMEOUT` | **NOT APPROVED — reviewer must fill** |
| Max spend ceiling | `TO_BE_APPROVED_MAX_SPEND_CEILING` | **NOT APPROVED — reviewer must fill** |

**Blockers.** Until all six fields have named-reviewer-approved values recorded
here or in a linked approval record:

- Cost/budget status remains NOT APPROVED.
- Any future harness implementation must treat missing budget config as a
  fail-closed stop condition.
- Live harness execution remains blocked.

### 5.3 Credential-Mode Decision: Required-Action Record

**Reviewer placeholder:** `TBD_CREDENTIAL_MODE_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Candidate comparison** (neither approved):

| Future choice | Current status | Required evidence before approval |
|---|---|---|
| Local-only API-key candidate | NOT APPROVED | Local-only storage boundary proof, git-exclusion proof, redaction proof, cleanup step, named reviewer decision. |
| WIF candidate | NOT APPROVED | Separate WIF approval record covering issuer, audience, subject, repository/ref/workflow, environment, trust policy, redaction, rollback, and CI permissions. |

**Standing rules regardless of which mode is chosen:**

- No production API-key fallback is approved.
- Credential source must stay outside git.
- No committed `.env` file is allowed.
- No tokens, keys, OIDC values, or JWT values in logs, artifacts, docs,
  screenshots, or client bundles.
- Fake provider remains default until a later approved runtime slice.

**Blockers.** Until a reviewer explicitly selects one candidate and records the
required evidence for that candidate:

- Credential-mode status remains NOT APPROVED.
- No credential use is authorized.
- Live harness execution remains blocked.

### 5.4 Synthetic Prompt Fixture: Required-Action Record

**Reviewer placeholder:** `TBD_SYNTHETIC_FIXTURE_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required fixture criteria.** Any approved fixture must satisfy all of the
following:

- Synthetic text only — not derived from real notes.
- No real note content.
- No names, emails, phone numbers, or PII of any kind.
- Short enough to fit within the approved (future) budget limits.
- Cannot be mistaken for production data.
- Reviewed by a named reviewer before any live run uses it.
- Stored only if it contains no secrets and is clearly marked synthetic.

**Required reviewer decisions:**

1. Approve or deny the fixture description (not the prompt text).
2. Approve or deny the fixture storage location (committed doc vs. local-only).
3. Confirm the fixture does not trigger content-policy filters.

**Blockers.** Until the reviewer approves a synthetic fixture description and
storage decision:

- Fixture status remains NOT APPROVED.
- No live run may use any prompt fixture.
- Live harness execution remains blocked.

### 5.5 Rollback/Disable Plan: Required-Action Record

**Reviewer placeholder:** `TBD_ROLLBACK_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required plan elements.** An approved rollback/disable plan must document:

- Named execution owner responsible for disabling the live run if it goes wrong.
- Named rollback owner responsible for confirming fake-provider default is
  restored after any live run.
- Explicit step to unset the live harness flag (no code change required).
- Explicit step to clear any local environment value after the run.
- Explicit confirmation that no route or provider default is switched.
- Explicit confirmation that no default CI live test is introduced.
- Explicit confirmation that no live provider output is persisted.
- Explicit confirmation that no evidence containing secrets is committed.

**The checklist in `docs/openai-live-harness-prerequisites.md` section 7 is a
checklist, not an approved plan.** An approved plan requires a named owner
and a commit-tied or PR-tied reviewer sign-off.

**Blockers.** Until the reviewer records an approved plan with named owners:

- Rollback/disable status remains NOT APPROVED.
- Live harness execution remains blocked.

### 5.6 No-Default-CI Proof: Required-Action Record

**Reviewer placeholder:** `TBD_CI_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required proof.** The reviewer must provide at least one of the following:

- A CI workflow inspection result (referenced by workflow file path and line
  range) confirming that `SYNAPSE_OPENAI_LIVE_TESTS`, `SYNAPSE_AI_PROVIDER=openai`,
  and all other live-enabling flags are absent from normal push CI jobs.
- A CI run log reference (run ID and relevant step) confirming that live tests
  are absent or explicitly skipped.
- An explicit written confirmation tied to a commit:

> I, [reviewer name], confirm that as of commit [commit SHA], normal push CI
> does not set live provider flags and live tests are skipped by default.

**Standing rules regardless of proof form:**

- No `workflow_dispatch` live provider job exists or is approved.
- Workflow changes require separate review before they are added.
- Default CI remains fake-only, credential-free, and network-free.

**Blockers.** Until an explicit proof artifact is recorded here:

- No-default-CI status remains NOT APPROVED.
- Live harness execution remains blocked.

### 5.7 Local-Only Boundary: Required-Action Record

**Reviewer placeholder:** `TBD_LOCAL_BOUNDARY_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required runbook elements.** An approved local-only boundary runbook must
confirm:

- Local developer machine only — no CI or hosted execution.
- Explicit opt-in flag required — no ambient activation.
- Synthetic prompt only — no real note content.
- No background summarization.
- No shared credentials — developer's local environment only.
- No committed live evidence containing secrets.
- No committed prompt text or raw provider body.
- No route behavior switch.
- No provider default switch.

**The boundary checklist in `docs/openai-live-harness-prerequisites.md`
section 9 is a checklist, not an approved runbook.** An approved runbook
requires a named reviewer and a commit-tied or PR-tied sign-off.

**Blockers.** Until the reviewer records an approved runbook with explicit
sign-off:

- Local-only boundary status remains NOT APPROVED.
- Local-only live execution remains blocked.

### 5.8 External Review Sign-Off: Required-Action Record

**Reviewer placeholder:** `TBD_EXTERNAL_REVIEWER`
**Current status:** PREPARED / STILL NOT APPROVED

**Required sign-off form.** The external reviewer must provide at least one of:

- A GitHub PR review approval on a slice that adds live harness evidence,
  with the reviewer explicitly stating whether the local-only live harness
  approval is granted or denied.
- A GitHub issue comment from a named external reviewer explicitly covering
  scope, data boundary, cost ceiling, rollback plan, and approval decision.
- A committed approval record in repo docs with named reviewer, date, commit
  SHA, and explicit approval or denial statement.

**Required scope.** The sign-off must explicitly address:

- Synthetic-only data — no real notes, no PII.
- No live production call.
- Budget ceiling (requires cost/budget approval first).
- Rollback and disable plan (requires rollback approval first).
- Local-only execution boundary (requires boundary approval first).
- Whether local-only live harness approval is **GRANTED** or **DENIED**.

**Blockers.** Until an external reviewer provides explicit sign-off against a
specific commit or PR:

- External sign-off status remains NOT APPROVED.
- Local-only live harness approval remains **DENIED / NOT GRANTED**.
- Live harness execution remains blocked.
- Credential use remains blocked.
- OpenAI API calls remain blocked.

## 6. Decision Rule

If any required reviewer decision is:

- Missing (not recorded at all), or
- Placeholder-only (no named reviewer, no date, no specific scope), or
- Insufficient (checklist or required-action record exists but no sign-off), or
- PREPARED / STILL NOT APPROVED (required-action record filled but not signed),

then:

- Approval remains **DENIED / NOT GRANTED**.
- Live harness execution remains blocked.
- Credential use remains blocked.
- OpenAI API calls remain blocked.
- OpenAI SDK, runtime, WIF runtime, and live harness skeleton remain blocked.

`PREPARED / STILL NOT APPROVED` is not an approval state.

## 7. Redacted Evidence Format

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

## 8. Future Approval Path

Recommended follow-up slices:

- **Slice 7L-G — Collect explicit reviewer approvals or close live harness path.**
  Required next step. Each `TBD_*` reviewer must either provide explicit sign-off
  or the evidence item must be permanently denied. If all 8 required items are
  explicitly approved by named reviewers, a later record may grant approval.
  If any item remains without explicit approval, approval must remain **DENIED /
  NOT GRANTED**.
- **Slice 7N — Opt-in live provider harness skeleton.**
  Only reachable after all evidence items are explicitly PRESENT and named-reviewer
  approved. Do not proceed to Slice 7N from this packet.

Do not proceed to Slice 7L-G automatically from this packet.
