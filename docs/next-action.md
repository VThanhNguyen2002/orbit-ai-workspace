# Next Action

## Objective

Slice 8Q-C is complete: the duplicated mobile `toErrorRecord` helper has been
extracted into one dependency-free helper used by all three note view-state
modules.

Recommended next task: **Slice 8R — Choose next product/value slice**. Do not
proceed automatically.

## Slice 8Q-C Result

Slice 8Q-C refactored the duplicated helper without changing behavior:

- Added `apps/mobile/src/features/notes/viewStateError.ts`.
- Updated note list, note detail, and summary history view-state modules to
  import `toErrorRecord`.
- Preserved existing error reason mapping, UI-safe messages, and state shapes.
- Left mobile test infra unchanged: `testGlobals.ts` and Vitest `--globals`
  remain the no-new-dependency compromise from Slice 8Q-B.

## Slice 8R Candidate

Choose the next high-value project increment. Keep the current gates unless a
future slice explicitly changes them:

- no dependency or lockfile changes
- no credentials, `.env`, OpenAI SDK, live provider, Supabase, Docker/RLS, SQL,
  or migrations
- no Expo/React Native, JSX/TSX, or rendered UI
- no `.gitleaksignore` broadening
- fake-provider-only demo constraints remain unchanged
