# Mobile Expo Initialization Approval Plan

## 1. Decision Status

> [!WARNING]
> *   **Expo/React Native initialization**: `DEFERRED` (See [mobile-expo-initialization-approval-record.md](mobile-expo-initialization-approval-record.md))
> *   **Package/lockfile changes**: `NOT APPROVED`
> *   **Rendered UI implementation**: `BLOCKED / DEFERRED`

---

## 2. Objective

Plan a formal approval process for initializing a minimal Expo/React Native mobile app shell in `apps/mobile`. This plan outlines the smallest safe set of dependencies, configuration updates, and CI modifications required before any UI components can be rendered.

---

## 3. Non-Goals

This approval plan explicitly excludes:

*   **Implementation/Execution in this slice**: No runtime files or screen components are written.
*   **Dependency Installation**: No package installation, command execution (`pnpm add`), or lockfile changes.
*   **Real Provider Connection**: No live LLM integrations or real OpenAI/Gemini endpoints.
*   **Credentials & Secrets**: No API keys, token configs, or `.env` files are introduced.
*   **Supabase/Database Integration**: No Postgres database, schemas, migrations, or local SQLite RLS configs.
*   **SSE/Streaming**: Streaming remains deferred.

---

## 4. Current Mobile Baseline

*   **Directory `apps/mobile`**: Exists as a placeholder containing `package.json`, `tsconfig.json`, `README.md`, and an un-rendered TypeScript logic layout.
*   **No UI Frameworks**: There are zero declared dependencies on React, React Native, Expo, Expo Router, JSX runtime, or renderers.
*   **No Rendered UI Runtime**: No entrypoint or rendering engine is active.
*   **TypeScript configuration**: `tsconfig.json` targets plain `.ts` files, not `.tsx` (no JSX parsing support).
*   **Slice 8D-B Source**: A dependency-free source structure exists containing:
    *   `apps/mobile/src/api/synapseClient.ts` (App-level client hook)
    *   `apps/mobile/src/features/notes/summaryHistoryApi.ts` (API adapter)
    *   `apps/mobile/src/features/notes/summaryHistoryViewState.ts` (ViewState mapping & error handling)
    *   `apps/mobile/src/features/notes/noteSummaryHistoryPlaceholder.ts` (Workspace metadata & placeholder regions)

---

## 5. Why Initialization Approval Is Needed

1.  **Declared Runtime Dependencies**: Rendered UI requires UI framework dependencies. Importing React or React Native packages without declaring them in `apps/mobile/package.json` violates workspace isolation principles.
2.  **Package and Lockfile Changes**: Initializing a framework requires modifying `package.json` and generating new hashes in the workspace lockfile (`pnpm-lock.yaml`). Any lockfile modification carries risk of dependency drift.
3.  **CI Surface and Pipelines**: Introducing mobile builds transitions the `apps/mobile` workspace scripts (lint, typecheck, test, build) from static placeholders to live scripts, which expands the CI pipeline runtime.
4.  **Local Dev Resources**: Mobile dependencies can significantly increase installation sizes and local compiler overhead, which must be budgeted against development VM limits.

---

## 6. Candidate Initialization Options

We analyze the following options for introducing a mobile app shell:

### Option A: Minimal Expo app shell without Expo Router
*   **Description**: Initialize a bare Expo project containing a single `App.tsx` entrypoint without navigation libraries (no Expo Router or React Navigation).
*   **Value**: High. Safely bootstraps the rendering pipeline with minimal overhead.
*   **Effort**: Low. Only adds standard Expo + React Native packages.
*   **Dependency Impact**: Smallest possible dependency footprint for an Expo project.
*   **CI Impact**: Low. Standard linting and typechecking can run in under 15 seconds.
*   **VM/Resource Impact**: Low. Minimum disk space and memory usage.
*   **Demo/CV Value**: Medium. Renders a single-screen layout, which is sufficient for note summary verification.
*   **Risk**: Low. Avoids router file-system complexity.
*   **Recommended Next Slice**: Slice 8D-E (Approve Option A) -> Slice 8D-F (Initialize Option A).

### Option B: Expo app shell with Expo Router
*   **Description**: Initialize an Expo app using the file-based navigation framework (Expo Router).
*   **Value**: Medium. Provides native-like routing for multiple screens, but introduces redundant routing complexity for a single-screen summarization demo.
*   **Effort**: Medium-High. Requires routing boilerplate, babel updates, and asset layouts.
*   **Dependency Impact**: High. Pulls in expo-router, react-native-safe-area-context, react-native-screens, etc.
*   **CI Impact**: Medium. Increases typecheck and build times.
*   **VM/Resource Impact**: Medium. Higher package count increases node_modules size.
*   **Demo/CV Value**: High. Showcases modern Expo Routing structures.
*   **Risk**: Medium. File-based routing has more breaking configurations and version mismatches.
*   **Recommended Next Slice**: Slice 8D-E (Approve Option B).

### Option C: React Native Web-oriented minimal setup
*   **Description**: Skip Expo entirely and construct a custom Vite or Webpack shell targeting React Native Web.
*   **Value**: Low. Diverges from the project's target Expo-first mobile architecture.
*   **Effort**: High. Custom bundling setup is required.
*   **Dependency Impact**: Medium. Custom Webpack/Vite loaders.
*   **CI Impact**: Medium.
*   **VM/Resource Impact**: Medium.
*   **Demo/CV Value**: Low. Does not demonstrate real mobile framework patterns.
*   **Risk**: High. Heavy maintenance burden.
*   **Recommended Next Slice**: Slice 8D-E (Approve Option C).

### Option D: Delay Expo initialization and return to backend/product work
*   **Description**: Postpone all frontend/mobile UI work entirely. Pivot immediately back to backend persistent storage planning (Supabase integration, RLS, migration).
*   **Value**: High for backend, but stalls the visualization of the summary history demo.
*   **Effort**: Low. No new packages.
*   **Dependency Impact**: Zero.
*   **CI Impact**: Zero.
*   **VM/Resource Impact**: Zero.
*   **Demo/CV Value**: Low. No visual proof of user flow.
*   **Risk**: Low.
*   **Recommended Next Slice**: Slice 9A (Supabase persistence planning).

---

## 7. Recommended Option

> [!TIP]
> **Option A is the recommended path.** It introduces the absolute minimum dependencies required to render a UI screen without routing overhead. If future approvals are met, Slice 8D-F should initialize a basic `App.tsx` shell, targeting standard Expo web output as the primary verification surface.

---

## 8. Proposed Dependency/Package Changes for Future Implementation

The following are *placeholder candidates* only. No installation commands are authorized in this slice.

*   **Expo SDK Target**: `TO_BE_SELECTED` (Recommend SDK 51 or stable equivalent)
*   **React version**: `TO_BE_SELECTED` (Matching Expo SDK target, e.g., `^18.2.0`)
*   **React Native version**: `TO_BE_SELECTED` (Matching Expo SDK target, e.g., `0.74.x`)
*   **TypeScript/TSX Config Impact**:
    *   Change compiler target in `apps/mobile/tsconfig.json` to include `"jsx": "react-jsx"`.
    *   Update TS config to include `.tsx` file extension mappings.
*   **Optional Test Renderer**: `TO_BE_SELECTED_OR_DEFERRED` (e.g., `@testing-library/react-native`)

---

## 9. Proposed App Structure

Once approved and initialized in a future slice, the mobile workspace will structure files as follows:

```
apps/mobile/
├── App.tsx                     # Core application entrypoint (Option A root)
├── package.json                # Declared Expo, React, React Native dependencies
├── tsconfig.json               # Updated to support JSX (.tsx)
└── src/
    ├── index.ts                # Entry exports
    ├── api/
    │   └── synapseClient.ts    # Reused client hook layer
    ├── features/
    │   └── notes/
    │       ├── summaryHistoryApi.ts        # Reused from 8D-B
    │       ├── summaryHistoryViewState.ts  # Reused from 8D-B
    │       └── components/
    │           └── NoteSummaryHistoryScreen.tsx # NEW UI component rendering ViewStates
```

---

## 10. CI and Script Impact

*   **Typechecking**: Change `apps/mobile/package.json` script `"typecheck": "tsc --noEmit"` to validate JSX source code.
*   **Building**: Update `"build": "expo export"` or custom web build commands.
*   **Testing**: Implement minimal unit/renderer tests only.
*   **Lighter CI Execution**: Avoid running expensive iOS/Android emulators, EAS builds, or simulator tasks in CI. Default pipeline targets only standard web transpilation, eslint, and typecheck.

---

## 11. Security/Privacy Boundaries

The future mobile app shell must adhere to the following rules:
1.  **No local credentials**: Hardcoded secrets, developer keys, or mock LLM access codes are prohibited.
2.  **Redacted Diagnostics**: The mobile app must not receive or render raw prompt payloads or diagnostic exceptions.
3.  **Transit Warnings**: The UI must explicitly notify users of the memory-only transience of generated summary history.
4.  **No Client-Side Secrets**: All communication must go through the backend API.

---

## 12. VM/Resource Constraints

*   **Disk space allocation**: VM disk allocation is limited. Cache folders (`.expo`, `.turbo`) will be added to `.gitignore`.
*   **No Emulators**: Testing will rely on lightweight React Native Web preview in the browser rather than booting heavy Android/iOS simulators.
*   **No heavy tooling**: Avoid adding third-party UI design libraries or state managers until core structures require them.

---

## 13. Approval Gates

To transition from planning to execution, explicit reviewer approvals are required for:
1.  **Dependency/Package Gate**: Review and sign off on exact versions of Expo, React, and React Native.
2.  **Lockfile Gate**: Review the modified `pnpm-lock.yaml` to ensure no transient library pollution.
3.  **CI Impact Gate**: Verify that the new mobile typecheck and build steps do not exceed the 2-minute CI threshold.
4.  **VM Resource Gate**: Verify that local browser builds do not consume excessive memory or crash the workspace environment.
5.  **Security/Privacy Gate**: Validate that no secrets or provider API keys are exposed.
6.  **Rollback Plan**: Clear plan to revert the mobile workspace changes if build/dependency failures block other developers.

---

## 14. Future Slices

*   **Slice 8D-E** — Approve or deny minimal Expo app shell initialization.
*   **Slice 8D-F** — Initialize minimal Expo app shell if approved.
*   **Slice 8D-G** — Render summary history screen using existing view-state.
*   **Slice 8E** — Notes detail demo polish.

---

## 15. Definition of Done

This planning slice is complete when:
1.  `docs/mobile-expo-initialization-approval-plan.md` is created and committed to `main`.
2.  `docs/summary-history-ui-consumption-plan.md` is updated to link to this plan.
3.  `docs/ai-summarization-implementation-plan.md` is updated to reflect Slice 8D-D planning status.
4.  `docs/security/privacy-and-data-handling.md` is updated to address environment config constraints.
5.  `docs/next-action.md` is updated to recommend Slice 8D-E.
6.  All fast checks pass cleanly without error.
