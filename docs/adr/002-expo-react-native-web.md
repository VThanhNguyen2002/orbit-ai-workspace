# ADR-002: Expo + React Native Web for Cross-Platform

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

Synapse must run on web, iOS, and Android. The project aims to maximize code sharing while maintaining native-quality UX on mobile and acceptable performance on web.

We need to choose between: separate apps per platform, React Native + separate web app, or a unified codebase approach.

## Decision

Use **Expo** (SDK 52+) with **React Native Web** to build a single codebase that renders natively on mobile and as a web app via React Native Web.

Use **Expo Router** for file-based routing (works on all platforms).

## Rationale

### Why Expo

- **Managed workflow** — no need for Xcode/Android Studio for development (critical for Ubuntu/VMware environment)
- **Expo Go** — test on physical devices without build toolchain
- **EAS Build** — cloud-based builds for iOS/Android when needed
- **expo-av** — audio recording API that works in Expo Go (no dev build required for voice memos)
- **Expo Router** — file-based routing that works on web and mobile, similar mental model to Next.js

### Why React Native Web over separate web app

- **Code sharing** — 80–90% of component code runs on all platforms
- **Single component library** — `@synapse/ui` works everywhere without platform-specific versions
- **Reduced maintenance** — one set of business logic, one routing structure
- **Portfolio demonstration** — cross-platform architecture is a key showcase item

### Why not Next.js + React Native (separate apps)

- Two separate routing systems
- Two separate component libraries (React DOM vs React Native)
- Shared logic works, but UI layer is duplicated
- More code to maintain for a solo developer

### Why not Flutter

- Dart ecosystem is smaller for AI/ML integrations
- Portfolio targets frontend engineering roles that expect React/TypeScript
- React Native Web produces standard DOM — better for SEO and accessibility tooling

## Consequences

### Positive
- Single `apps/mobile` directory serves web, iOS, and Android
- UI components use React Native primitives (`View`, `Text`, `Pressable`) which map to DOM elements on web
- Expo Router provides consistent navigation across platforms
- Hot reload works on all platforms

### Negative
- Some web-specific patterns are harder (no `div` semantics, limited CSS features)
- React Native Web adds bundle size (~40KB gzipped)
- Not all React Native libraries support web
- Web performance may lag behind a pure React app

### Mitigations
- Use `Platform.select()` for platform-specific code paths
- Create `.web.tsx` overrides for components that need web-specific rendering
- Monitor bundle size with analyzer, lazy load where possible
- Choose libraries with web support (check react-native-directory.com)

## Platform-Specific Files Convention

When a component needs different behavior per platform:

```
components/
  VoiceRecorder.tsx          # Shared logic
  VoiceRecorder.native.tsx   # Mobile-specific (expo-av)
  VoiceRecorder.web.tsx      # Web-specific (MediaRecorder API)
```

Metro/Webpack resolve the correct file automatically based on platform.

**Rule:** Platform-specific files should be < 10% of total component files. If more components need overrides, the abstraction is wrong.

## Routing

```
apps/mobile/app/
  _layout.tsx          # Root layout (tab navigator)
  (tabs)/
    index.tsx          # Notes list
    tasks.tsx          # Tasks list
    recordings.tsx     # Voice memos
    search.tsx         # Semantic search
  note/[id].tsx        # Note detail
  settings.tsx         # User settings
  login.tsx            # Auth screen
```

Expo Router handles deep linking on mobile and URL routing on web from the same file structure.

## Constraints

1. All UI components must use React Native primitives — no `<div>`, `<span>`, `<input>`
2. Styling via `StyleSheet.create()` or a compatible solution (no Tailwind, no CSS modules)
3. Libraries must be checked for web compatibility before adoption
4. Web-specific meta tags handled via `expo-router`'s `<Head>` component
