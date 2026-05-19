# ADR-011: Observability And Error Handling

**Status:** Accepted
**Date:** 2026-05-19
**Author:** Viet Thanh Nguyen

## Context

Synapse has multiple failure-prone boundaries: offline sync, Supabase, AI providers, audio upload/transcription, and cross-platform clients. Debugging must be possible without exposing private user content.

## Decision

Use **structured request-scoped logging**, **standard API error envelopes**, and **Sentry for exception/performance monitoring**.

Every API request receives a `request_id`. Errors are classified into safe categories and returned with the same envelope shape. Logs and Sentry events are scrubbed of user content.

## Rationale

- Request ids connect client-visible failures to backend logs.
- Error categories let the client decide retry, conflict, auth, or user-facing behavior.
- Structured logs are searchable and useful before custom dashboards exist.
- Sentry provides exception grouping and performance traces without building infrastructure.

## Consequences

### Positive

- Failures are diagnosable across client, API, sync, and AI paths.
- User support can ask for a request id instead of private content.
- Expected failures such as offline/network errors can be separated from bugs.
- Performance regressions can be tracked from the start.

### Negative

- Scrubbing must be maintained as request shapes evolve.
- Over-logging can create cost/noise.
- Sentry sampling may miss rare traces.

### Mitigations

- Define a denylist of sensitive fields and scrub request bodies by default.
- Log metadata and counts, not note/transcript/prompt contents.
- Keep provider errors classified and safe before they reach the client.
- Add tests for the standard error envelope and request id propagation.

## Implementation Notes

See [observability.md](../architecture/observability.md).

Minimum implementation before production-like demos:

- FastAPI request id middleware
- global exception handler
- structured JSON logs
- Sentry initialization with PII scrubbing
- client error handling that preserves `request_id`
