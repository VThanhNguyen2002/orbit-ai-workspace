# Codex Handoff Notes — Slice 8Q-C

_Generated: 2026-06-08. Do NOT proceed to coding automatically._

---

## 1. Current Project Checkpoint

| Field | Value |
|---|---|
| Base commit before Slice 8Q-C | `cbbe07d` — previous green `origin/main` |
| Latest green CI run before Slice 8Q-C | `27111243926` — completed success |
| Pre-slice worktree state | Clean (verified: `git status --short` empty before local edits) |
| Gitleaks result | No leaks found |

### Completed Slices (8A-R through 8Q-C)

| Slice | Summary |
|---|---|
| 8A | Backend summary history (memory-only, newest-first, fake provider) |
| 8B | Summary history API client method + tests |
| 8C | Summary history UI/API consumption plan (docs-only) |
| 8D-A | Inspect/init minimal mobile screen structure |
| 8D-B | Dependency-free mobile summary history adapter + view-state |
| 8D-C | Minimal screen/component decision |
| 8D-D | Expo/React Native initialization approval plan |
| 8D-E | Expo initialization decision — DEFERRED |
| 8E | Backend/product demo polish (newest-first backend history, dependency-free generate state) |
| 8F | Dependency-free API-level demo runbook |
| 8G | Rendered mobile demo unblock decision packet — DEFERRED (10/12 gates missing) |
| 8H | Note CRUD / summary demo API walkthrough hardening (docs-only) |
| 8I | Dependency-free API demo evidence hardening / API client gap review (docs-only) |
| 8K | Dependency-free mobile note list/detail view-state foundations |
| 8L | Mobile note + summary view-state walkthrough/readiness review — READY verdict |
| 8M | README / CV / demo narrative polish — accurate capability table, explicit deferrals |
| 8N-B | Dependency-free mobile view-state unit tests (Vitest) |
| 8O | Dependency-free local API demo script (`scripts/demo-api.sh`) |
| 8P | Demo script validation / README walkthrough alignment — all docs aligned |
| 8Q-A | Codex handoff notes — handoff notes documented |
| 8Q-B-SPEC | Mobile API client boundary implementation packet for Codex (docs-only) |
| 8Q-B | Mobile test script + API client boundary hardening |
| 8Q-C | Deduplicated mobile view-state error helper |

### Current Product/Demo Capabilities

- **FastAPI backend** with Notes CRUD and fake-provider AI summarization running locally.
- **API demo script** (`scripts/demo-api.sh`): bash/curl/python3 only; refuses non-local URLs;
  exercises health check, note CRUD, two fake summaries, newest-first verification.
- **Summary history** returned newest-first from memory store via `GET /v1/ai/notes/{id}/summaries`.
- **API client** (`packages/api-client`): Notes CRUD + `client.ai.summarizeNote()` + `client.ai.listNoteSummaries()`.
- **Shared Zod contracts** (`packages/shared`): Notes, AI summarization wire contracts, summary schema, history envelope, schema registry.
- **Mobile TypeScript** (`apps/mobile/src`): dependency-free note list/detail/summary view-state, injected API adapter, no Expo runtime.
- **Mobile tests**: Vitest unit coverage for note list, note detail, summary history adapter/orchestrator, and mobile client composition.
- **README**: accurate capability table, explicit deferrals table, architecture overview, quality gates, security stance.

---

## 2. What Is Implemented

### FastAPI Backend Notes CRUD

- `apps/api/app/routers/notes.py` — `GET/POST /v1/notes`, `GET/PUT/DELETE /v1/notes/{id}`.
- Memory-only `NotesRepository`; no database, no SQL, no Supabase.
- Auth-context injection present; RS256 JWT verifier implemented but JWKS not live-wired.
- Ruff lint + pytest CI-green.

### Fake-Provider AI Summarization

- `POST /v1/ai/notes/{note_id}/summarize` — fake provider returns deterministic canned output.
- `apps/api/app/services/fake_provider.py` — no network calls, no SDK, no credentials.
- Provider selection config-driven; `ai_provider="fake"` is the only active path.
- Full prompt builder (`ai_prompting.py`) and redaction helper in place; no content logged.

### Summary History Newest-First

- `GET /v1/ai/notes/{note_id}/summaries` — returns owned summaries newest-first.
- In-memory store only; resets on server restart; no persistence, no SQL.

### API Client Integration

- `packages/api-client/src/` — Notes CRUD methods + AI namespace (`summarizeNote`, `listNoteSummaries`).
- Shared `SynapseApiClient` type; injected `fetch` + `getAuthToken` for testability.

### Shared Zod Contracts / Schema Registry

- `packages/shared/src/ai/index.ts` — `SummarizeRequestSchema`, `SummarizeResponseSchema`, SSE event schemas, `ListSummariesResponse`.
- `packages/shared/src/domain/index.ts` — `SummarySchema`, `SummaryActionItemSchema`, `SummarySourceTypeSchema`.
- `packages/shared/src/notes/index.ts` — Note contracts.
- Schema registry (`schemaRegistry`) covers all registered contracts.

### Mobile Dependency-Free Note/Summary View-State

- `apps/mobile/src/features/notes/noteListViewState.ts` — idle/loading/success/error/empty states.
- `apps/mobile/src/features/notes/noteDetailViewState.ts` — single note states.
- `apps/mobile/src/features/notes/summaryHistoryViewState.ts` — summary history adapter + orchestrator.
- `apps/mobile/src/features/notes/viewStateError.ts` — shared dependency-free error record helper used by all three view-state modules.
- `apps/mobile/src/api/synapseClient.ts` — `createMobileSynapseClient()` wraps `createApiClient`; `Pick<SynapseApiClient, "ai" | "notes">` boundary; injectable config.
- No Expo, no JSX, no TSX, no React Native runtime.

### Mobile View-State Tests

- `apps/mobile/src/features/notes/*.test.ts` — Vitest unit tests for all three view-state modules and note API adapters.
- `apps/mobile/src/api/synapseClient.test.ts` — fake-fetch composition test for `createMobileSynapseClient()`, note list/detail adapters, and summary history adapter.
- All mobile tests run via `pnpm --filter mobile test`, which invokes the existing workspace Vitest install with `--globals`.
- Vitest globals are an intentional no-new-dependency compromise. Direct `vitest` imports are deferred until mobile owns, or is explicitly approved for, a Vitest dependency.

### API Demo Script

- `scripts/demo-api.sh` — bash/curl/python3 only; health, CRUD, two fake summaries, newest-first verification.
- Refuses non-local `SYNAPSE_DEMO_API_BASE_URL` at runtime.
- `bash -n scripts/demo-api.sh` syntax check passes.

### README / Demo Walkthrough Alignment

- `README.md` — accurate; two-terminal startup, demo script invocation, no overclaims.
- `docs/api-demo-walkthrough.md` — all 9 steps aligned with script, URL override documented.
- No claim of OpenAI, Supabase, Docker, persisted storage, rendered mobile, or deployed app.

---

## 3. What Is Explicitly Blocked

| Blocked Item | Reason |
|---|---|
| Live OpenAI provider | 0/8 named approvals; all gates MISSING |
| OpenAI SDK install | NOT APPROVED / DENIED; all 12 gates MISSING |
| Real credentials / `.env` | Never committed; not approved |
| WIF runtime | Not approved; docs-only planning only |
| Supabase / Docker / RLS | Out of scope; paused |
| SQL / migrations | Out of scope |
| Expo / React Native initialization | DEFERRED; 10/12 approval gates missing |
| Rendered mobile UI | Blocked until Expo init approved |
| Package / lockfile edits | Not approved unless explicitly requested per-slice |
| External network calls in CI | Not approved |
| Production persistence | Not in scope |
| `.gitleaksignore` broadening | Never approved; exact fingerprint-only posture maintained |
| Real-looking token/JWT/API-key examples | Never added to docs or code |

---

## 4. Verification Baseline

Run these commands locally before and after any coding slice to confirm green state.

```bash
# 1. Install (frozen)
pnpm install --frozen-lockfile

# 2. API lint
pnpm --filter @synapse/api lint        # ruff check

# 3. API tests
pnpm --filter @synapse/api test        # pytest

# 4. API client tests
pnpm --filter @synapse/api-client test

# 5. Shared contracts check
pnpm --filter @synapse/shared test     # or: pnpm contracts:check

# 6. Mobile lint
pnpm --filter mobile lint

# 7. Mobile direct tsc (dependency-free TypeScript typecheck)
pnpm --filter mobile exec tsc --noEmit -p tsconfig.json

# 8. Mobile tests
pnpm --filter mobile test

# 9. Root lint / typecheck / test / build
pnpm lint
pnpm typecheck
pnpm test
pnpm build

# 10. Secret scan
gitleaks detect --source=. --redact

# 11. Demo script syntax check
bash -n scripts/demo-api.sh
```

> Note: Node.js 20 deprecation annotation appears in GitHub Actions output but does NOT fail CI.
> This is a known residual annotation; CI is green.

---

## 5. Agent Rules

| Rule | Detail |
|---|---|
| **AG** handles | Docs / planning / report slices (e.g., this handoff, decision packets, readiness reviews) |
| **Codex/C** handles | Coding / testing / refactor / security audit slices |
| **ChatGPT** | Remains review gate before next slice is approved — do not skip |
| **Worktree** | Must be clean before any slice starts |
| **No auto-proceed** | Never automatically begin the next slice; stop and report |
| **No force push** | `git push --force` is never permitted |
| **Package/dep changes** | Require explicit per-slice approval; never incidental |
| **Destructive git** | `git reset --hard`, `git clean -fd`, branch deletion — never without explicit approval |

---

## 6. Next Candidate Slice

### `Slice 8R: Choose Next Product/Value Slice`

**Value:** Pick the next high-signal project increment now that the mobile
view-state test and refactor cleanup path is complete.

**Risk:** Depends on selected scope. Keep the same dependency, credential,
provider, Supabase, Docker, and rendered-mobile gates unless explicitly changed.

---

## 7. Exact Next Recommended Task

**If coding quota is available:**

> **`Slice 8R — Choose next product/value slice`**
>
> Choose the next dependency-free backend, shared-contracts, API client, docs,
> or portfolio-value improvement. Do not assume approval for dependencies,
> lockfile changes, live providers, Supabase, Docker, Expo, or rendered UI.

If coding quota is unavailable, keep Slice 8R as a planning/product-choice
slice and choose a docs-only or review-only option there.

---

## 8. Stop Conditions for Codex

Codex **must stop immediately and report** before making any change if:

1. Working tree is dirty before slice start (unstaged or staged changes present).
2. CI is not green on latest `origin/main`.
3. Any package manifest (`package.json`, `pyproject.toml`, `requirements*.txt`) edit is needed.
4. Any lockfile (`pnpm-lock.yaml`, `poetry.lock`) edit is needed.
5. An external service call is required (OpenAI, Supabase, Docker, etc.).
6. A `.env` file or credential of any kind would be created or referenced.
7. Supabase, Docker, OpenAI SDK, or Expo initialization is needed.
8. Generated secrets, token-like strings, or API-key-like examples would be added to any file.
9. A SQL file or migration file would be created or modified.
10. A rendered mobile UI file (JSX, TSX, native component) would be created.

In all cases: **STOP, report the blocker, and await explicit approval.**

---

## 9. Residual Risks

| Risk | Severity | Owner |
|---|---|---|
| Direct `vitest` imports in mobile tests are deferred until mobile owns/receives an approved Vitest dependency | Low | Future package approval slice |
| Node.js 20 deprecation annotation in GitHub Actions | Low — CI green, cosmetic only | Future Node upgrade slice |
| Summary history is memory-only (resets on restart) | Known/accepted — demo-only scope | Future persistence slice |
| Expo / rendered mobile UI blocked | Accepted — 10/12 gates missing | Blocked pending approval |
| OpenAI SDK / live provider blocked | Accepted — NOT APPROVED / DENIED | Blocked pending all 8 named approvals |
