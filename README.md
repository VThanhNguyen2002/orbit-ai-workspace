# Synapse

**Personal engineering project — architecture-focused notes and AI summarization system.**

A monorepo demonstrating backend REST API design, shared TypeScript contracts, typed API client, dependency-injected mobile view-state foundations, and a fake-provider AI summarization flow — all with strict quality gates and security checks.

> **Portfolio / non-commercial.** This is not a production application. It exists to demonstrate engineering discipline across the full stack.

---

## What Is Currently Implemented

| Area | Status | Notes |
|---|---|---|
| **FastAPI backend** | ✅ Complete | Notes CRUD, versioned update/delete, user isolation, conflict responses |
| **AI summarization** | ✅ Complete | Fake-provider only — deterministic, in-memory, no live AI calls |
| **Summary history** | ✅ Complete | Memory-only, newest-first, cleared on restart |
| **Shared Zod contracts** | ✅ Complete | Schema registry, snake_case wire contracts, strict envelope validation |
| **API client** | ✅ Complete | Typed, injection-ready, schema-validated, no fetch in mobile features |
| **Mobile view-state** | ✅ Complete | Dependency-free TypeScript — note list, detail, summary history |
| **Backend tests** | ✅ Complete | pytest: CRUD, isolation, fake summarize, newest-first history, leak checks |
| **TypeScript tests** | ✅ Complete | Vitest: API client notes + AI methods, shared contract schemas |
| **CI** | ✅ Complete | GitHub Actions: lint, typecheck, test, contract check, gitleaks |
| **Security checks** | ✅ Complete | gitleaks, redaction tests, error sanitization, no credential fixtures |

---

## What Is Explicitly Deferred / Not Implemented

| Area | Status |
|---|---|
| **Rendered mobile UI** | ❌ Deferred — Expo/React Native not initialized |
| **OpenAI SDK** | ❌ NOT APPROVED / DENIED — fake provider is the only active provider |
| **Live AI calls** | ❌ Not implemented — no credentials required or present |
| **Supabase** | ❌ Not active — no running Supabase instance, no Docker required |
| **PostgreSQL / RLS** | ❌ Not active — notes and summaries use in-memory repositories |
| **Database persistence** | ❌ Not implemented — all state is memory-only, resets on restart |
| **Auth (JWT)** | ⚠️ Structural only — JWT validation wired but no Supabase Auth runtime |
| **Offline sync** | ❌ Not implemented |
| **Web frontend** | ❌ Not implemented |

> **Summary history is memory-only.** It is demo/test state and is not persisted across backend restarts.

---

## Repository Structure

```
synapse/
├── apps/
│   ├── api/               # FastAPI backend (Python 3.11+)
│   │   ├── app/
│   │   │   ├── routers/   # notes.py, ai.py
│   │   │   ├── services/  # notes, ai_summarization, ai_prompting
│   │   │   └── providers/ # fake provider (default)
│   │   └── tests/         # pytest test suite
│   └── mobile/            # TypeScript view-state only (no Expo yet)
│       └── src/
│           └── features/notes/
│               ├── noteListApi.ts          # DI adapter → client.notes.list
│               ├── noteDetailApi.ts        # DI adapter → client.notes.get
│               ├── summaryHistoryApi.ts    # DI adapter → client.ai.*
│               ├── noteListViewState.ts    # idle/loading/empty/success/error states
│               ├── noteDetailViewState.ts  # idle/loading/success/error states
│               └── summaryHistoryViewState.ts  # + summarizing state, dedup, sort
├── packages/
│   ├── shared/            # Zod schemas, types, contract registry
│   ├── api-client/        # Typed HTTP client (Vitest tests)
│   └── config/            # Shared ESLint / TS config
├── docs/                  # Architecture records, decision packets, demo walkthrough
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        apps/api (FastAPI)                       │
│  POST /v1/notes   GET /v1/notes   GET /v1/notes/{id}  ...      │
│  POST /v1/ai/notes/{id}/summarize                               │
│  GET  /v1/ai/notes/{id}/summaries                               │
│  ↕ in-memory repos (FakeProvider AI, dict-backed Notes)         │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST (JSON envelopes)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│             packages/api-client (TypeScript)                    │
│  client.notes.{list,get,create,update,delete}                   │
│  client.ai.{summarizeNote, listNoteSummaries}                   │
│  ↕ Zod-validated responses (packages/shared schemas)            │
└────────────────────────┬────────────────────────────────────────┘
                         │ injected via Pick<> structural types
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│         apps/mobile/src (TypeScript view-state, no Expo)        │
│  noteListApi → noteListViewState (idle/loading/empty/success/error)
│  noteDetailApi → noteDetailViewState (+ not_found / invalid_response)
│  summaryHistoryApi → summaryHistoryViewState (+ summarizing, dedup)
│  All adapters: no raw fetch, no URL construction, no credentials │
└─────────────────────────────────────────────────────────────────┘
```

**Key design properties:**

- **Provider abstraction** — AI summarization uses a `FakeProvider` by default. The provider boundary is compile-enforced; no provider SDK is installed.
- **Fail-closed** — AI feature is disabled unless `SYNAPSE_AI_SUMMARIZATION_ENABLED=true`. Missing or unknown providers fail closed.
- **Injection-pure mobile adapters** — Mobile feature modules receive `Pick<>`-narrowed client slices. They cannot accidentally call methods outside their scope.
- **Schema-validated at the boundary** — All API client responses are parsed through Zod schemas before reaching view-state mappers.
- **Error sanitization** — Error states return only typed constant strings. No backend diagnostics, auth headers, provider identity, or raw error envelopes reach view-state consumers.

---

## Demo Walkthrough

See **[docs/api-demo-walkthrough.md](docs/api-demo-walkthrough.md)** for the step-by-step demo combining Note CRUD and fake-provider AI summarization.

Demo requires only:

```bash
cd apps/api
SYNAPSE_AI_SUMMARIZATION_ENABLED=true uvicorn app.main:app --reload
```

No Supabase, Docker, OpenAI API key, or `.env` file required.

---

## Running Quality Gates

```bash
# Install dependencies (Node.js 20+, pnpm 9+)
pnpm install --frozen-lockfile

# TypeScript lint + typecheck + test + build
pnpm lint
pnpm typecheck
pnpm test
pnpm build

# Mobile-specific typecheck (no Expo, TypeScript-only)
pnpm --filter mobile exec tsc --noEmit -p tsconfig.json

# API client tests
pnpm --filter @synapse/api-client test

# Shared contract checks
pnpm --filter @synapse/shared contracts:check
# or:
pnpm check-schemas

# Backend (Python 3.11+, inside apps/api virtualenv)
cd apps/api
python3 -m ruff check .
python3 -m pytest

# Security / credential scan
gitleaks detect --source=. --redact
```

All of the above run on CI automatically on every push to `main`.

---

## Security Stance

- **No credentials** — No OpenAI API key, Supabase key, JWT secret, or `.env` file is required to run tests or the demo.
- **Fake provider only** — AI summarization is backed by a deterministic in-memory `FakeProvider`. No live provider call is made anywhere in the codebase.
- **gitleaks** — Runs on every CI push. Only exact-fingerprint entries appear in `.gitleaksignore`.
- **Redaction tests** — Backend tests verify that AI summary responses, history listings, and captured logs do not expose prompt text, raw note content, bearer-like values, `sk-`-prefix strings, or raw diagnostic detail.
- **Error sanitization** — View-state error mappers return typed constant strings only. Provider identity, backend error detail, and schema parse errors are never forwarded to view-state consumers.
- **User isolation** — Notes are scoped per user. Cross-user access returns 404, not 403, to avoid information leakage.

See [docs/security/privacy-and-data-handling.md](docs/security/privacy-and-data-handling.md) for the full security stance.

---

## Documentation Index

| Document | Purpose |
|---|---|
| [API Demo Walkthrough](docs/api-demo-walkthrough.md) | Step-by-step Note CRUD + fake AI demo |
| [Mobile View-State Readiness Review](docs/mobile-viewstate-readiness-review.md) | Slice 8L review — READY verdict |
| [Rendered Mobile Demo Decision](docs/rendered-mobile-demo-unblock-decision-packet.md) | Expo/RN gate status — DEFERRED |
| [AI Summarization Plan](docs/ai-summarization-implementation-plan.md) | Master implementation record |
| [Backend Demo Polish Record](docs/backend-product-demo-polish-record.md) | Slice 8E–8F demo polish record |
| [Security & Privacy](docs/security/privacy-and-data-handling.md) | Full security stance and threat model |
| [Next Action](docs/next-action.md) | Current recommended next task |

---

## Tech Stack (Actual Current State)

```
Monorepo        Turborepo + pnpm
Backend         FastAPI (Python 3.11) — in-memory repositories
AI              FakeProvider (deterministic, memory-only) — no SDK installed
API Client      TypeScript, Zod-validated, injection-ready
Mobile          TypeScript view-state only — no Expo, no rendered UI
Shared          Zod schema registry, snake_case contracts
Tests           pytest (backend) + Vitest (TypeScript)
CI/CD           GitHub Actions (lint, typecheck, test, gitleaks)
```

---

## Environment Requirements

- **Node.js 20+**, **pnpm 9+** — for TypeScript packages and CI
- **Python 3.11+** — for FastAPI backend and pytest
- **No Supabase CLI required** — repositories are in-memory
- **No Docker required** — no database runtime
- **No Android Studio, iOS simulator, or Expo CLI required** — mobile is TypeScript-only

Resource-conscious setup — runs on Ubuntu/VMware without heavy tooling.

---

## License

MIT
