# Rendered Mobile Demo Unblock Decision Packet

Slice: **8G**
Date: 2026-06-06
Status: **DOCS-ONLY — Decision Required**

---

## 1. Objective

Decide whether the project should unblock rendered mobile demo work now, after
the API-level fake-provider demo runbook completed in Slice 8F, or defer it and
continue backend/product work.

This packet revisits all deferred Expo/React Native initialization gates from
the approval record in
[`docs/mobile-expo-initialization-approval-record.md`](mobile-expo-initialization-approval-record.md)
and surfaces the decision criteria clearly so the user can choose a path.

No packages are installed. No package manifests or lockfiles are edited. No
Expo or React Native runtime is initialized. No rendered UI is implemented. No
live provider, credential, `.env`, SQL, migration, Supabase state, Docker work,
OpenAI SDK, or WIF runtime is touched.

---

## 2. Current Status

### 2.1 What Exists

| Component | Status |
|---|---|
| Backend fake summary history (`GET /v1/ai/notes/{id}/summaries`) | ✅ Complete — returns newest first |
| Backend fake summarize endpoint (`POST /v1/ai/notes/{id}/summarize`) | ✅ Complete — deterministic fake provider |
| Backend demo tests (note detail → empty history → generate → list) | ✅ Complete — covers leak checks |
| API client (`client.ai.summarizeNote`, `client.ai.listNoteSummaries`) | ✅ Complete — Zod-validated, typed |
| Shared contracts (`Summary`, `ListSummariesResponse`) | ✅ Complete — in `@synapse/shared` |
| Mobile TypeScript source structure | ✅ Complete — dependency-free |
| `apps/mobile/src/api/synapseClient.ts` | ✅ Complete — app-level client boundary |
| `apps/mobile/src/features/notes/summaryHistoryApi.ts` | ✅ Complete — adapter with `listSummaries`, `summarizeForNote` |
| `apps/mobile/src/features/notes/summaryHistoryViewState.ts` | ✅ Complete — idle/loading/empty/success/error/summarizing states |
| `apps/mobile/src/features/notes/noteSummaryHistoryPlaceholder.ts` | ✅ Complete — region placeholder, no rendering |
| API-level demo runbook | ✅ Complete — `docs/backend-product-demo-polish-record.md` |

### 2.2 What Does NOT Exist

| Component | Status |
|---|---|
| Rendered mobile UI (screens, JSX, components) | ❌ Does not exist |
| Expo/React Native runtime | ❌ Not initialized |
| `App.tsx` entrypoint | ❌ Does not exist |
| JSX / `.tsx` support in `tsconfig.json` | ❌ Not configured (`"include": ["src/**/*.ts"]` only) |
| React, React Native, Expo declared in `package.json` | ❌ Zero UI dependencies |
| Lockfile entry for any mobile UI framework | ❌ Not present |
| Navigation / Expo Router | ❌ Not initialized |
| Emulator/device CI | ❌ Not configured |

### 2.3 Known Limitations

- **Memory-only summary history**: All summary history resets when the backend
  process restarts. There is no persistent database storage.
- **Fake provider only**: No live OpenAI/Gemini/Groq provider is wired. All
  summaries are deterministic fake output.
- **OpenAI SDK**: Decision remains `NOT APPROVED / DENIED`. No real AI API
  calls are possible.
- **Supabase/Docker/RLS**: Remain out of scope and not approved.
- **Package/lockfile changes**: Not approved for any new mobile UI dependencies.

---

## 3. Candidate Paths

Four options are evaluated below.

---

### Option A — Approve Minimal Expo Shell Initialization Now

**Description**: Approve `apps/mobile` initialization with a bare Expo app
shell containing a single `App.tsx` entry (no Expo Router), add Expo SDK,
React, and React Native to `apps/mobile/package.json`, update `pnpm-lock.yaml`,
and update `tsconfig.json` to support JSX. Render a single summary history
screen using the existing view-state layer.

| Dimension | Assessment |
|---|---|
| **Value** | High — provides first rendered screen, visual summary flow for CV/portfolio |
| **Effort** | Medium — Expo shell only, reuses existing view-state and API adapter |
| **Risk** | Medium — unverified dependency size, CI runtime unknown, workspace resource limits unconfirmed |
| **Dependency / package impact** | Requires editing `apps/mobile/package.json` and `pnpm-lock.yaml`. Adds Expo SDK, React, React Native, and transitive dependencies. **All package manifest and lockfile changes require explicit user approval first.** |
| **VM / resource impact** | Unknown. Expo `node_modules` footprint is significant (hundreds of MB). Workspace memory constraints not confirmed. |
| **CI impact** | Unknown. Mobile typecheck and lint steps expand CI runtime. 2-minute CI budget impact unverified. |
| **Demo / CV value** | High — visible rendered UI is more compelling than code-only or API-only demos |
| **Recommended agent** | Mobile / Frontend developer agent (post-approval) |
| **Next slice if chosen** | Slice 8H — Initialize minimal Expo app shell with approved dependencies |

**Approval gate status for Option A**:

| Gate | Status |
|---|---|
| Dependency / package approval | **MISSING** |
| Lockfile approval | **MISSING** |
| CI impact approval | **MISSING** |
| VM resource approval | **MISSING** |
| Security / privacy approval | CONFIRMED (static boundaries in `docs/security/privacy-and-data-handling.md`) |
| Rollback plan | **MISSING** |
| Reviewer sign-off | **ABSENT** |
| Expo SDK version selected | **MISSING** (placeholder `TO_BE_SELECTED`) |
| React / React Native version selected | **MISSING** (placeholder `TO_BE_SELECTED`) |
| No-emulator / default-CI proof | **MISSING** |
| Package size / build impact review | **MISSING** |
| Local dev command plan | **MISSING** (current scripts are placeholders: `echo "Expo app is not initialized yet"`) |

> [!WARNING]
> **10 of 12 approval gates are MISSING or ABSENT.** Option A cannot proceed
> until the user explicitly provides approvals for all missing gates. Rendered
> mobile work remains **BLOCKED** until then.

---

### Option B — Defer Expo/RN and Continue Backend/Product Demo Work

**Description**: Leave Expo initialization deferred. Continue building backend
demo value: polish note CRUD endpoints, add more demo API runbooks, harden the
fake-provider flow, write API client/domain tests, and produce a demo
walkthrough doc. No new dependencies.

| Dimension | Assessment |
|---|---|
| **Value** | High for backend/product depth. Maintains the existing clean CI green state. |
| **Effort** | Low — no new packages, no new runtime setup, no mobile tooling. |
| **Risk** | Low — no package drift, no VM resource risk, no CI expansion. |
| **Dependency / package impact** | Zero. No manifests or lockfiles edited. |
| **VM / resource impact** | Zero. |
| **CI impact** | Zero. |
| **Demo / CV value** | Medium — backend demo depth and API walkthrough scripts show engineering rigor; less visually striking than a rendered screen. |
| **Recommended agent** | Backend developer agent |
| **Next slice if chosen** | Slice 8H — Note CRUD / summary demo API walkthrough hardening |

> [!TIP]
> Option B is the **safe default** if any approval gate remains missing. It
> keeps the project moving productively without accumulating dependency or CI
> risk.

---

### Option C — Create Static Screenshots or Mockups Outside Runtime

**Description**: Produce static design mockups or hand-drawn wireframe images
of the note summary history screen without running Expo, React Native, or any
mobile runtime. The mockups live in `docs/` as image files or ASCII diagrams.

| Dimension | Assessment |
|---|---|
| **Value** | Low-to-Medium — provides visual evidence of the intended UX without runtime risk |
| **Effort** | Low — no code, no packages, design tool or text-based diagrams only |
| **Risk** | Low — no runtime, no dependencies, no CI impact |
| **Dependency / package impact** | Zero |
| **VM / resource impact** | Zero |
| **CI impact** | Zero |
| **Demo / CV value** | Low-Medium — static mockups show UI intent; lack interactivity and real data flow |
| **Recommended agent** | Documentation / Design agent |
| **Next slice if chosen** | Can combine with Slice 8H backend work; no separate slice required |

> [!NOTE]
> Option C is a useful complement to any other option. It does not block or
> require any dependency approval. However, it does not demonstrate a real
> working flow and provides limited portfolio value compared to a running app.

---

### Option D — Lightweight Web-Only Demo Shell Using Existing Dependencies

**Description**: Inspect whether the existing workspace dependencies (TypeScript,
`@synapse/api-client`, `@synapse/shared`) are sufficient to serve a minimal
browser-rendered HTML/JS or TypeScript-based demo page that calls the fake
backend and renders summary output, **without installing any new packages**.

| Dimension | Assessment |
|---|---|
| **Value** | Medium — provides visible, interactive demo without mobile toolchain |
| **Effort** | Medium — requires a small web harness; view-state layer exists but has no JSX renderer |
| **Risk** | Low-to-Medium — no new packages; however the existing workspace has no web bundler wired for mobile; `apps/mobile/tsconfig.json` currently only includes `*.ts` files (no JSX) |
| **Dependency / package impact** | Zero if limited to plain TypeScript + `fetch`. Any bundler (Vite, etc.) would require a new package. |
| **VM / resource impact** | Minimal |
| **CI impact** | Minimal — only a new script in `package.json`, no new toolchain |
| **Demo / CV value** | Medium — browser-rendered is less impressive than native mobile but more impressive than code-only |
| **Recommended agent** | Frontend developer agent (post-feasibility check) |
| **Next slice if chosen** | Slice 8H — Web-only summary demo shell (no new packages) |

> [!NOTE]
> Option D is only viable if no new packages are required. The current mobile
> workspace has no JSX runtime, no bundler, and no renderer. A plain
> `<script type="module">` with `fetch` calls to the backend could technically
> demonstrate the API flow in a browser without any packages, but would not
> produce a styled mobile-like UI. If a bundler or JSX renderer is needed,
> Option D collapses into a reduced form of Option A and would require the same
> package/lockfile approval gates.

---

## 4. Approval Gates

The following gates must all be satisfied before any rendered mobile
implementation can proceed.

| Gate | Current Status | Required Before |
|---|---|---|
| 1. Dependency / package approval | **MISSING** | Any `package.json` edit |
| 2. Lockfile approval | **MISSING** | Any `pnpm-lock.yaml` edit |
| 3. CI impact approval | **MISSING** | Any CI script expansion |
| 4. VM resource approval | **MISSING** | Any Expo / RN install |
| 5. Security / privacy approval | ✅ CONFIRMED | (Already done; maintains static boundaries) |
| 6. Rollback plan | **MISSING** | Mobile workspace init |
| 7. Reviewer sign-off | **ABSENT** | Any implementation slice |
| 8. Expo SDK version selected | **MISSING** | `package.json` edit |
| 9. React / React Native version selected | **MISSING** | `package.json` edit |
| 10. No-emulator / default-CI proof | **MISSING** | CI workflow change |
| 11. Package size / build impact review | **MISSING** | Lockfile edit |
| 12. Local dev command plan | **MISSING** | `dev` / `build` scripts are placeholders |

**Current score: 1 of 12 gates satisfied.**

---

## 5. Decision Rule

> [!IMPORTANT]
> **If any required gate in section 4 is missing or absent, rendered mobile
> work remains BLOCKED.**
>
> The following remain NOT APPROVED until explicit user sign-off:
> - Expo/React Native dependency installation
> - `apps/mobile/package.json` manifest edits (for UI dependencies)
> - `pnpm-lock.yaml` lockfile edits
> - Rendered UI component implementation
> - Emulator / device CI configuration
> - Live OpenAI / Supabase / RLS / provider work

---

## 6. Recommended Decision

**Recommendation: DEFER rendered mobile UI work. Proceed with Option B.**

### Rationale

1. **10 of 12 approval gates are missing.** No concrete evidence — lockfile
   diff, CI timing, VM resource budget, pinned SDK versions, rollback plan, or
   reviewer sign-off — has been provided. Proceeding without these gates
   carries real risk of workspace instability, CI budget overrun, and
   unreviewed dependency drift.

2. **Backend/product demo depth has more immediate value.** The fake-provider
   API flow is verified and runnable. Note CRUD endpoints, API client tests,
   and demo walkthrough hardening add portfolio substance without risk.

3. **The view-state layer is already complete.** The mobile TypeScript
   foundation (`summaryHistoryApi.ts`, `summaryHistoryViewState.ts`) is in
   place. When approvals are eventually granted, the rendered screen
   implementation is a well-scoped, low-risk slice.

4. **Memory-only history remains a demo limitation.** Without persistent
   storage, rendered mobile UI would still need to explain the reset caveat;
   this weakens the demo impression even if rendering is unblocked.

5. **Dependency-free posture is a strength.** The repository demonstrates
   clean TypeScript contracts, Zod validation, injected dependencies, and
   tested view-state logic without runtime framework overhead. That is a
   credible portfolio signal on its own.

**If the user explicitly provides approvals for all 12 gates listed in
section 4 — in writing, in a dedicated approval record — Option A becomes the
recommended path and the next slice becomes Slice 8H (Initialize minimal Expo
app shell with approved dependencies).**

---

## 7. Safe Next Work (If Deferred)

If the decision is to defer rendered mobile UI, the following work is
productive and dependency-free:

| Priority | Work | Slice |
|---|---|---|
| 1 | Note CRUD flow demo polish — harden `POST /v1/notes`, `GET`, `PATCH`, `DELETE` demo sequences and add runbook coverage | Slice 8H |
| 2 | Summary demo API walkthrough hardening — expand the runbook with error/edge-case paths (note not found, empty history, repeated generation) | Slice 8H |
| 3 | API client / domain tests — add unit tests for `client.notes.*` methods and edge cases in contract parsing | Slice 8H |
| 4 | Docs / demo walkthrough — produce a single-page demo script combining note CRUD and summary flow for a reviewer or CV audience | Slice 8H |
| 5 | Static mockup of summary history screen (Option C) — ASCII or image-based UX sketch in `docs/` | Slice 8H |

None of the above require new packages, lockfile changes, or Expo
initialization.

---

## 8. Blocked Work

Until all gates in section 4 are approved, the following work is explicitly
**BLOCKED**:

- ❌ Expo / React Native dependency install
- ❌ `apps/mobile/package.json` edits to add UI framework dependencies
- ❌ `pnpm-lock.yaml` modifications for mobile UI packages
- ❌ Rendered UI component implementation (`.tsx`, `App.tsx`, screens)
- ❌ Emulator / device CI configuration
- ❌ Live OpenAI API calls or SDK installation
- ❌ Supabase / Docker / RLS / live provider wiring
- ❌ SQL execution or database migrations
- ❌ WIF runtime token exchange
- ❌ `.gitleaksignore` broadening
- ❌ `.env` files or credential introduction

---

## 9. Future Slices

**If DEFERRED (recommended)**:

> **Slice 8H — Note CRUD / summary demo API walkthrough hardening**
>
> Polish the note CRUD and summary demo sequences as an API/code-level
> runbook. Add edge-case paths, error coverage, and a combined demo
> walkthrough script. Dependency-free, no lockfile changes, no rendered UI.

**If APPROVED (all 12 gates signed off by user)**:

> **Slice 8H — Initialize minimal Expo app shell with approved dependencies**
>
> Bootstrap `apps/mobile` with the approved Expo SDK version, a single
> `App.tsx` entry, JSX-enabled `tsconfig.json`, and a minimal summary history
> screen using the existing view-state layer. No Expo Router, no live
> provider, no credentials.

---

## 10. Definition of Done

This slice is docs-only. It is complete when:

- [x] `docs/rendered-mobile-demo-unblock-decision-packet.md` is created and
  committed to `main`.
- [x] The packet states explicitly whether rendered mobile demo initialization
  is approved, deferred, or blocked.
- [x] Missing approval evidence is listed as concrete prerequisites (section 4).
- [x] The next safe product step is named (section 7 / section 9).
- [x] Fake-provider-only demo constraints remain unchanged.
- [x] Security/privacy constraints remain unchanged.
- [x] Fast checks pass: clean working tree, no `.env`/SQL/migration files
  tracked, no gitleaks findings.
- [x] Companion docs are minimally updated to record the Slice 8G decision
  and point `next-action.md` at the deferred Slice 8H.
- [x] No runtime, dependency, secret, package manifest, lockfile, rendered UI,
  or CI changes are made.
