# Performance Budget

## Goals

Synapse should feel fast locally, predictable over the network, and transparent when AI work takes time.

## Budgets

| Area | Budget | Notes |
|------|--------|-------|
| App startup with warm local data | < 500ms to first usable screen | No network required |
| Notes list local query | < 200ms for 100 notes | Render from local persistence |
| API CRUD p95 | < 500ms | Excludes AI endpoints |
| Sync push batch | < 1s for 100 operations | Server processing time |
| Sync pull | < 1s for 500 changed entities | Use `has_more` for larger deltas |
| Semantic search | < 500ms for 1,000 embeddings | Query embedding + pgvector search |
| AI first token | < 2s target, < 3s warning | Stream progress via SSE |
| Web Lighthouse performance | >= 90 Phase 1, >= 95 Phase 3 | Desktop and mobile profiles |
| Web accessibility | >= 90 Phase 1, >= 95 Phase 3 | Lighthouse plus manual checks |

## Bundle And Runtime Guardrails

- Do not initialize Expo-native modules until the mobile app actually needs them.
- Keep `@synapse/shared` free of React, React Native, Expo, DOM, and Node-only APIs.
- Avoid large AI or vector libraries in the client bundle.
- Lazy-load heavy screens and provider-specific UI.
- Keep voice/audio binaries out of local database storage.

## API Guardrails

- Paginate list endpoints.
- Cap sync pull responses at 500 entities with `has_more`.
- Rate-limit AI and sync endpoints separately from CRUD.
- Log slow DB queries over 500ms and investigate p95 regressions.
- Do not return full note/transcript content in search results unless the endpoint explicitly requires it.

## Measurement

| Metric | Source |
|--------|--------|
| API duration | FastAPI middleware logs and Sentry performance |
| AI first token | SSE service timing |
| Sync duration | client sync telemetry plus API logs |
| Local query time | client performance marks |
| Web vitals | Lighthouse and browser performance APIs |

## Regression Policy

A feature can exceed a budget temporarily only if the PR documents:

- the measured value
- why it exceeds the budget
- what follow-up will bring it back under budget

Performance issues that risk data loss, blocked startup, or unusable offline mode must be fixed before merge.
