# Observability

## Overview

Synapse uses structured logging, request tracing, error classification, and performance monitoring to maintain visibility into system health. Phase 1 focuses on actionable observability — no dashboards for dashboards' sake.

## Wave 2 Implementation Contract

Observability must explain user-impacting failures without exposing user content.

| Signal | Owner | Minimum Fields |
|--------|-------|----------------|
| API request log | FastAPI middleware | `request_id`, method, path, status, duration_ms, user_id when authenticated |
| API error log | Exception handler | `request_id`, error_code, error_category, safe_message, status |
| Sync event | Sync service/client | operation_count, applied_count, conflict_count, failed_count, duration_ms |
| AI event | AI service | provider, model, operation, token_count if available, duration_ms, outcome |
| Client error | Mobile app | app_version, platform, route/screen, request_id when tied to API |

Privacy rules:

- Never log note content, task descriptions, transcript text, summary text, prompts, embeddings, JWTs, refresh tokens, or audio paths containing raw user data.
- Use `user_id` for correlation; do not send email addresses to logs or Sentry.
- Request bodies are scrubbed before Sentry capture.
- User-facing errors include `request_id` so support can correlate without asking for private content.

Operational gates:

- CI must keep lint/typecheck/test green before observability code lands.
- API integration tests assert the standard error envelope includes `request_id`.
- Sync tests assert failures are classified as retryable, conflict, validation, or terminal.

## Observability Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Structured logging (backend) | Python `structlog` | JSON-formatted, leveled, request-scoped logs |
| Request tracing | `request_id` middleware | Correlate all log entries for a single request |
| Error tracking | Sentry (backend + frontend) | Exception capture with context, grouping, alerting |
| Performance monitoring | Sentry Performance | Transaction traces, slow query detection |
| Uptime monitoring | Supabase Health + external ping | `/v1/health` endpoint check |
| Client-side errors | Sentry React Native SDK | JS exceptions, unhandled promise rejections |

## Structured Logging (Backend)

### Configuration

```python
# app/core/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| `DEBUG` | Development-only detail | SQL query parameters, cache hit/miss |
| `INFO` | Normal operations | Request received, sync completed, AI response streamed |
| `WARNING` | Degraded but functional | AI provider slow (>5s), retry triggered, rate limit approaching |
| `ERROR` | Failed operation, user impacted | AI provider failure, sync conflict, DB query failure |
| `CRITICAL` | System-wide problem | DB connection lost, all AI providers down |

**Production log level:** `INFO` (no DEBUG in production).

### Request-Scoped Logging

Every request gets a `request_id` and `user_id` bound to the log context:

```python
# app/middleware/request_context.py
from uuid import uuid4
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        # Add user_id after auth (set by auth dependency)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

### Log Output Format

```json
{
  "timestamp": "2025-05-18T10:30:00.123Z",
  "level": "info",
  "logger": "app.routes.notes",
  "request_id": "req_abc123",
  "user_id": "user_def456",
  "event": "note_created",
  "note_id": "note_ghi789",
  "duration_ms": 45
}
```

### What Gets Logged

| Event | Level | Fields |
|-------|-------|--------|
| Request received | INFO | method, path, user_id |
| Request completed | INFO | method, path, status_code, duration_ms |
| AI stream started | INFO | provider, model, source_type, source_id |
| AI stream completed | INFO | provider, model, token_count, duration_ms |
| AI provider error | ERROR | provider, model, error_type, error_message |
| AI provider fallback | WARNING | failed_provider, fallback_provider |
| Sync push received | INFO | operation_count, user_id |
| Sync conflict detected | WARNING | entity_type, entity_id, client_version, server_version |
| Rate limit triggered | WARNING | user_id, endpoint, current_count, limit |
| DB query slow (>500ms) | WARNING | query_name, duration_ms |
| Unhandled exception | ERROR | exception_type, exception_message, stack_trace |

### What NEVER Gets Logged

- Note content, task descriptions, or any user-generated text
- JWT tokens or auth credentials
- Voice memo audio data or transcript content
- Embedding vectors
- Email addresses (use `user_id` only)

## Error Classification

### Backend Error Types

```python
# app/core/errors.py
from enum import Enum

class ErrorCategory(str, Enum):
    VALIDATION = "validation"       # Bad input, client can fix
    AUTH = "auth"                    # Token issues
    NOT_FOUND = "not_found"         # Entity doesn't exist
    CONFLICT = "conflict"           # Version mismatch
    RATE_LIMIT = "rate_limit"       # Too many requests
    PROVIDER = "provider"           # External service failure (AI, storage)
    INTERNAL = "internal"           # Bug in our code
```

### Error Response Enrichment

All errors include `request_id` so users can report issues with a correlation ID:

```json
{
  "error": {
    "code": "PROVIDER_ERROR",
    "message": "AI summarization failed. Please try again.",
    "category": "provider"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### Sentry Integration

```python
# app/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,  # "production", "staging", "development"
    traces_sample_rate=0.1,            # 10% of transactions traced
    profiles_sample_rate=0.1,
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    before_send=scrub_pii,             # Remove any accidentally captured PII
)

def scrub_pii(event, hint):
    """Remove user content from Sentry events."""
    if "request" in event and "data" in event["request"]:
        event["request"]["data"] = "[REDACTED]"
    return event
```

**Sentry rules:**
1. All unhandled exceptions are reported automatically
2. `PROVIDER` errors are reported but not alerted (expected transient failures)
3. `INTERNAL` errors trigger immediate alert (Slack notification)
4. Request body is ALWAYS scrubbed before sending to Sentry (contains user content)
5. `user_id` is set on Sentry scope, but email is NOT sent

## Client-Side Observability

### Sentry React Native SDK

```typescript
// apps/mobile/src/core/sentry.ts
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: Config.SENTRY_DSN,
  environment: Config.ENVIRONMENT,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Scrub any user content from breadcrumbs
    if (event.breadcrumbs) {
      event.breadcrumbs = event.breadcrumbs.map(b => ({
        ...b,
        data: undefined, // Remove all breadcrumb data
      }));
    }
    return event;
  },
});
```

### Client Error Categories

| Category | Example | Reporting |
|----------|---------|-----------|
| JS exception | Unhandled promise rejection in component | Sentry auto-capture |
| Network failure | API request timeout | Logged locally, not sent to Sentry (expected offline) |
| Sync failure | Push/pull error after retries exhausted | Sentry manual capture with sync context |
| Storage failure | WatermelonDB write failure | Sentry manual capture (critical) |

## Performance Monitoring

### Backend Metrics (Sentry Performance)

| Metric | Threshold | Alert |
|--------|-----------|-------|
| API response time (p95) | < 500ms | WARNING if > 500ms sustained |
| AI streaming first token | < 2s | WARNING if > 3s average |
| DB query time (p95) | < 100ms | WARNING if > 200ms |
| Sync push processing | < 1s per batch | WARNING if > 2s |
| Error rate | < 1% of requests | CRITICAL if > 5% |

### Health Endpoint

```json
GET /v1/health

{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-05-18T10:30:00Z",
  "checks": {
    "database": "connected",
    "ai_primary": "available",
    "storage": "connected"
  }
}
```

Health check runs every 60 seconds via external monitor. Alerts if endpoint returns non-200 or `status !== "healthy"` for 3 consecutive checks.

## Log Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Application logs (stdout) | 30 days | Cloud provider log service (Railway / Fly.io) |
| Sentry events | 90 days | Sentry cloud |
| Health check history | 90 days | External monitor |

## Tradeoffs

| Decision | Upside | Downside |
|----------|--------|----------|
| structlog over stdlib logging | Structured JSON, context binding | Learning curve for Python devs used to stdlib |
| Sentry for both error + perf | Single tool, correlated data | Cost scales with volume; 10% sampling in Phase 1 |
| No custom metrics/dashboards (Phase 1) | Faster to ship | Less granular visibility; rely on logs + Sentry |
| Aggressive PII scrubbing | Privacy-safe observability | Harder to debug content-specific issues |

## Assumptions

1. 10% trace sampling is sufficient for Phase 1 traffic volume
2. Sentry free/team tier is sufficient for Phase 1
3. Cloud provider's built-in log viewer is sufficient (no ELK/Grafana in Phase 1)
4. Request body scrubbing catches all PII before it reaches Sentry
5. `request_id` in error responses is sufficient for user-reported issue correlation
