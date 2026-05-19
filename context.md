# Synapse — Project Context

> Load this file when working on the Synapse project.

## Identity

- **Name**: Synapse
- **Type**: Portfolio-grade engineering project
- **Purpose**: Demonstrate cross-platform AI productivity system architecture
- **Repository**: https://github.com/VThanhNguyen2002/orbit-ai-workspace

## Scope

Cross-platform (Web + Mobile) offline-first AI productivity companion.

Core capabilities: notes, tasks, voice memos, AI summarization, semantic search, realtime sync.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Monorepo | Turborepo + pnpm |
| Frontend | Expo + React Native + React Native Web + TypeScript |
| Backend | FastAPI + Python |
| Database | Supabase (PostgreSQL + Auth + Storage + Realtime + pgvector) |
| AI | OpenAI / Groq / Gemini + Whisper |
| Testing | Vitest + Playwright |
| CI/CD | GitHub Actions |
| Deploy | Vercel + Render + EAS Build |

## Current Phase

Phase 1 — Foundation (planning)

## Constraints

- Ubuntu on VMware — resource-constrained
- No Android Studio, no local LLMs, no Kubernetes
- Cloud-native services preferred
- Lightweight development workflow

## Key Files

| File | When to Load |
|------|-------------|
| `docs/architecture/overview.md` | System design decisions |
| `docs/architecture/data-model.md` | Entity relationships |
| `docs/architecture/api-contract.md` | API design |
| `docs/architecture/offline-sync.md` | Sync architecture |
| `docs/roadmap.md` | Phase definitions and acceptance criteria |
| `docs/definition-of-done.md` | Completion criteria |

## Conventions

Inherits workspace-level conventions:

- `execution-guardrails.md` — before running commands
- `git-convention.md` — before commits/branches
- `testing-standard.md` — before writing tests
