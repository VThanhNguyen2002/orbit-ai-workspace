# Implementation Roadmap

## Overview

Three phases, each building on the previous. Each phase produces a deployable, demonstrable system — not just documentation.

**Total estimated timeline:** 12–16 weeks for a solo developer working part-time.

---

## Phase 1 — Foundation (Weeks 1–6)

### Goal
Prove the architecture works: monorepo builds, shared code runs on web and mobile, data flows end-to-end, AI responds.

### Milestones

#### Week 1–2: Monorepo + Auth
- Initialize Turborepo + pnpm workspace
- Create all package scaffolds (`shared`, `ui`, `api-client`, `config`)
- Set up TypeScript strict mode, ESLint, Prettier
- Set up Supabase project (database, auth, storage)
- Implement auth flow (sign up, log in, token persistence)
- Create RLS policies for all tables
- Deploy: API to Render, web to Vercel

**Deliverable:** User can sign up on web and mobile, JWT persists across restarts.

#### Week 3–4: Notes + Tasks + Realtime
- Define Zod schemas in `@synapse/shared` (Note, Task)
- Build JSON Schema bridge for Python validation
- Implement Notes CRUD (API + frontend)
- Implement Tasks CRUD (API + frontend)
- Build shared UI primitives (`@synapse/ui`: Button, Input, Card, etc.)
- Wire Supabase Realtime subscriptions
- Implement optimistic updates in Zustand stores

**Deliverable:** Notes and tasks work on both platforms, edits sync in realtime.

#### Week 4–5: Voice + AI
- Voice recording component (mobile, using `expo-av`)
- File upload to Supabase Storage
- Whisper transcription endpoint
- LLM summarization with SSE streaming
- Action item extraction
- Summary display in UI

**Deliverable:** Record voice memo → see transcript → see AI summary with action items.

#### Week 5–6: Testing + Polish
- Unit tests for `@synapse/shared` (≥ 80% coverage)
- Integration tests for API endpoints
- One E2E test (create note flow)
- GitHub Actions CI (lint + typecheck + test)
- Lighthouse audit and initial optimization
- Fix accessibility issues from audit

**Deliverable:** CI green, Lighthouse 90+, tests pass.

### Phase 1 Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| React Native Web compatibility issues | High — blocks web rendering | Test web early, maintain web-specific overrides in `@synapse/ui` |
| Supabase Realtime reliability | Medium — affects sync UX | Implement reconnection logic, fall back to polling |
| Expo Go limitations for voice recording | Medium — may need dev build | Use `expo-av` which works in Expo Go |
| Zod → JSON Schema fidelity | Low — edge cases in schema conversion | Test critical schemas manually, keep schemas simple |

---

## Phase 2 — Offline + AI Memory (Weeks 7–10)

### Goal
Make the app useful without internet. Add semantic search so users can find content by meaning, not just keywords.

### Milestones

#### Week 7–8: Offline Sync
- Implement WatermelonDB local persistence (SQLite on mobile, web adapter with browser persistence)
- Build sync queue with FIFO processing
- Implement connectivity detection
- Build pull sync endpoint (`/v1/sync/pull`)
- Build batch push endpoint (`/v1/sync/push`)
- Handle offline → online transition
- Implement retry logic with exponential backoff

**Deliverable:** User edits a note offline, comes back online, note syncs without data loss.

#### Week 8–9: Conflict Resolution
- Implement version-based conflict detection
- Auto-resolve: last-write-wins for different fields
- Surface overlapping conflicts to UI
- Build conflict resolution UI (show both versions, let user choose)
- Test: edit same note on two devices while offline

**Deliverable:** Conflicts detected and resolved (automatically or by user).

#### Week 9–10: Semantic Search + Embeddings
- Implement embedding generation on content create/update
- Build chunking logic for long content
- Implement search endpoint with pgvector cosine similarity
- Build search UI (query input, ranked results with snippets)
- Implement personal RAG: question → search → LLM answer with sources

**Deliverable:** User searches "what did I discuss about Q3?" and gets relevant notes ranked by similarity.

### Phase 2 Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sync queue corruption on app crash | High — data loss | Write-ahead logging: persist queue state before processing |
| pgvector performance at scale | Low (small dataset) — but design for it | IVFFlat index, limit embeddings per user |
| Browser storage limits on web | Low — text is small | Monitor WatermelonDB web adapter storage usage, warn at 80% capacity |
| Conflict resolution UX complexity | Medium — confusing UI | Keep it simple: show diff, offer 3 options (keep mine, keep theirs, merge) |

---

## Phase 3 — Engineering Excellence (Weeks 11–16)

### Goal
Turn a working app into a portfolio showcase. Optimize everything. Document everything. Automate everything.

### Milestones

#### Week 11–12: Testing Maturity
- Increase unit test coverage to ≥ 80% across all packages
- Add integration tests for sync operations
- Add E2E tests for critical flows (Playwright for web)
- Add offline sync test (mock network disconnection)
- All tests in CI with coverage reporting

**Deliverable:** Comprehensive test suite with coverage reports visible in CI.

#### Week 12–13: Performance + Accessibility
- Bundle analysis and code splitting
- Lazy load routes and heavy components
- Image optimization (WebP, proper sizing)
- Lighthouse Performance ≥ 95
- WCAG 2.1 AA audit and remediation
- Keyboard navigation for all flows
- Screen reader testing

**Deliverable:** Lighthouse all-green (95+ performance, 95+ accessibility).

#### Week 13–14: CI/CD + Deployment
- GitHub Actions: full pipeline (lint → typecheck → test → build → deploy)
- Staging environment auto-deploy on merge to `main`
- Production deploy on release tag
- EAS Build configuration for mobile releases
- Environment variable management across environments

**Deliverable:** Merge → auto-deploy → live in < 10 minutes.

#### Week 14–16: Design System + Polish
- Document all design tokens
- Component catalog (Storybook or similar)
- Error tracking setup (Sentry)
- API monitoring and logging
- Performance monitoring (Web Vitals reporting)
- Final README polish with architecture diagrams
- Record demo video / screenshots for portfolio

**Deliverable:** Complete, documented, monitored production system.

---

## What "Done" Looks Like

When all three phases are complete, the project demonstrates:

| Capability | Evidence |
|------------|----------|
| Cross-platform engineering | Same codebase runs on web, iOS, Android |
| Shared architecture | Monorepo with shared types, validation, UI components |
| Offline-first | Works without network, syncs on reconnect |
| Realtime sync | Multi-device changes appear in < 2 seconds |
| AI integration | Streaming summarization, voice transcription, semantic search |
| Performance | Lighthouse 95+, optimized bundles, lazy loading |
| Accessibility | WCAG 2.1 AA, keyboard nav, screen reader support |
| Testing maturity | 80%+ coverage, E2E tests, offline tests, CI enforcement |
| CI/CD | Automated lint → test → build → deploy pipeline |
| Security | RLS, API key isolation, signed URLs, no secrets in code |

This is the engineering resume.
