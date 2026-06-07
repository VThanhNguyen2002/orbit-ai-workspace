# Mobile API Client Boundary Implementation Packet — Slice 8Q-B

This implementation packet outlines the task to review and harden the mobile API client construction boundary in `apps/mobile/src/api/synapseClient.ts`. It provides background context, options, rules, and a prompt for a future Codex coding session.

---

## 1. Purpose

The file `apps/mobile/src/api/synapseClient.ts` serves as the primary boundary for creating the API client instance used by the mobile application.

Currently:
- The type `MobileSynapseClient` is defined as:
  ```typescript
  export type MobileSynapseClient = Pick<SynapseApiClient, "ai">;
  ```
- This narrows the client type to only expose the `ai` namespace.
- However, mobile feature adapters (e.g., `createNoteListApi` and `createNoteDetailApi` in `apps/mobile/src/features/notes/`) require the `notes` namespace from the API client.
- This creates a TypeScript type mismatch at the boundary interface if a developer tries to pass the client returned by `createMobileSynapseClient()` to the notes API adapters.
- Reviewing and hardening this boundary ensures type safety, keeps the mobile app dependency-free and credentials-free, and prevents the leakage of any production provider assumptions into the mobile codebase.

---

## 2. Current Boundary Summary

The following files constitute the current boundary:

- **`apps/mobile/src/api/synapseClient.ts`**:
  Defines `MobileSynapseClient` using `Pick<SynapseApiClient, "ai">`, and `createMobileSynapseClient` returning that narrow type.
- **`apps/mobile/src/features/notes/noteListApi.ts`**:
  Declares `NoteListApiClient` expecting `readonly notes: Pick<NotesApi, "list">`.
- **`apps/mobile/src/features/notes/noteDetailApi.ts`**:
  Declares `NoteDetailApiClient` expecting `readonly notes: Pick<NotesApi, "get">`.
- **`apps/mobile/src/features/notes/summaryHistoryApi.ts`**:
  Declares `SummaryHistoryApiClient` expecting `readonly ai: Pick<AiApi, "listNoteSummaries" | "summarizeNote">`.
- **`packages/api-client/src/index.ts`**:
  Exposes the full `SynapseApiClient` type containing both `notes` and `ai` namespaces.
- **`apps/mobile/src/index.ts`**:
  Exports all of the above so that the app shell or screens can consume them.

---

## 3. Decision Options for Codex

When executing this slice, Codex must choose the appropriate option:

### Option A — No Code Changes
* **When to use**: If the boundary is determined to be already safe and sufficient as designed (e.g. if the narrow scoping was a strict design decision and there is a different pattern planned for notes API integration on mobile).
* **Deliverable**: A docs-only review record documenting the rationale.

### Option B — Test-Only Hardening
* **When to use**: If the boundary is determined to be safe but currently lacks test coverage verifying that configuration overrides (e.g. `baseUrl`, custom `fetch`, and `getAuthToken`) are correctly forwarded.
* **Deliverable**: Add `apps/mobile/src/api/synapseClient.test.ts` with focused unit tests.

### Option C — Small Boundary Hardening (Recommended)
* **When to use**: To resolve the mismatch where `notes` CRUD is omitted from `MobileSynapseClient`.
* **Deliverable**:
  1. Modify `apps/mobile/src/api/synapseClient.ts` to include `"notes"` in the picked properties:
     ```typescript
     export type MobileSynapseClient = Pick<SynapseApiClient, "ai" | "notes">;
     ```
  2. Create `apps/mobile/src/api/synapseClient.test.ts` to test client construction, base URL defaults, custom fetch propagation, and auth token propagation.
  3. Ensure no lockfiles, package manifests, or external dependencies are touched.

---

## 4. Decision Rules

Codex must adhere to the following rules when executing this slice:
- **Prefer Option C** (or Option B if Option C is deemed out of scope or blocked).
- **Keep everything plain TypeScript**: No React/JSX/TSX, no Expo CLI, and no React Native components or native files.
- **No package manifest / lockfile edits**: Do not add, remove, or modify any dependencies.
- **No credentials or `.env`**: Never add or read local environment credentials or mock API keys.
- **No external network calls**: Ensure all tests run with mock `fetch` implementations.
- **No raw fetch in feature modules**: Feature modules must continue to use the injected API client interfaces.
- **No live provider assumptions**: Do not leak OpenAI, Supabase, Docker, or live provider configurations into mobile code.

---

## 5. Expected Files for Codex

Depending on the chosen option, Codex may edit or create:
- `apps/mobile/src/api/synapseClient.ts` (Option C)
- `apps/mobile/src/api/synapseClient.test.ts` (Option B / Option C)
- `docs/codex-handoff-notes.md` (Update checkpoint/completed tasks)
- `docs/next-action.md` (Update next action)
- `docs/ai-summarization-implementation-plan.md` (Update history matrix)

---

## 6. Test Plan for Codex

To verify the changes, Codex must run the following validation pipeline:

```bash
# 1. Mobile Lint Check
pnpm --filter @synapse/mobile lint

# 2. Mobile TypeScript Type Check
cd apps/mobile && npx tsc --noEmit && cd ../..

# 3. Mobile Unit Tests (using Workspace Vitest)
pnpm --filter @synapse/api-client exec vitest run --globals --root ../.. apps/mobile/src/**/*.test.ts

# 4. Root Verification Baseline
pnpm lint
pnpm typecheck
pnpm test
pnpm build

# 5. Secrets Scan
gitleaks detect --source=. --redact
```

---

## 7. Security Checklist

Verify that the changes:
- [ ] Do not include any `.env` files or hardcoded credentials.
- [ ] Do not add any live OpenAI API calls or live OpenAI SDK dependencies.
- [ ] Do not use real-looking token or API key examples in code/tests.
- [ ] Do not modify `.gitleaksignore`.
- [ ] Contain no SQL or DB schema migrations.

---

## 8. Stop Conditions for Codex

Codex must **stop immediately and report** if:
1. The working tree is dirty before beginning the slice.
2. The CI is not green on the current commit.
3. Package manifests (`package.json`) or lockfiles need to be modified.
4. An external service call or integration (OpenAI, Supabase, Docker) is required.
5. Rendered UI files, JSX, TSX, Expo, or React Native components are needed.

---

## 9. Exact Codex Prompt

When the coding session begins, copy and paste the following prompt:

```markdown
Please implement Slice 8Q-B — Review mobile API client construction boundary.

1. Read apps/mobile/src/api/synapseClient.ts and verify how MobileSynapseClient is defined.
2. Note that MobileSynapseClient currently omits "notes", which is required by noteListApi and noteDetailApi.
3. Update apps/mobile/src/api/synapseClient.ts so that MobileSynapseClient includes both "ai" and "notes" namespaces:
   export type MobileSynapseClient = Pick<SynapseApiClient, "ai" | "notes">;
4. Create apps/mobile/src/api/synapseClient.test.ts testing:
   - Client construction with default base URL.
   - Client construction with custom baseUrl.
   - Injected config (fetch and getAuthToken) propagation.
5. Do not modify package.json or pnpm-lock.yaml. Keep mobile dependency-free.
6. Verify changes using:
   - pnpm --filter @synapse/mobile lint
   - cd apps/mobile && npx tsc --noEmit
   - pnpm --filter @synapse/api-client exec vitest run --globals --root ../.. apps/mobile/src/**/*.test.ts
   - pnpm test
   - gitleaks detect --source=. --redact
7. Update docs/next-action.md and docs/ai-summarization-implementation-plan.md to reflect Slice 8Q-B as complete.
8. Follow all stop conditions in docs/mobile-api-client-boundary-implementation-packet.md.
```

---

## 10. Post-Implementation Notes to Write After Codex Finishes

Once Codex completes the work, it must document:
- The selected option (Option C is expected).
- The exact files modified or created.
- The outcome of the test run, including any console warnings.
- Any type-safety gaps or boundary limitations discovered.
- Any unexpected blockers encountered.
- Recommendation on whether the `toErrorRecord` cleanup (Slice 8Q-C) is next or deferred.
