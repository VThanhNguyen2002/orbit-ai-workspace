# ADR-004: FastAPI Python Backend

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

Synapse needs a backend for AI orchestration: LLM completions, Whisper transcription, embedding generation, and semantic search. These operations require Python-ecosystem libraries (OpenAI SDK, LangChain/LlamaIndex if needed, numpy).

The frontend is TypeScript. The backend language is an independent decision.

## Decision

Use **FastAPI** (Python 3.11+) as the backend API framework.

## Rationale

### Why Python

- **AI ecosystem** — OpenAI SDK, Whisper, embedding libraries, numpy, scipy are all Python-first
- **LLM libraries** — LangChain, LlamaIndex, instructor — all Python
- **First-class async** — Python 3.11+ async/await with asyncio is mature
- **Portfolio signal** — demonstrates polyglot capability (TypeScript frontend + Python backend)

### Why FastAPI over Flask/Django

- **Native async** — async route handlers without WSGI adapter hacks
- **Automatic OpenAPI docs** — Swagger UI out of the box for API documentation
- **Pydantic v2** — request/response validation with JSON Schema compatibility (bridges to Zod)
- **Streaming support** — `StreamingResponse` for SSE without third-party libraries
- **Performance** — among the fastest Python frameworks (Starlette + uvicorn)
- **Type hints** — full type annotation support, catches errors before runtime

### Why not Node.js/Express

- OpenAI's Node SDK exists but Python AI ecosystem is broader
- Would lose LangChain/LlamaIndex as options for RAG
- A separate Python service would still be needed for advanced AI features
- All-Node would skip the polyglot portfolio signal

### Why not Supabase Edge Functions

- Deno runtime — limited library support
- No streaming response support
- Cold start latency
- Suitable for simple triggers, not AI orchestration

## Consequences

### Positive
- Direct access to entire Python AI ecosystem
- AsyncIO handles concurrent AI requests efficiently
- Pydantic validation aligns with Zod schemas via JSON Schema bridge
- OpenAPI spec generated automatically — useful for API documentation
- uvicorn with hot reload provides fast development feedback

### Negative
- Two runtimes in the monorepo (Node.js + Python)
- TypeScript ↔ Python type sharing requires the JSON Schema bridge
- Deployment requires a Python-capable host (Render, Railway) separate from Vercel
- Python dependency management (pyproject.toml + pip/uv) is independent from pnpm

### Mitigations
- Root-level scripts coordinate both runtimes: `pnpm dev` starts Turborepo + uvicorn
- JSON Schema bridge ensures validation parity with a single build step
- Render's free tier handles FastAPI deployment with minimal configuration
- `uv` as Python package manager for fast, reliable installs

## Project Structure

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app creation, middleware, lifespan
│   ├── core/
│   │   ├── config.py          # Settings (pydantic-settings, env vars)
│   │   ├── deps.py            # Dependency injection (get_current_user, get_db)
│   │   └── middleware.py      # Request ID, CORS, error handling
│   ├── routers/
│   │   ├── notes.py
│   │   ├── tasks.py
│   │   ├── voice_memos.py
│   │   ├── search.py
│   │   ├── sync.py
│   │   └── health.py
│   ├── services/
│   │   ├── ai/
│   │   │   ├── base.py        # Abstract provider interfaces
│   │   │   ├── openai.py
│   │   │   ├── groq.py
│   │   │   └── whisper.py
│   │   ├── note_service.py
│   │   ├── task_service.py
│   │   └── sync_service.py
│   ├── models/
│   │   ├── note.py            # Pydantic request/response models
│   │   ├── task.py
│   │   └── common.py          # Shared response envelope, pagination
│   └── schemas/               # Generated JSON Schema files from @synapse/shared
├── tests/
│   ├── conftest.py
│   ├── test_notes.py
│   └── test_ai.py
├── pyproject.toml
├── Dockerfile
└── Makefile
```

## Key Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "supabase>=2.0",
    "openai>=1.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "ruff", "mypy"]
```
