# Synapse

**Offline-First AI Productivity Companion**

> A Living Engineering Resume for Cross-Platform AI Systems

---

## What Is Synapse?

Synapse is a cross-platform productivity system that captures notes, manages tasks, records voice memos, and uses AI to summarize, extract action items, and enable semantic search over personal knowledge.

It works offline-first, syncs in realtime, and runs on both web and mobile from a single codebase.

**This is not a startup.** Synapse exists to demonstrate production-grade engineering across the full stack.

## Engineering Focus

| Area | Target |
|------|--------|
| Performance | Lighthouse 90+, Core Web Vitals green |
| Accessibility | WCAG 2.1 AA, semantic HTML, keyboard navigation |
| Architecture | Shared monorepo, platform abstraction, offline-first |
| Testing | Unit + integration + E2E, offline sync testing |
| AI Integration | Streaming responses, semantic search, voice transcription |
| Realtime | Optimistic updates, conflict resolution, eventual consistency |

## Tech Stack

```
Monorepo        Turborepo + pnpm
Frontend        Expo + React Native + React Native Web + TypeScript
Backend         FastAPI + Python
Database        Supabase (PostgreSQL, Auth, Storage, Realtime, pgvector)
AI              OpenAI / Groq / Gemini APIs + Whisper
Deployment      Vercel (web) + Render (API) + EAS Build (mobile)
Testing         Vitest + Playwright
CI/CD           GitHub Actions
```

## Monorepo Structure

```
synapse/
├── apps/
│   ├── mobile/          # Expo app (iOS + Android + Web)
│   └── api/             # FastAPI backend
├── packages/
│   ├── shared/          # Business logic, types, validation
│   ├── ui/              # Cross-platform UI components
│   ├── api-client/      # Typed HTTP/WebSocket client
│   └── config/          # Shared configuration, constants
├── docs/                # Architecture, ADRs, standards
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## Architecture

See [docs/architecture/overview.md](docs/architecture/overview.md) for the full system design.

Key architectural properties:

- **Offline-first**: Local persistence with background sync queue
- **Shared logic**: Business rules, validation, and types shared across platforms
- **AI abstraction**: Provider-agnostic AI layer with streaming support
- **Realtime sync**: Supabase Realtime with optimistic updates and conflict resolution

## Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1 — Foundation | Auth, notes, tasks, voice, AI summary, shared packages | Planned |
| 2 — Offline + AI Memory | Offline sync, semantic search, embeddings, personal RAG | Planned |
| 3 — Engineering Excellence | Testing, perf optimization, a11y audits, CI/CD, design system | Planned |

See [docs/roadmap.md](docs/roadmap.md) for detailed acceptance criteria per phase.

## Documentation

| Document | Purpose |
|----------|---------|
| [Architecture Overview](docs/architecture/overview.md) | System design and component relationships |
| [Monorepo Strategy](docs/architecture/monorepo.md) | Package boundaries and build pipeline |
| [Data Model](docs/architecture/data-model.md) | Core entities and relationships |
| [API Contract](docs/architecture/api-contract.md) | Endpoint design and validation |
| [Offline Sync](docs/architecture/offline-sync.md) | Sync queue, conflicts, reconciliation |
| [AI Integration](docs/architecture/ai-integration.md) | Provider abstraction and streaming |
| [Security & Privacy](docs/security/privacy-and-data-handling.md) | Data handling and isolation |
| [ADRs](docs/adr/) | Architecture Decision Records |

## Development

```bash
# Install dependencies
pnpm install

# Start all apps in development
pnpm dev

# Run tests
pnpm test

# Lint and typecheck
pnpm lint && pnpm typecheck
```

## Environment Requirements

- Node.js 20+
- pnpm 9+
- Python 3.11+
- Supabase CLI
- Ubuntu / macOS (no Android Studio required for web dev)

Resource-conscious setup — designed to run on Ubuntu/VMware without heavy tooling.

## License

MIT
