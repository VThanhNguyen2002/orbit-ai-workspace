# Synapse Mobile

Frontend application placeholder for future Expo + React Native Web work.

Expo is intentionally not initialized yet. This package currently exists to hold
workspace dependencies, scripts, and planning docs while backend and shared
contract foundations are completed.

## Expected Direction

- One Expo app in `apps/mobile` will eventually target web, iOS, and Android.
- React Native Web is the planned browser runtime.
- Expo Router is the planned routing layer once initialization starts.
- `@synapse/shared` provides contracts and pure types.
- `@synapse/api-client` provides typed API access.
- `@synapse/ui` will provide cross-platform primitives and tokens.

## Local Constraints

The early frontend foundation should stay VMware-friendly:

- no Android Studio requirement yet
- no emulator requirement yet
- no native builds or EAS setup yet
- no real secrets or production environment values
- no Expo-native modules until a planned feature needs them

Use the root docs, especially `docs/frontend-foundation-plan.md`, as the source
of truth before initializing Expo.
