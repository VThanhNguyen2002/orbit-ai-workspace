# OpenAI SDK Dependency Approval Record

## Slice 7M-C

Date: 2026-06-03

---

## 1. Objective

Record an explicit approval or denial decision for the `openai` Python SDK
dependency. Named reviewers must complete every dependency gate listed in
section 4 before any SDK install, manifest change, or runtime import is
authorized.

This document is docs-only. It does not install the SDK, change any dependency
manifest or lockfile, add runtime imports, add credentials, perform API calls,
or change runtime behavior.

---

## 2. Decision Status

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

| Item | Decision |
|---|---|
| SDK dependency install (`pip install openai`) | **NOT APPROVED** |
| `pyproject.toml` / `requirements.txt` / lockfile change | **NOT APPROVED** |
| Runtime SDK import in any module | **NOT APPROVED** |
| Credential or API key use | **NOT APPROVED** |
| Real OpenAI API call | **NOT APPROVED** |
| Live harness path | **CLOSED / BLOCKED** (0 of 8 named reviewer approvals) |

No named reviewer has provided explicit approval for any gate in section 4.
Because required approvals are missing or insufficient, the SDK dependency must
remain denied. No placeholder document, checklist, or planning document
constitutes approval.

*Update: Slice 7M-E formally re-evaluated this decision based on prepared prerequisites and confirmed that all evidence is still missing. See `docs/openai-sdk-dependency-reevaluation-record.md`. The decision remains NOT APPROVED / DENIED.*

---

## 3. Evidence Reviewed

The following evidence was reviewed to produce this record:

| Evidence item | Status | Notes |
|---|---|---|
| `docs/openai-sdk-dependency-review-packet.md` | PRESENT | Supply-chain, runtime, credential, testing, and CI checklists exist. Decision in packet: NOT APPROVED. |
| `docs/openai-sdk-adapter-plan.md` | PRESENT | Future adapter boundary, injectable transport, credential constraints, approval gates documented. Not an approval. |
| `docs/openai-provider-integration-plan.md` | PRESENT | Provider integration strategy documented. Not an approval. |
| `docs/security/privacy-and-data-handling.md` | PRESENT | Security and privacy constraints documented. Named security/privacy reviewer approval: absent. |
| `docs/ai-summarization-implementation-plan.md` | PRESENT | Summarization plan and per-slice update history documented. No SDK approval granted. |
| `apps/api/app/services/openai_sdk_adapter.py` | PRESENT | Mocked SDK adapter boundary exists; imports no real SDK; not runtime-wired. |
| `apps/api/tests/test_openai_sdk_adapter.py` | PRESENT | Fake-only adapter tests exist; no real SDK import; no credential or network use. |
| `docs/next-action.md` | PRESENT | Recommends Slice 7M-C; confirms dependency NOT APPROVED. |
| Fake provider as runtime default | CONFIRMED | `FakeSummarizationProvider` is the only runtime-enabled provider. `ai_provider=openai` fails closed. |
| Live harness approval | CONFIRMED ABSENT | CLOSED / BLOCKED — 0 of 8 named reviewer approvals (Slice 7L-G). |
| Named dependency reviewer approval | ABSENT | No named reviewer has approved the dependency. |
| Named security/privacy reviewer approval | ABSENT | `TBD_SECURITY_PRIVACY_REVIEWER` slot remains placeholder-only. |
| Named license reviewer approval | ABSENT | No license reviewer has reviewed or approved the `openai` SDK license. |
| Named supply-chain reviewer approval | ABSENT | No supply-chain reviewer has approved the dependency. |
| Named CI impact reviewer approval | ABSENT | No CI reviewer has approved the CI/build impact. |
| Mocked adapter tests pass | CONFIRMED | Tests are dependency-free and pass without real SDK install. They do not imply SDK approval. |

---

## 4. Approval Checklist

| Evidence item | Status | Decision | Notes |
|---|---|---|---|
| Dependency owner approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 4. No named reviewer sign-off yet. |
| Security / privacy approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 5. `TBD_SECURITY_PRIVACY_REVIEWER` empty. |
| License approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 6. License not yet identified. |
| Supply-chain risk approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 7. No dep enumeration; no vuln scan. |
| CI / build impact approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 8. No CI review completed. |
| Rollback plan approval | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 9. No rollback path documented. |
| No-default-live-run proof | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 10. No CI reviewer confirmation. |
| External review gate | PREPARED / STILL NOT APPROVED | **DENIED** | Checklist in prerequisites section 11. No external reviewer identified. |
| Pinned version selection | PREPARED / STILL NOT APPROVED | **DENIED** | Requirement in prerequisites section 4. No version selected. |
| Transitive dependency review | PREPARED / STILL NOT APPROVED | **DENIED** | Requirement in prerequisites section 7. No enumeration performed. |
| Vulnerability scan plan | PREPARED / STILL NOT APPROVED | **DENIED** | Requirement in prerequisites section 7. No scan planned or run. |
| Update policy | PREPARED / STILL NOT APPROVED | **DENIED** | Requirement in prerequisites section 4. No policy defined. |

**Decision rule:** Because every required approval gate is PREPARED / STILL NOT
APPROVED (prerequisites defined but not satisfied by named reviewers), the SDK
dependency must remain NOT APPROVED. No install, manifest change, runtime
import, credential use, API call, or live harness activation is allowed until
all gates are resolved.

See `docs/openai-sdk-dependency-prerequisites.md` for the full prerequisite
checklist for each gate.

---

## 5. Dependency Denial Rationale

The OpenAI SDK dependency is denied for the following specific reasons:

1. **No pinned version selected.** The candidate SDK version is
   `TO_BE_SELECTED`. No exact version or bounded range has been approved.
2. **No license review completed.** The `openai` SDK license (`TO_BE_REVIEWED`)
   has not been confirmed OSI-compatible or otherwise explicitly approved.
3. **No transitive dependency review.** The SDK's transitive dependencies have
   not been enumerated, reviewed for security, or reviewed for license
   compatibility.
4. **No supply-chain approval.** No named supply-chain reviewer has approved
   package source, pinned version, lockfile impact, transitive deps, or update
   policy.
5. **No vulnerability scan.** No `pip-audit` or equivalent has been run against
   any candidate SDK version to confirm no open critical CVEs.
6. **No CI impact approval.** Install time, package size, and lockfile diff have
   not been reviewed or approved by a named CI reviewer.
7. **No rollback plan approved.** No explicit rollback or dependency-removal
   path has been documented or approved.
8. **No named reviewer approvals exist.** All eight reviewer gate slots in the
   dependency review packet (section 6) remain `TBD_*` placeholder-only.
9. **Live harness path is closed.** The live harness approval path remains
   CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST (Slice 7L-G — 0 of 8 named
   reviewer approvals).
10. **Credential mode is not approved for production.** No credential-mode
    reviewer has approved `OPENAI_API_KEY` local use or any other credential
    path for production.

---

## 6. What Remains Allowed

The following items remain allowed without SDK approval:

- Mocked interface tests using injected fake SDK-like clients
  (`apps/api/tests/test_openai_sdk_adapter.py`).
- Docs planning and boundary design documents.
- Dependency-free adapter boundary
  (`apps/api/app/services/openai_sdk_adapter.py`) that imports no real SDK.
- Fake provider as the only runtime default (`ai_provider=fake`).
- Redaction and fail-closed tests using synthetic data.
- External review preparation (checklist, evidence packet, reviewer
  solicitation).

---

## 7. Explicitly Blocked

The following items remain explicitly blocked until all approval gates in
section 4 are resolved:

- SDK install (`pip install openai` or equivalent)
- Any `pyproject.toml`, `requirements.txt`, or lockfile edit
- Runtime import of the `openai` SDK in any module
- Real OpenAI API call
- Adding or using `OPENAI_API_KEY` or any provider credential
- Implementing WIF runtime token exchange
- Switching default runtime provider from `fake` to `openai`
- Opening the live harness path
- Adding a `workflow_dispatch` live provider CI job
- Default CI live tests using any real provider
- Production API-key fallback without credential-mode reviewer sign-off

---

## 8. Reopen Criteria

Future SDK dependency approval may be reconsidered only if all of the
following conditions are met and explicitly documented with named reviewer
sign-offs:

1. **Exact SDK package and version selected.** A specific pinned version or
   bounded range from the official PyPI `openai` package is chosen.
2. **License reviewed and approved.** The SDK license has been confirmed by a
   named license reviewer to be compatible with the project's requirements.
3. **Transitive dependencies enumerated.** All transitive deps are listed and
   individually reviewed for license, security, and size.
4. **Vulnerability scan approved.** `pip-audit` or equivalent has been run
   against the pinned candidate version; no open critical CVEs exist; a named
   reviewer has approved the result.
5. **CI / build impact reviewed.** Install time and total package size are
   acceptable; lockfile diff is reviewed; a named CI reviewer has approved.
6. **Rollback plan approved.** An explicit step to remove the dependency is
   documented and approved by a named reviewer.
7. **Credential mode separately approved.** Local API-key use or any other
   credential path has been approved by a named credential-mode reviewer per the
   evidence packet.
8. **External review sign-off exists.** `TBD_EXTERNAL_REVIEWER` slot is filled
   with an actual named reviewer who has provided explicit sign-off.
9. **All 8 dependency gate reviewers are named and have approved.** No `TBD_*`
   placeholder may remain in any required reviewer slot.

---

## 9. Future Slices

Recommended follow-up slices:

- **Slice 7M-D — Resolve OpenAI SDK dependency approval prerequisites.**
  *(Complete — all 12 gates PREPARED / STILL NOT APPROVED.
  Record: `docs/openai-sdk-dependency-prerequisites.md`.)*
- **Slice 7M-E — Re-evaluate SDK dependency approval with evidence.**
  *(Complete — all evidence missing. Record: `docs/openai-sdk-dependency-reevaluation-record.md`. Decision remains NOT APPROVED / DENIED.)*
- **Slice 7M-F — Optional SDK dependency install.** Only reachable after Slice
  7M-H records explicit named approval for every gate in section 4.
- **Slice 7M-G — Keep mocked adapter path dependency-free.** *(Complete — Record: `docs/openai-sdk-dependency-free-strategy.md`.)*
- **Slice 7M-H — Dependency-free OpenAI adapter hardening plan.**
- **Slice 7M-I — Provider boundary cleanup/refactor planning.**
- **Slice 7N — Live harness skeleton.** Only reachable after all 8 live harness
  approvals exist and a separate implementation slice is approved. Live path
  remains CLOSED.

Do not proceed to any of the above automatically.

---

## 10. Non-Goals (This Slice)

This record explicitly excludes:

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

## 11. Definition Of Done

This slice is complete when:

- `docs/openai-sdk-dependency-approval-record.md` exists.
- Decision is explicitly recorded as NOT APPROVED / DENIED.
- All 12 gate items are marked MISSING.
- Referenced docs are minimally updated to acknowledge Slice 7M-C.
- `docs/next-action.md` recommends Slice 7M-D.
- No SDK dependency, credential, `.env` file, API call, token exchange, WIF
  runtime, backend route, API client method, SSE/frontend, Supabase, SQL,
  migration, lockfile, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- OpenAI SDK dependency decision remains NOT APPROVED / DENIED.
