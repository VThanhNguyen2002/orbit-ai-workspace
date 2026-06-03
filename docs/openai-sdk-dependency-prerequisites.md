# OpenAI SDK Dependency Approval Prerequisites

## Slice 7M-D

Date: 2026-06-03

---

## 1. Objective

Prepare required-action records for each missing approval gate identified in
`docs/openai-sdk-dependency-approval-record.md`. This document maps each MISSING
gate to a concrete prerequisite checklist so that future named reviewers know
exactly what evidence is required before approval can be reconsidered.

**This document is not approval.** Preparing prerequisite checklists does not
install the SDK, change any dependency manifest, add runtime imports, add
credentials, perform API calls, or change runtime behavior.

---

## 2. Current Decision Status

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

| Item | Decision |
|---|---|
| SDK dependency install (`pip install openai`) | NOT APPROVED |
| `pyproject.toml` / `requirements.txt` / lockfile change | NOT APPROVED |
| Runtime SDK import in any module | NOT APPROVED |
| Credential or API key use | NOT APPROVED |
| Real OpenAI API call | NOT APPROVED |
| Live harness path | CLOSED / BLOCKED (0 of 8 named reviewer approvals) |

Preparing prerequisites does not change the above decisions. All 12 gates
remain MISSING until named reviewers provide explicit evidence-backed sign-offs.
*(Update: Slice 7M-E re-evaluated this and found all evidence still missing. See `docs/openai-sdk-dependency-reevaluation-record.md`).*

---

## 3. Missing Approval Gates

| Approval gate | Current status | Required evidence | Reviewer placeholder | Next action |
|---|---|---|---|---|
| Dependency owner approval | MISSING | Named owner selects exact SDK version; signs off on install | `TBD_DEPENDENCY_OWNER` | Solicit named reviewer; fill section 4 |
| Security / privacy approval | MISSING | Named reviewer confirms credential/logging/redaction rules; signs off | `TBD_SECURITY_PRIVACY_REVIEWER` | Solicit named reviewer; fill section 5 |
| License approval | MISSING | SDK license identified; compatibility confirmed; transitive licenses reviewed | `TBD_LICENSE_REVIEWER` | Complete license review; fill section 6 |
| Supply-chain risk approval | MISSING | Package source, pinned version, changelog, transitive deps, vuln scan, update policy all reviewed | `TBD_SUPPLY_CHAIN_REVIEWER` | Complete supply-chain review; fill section 7 |
| CI / build impact approval | MISSING | Install time, package size, Python compat, lockfile diff, no-live-test proof reviewed | `TBD_CI_REVIEWER` | Complete CI review; fill section 8 |
| Rollback plan approval | MISSING | Explicit dependency removal path documented and approved | `TBD_ROLLBACK_REVIEWER` | Document rollback path; fill section 9 |
| No-default-live-run proof | MISSING | Named CI reviewer confirms CI stays fake-only, credential-free, network-free after install | `TBD_CI_REVIEWER` | Prepare CI posture proof; fill section 10 |
| External review gate | MISSING | Named external reviewer signs off on version, risk checklist, and rollback | `TBD_EXTERNAL_REVIEWER` | Solicit external reviewer; fill section 11 |
| Pinned version selection | MISSING | Exact PyPI version or bounded range selected and documented | `TBD_DEPENDENCY_OWNER` | Select candidate version; record in section 4 |
| Transitive dependency review | MISSING | All transitive deps enumerated; each reviewed for license, security, size | `TBD_SUPPLY_CHAIN_REVIEWER` | Enumerate deps; record in section 7 |
| Vulnerability scan plan | MISSING | `pip-audit` or equivalent planned; candidate version confirmed CVE-free | `TBD_SUPPLY_CHAIN_REVIEWER` | Plan and execute scan; record result in section 7 |
| Update policy | MISSING | Explicit policy for reviewing SDK updates before applying them | `TBD_DEPENDENCY_OWNER` | Define update policy; record in section 4 |

---

## 4. Dependency Owner Prerequisite

**Status: MISSING / NOT APPROVED**

A named dependency owner must provide the following before gateway can advance:

| Required item | Expected content | Current value |
|---|---|---|
| Reviewer name | Full name or handle of named owner | `TBD_DEPENDENCY_OWNER` |
| SDK package name | Official PyPI package to be added | `openai` (unconfirmed — pending official docs review) |
| Candidate version | Exact version or bounded range | `TO_BE_SELECTED` |
| Version pin strategy | Exact pin (`==x.y.z`) or bounded range (`>=x.y,<x.z`) | `TO_BE_PINNED` |
| Update policy | How SDK updates will be reviewed before applying | `TO_BE_DEFINED` |
| Approval wording | Explicit sign-off stating install is approved for the selected version | Not present |

No placeholder above constitutes approval. The dependency owner must replace
each `TO_BE_*` field with a verified, named, dated decision before any install
is authorized.

---

## 5. Security / Privacy Prerequisite

**Status: MISSING / NOT APPROVED**

A named security/privacy reviewer must confirm all of the following:

| Security requirement | Required confirmation |
|---|---|
| No credential logging | `OPENAI_API_KEY` or equivalent must never appear in logs, errors, or reprs |
| No prompt/content logging | Note title, note content, and prompt text must not appear in logs |
| No raw SDK body logging | Raw SDK response body must not appear in logs or public errors |
| No auth header logging | Raw `Authorization` header value must be redacted before any logging |
| Redaction required | All diagnostics must pass through the redaction helper before reaching logs or public error surfaces |
| Fail-closed behavior required | SDK import failure, missing credentials, and invalid config must all fail closed at provider construction |
| No PII in prompts | Prompts must not include user email, display name, or user auth tokens |
| Safe error mapping | All SDK errors must map to coarse public errors; raw SDK bodies must not reach routers or clients |

The reviewer must provide explicit written sign-off confirming each item is
satisfied for the selected SDK version and its transitive dependencies.

---

## 6. License Prerequisite

**Status: MISSING / NOT APPROVED**

A named license reviewer must complete all of the following:

| License requirement | Required action |
|---|---|
| SDK license identification | Identify the exact license for the candidate `openai` SDK version from the official package metadata |
| License compatibility review | Confirm the license is compatible with the project's requirements (OSI-compatible or otherwise explicitly approved) |
| Transitive dependency licenses | Enumerate transitive dependencies; identify each license; confirm compatibility |
| No copyleft surprises | Confirm no transitive dependency carries a copyleft license that would affect the project |
| License approval wording | Explicit sign-off stating the license is acceptable for production use |

No install is authorized until a named license reviewer provides explicit
written confirmation that the SDK and all transitive dependencies are
license-compatible.

---

## 7. Supply-Chain Prerequisite

**Status: MISSING / NOT APPROVED**

A named supply-chain reviewer must complete all of the following:

| Supply-chain requirement | Required action |
|---|---|
| Package source verification | Confirm the candidate `openai` package is the official SDK published on PyPI by OpenAI; verify maintainer identity against official OpenAI SDK documentation |
| Pinned version | Record exact pinned version (or bounded range) approved by the dependency owner |
| Release / changelog review | Review the SDK changelog for the candidate version: identify breaking changes, removed features, and security advisories |
| Transitive dependencies | Enumerate all transitive dependencies installed by `openai==<candidate>`; record each package, version, and license |
| Vulnerability scan | Run `pip-audit --requirement <candidate>` or equivalent; confirm no open critical or high CVEs; document the scan result |
| No unreviewed postinstall scripts | Confirm no postinstall scripts execute during `pip install openai==<candidate>` |
| Minimal dependency additions | Confirm only the minimum required packages are added; no unnecessary transitive deps |
| Update policy | Define and document how SDK updates will be evaluated before applying them (e.g., changelog review + re-scan required before version bump) |
| Rollback path | Define the explicit step to remove the dependency if a rollback is required (covered further in section 9) |

All items above must be completed and signed off by a named reviewer before any
install is authorized.

---

## 8. CI / Build Impact Prerequisite

**Status: MISSING / NOT APPROVED**

A named CI reviewer must complete all of the following:

| CI requirement | Required action |
|---|---|
| Install time impact | Measure `pip install openai==<candidate>` time impact on the CI baseline; confirm it is acceptable |
| Package size impact | Confirm total installed size (SDK + transitive deps) is acceptable for the CI environment |
| Python version compatibility | Confirm the candidate SDK version supports all Python versions used in CI |
| Lockfile diff review | Review the full lockfile diff produced by adding the dependency; confirm no unexpected additions |
| No default live tests | Confirm CI remains fake-only, credential-free, and network-free after the dependency is installed |
| No workflow secret changes | Confirm CI workflow files are not modified as part of the dependency install slice |
| No `workflow_dispatch` live job | Confirm no live provider workflow job is added in the dependency install slice |
| CI reviewer sign-off | Named CI reviewer provides explicit written confirmation of all items above |

---

## 9. Rollback Prerequisite

**Status: MISSING / NOT APPROVED**

A named rollback owner must document and approve the following:

| Rollback requirement | Required detail |
|---|---|
| Dependency removal path | Exact steps to remove `openai` from `pyproject.toml` (or equivalent) and regenerate the lockfile without affecting other dependencies |
| Fake provider remains default | After rollback, `ai_provider=fake` must remain the only runtime-enabled default |
| Runtime guard remains fail-closed | After rollback, `ai_provider=openai` must continue to fail closed at runtime |
| No route switch | Rollback must not require any router or service change; provider selection must be purely config-driven |
| No live provider default | Rollback must restore the system to a state where no live provider is reachable by default |
| Rollback test plan | Describe how the rollback will be verified (e.g., CI passes fake-only after dependency removal) |
| Rollback reviewer sign-off | Named rollback owner provides explicit written confirmation of the rollback plan |

---

## 10. No-Default-Live-Run Prerequisite

**Status: MISSING / NOT APPROVED**

A named CI reviewer must confirm all of the following:

| No-live-run requirement | Required confirmation |
|---|---|
| Normal push CI does not set live flags | Confirm no environment variable, workflow input, or matrix entry activates live provider behavior on a normal push |
| No live provider job by default | Confirm no job in the CI workflow calls the OpenAI API or any other live provider on normal push |
| No `workflow_dispatch` live validation | Confirm no `workflow_dispatch` input enables live provider calls unless a separately approved slice adds it |
| No credentials in CI | Confirm no `OPENAI_API_KEY` or equivalent secret is added to CI environment by the dependency install slice |
| Fake-only proof | Confirm tests still pass with no credentials present; network is blocked at test level |
| CI reviewer sign-off | Named CI reviewer provides explicit written confirmation of all items above |

---

## 11. External Review Prerequisite

**Status: MISSING / NOT APPROVED**

A named external reviewer must provide all of the following:

| External review requirement | Required content |
|---|---|
| Reviewer identity | Named external reviewer (not a project contributor) |
| SDK version reviewed | Exact version of the `openai` SDK evaluated |
| Risk checklist reviewed | Reviewer confirms supply-chain, license, security, and CI risk items from sections 5–10 |
| Rollback reviewed | Reviewer confirms the rollback plan from section 9 is adequate |
| Approval wording | Explicit written sign-off from the named external reviewer |
| Review location | Sign-off must be recorded in `docs/openai-sdk-dependency-approval-record.md` or a linked PR review |

---

## 12. Resolution Matrix

Preparing this prerequisite document (Slice 7M-D) does not satisfy any approval
gate. Each gate moves from MISSING to PREPARED / STILL NOT APPROVED.

| Prerequisite | Prepared in 7M-D | New status | Why dependency still denied | Next required action |
|---|---|---|---|---|
| Dependency owner approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No named reviewer has signed off | Solicit `TBD_DEPENDENCY_OWNER`; get explicit sign-off |
| Security / privacy approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No named reviewer has signed off | Solicit `TBD_SECURITY_PRIVACY_REVIEWER`; get explicit sign-off |
| License approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No license review completed | Identify license; solicit `TBD_LICENSE_REVIEWER` |
| Supply-chain risk approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No transitive dep enumeration; no vuln scan | Complete supply-chain review; solicit `TBD_SUPPLY_CHAIN_REVIEWER` |
| CI / build impact approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No CI impact review completed | Complete CI review; solicit `TBD_CI_REVIEWER` |
| Rollback plan approval | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No rollback path documented | Document rollback; solicit `TBD_ROLLBACK_REVIEWER` |
| No-default-live-run proof | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No CI reviewer confirmation | Prepare proof; solicit `TBD_CI_REVIEWER` |
| External review gate | ✓ Checklist defined | PREPARED / STILL NOT APPROVED | No external reviewer identified | Solicit `TBD_EXTERNAL_REVIEWER` |
| Pinned version selection | ✓ Requirement documented | PREPARED / STILL NOT APPROVED | No version selected | `TBD_DEPENDENCY_OWNER` must select and record candidate version |
| Transitive dependency review | ✓ Requirement documented | PREPARED / STILL NOT APPROVED | No enumeration performed | `TBD_SUPPLY_CHAIN_REVIEWER` must enumerate and review |
| Vulnerability scan plan | ✓ Requirement documented | PREPARED / STILL NOT APPROVED | No scan planned or run | `TBD_SUPPLY_CHAIN_REVIEWER` must plan and run scan |
| Update policy | ✓ Requirement documented | PREPARED / STILL NOT APPROVED | No policy defined | `TBD_DEPENDENCY_OWNER` must define and record policy |

**PREPARED / STILL NOT APPROVED is not an approval state.** All gates remain
denied. No install, manifest change, runtime import, credential use, or API
call is authorized by this document.

---

## 13. Future Path

Recommended follow-up slices:

- **Slice 7M-E — Re-evaluate SDK dependency approval with evidence.** *(Complete — all evidence missing. Record: `docs/openai-sdk-dependency-reevaluation-record.md`. Decision remains NOT APPROVED / DENIED.)*
- **Slice 7M-F — Optional SDK dependency install.** Only reachable after Slice
  7M-H records explicit named approval for every gate. Includes `pyproject.toml`
  edit, lockfile regeneration, and CI verification.
- **Slice 7M-G — Keep mocked SDK adapter path dependency-free.** Documents permanent or long-term strategy for maintaining
  the mocked adapter boundary without installing the real SDK. Recommended since Slice 7M-E denied approval again.

Do not proceed to any of the above automatically.

---

## 14. Non-Goals (This Slice)

This document explicitly excludes:

- SDK installation or any dependency manifest change.
- Runtime SDK import.
- Credential addition.
- Real OpenAI API calls.
- WIF runtime implementation.
- Token exchange.
- GitHub OIDC token requests.
- Live harness path changes.
- Backend route changes.
- API client method changes.
- SSE streaming implementation.
- Frontend or Expo work.
- Supabase / RLS work, SQL, migrations, or generated Supabase state.
- `.gitleaksignore` changes.

---

## 15. Definition Of Done

This slice is complete when:

- `docs/openai-sdk-dependency-prerequisites.md` exists.
- All 12 missing gates have a defined prerequisite checklist.
- Each gate status is updated to PREPARED / STILL NOT APPROVED.
- `docs/openai-sdk-dependency-approval-record.md` is updated to reflect the new
  PREPARED / STILL NOT APPROVED status for each gate.
- Referenced docs are minimally updated to acknowledge Slice 7M-D.
- `docs/next-action.md` recommends Slice 7M-E.
- No SDK dependency, credential, `.env` file, API call, token exchange, WIF
  runtime, backend route, API client method, SSE/frontend, Supabase, SQL,
  migration, lockfile, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- OpenAI SDK dependency decision remains NOT APPROVED / DENIED.
