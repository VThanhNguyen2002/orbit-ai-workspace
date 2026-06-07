# Next Action

## Objective

Recommended next task: **Slice 8O — dependency-free demo script** or
**Slice 8O — CV / portfolio narrative doc**.

The README/demo narrative is accurate (Slice 8M complete), and mobile
view-state unit coverage is now in place (Slice 8N-B complete). See
[`docs/rendered-mobile-demo-unblock-decision-packet.md`](rendered-mobile-demo-unblock-decision-packet.md)
for the rendered mobile gate status. See
[`docs/api-demo-walkthrough.md`](api-demo-walkthrough.md) for the API-level demo
script and mobile view-state surface.

## Slice 8N-B Result

Slice 8N-B adds dependency-free unit tests for the existing mobile TypeScript
view-state modules and API adapters.

Changes:

- `apps/mobile/src/features/notes/noteListViewState.test.ts` — idle, loading,
  empty, success ordering, UI-safe errors, and injected load orchestration.
- `apps/mobile/src/features/notes/noteDetailViewState.test.ts` — idle,
  loading, success mapping, not-found/invalid/unavailable UI-safe errors, and
  injected load orchestration.
- `apps/mobile/src/features/notes/summaryHistoryViewState.test.ts` — loading,
  summarizing, empty, newest-first success, append/dedupe, UI-safe errors,
  memory-only notice, and injected list/summarize orchestration.
- `apps/mobile/src/features/notes/noteApiAdapters.test.ts` — injected API
  client method usage and shared schema validation.
- `apps/mobile/src/features/notes/testFixtures.ts` and `testGlobals.ts` —
  inert fixtures and a tiny Vitest-global bridge that avoids adding a mobile
  `vitest` dependency.
- `docs/ai-summarization-implementation-plan.md` — Slice 8N-B entry added.
- `docs/security/privacy-and-data-handling.md` — mobile test security boundary
  recorded.
- `docs/next-action.md` — updated to Slice 8N-B result and next candidates.

Coverage notes:

- Existing test infrastructure was sufficient without package or lockfile
  changes by running the package-owned Vitest binary with the repo root.
- Mobile tests do not import `vitest` directly, so mobile typecheck remains
  dependency-free.
- Root `pnpm test` still runs existing package scripts; the targeted mobile
  command is:

```sh
pnpm --filter @synapse/api-client exec vitest run --globals --root ../.. apps/mobile/src/features/notes/*.test.ts
```

## Slice 8O Candidates

### Option A — CV / portfolio narrative doc

Write a `docs/portfolio-summary.md` that frames the project for a job
application or CV, covering tech decisions, what was built vs. deferred, and
honest capability claims. Dependency-free, docs-only.

### Option B — API demo walkthrough CLI script

Write a shell script (`scripts/demo.sh`) that runs the Note CRUD + fake AI demo
sequence using `curl` against a locally running backend. No new dependencies.

Do not proceed to any Slice 8O option automatically.

## Slice 8O Gate

- Do not install dependencies, modify package manifests, or modify lockfiles.
- Do not initialize Expo, React Native runtime UI, routers, native files, JSX,
  or TSX.
- Do not introduce a live provider, OpenAI SDK, credentials, `.env`, WIF
  runtime, SSE streaming, SQL, migrations, Supabase state, Docker work, or
  generated state.
- If rendered mobile demo work is reconsidered, first satisfy the approval
  gates in `docs/rendered-mobile-demo-unblock-decision-packet.md`.

## Definition Of Done

- Mobile view-state tests remain dependency-free and deterministic.
- All targeted checks pass.
- No dependency, lockfile, rendered UI, live provider, credential, SQL,
  migration, Supabase, Docker, or production persistence change is made.
- Fake-provider-only demo constraints remain unchanged.
- Security/privacy constraints remain unchanged.
