# Definition of Done

## Per-Phase Acceptance Criteria

Every phase has concrete, measurable criteria. A phase is not complete until all criteria pass.

---

## Phase 1 — Foundation

### Monorepo & Shared Architecture
- [ ] Turborepo builds all packages without errors
- [ ] `pnpm typecheck` passes with zero errors across all packages
- [ ] `@synapse/shared` is consumed by both `apps/mobile` and `apps/api` (via JSON Schema)
- [ ] At least 3 shared Zod schemas have corresponding Python validation in the backend
- [ ] No circular dependencies between packages (verified by Turborepo)

### Authentication
- [ ] User can sign up and log in on web
- [ ] User can sign up and log in on mobile (Expo Go)
- [ ] Auth tokens persist across app restarts
- [ ] Unauthenticated requests return 401
- [ ] RLS policies prevent cross-user data access (verified by test)

### Notes CRUD
- [ ] Create, read, update, soft-delete notes on web
- [ ] Create, read, update, soft-delete notes on mobile
- [ ] Notes list loads in < 200ms for 100 notes
- [ ] Optimistic updates — UI updates before server confirms
- [ ] Version conflict returns 409 with server data

### Task Management
- [ ] Create, read, update, soft-delete tasks
- [ ] Filter tasks by status
- [ ] Tasks linked to notes display source reference
- [ ] Status transitions work (todo → in_progress → done)

### Realtime Sync
- [ ] Editing a note on web reflects on mobile within 2 seconds
- [ ] Editing a note on mobile reflects on web within 2 seconds
- [ ] Deleting an entity removes it from other devices
- [ ] Creating an entity appears on other devices

### Voice Recording (Mobile)
- [ ] Record voice memo on mobile
- [ ] Upload to Supabase Storage
- [ ] Playback recorded memo
- [ ] Duration and file size tracked correctly

### AI Summarization
- [ ] POST to summarize endpoint returns streaming response
- [ ] Tokens render progressively in UI
- [ ] Action items extracted and stored
- [ ] Summary persisted and visible on other devices via Realtime
- [ ] Error during summarization shows user-friendly message

### Shared UI Components
- [ ] At least 5 components from `@synapse/ui` used in `apps/mobile`
- [ ] Components render correctly on both web and mobile
- [ ] Design tokens (colors, spacing, typography) defined in `@synapse/ui/tokens`

### Testing
- [ ] `@synapse/shared` has ≥ 80% test coverage
- [ ] API routes have integration tests with mocked AI providers
- [ ] At least one E2E test (create note → verify appears in list)
- [ ] All tests pass in CI (GitHub Actions)

### Performance
- [ ] Web app Lighthouse Performance score ≥ 90
- [ ] Web app Lighthouse Accessibility score ≥ 90
- [ ] LCP < 2.5s on web
- [ ] No layout shift (CLS < 0.1)

---

## Phase 2 — Offline + AI Memory

### Offline-First
- [ ] Notes are readable when device is offline
- [ ] Notes are editable when offline, changes sync when back online
- [ ] Sync queue processes all pending operations on reconnect
- [ ] Failed sync operations surface in UI with retry option
- [ ] App startup without network loads from local persistence in < 500ms

### Conflict Resolution
- [ ] Version conflict detected when same entity edited on two devices
- [ ] Auto-resolve works for non-overlapping field changes
- [ ] Overlapping conflicts surface to user with both versions
- [ ] Conflict resolution test: edit note offline on device A and B, bring both online, verify resolution

### Semantic Search
- [ ] Embeddings generated for all notes and transcripts
- [ ] Search returns relevant results ranked by similarity
- [ ] Search results include snippet with matching context
- [ ] Search latency < 500ms for 1000 embeddings
- [ ] Empty/irrelevant queries return empty results (no crashes)

### Local Persistence
- [ ] MMKV (mobile) stores and retrieves entities correctly
- [ ] IndexedDB (web) stores and retrieves entities correctly
- [ ] Last sync timestamp persisted and used for delta sync
- [ ] Local store cleared on logout

### Personal RAG
- [ ] User can ask natural language question about their notes
- [ ] System retrieves relevant content via semantic search
- [ ] LLM generates answer grounded in retrieved content
- [ ] Response includes source references (which notes/memos contributed)

---

## Phase 3 — Engineering Excellence

### Testing Maturity
- [ ] Unit test coverage ≥ 80% across all packages
- [ ] Integration test coverage for all API endpoints
- [ ] E2E tests for critical user flows (auth, create note, search, sync)
- [ ] Offline sync test: automated test that toggles connectivity
- [ ] Tests run in CI on every PR

### Performance Optimization
- [ ] Lighthouse Performance ≥ 95
- [ ] Bundle size < 200KB gzipped (web)
- [ ] Code splitting: routes lazy-loaded
- [ ] Images optimized (WebP, proper sizing)
- [ ] No render-blocking resources

### Accessibility
- [ ] Lighthouse Accessibility ≥ 95
- [ ] All interactive elements keyboard-navigable
- [ ] Screen reader can navigate all core flows
- [ ] Color contrast meets WCAG 2.1 AA
- [ ] Focus management on route transitions

### CI/CD
- [ ] GitHub Actions: lint + typecheck + test on every PR
- [ ] GitHub Actions: deploy to staging on merge to main
- [ ] GitHub Actions: deploy to production on release tag
- [ ] EAS Build configured for mobile releases
- [ ] Deployment takes < 10 minutes

### Design System
- [ ] All design tokens documented
- [ ] Component catalog (Storybook or equivalent) for `@synapse/ui`
- [ ] Typography, color, spacing scales defined and consistent

### Observability
- [ ] Error tracking configured (Sentry or equivalent)
- [ ] API response times logged
- [ ] AI operation costs tracked
- [ ] Client-side performance metrics collected

---

## Cross-Phase Standards (Apply to All Phases)

- [ ] TypeScript strict mode enabled, zero `any` types
- [ ] ESLint passes with zero warnings
- [ ] All commits follow conventional commit format
- [ ] No secrets committed to git (verified by CI)
- [ ] README accurately reflects current state
