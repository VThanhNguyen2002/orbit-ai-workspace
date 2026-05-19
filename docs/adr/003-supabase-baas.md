# ADR-003: Supabase as Backend-as-a-Service

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

Synapse needs: PostgreSQL database, user authentication, file storage for voice memos, realtime data subscriptions, and vector search (pgvector). Building and operating each of these services independently is infeasible for a solo developer.

## Decision

Use **Supabase** as the primary BaaS, providing Auth, Database (PostgreSQL), Storage, and Realtime from a single platform.

## Rationale

### Why Supabase

- **All-in-one** — Auth + PostgreSQL + Storage + Realtime in a single service
- **PostgreSQL** — real database, not a document store; enables pgvector for embedding search
- **Row Level Security** — authorization at the database level, not just the API
- **Realtime** — built-in WebSocket subscriptions for database changes
- **Generous free tier** — 500MB database, 1GB storage, 50K monthly active users
- **Self-hostable** — can migrate to self-hosted Supabase if needed
- **Client libraries** — official JS/TS SDK with TypeScript types

### Why not Firebase

- Firestore is a document store — poor fit for relational data with JOINs
- No pgvector equivalent — would need separate vector DB
- Firebase Realtime Database has data modeling limitations
- Vendor lock-in is stronger (proprietary query language)

### Why not building custom backend + DB

- Requires provisioning and managing PostgreSQL, Redis (for realtime), S3 (for storage)
- Auth implementation from scratch is error-prone
- Operational overhead is disproportionate for a portfolio project
- Supabase provides all of this with zero infrastructure management

### Why not Neon + Clerk + Upstash separately

- More integrations to configure and maintain
- No unified Realtime out of the box
- Higher complexity for comparable functionality
- Supabase's bundled approach reduces surface area

## Consequences

### Positive
- Single dashboard for database, auth, storage, and realtime monitoring
- RLS policies provide defense-in-depth authorization
- pgvector is available via a PostgreSQL extension — no separate vector DB
- Supabase migrations provide schema version control
- Client SDK handles JWT refresh automatically

### Negative
- Supabase Realtime has connection limits on free tier (200 concurrent)
- Storage has 50MB file size limit on free tier
- Edge Functions run on Deno, not Node — limited if we need server-side hooks
- Tied to Supabase's PostgreSQL version and extension support

### Mitigations
- Connection limits are not an issue for single-user / portfolio usage
- Voice memos capped at 25MB (Whisper API limit) — well within storage limits
- Edge Functions only used for simple triggers (user creation hook) — no complex logic
- Core AI logic lives in FastAPI, not Supabase

## Usage Pattern

### Client-side (Frontend)

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!
);

// Auth
const { data, error } = await supabase.auth.signInWithPassword({ email, password });

// CRUD (RLS-protected)
const { data: notes } = await supabase.from('notes').select('*').order('updated_at', { ascending: false });

// Realtime
supabase.channel('notes').on('postgres_changes', { event: '*', schema: 'public', table: 'notes' }, handler).subscribe();

// Storage (signed URL via API)
const { data: url } = await supabase.storage.from('voice-memos').createSignedUrl(path, 300);
```

### Server-side (FastAPI)

```python
from supabase import create_client

# Service role client — bypasses RLS for system operations
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# User-scoped client — respects RLS
supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY, headers={"Authorization": f"Bearer {user_jwt}"})
```

**Rule:** `supabase_admin` is used only for system operations (embedding generation, scheduled cleanup). All user-facing operations use `supabase_user` with RLS.

## Free Tier Constraints

| Resource | Free Tier Limit | Synapse Usage Estimate |
|----------|----------------|----------------------|
| Database | 500 MB | < 100 MB (text data) |
| Storage | 1 GB | < 500 MB (voice memos) |
| Auth users | 50K MAU | 1 (solo use) |
| Realtime connections | 200 concurrent | 2–3 (personal devices) |
| Edge Function invocations | 500K/month | < 1K (triggers only) |

Synapse operates well within free tier for development and portfolio demonstration.
