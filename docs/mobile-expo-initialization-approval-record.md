# Mobile Expo Initialization Approval Record

## Slice 8G Re-Evaluation — 2026-06-06

Slice 8G re-audited all approval gates in this record as part of the
[Rendered Mobile Demo Unblock Decision Packet](rendered-mobile-demo-unblock-decision-packet.md).
**No gate status has changed.** 10 of 12 gates remain MISSING or ABSENT;
only the Security/Privacy gate is CONFIRMED. Decision remains **DEFERRED**.

Recommended safe next work: Slice 8H — Note CRUD / summary demo API walkthrough hardening.

---

## 3. Slice 8D-E

Date: 2026-06-04

---

## 1. Objective

Record a formal approval or denial decision for the initialization of a minimal Expo/React Native mobile app shell in `apps/mobile`. This is a docs-only record. It does not install any packages, edit `package.json`, modify the workspace lockfile, run any mobile commands, or change any runtime behavior.

---

## 2. Decision Status

**Expo/React Native initialization decision: DEFERRED.**

| Item | Decision |
|---|---|
| Expo/React Native app shell initialization | **DEFERRED** |
| Modifying `apps/mobile/package.json` to add Expo/React Native deps | **NOT APPROVED** |
| `pnpm-lock.yaml` modification for mobile dependencies | **NOT APPROVED** |
| Adding typecheck/build scripts for Expo | **NOT APPROVED** |
| Implementing rendered UI components | **BLOCKED / DEFERRED** |

Because required dependency, lockfile, CI, and VM resource approvals are missing, the initialization must remain DEFERRED.

---

## 3. Evidence Reviewed

The following evidence was reviewed to produce this record:

1.  **Mobile Workspace Baseline**: `apps/mobile` remains uninitialized, containing only static placeholders and the dependency-free structure added in Slice 8D-B.
2.  **No Rendered UI Dependencies**: No React, React Native, or Expo dependencies are currently declared in `apps/mobile/package.json`.
3.  **Missing Package Versions**: No specific stable Expo SDK, React version, or React Native version has been selected or validated.
4.  **No Lockfile Footprint**: No pnpm lockfile update has been staged or reviewed to confirm the transitive dependency size.
5.  **CI Impact Unknown**: The footprint of mobile building/typechecking on the 2-minute CI time constraint remains unverified.
6.  **VM Resource Constraints**: Disk and memory space limits in the development workspace have not been confirmed as sufficient to support Node/Expo builds without crash risks.

---

## 4. Approval Checklist

| Approval Item | Status | Evidence | Decision | Notes |
|---|---|---|---|---|
| Dependency/Package Approval | MISSING | None | **DENIED** | No version select done. |
| Lockfile Approval | MISSING | None | **DENIED** | No lockfile diff reviewed. |
| CI Impact Approval | MISSING | None | **DENIED** | CI script changes not reviewed. |
| VM Resource Approval | MISSING | None | **DENIED** | No workspace memory proof. |
| Security/Privacy Approval | CONFIRMED | `docs/security/privacy-and-data-handling.md` updated | **APPROVED** | Static boundaries established. |
| Rollback Plan | MISSING | None | **DENIED** | No rollback commands verified. |
| Reviewer Sign-off | ABSENT | None | **DENIED** | No named reviewer signatures. |
| Expo SDK Target Selected | MISSING | None | **DENIED** | Pinned version is `TO_BE_SELECTED`. |
| React/React Native Version Selected | MISSING | None | **DENIED** | Pinned versions are `TO_BE_SELECTED`. |
| No-Emulator/Default-CI Proof | MISSING | None | **DENIED** | No validation of lightweight CI config. |
| Package Size/Build Impact Review | MISSING | None | **DENIED** | Size footprint unquantified. |
| Local Dev Command Plan | MISSING | None | **DENIED** | Scripts are still placeholders. |

---

## 5. Decision Rule

If any required gate in section 4 is missing or insufficient:
*   Expo/React Native initialization remains **DEFERRED**.
*   No dependency installation is allowed.
*   No package manifest or lockfile changes are allowed.
*   No rendered UI implementation is allowed.

---

## 6. If Approved (Deferred Constraints)

Should initialization be approved in a future slice, it must adhere to the following constraints:
1.  **Minimal Expo App Shell Only**: Bootstraps the application via a single `App.tsx` entrypoint.
2.  **No Expo Router**: No file-system routing library may be imported without a separate approval record.
3.  **No Emulator/Device CI**: Standard CI runs must avoid emulator/simulator dependencies, validating only web transpilation and typecheck.
4.  **No Credentials/Secrets**: Environment configs must not bundle any tokens, provider API keys, or private variables.
5.  **No Live Provider**: Backend fake provider remains the default runtime provider.
6.  **No Supabase/Docker/RLS**: Local database work remains deferred.
7.  **Rollback Plan Required**: Git revert instructions must be documented to restore workspace state instantly if builds break.

---

## 7. Next Safe Path (If Denied/Deferred)

Because initialization is deferred, the safe path is:
*   Defer mobile dependencies and proceed to backend/product demo polish (Slice 8E) to refine the user summary history experience via the existing fake provider flow.
*   Optionally prepare a mobile dependency approval packet in a future slice if Expo setup becomes critical.

---

## 8. Recommended Decision

**DEFER** initialization of the Expo/React Native app shell. The risks associated with unverified dependency size, unknown CI runtime impact, and workspace resource limits outweigh the benefit of immediate UI rendering.

---

## 9. Future Slices

Based on the DEFERRED decision, the recommended follow-up slices are:
*   **Slice 8E** — Backend/product demo polish using existing fake-provider flow *(Complete)*.
*   **Slice 8F** — Dependency-free API-level demo runbook *(Complete)*.
*   **Slice 8G** — Rendered mobile demo unblock decision packet *(Complete — decision DEFERRED, safe next: Slice 8H)*.
*   **Slice 8H** — Note CRUD / summary demo API walkthrough hardening (recommended next action if deferred).
*   **Slice 8D-F** — Mobile dependency approval packet (if mobile UI execution is explicitly requested next).

---

## 10. Definition of Done

*   `docs/mobile-expo-initialization-approval-record.md` exists.
*   Decision is explicitly recorded as **DEFERRED**.
*   Roadmaps, security docs, and next-action documents are updated.
*   No runtime or package dependencies are installed.
*   No lockfile changes are made.
