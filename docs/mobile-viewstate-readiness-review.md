# Mobile View-State Readiness Review

Slice: **8L**
Date: 2026-06-07
Status: **COMPLETE — READY**

---

## 1. Objective

Review the dependency-free mobile note list, note detail, and summary history
view-state foundations together, confirm their API consumption story is
screen-ready, and keep rendered mobile UI work deferred unless the missing
approval gates are explicitly satisfied.

This is a read-only review. No runtime code, tests, package manifests,
lockfiles, dependencies, Expo/React Native runtime, rendered UI, OpenAI SDK,
credentials, `.env` files, SQL, migrations, Supabase state, or Docker work
was added.

---

## 2. Preflight

| Check | Result |
|---|---|
| Expected HEAD commit `1f37332` | ✅ CONFIRMED |
| CI run 27085840282 | ✅ CONFIRMED completed success |
| Working tree clean | ✅ CONFIRMED |

---

## 3. Files Reviewed

- `apps/mobile/src/index.ts`
- `apps/mobile/tsconfig.json`
- `apps/mobile/src/features/notes/noteListApi.ts`
- `apps/mobile/src/features/notes/noteDetailApi.ts`
- `apps/mobile/src/features/notes/noteListViewState.ts`
- `apps/mobile/src/features/notes/noteDetailViewState.ts`
- `apps/mobile/src/features/notes/noteListPlaceholder.ts`
- `apps/mobile/src/features/notes/noteDetailPlaceholder.ts`
- `apps/mobile/src/features/notes/summaryHistoryApi.ts`
- `apps/mobile/src/features/notes/summaryHistoryViewState.ts`
- `apps/mobile/src/features/notes/noteSummaryHistoryPlaceholder.ts`
- `packages/api-client/src/index.ts`
- `packages/api-client/src/notes.test.ts`
- `packages/api-client/src/ai.test.ts`
- `docs/api-demo-walkthrough.md`
- `docs/backend-product-demo-polish-record.md`
- `docs/rendered-mobile-demo-unblock-decision-packet.md`
- `docs/ai-summarization-implementation-plan.md`
- `docs/security/privacy-and-data-handling.md`
- `docs/next-action.md`

---

## 4. Readiness Verdict

**READY as a portfolio/product architecture layer.**

The three view-state modules are coherent, safe, and screen-ready: a future
rendered screen can consume their output types without any structural rework.
TypeScript-only verification is sufficient for the current deferred-UI posture.

---

## 5. Coherence Findings

### Module pattern

All three modules follow an identical structural template:

| Step | Factory/Function |
|---|---|
| Idle shell | `createIdle*ViewState()` |
| Loading shell | `createLoading*ViewState()` |
| Data → success/empty | `map*DataToViewState(data)` |
| Error dispatch | `map*ErrorToViewState(error)` |
| Async orchestrator | `load*ViewState(api, ...)` |
| Private error helper | `createError*ViewState(...)` |

Summary history adds `createSummarizingViewState`, `appendSummaryHistoryItemToViewState`,
`summarizeNoteAndMapSummaryHistoryViewState`, `mergeSummaryHistoryItems`, and
`sortSummariesNewestFirst` — all justified by the write-path mutate-and-append
semantic and consistent with the template.

### State field consistency

| Field | NoteList | NoteDetail | SummaryHistory |
|---|---|---|---|
| `status` | ✅ | ✅ | ✅ |
| `message` | ✅ | ✅ | ✅ |
| `isLoading` | ✅ | ✅ | ✅ |
| `canRetry` | ✅ | ✅ | ✅ |
| `errorReason` | ✅ | ✅ | ✅ |
| `noteId` | — (not applicable) | ✅ | ✅ |
| `items` | ✅ | — (single note) | ✅ |
| `isSummarizing` | — | — | ✅ (justified) |
| `memoryNotice` | — | — | ✅ (justified) |

Asymmetries are intentional, not inconsistent.

### Adapter boundaries

All three adapters use `Pick<>` narrowing against `NotesApi` or `AiApi`:

- `NoteListApiClient` = `{ notes: Pick<NotesApi, "list"> }`
- `NoteDetailApiClient` = `{ notes: Pick<NotesApi, "get"> }`
- `SummaryHistoryApiClient` = `{ ai: Pick<AiApi, "listNoteSummaries" | "summarizeNote"> }`

No `SynapseApiClient` import, no `fetch` import, no URL construction in any
mobile feature module. Adapter boundaries are injection-pure.

### Schema validation placement

All Zod validation (`ListNotesDataSchema.parse`, `NoteSchema.parse`,
`ListSummariesDataSchema.parse`, `SummarySchema.parse`) sits at the adapter
layer. View-state mappers receive already-typed domain data and have no
awareness of wire shape. **Correct placement.**

### Naming

`NoteList*`, `NoteDetail*`, `SummaryHistory*` prefixes are consistent. Status
unions are consistent: `"idle" | "loading" | "success" | "empty" | "error"`
(plus `"summarizing"` for summary history). All factory/mapper functions are
exported; private helpers are not.

---

## 6. Product and Demo Value

**Real value despite no rendered UI.** The foundation demonstrates:

1. Dependency injection at the API client layer via structural `Pick<>` types.
2. Clean adapter boundary separating network concerns from view-state concerns.
3. Schema validation at the adapter, preventing malformed wire data from entering the view layer.
4. Exhaustive state machines covering the full screen lifecycle.
5. Ordering and deduplication in the summary history module (newest-first sort, id-deduped merge).
6. Safety-first error mapping — coarse user-safe messages, no raw error propagation.
7. Placeholder metadata — future screen regions and non-goals documented as typed constants.

**Honest CV/portfolio claim:** "mobile-side architecture foundation in plain
TypeScript, dependency-injected, screen-ready, validated against shared
contracts." The claim avoids overclaiming Expo or React Native rendering.

**Overclaiming check:**

- Placeholder `NON_GOALS` arrays include `"No rendered mobile UI while Expo initialization is deferred."`
- `apps/mobile/tsconfig.json` includes only `"src/**/*.ts"` — physically prevents accidental `.tsx` addition.
- `docs/rendered-mobile-demo-unblock-decision-packet.md` gates rendered UI on 12 missing approvals.

---

## 7. Safety Findings

### Error state leakage

All `map*ErrorToViewState` functions branch on `error.name`, `error.status`,
and `error.code` from API client error types, then return only typed constant
strings. Raw error objects, Zod parse details, auth headers, provider keys, and
token-like strings are never reachable from view-state.

Error messages in use:

| Message | Context |
|---|---|
| `"Notes are unavailable right now."` | NoteList unavailable |
| `"Notes could not be displayed because the response was not recognized."` | NoteList invalid response |
| `"Note detail is unavailable right now."` | NoteDetail unavailable |
| `"We could not find that note."` | NoteDetail / SummaryHistory not found |
| `"Note detail could not be displayed because the response was not recognized."` | NoteDetail invalid response |
| `"Summary history could not be displayed because the response was not recognized."` | SummaryHistory invalid response |
| `"Summary history is unavailable right now."` | SummaryHistory unavailable |

All safe. No backend diagnostics, stack traces, or credential values reachable.

### Note content in success states

`NoteDetailViewState.note.content` carries authorized note content by design.
Note detail display is the purpose of the CRUD surface; this is consistent with
`docs/security/privacy-and-data-handling.md`. `NoteListViewState` carries only
a `contentPreview` (truncated to 160 chars), appropriate for a list row.

### AI summary content

`SummaryHistoryListItem` exposes only `id`, `content`, `createdAt`,
`actionItems`. Provider fields (`provider`, `model`) are intentionally omitted
from the view-state mapper. AI-generated summary content is exposed; raw note
content, prompt text, and provider diagnostics are not.

### Memory-only notice

`SUMMARY_HISTORY_MEMORY_NOTICE` is included in every `SummaryHistoryViewState`
return value — idle, loading, summarizing, success, empty, and error. A future
screen cannot accidentally omit it. `noteSummaryHistoryPlaceholder.ts` also
surfaces `memoryNotice` as a top-level field on the placeholder object.

### Credentials and tokens

No real-looking JWT, API key, or `sk-` prefix strings found in any reviewed
file. The `"tok_ai_test"` string in `ai.test.ts` is a mock auth token for a
test fixture verifying header inclusion — not a real credential.

---

## 8. Gaps and Risks

| Item | Severity | Action |
|---|---|---|
| `toErrorRecord` duplicated 3× (4-line helper) | Low | Defer — consolidate when a fourth view-state module forces the issue |
| No mobile-specific async tests for `load*ViewState` orchestrators | Low | Acceptable — API-client tests cover adapter layer; pure TS view-state logic verified by typecheck |
| `api-demo-walkthrough.md` §9 lists note list/detail exports but not summary history exports | Low | Minor doc gap, not a correctness issue |
| `apps/mobile/src/api/synapseClient.ts` not reviewed in this slice | Note | Defer — review when client construction boundary becomes relevant |
| Placeholder `dev`/`build` scripts in `apps/mobile/package.json` | Low | Intentional — communicate deferred status clearly |

No high-severity gap found.

---

## 9. Option Comparison

### Option A — Docs-only walkthrough/readiness record (this slice)

| Dimension | Assessment |
|---|---|
| Value | High — formalizes review, adds to portfolio doc layer |
| Effort | Low |
| Risk | Zero |
| Dependency impact | Zero |
| Demo/CV value | Medium-High |
| Recommended agent | Documentation agent |
| Do now or defer? | **Done in this slice** |

### Option B — TypeScript refactor to consolidate `toErrorRecord`

| Dimension | Assessment |
|---|---|
| Value | Low — 4-line helper, 3 copies |
| Effort | Low — but requires code change and CI pass |
| Risk | Low-Medium |
| Dependency impact | Zero |
| Demo/CV value | Very low — invisible to reviewer |
| Recommended agent | TypeScript agent |
| Do now or defer? | **Defer** — do when a fourth module forces it |

### Option C — README / CV / demo narrative polish

| Dimension | Assessment |
|---|---|
| Value | High — direct recruiter/portfolio impact |
| Effort | Low-Medium — docs only |
| Risk | Zero |
| Dependency impact | Zero |
| Demo/CV value | High — top-level README is first thing any reviewer sees |
| Recommended agent | Documentation agent |
| Do now or defer? | **Recommended next — Slice 8M** |

### Option D — Reopen Expo/React Native approval path

| Dimension | Assessment |
|---|---|
| Value | High if all gates satisfied; Zero if they aren't |
| Effort | High — 12 gates still missing |
| Risk | Medium-High |
| Dependency impact | High — package.json + lockfile edits required |
| Demo/CV value | High if rendered UI exists; Zero if only approval process |
| Recommended agent | Mobile/Frontend developer agent (post-approval) |
| Do now or defer? | **Do NOT reopen now** — 12/12 gates missing |

---

## 10. Recommended Next Slice

**Slice 8M — README / CV / demo narrative polish.**

The mobile foundation is complete. The API demo is complete. The next
highest-leverage work is top-of-repo narrative polish: a recruiter-facing
`README.md`, a CV-aligned project description, and/or a one-page portfolio
summary. Dependency-free, no code, no lockfile changes.

Do not proceed to Option B (refactor) or Option D (Expo/RN) automatically.

---

## 11. Explicit Non-Changes

- No runtime code, tests, or package configuration was changed.
- No package manifests, lockfiles, or dependencies were modified.
- No Expo, React Native runtime, rendered mobile UI, router, or native files.
- No OpenAI SDK, live provider, provider credential, `.env`, WIF runtime, SSE
  streaming, SQL, migration, Supabase state, Docker, or generated state.
- No durable summary persistence; summary history remains memory-only for
  fake-provider demos and resets with the backend process.
- Fake-provider-only demo constraints remain unchanged.
- Security/privacy constraints remain unchanged.
- `.gitleaksignore` remains exact-fingerprint only.
- Expo/React Native initialization remains BLOCKED/DEFERRED pending 12 missing
  approval gates.

---

## 12. Verification

```bash
pnpm install --frozen-lockfile

cd apps/api
python3 -m ruff check .
python3 -m pytest
cd ../..

pnpm --filter @synapse/api-client test
pnpm --filter @synapse/shared contracts:check
pnpm --filter mobile lint
pnpm --filter mobile exec tsc --noEmit -p tsconfig.json

pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Security posture check:

```bash
gitleaks detect --source=. --redact
git ls-files -- ".env" ".env.*" "*.sql" "supabase/migrations/*"
```

Expected posture:

- no `.env` files
- no OpenAI SDK dependency
- no provider credentials
- no SQL or migrations
- no Supabase generated state
- no live provider runtime changes
- no rendered mobile UI or package changes
- no real credential examples
- `.gitleaksignore` remains exact-fingerprint only
