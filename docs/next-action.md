# Next Action

## Objective

Slice 8Q-B is complete: mobile tests now run through `pnpm --filter mobile test`,
and `MobileSynapseClient` now exposes both `ai` and `notes`.

Recommended next task: **Slice 8Q-C** — refactor the duplicated mobile
`toErrorRecord` helper. Do not proceed automatically.

## Slice 8Q-B Result

Slice 8Q-B fixed the mobile API client boundary and made mobile tests part of
the normal workspace test flow without adding dependencies or touching the
lockfile.

- `apps/mobile/src/api/synapseClient.ts` now uses
  `Pick<SynapseApiClient, "ai" | "notes">`.
- `apps/mobile/package.json` now runs mobile tests with existing workspace
  Vitest tooling: `pnpm --filter mobile test`.
- Mobile tests intentionally keep `testGlobals.ts` and Vitest `--globals` as a
  no-new-dependency compromise.
- Direct imports from `vitest` are deferred until mobile owns, or is explicitly
  approved for, a Vitest dependency.
- `apps/mobile/src/api/synapseClient.test.ts` proves one
  `createMobileSynapseClient()` composes with note list, note detail, and
  summary history adapters using fake fetch responses only.

## Slice 8Q-C Candidate

Refactor the duplicated `toErrorRecord` helper from `noteListViewState.ts`,
`noteDetailViewState.ts`, and `summaryHistoryViewState.ts` into a shared mobile
utility. Keep behavior unchanged and preserve UI-safe error messages.

## Gates

- Do not add dependencies or edit lockfiles.
- Do not initialize Expo, React Native, JSX/TSX, or rendered UI.
- Do not add OpenAI SDK, credentials, `.env`, SQL, migrations, Supabase state,
  Docker/RLS/live-provider work, or `.gitleaksignore` changes.
- Keep fake-provider-only demo constraints unchanged.
