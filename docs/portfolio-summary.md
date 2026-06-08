# Synapse — Portfolio / Demo Summary

_Slice 9D · 2026-06-08 · Docs-only_

---

## 1. Project One-Liner

**Synapse** is a personal, non-commercial portfolio project demonstrating
contract-first API design, demo-safe fake-provider AI summarization, CI quality
gates, and dependency-free mobile TypeScript architecture — without claiming
production AI, rendered mobile UI, or live database persistence.

> This is not a production application. It exists to show engineering discipline
> across the full stack using safe, reproducible, credential-free techniques.

---

## 2. Currently Implemented Capabilities

| Capability | Status | Detail |
|---|---|---|
| **FastAPI Notes CRUD** | ✅ Complete | `GET/POST /v1/notes`, `GET/PATCH/DELETE /v1/notes/{id}`; memory-backed |
| **Versioned conflict detection** | ✅ Complete | `PATCH` with stale version → HTTP 409 + `expected`/`actual`/`server_data` |
| **Soft-delete isolation** | ✅ Complete | Deleted notes return 404; `is_deleted` + `deleted_at` set; hidden from list |
| **User ownership isolation** | ✅ Complete | Cross-user note access returns safe 404 (no 403 leakage) |
| **Fake-provider AI summarization** | ✅ Complete | Deterministic canned output; no network call, no SDK, no credentials |
| **Memory-only summary history** | ✅ Complete | Newest-first; resets on server restart; no persistence |
| **API client** | ✅ Complete | Typed, Zod-validated, injection-ready; notes CRUD + AI methods |
| **Shared Zod contracts** | ✅ Complete | Schema registry; snake_case wire contracts; strict envelope validation |
| **Mobile view-state foundation** | ✅ Complete | Dependency-free TypeScript — note list, detail, summary history, note mutation (create/update/delete) |
| **Mobile view-state unit tests** | ✅ Complete | Vitest coverage for all four view-state modules and API adapters |
| **Local API demo script** | ✅ Complete | `scripts/demo-api.sh` — bash/curl/python3 only; 13-step verified flow |
| **CI pipeline** | ✅ Complete | GitHub Actions: lint, typecheck, test, Zod contract check, gitleaks |
| **Security posture** | ✅ Complete | Gitleaks, redaction tests, error sanitization, no credential fixtures |

---

## 3. Demo Flow

### Quick Start

Terminal 1 — backend:

```bash
cd apps/api
SYNAPSE_AI_SUMMARIZATION_ENABLED=true uvicorn app.main:app --reload
```

Terminal 2 — demo script:

```bash
scripts/demo-api.sh
```

No Supabase, Docker, OpenAI API key, `.env` file, or package install required.

### Verified End-to-End Flow (13 steps)

```
1.  Health check                     → HTTP 200, status: ok
2.  Note create                      → HTTP 201, note_id + version captured
3.  Note list                        → HTTP 200, created note appears
4.  Note detail                      → HTTP 200, content accessible by owner
5.  Empty summary history            → HTTP 200, items: []
6.  Fake summarize (first)           → HTTP 200, summary_id + fake/fake-model-v1
7.  Summary history (one item)       → HTTP 200, items: [first_summary]
8.  Fake summarize (second)          → HTTP 200, distinct summary_id
9.  Summary history newest-first     → HTTP 200, items[0]=second, items[1]=first
10. Note update (correct version)    → HTTP 200, version incremented
11. Note update (stale version)      → HTTP 409, conflict envelope
12. Note delete (correct version)    → HTTP 200, is_deleted=true, deleted_at set
13. Deleted note GET                 → HTTP 404, soft-delete isolation confirmed
```

Full step-by-step: [`docs/api-demo-walkthrough.md`](api-demo-walkthrough.md)
Detailed endpoint list: [`docs/api-endpoint-summary.md`](api-endpoint-summary.md)

---

## 4. Architecture Value

### Contract-First Shared DTOs

All wire types live in `packages/shared` as Zod schemas. Backend, API client,
and mobile view-state all consume the same validated contracts. Shape mismatches
fail at parse time, not at runtime.

### Backend / API Client / Shared Contract Alignment

The API client (`packages/api-client`) validates every HTTP response against
`packages/shared` schemas before returning data to callers. Schema drift between
backend and client is caught in TypeScript tests, not in production.

### Fake-Provider Boundary

The AI summarization provider is selected by config. `ai_provider="fake"` is the
only active path. The provider interface is compile-enforced; swapping providers
does not change the route layer. No provider SDK is installed.

### Fail-Closed Provider Stance

AI summarization is **disabled by default** (`SYNAPSE_AI_SUMMARIZATION_ENABLED`
must be set explicitly). Unknown or misconfigured providers fail closed with a
503 rather than silently falling through.

### Mobile View-State Separated from Rendered UI

`apps/mobile/src` is pure TypeScript — no Expo, no JSX, no React Native runtime.
View-state orchestrators receive injected API adapter slices (`Pick<>` narrowed)
and produce typed state values. Future screen components can consume these
directly once Expo is initialized.

### Dependency-Free Demo Strategy

The demo script requires only `bash`, `curl`, and `python3`. The mobile
package adds zero runtime dependencies. TypeScript contracts and API client are
dependency-minimized and tested without live network access.

---

## 5. Security Posture

| Property | Status |
|---|---|
| No live OpenAI API call | ✅ Fake provider only; no network request made |
| No OpenAI SDK installed | ✅ NOT APPROVED / DENIED; dependency not added |
| No real credentials | ✅ No API key, Supabase key, JWT secret, or `.env` required |
| No `.env` required for demo | ✅ Script uses only env flag `SYNAPSE_AI_SUMMARIZATION_ENABLED=true` |
| No Supabase / Docker / RLS runtime | ✅ Notes and summaries are in-memory only |
| No rendered Expo / React Native UI | ✅ Mobile is TypeScript view-state only; Expo init DEFERRED |
| No production persistence | ✅ All state resets on backend restart |
| Memory-only summary history | ✅ Clearly documented; not presented as persistence |
| Gitleaks | ✅ Runs on every CI push; no leaks found |
| Redaction tests | ✅ AI surfaces verified to not expose prompt, raw note content, or credentials |
| Error sanitization | ✅ View-state errors return typed constant strings only |
| User isolation | ✅ Cross-user 404 (not 403) to prevent enumeration |

Full security stance: [`docs/security/privacy-and-data-handling.md`](security/privacy-and-data-handling.md)

---

## 6. Portfolio / CV-Safe Capability Bullets

These bullets are honest, verifiable, and free of overclaims. Do not use them
as-is in a CV without review — they are reference anchors for later wording.

- Designed and implemented a **versioned REST API** with conflict detection
  (HTTP 409), soft-delete isolation, and user-scoped ownership using FastAPI
  (Python 3.11).
- Built a **contract-first shared schema layer** using Zod (`packages/shared`)
  consumed by backend, typed API client, and mobile view-state modules.
- Implemented a **demo-safe fake-provider AI summarization flow** with
  configurable provider boundary, fail-closed defaults, and no SDK dependency.
- Authored a **dependency-free TypeScript mobile view-state foundation** with
  injected API adapters, typed state machines, and Vitest unit tests — covering note
  list, detail, summary history, and note mutations (create/update/delete).
- Maintained **strict CI/security quality gates**: GitHub Actions, gitleaks
  secret scanning, Ruff lint, pytest, Vitest, and Zod contract validation on
  every push.
- Wrote a **reproducible local demo script** (`bash`/`curl`/`python3`) covering
  13 verified API steps including conflict detection and soft-delete isolation.

**What these bullets do NOT claim:**

- Production AI (OpenAI SDK is not installed; all AI is fake/deterministic)
- Rendered mobile app (Expo/React Native initialization is deferred)
- Deployed production system (no hosting, no cloud deployment)
- Live Supabase / PostgreSQL / RLS (all state is memory-only)
- Offline-first sync (not implemented)

---

## 7. Remaining Limitations

| Limitation | Status |
|---|---|
| Memory-only summary history | Accepted — resets on restart; demo scope only |
| Rendered mobile UI | Deferred — Expo/React Native initialization needs 10/12 missing approval gates |
| Supabase / PostgreSQL / RLS | Deferred — out of scope; no Docker required |
| Live OpenAI provider | Deferred — NOT APPROVED / DENIED; all 8 named approval gates missing |
| Direct `vitest` imports in mobile tests | Deferred — using workspace Vitest globals as no-new-dependency compromise until mobile owns/approves Vitest dep |
| GitHub Actions Node.js 20 deprecation | Non-blocking annotation; CI passes; future Node upgrade needed |
| No web frontend | Not implemented; out of scope |
| No offline sync | Not implemented; out of scope |

---

## 8. Recommended Next Slices

| Option | Description | Effort | Agent |
|---|---|---|---|
| **Slice 9D** — Portfolio/release review gate | Audit documentation clarity and project positioning | Very low | AG |
| **Slice 10A** — Next product domain | Choose next product feature (e.g., note search/tag/pagination) | Low–Medium | Codex |
| **Pause** — Portfolio review as-is | Current state is demo-complete and CV-honest; pause feature work and use for portfolio review now | Zero | — |

> **Recommendation:** If the primary goal is portfolio readiness, the project is
> in a good state for review as-is. Slice 9D (portfolio/release review gate) is the
> final validation step. Slice 10A should only start if a concrete product gap needs filling.
