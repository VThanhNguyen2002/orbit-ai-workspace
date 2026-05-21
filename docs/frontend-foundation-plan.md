# Frontend Foundation Plan

## Purpose

This plan prepares the future Web + Mobile foundation without initializing Expo
or adding product UI. It records how `apps/mobile` should eventually become the
single React Native app for mobile and web while preserving current package
boundaries and VMware-friendly development.

## Direction

Synapse will use Expo with React Native Web from one `apps/mobile` application.
Expo Router will provide shared file-based routing across web, iOS, and Android
when initialization begins. The first initialized app should stay small: route
shell, theme/tokens wiring, health/version client smoke check, and placeholder
screens only after the foundation is ready.

React Native Web remains the web strategy. Shared UI should prefer React Native
primitives (`View`, `Text`, `Pressable`, text inputs, lists) so components can
run on native and web. Platform-specific files such as `.web.tsx` or
`.native.tsx` are allowed only where a real platform capability differs.

## Shared Package Usage

- `@synapse/shared`: source of truth for wire contracts, entity types, sync DTOs,
  error envelopes, and pure utilities. It must stay platform-agnostic.
- `@synapse/api-client`: fetch-based API access, error handling, and future
  endpoint methods. It owns no auth storage and imports no UI.
- `@synapse/ui`: future cross-platform primitives, tokens, layouts, and
  presentational components. It should accept data via props and never fetch.
- `@synapse/config`: shared constants and environment schema only.
- `apps/mobile`: runtime composition layer for Expo, navigation, auth session
  wiring, local persistence adapters, sync orchestration, and device APIs.

## Runtime Boundaries

- Packages never import from `apps/*`.
- `@synapse/shared` stays free of React, React Native, Expo, DOM, Node-only APIs,
  and side effects.
- `@synapse/ui` stays rendering-only and does not import `@synapse/api-client`.
- `@synapse/api-client` stays fetch/SSE-only and does not import UI or storage.
- Local persistence, secure storage, connectivity detection, and platform APIs
  live in `apps/mobile` behind app-level adapters.

## Lightweight VMware-Friendly Approach

The first frontend pass should not require Android Studio, Xcode, emulators, or
native builds. Prefer:

- Expo web dev server for local browser checks.
- Expo Go on a physical device later, only when device behavior needs checking.
- No native module adoption until the feature that needs it is planned.
- Placeholder mobile scripts until Expo is intentionally initialized.
- Small dependency additions with web compatibility checked before adoption.

## Future Initialization Plan

1. Confirm the exact Expo SDK and React Native Web versions.
2. Initialize Expo inside `apps/mobile` without replacing workspace package
   dependencies.
3. Add TypeScript, Expo Router, and web entry support.
4. Wire path aliases and workspace package imports.
5. Add minimal route shell only: root layout and empty placeholder routes.
6. Add environment config using placeholder values only.
7. Add smoke tests for route rendering and API client health/version parsing.
8. Keep CI green with lint, typecheck, test, and build placeholders replaced only
   when the app can run them reliably.

## Offline-First Constraints

The UI must eventually render from local persistence first. Network state should
affect sync progress, not whether basic reads and writes feel usable. Future
state and persistence planning should account for:

- optimistic writes before network confirmation
- sync queue durability
- conflict records and version-based resolution
- local reads under startup and offline budgets
- no voice/audio binaries in the primary local database

## Testing Strategy

- Unit/package tests for pure helpers, API client parsing, and future UI
  primitives.
- App tests for route shell rendering, accessibility labels, loading/error
  states, and adapter behavior with mocked runtime dependencies.
- Offline/sync tests with mocked API and deterministic clocks before CRUD ships.
- Web smoke checks first; native smoke checks later through Expo Go or EAS when
  native behavior is required.
- No real network, real auth provider, real Supabase, or AI provider calls in
  frontend tests.

## Performance And Accessibility Guardrails

- Keep warm local startup under the documented 500ms target once local data
  exists.
- Avoid importing heavy native, AI, vector, or persistence libraries into the
  initial bundle before feature code needs them.
- Lazy-load heavy feature screens after the app shell exists.
- Design UI primitives with accessibility labels, disabled/loading states, and
  keyboard/web focus behavior from the start.
- Keep Lighthouse web performance and accessibility budgets visible before
  production UI work begins.

## Non-Goals

- No Expo initialization in this slice.
- No CRUD, sync, auth, Supabase, AI provider, or voice memo implementation.
- No production UI screens or navigation tree.
- No Android Studio, emulator, native build, or EAS setup requirement.
- No secrets, real environment values, or provider keys.

## Definition Of Done

- Frontend direction and runtime boundaries are documented.
- `apps/mobile` remains a placeholder and clearly says Expo is not initialized.
- Future initialization steps are small enough for a VMware/local workflow.
- Testing, performance, accessibility, and offline-first expectations are noted.
- Next recommended work points to Slice 6 planning, not implementation.
