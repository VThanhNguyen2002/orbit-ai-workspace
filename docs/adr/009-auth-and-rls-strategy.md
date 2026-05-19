# ADR-009: Auth And RLS Strategy

**Status:** Accepted
**Date:** 2026-05-19
**Author:** Viet Thanh Nguyen

## Context

Synapse stores private personal notes, tasks, transcripts, summaries, and embeddings. Data isolation must be enforced even if application code has a bug.

## Decision

Use **Supabase Auth for identity** and **PostgreSQL Row-Level Security for data isolation**.

The client obtains Supabase JWTs. FastAPI validates bearer tokens and uses the authenticated `user_id` for all request handling. User-owned tables enable RLS and include policies based on `auth.uid()`.

## Rationale

- Supabase Auth avoids building custom password/session infrastructure.
- RLS provides database-level isolation, not just API-level checks.
- JWT bearer auth works across mobile, web, and backend requests.
- The approach aligns with Supabase Realtime and Storage policy enforcement.

## Consequences

### Positive

- Strong defense in depth for cross-user access.
- Less custom auth code to maintain.
- Storage policies can match the same user ownership model.
- API tests can prove isolation through realistic requests.

### Negative

- RLS policy mistakes can block valid access or expose data.
- Service-role usage bypasses RLS and must be tightly controlled.
- Local offline mode must handle expired tokens until reconnect.

### Mitigations

- Add RLS tests for every user-owned table.
- Keep service-role keys out of request handlers.
- Refresh auth before processing sync queues.
- Log auth failures by safe category only; never log token contents.

## Implementation Notes

See [auth-and-rls.md](../architecture/auth-and-rls.md).

Every new user-owned table must ship with RLS policies and cross-user isolation tests in the same change.
