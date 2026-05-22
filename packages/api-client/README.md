# @synapse/api-client

Typed API client baseline for Synapse HTTP calls.

## Baseline Surface

- `createApiClient({ baseUrl, fetch, getAuthToken })`
- `client.request(path, options)` for typed envelope-aware requests
- `client.health()` for `GET /v1/health`
- `client.version()` for `GET /v1/version`
- `client.notes.list(query)` for `GET /v1/notes`
- `client.notes.create(payload)` for `POST /v1/notes`
- `client.notes.get(note_id)` for `GET /v1/notes/{note_id}`
- `client.notes.update(note_id, payload)` for `PATCH /v1/notes/{note_id}`
- `client.notes.delete(note_id, payload)` for `DELETE /v1/notes/{note_id}`

The client validates shared success and error envelopes from `@synapse/shared`.
HTTP error envelopes throw `ApiClientError`, network failures throw
`ApiNetworkError`, and malformed API responses throw `ApiInvalidResponseError`.
Notes request payloads use the shared snake_case Notes request contracts. The
client does not own auth state, persistence, offline sync, or UI behavior.

Auth is intentionally callback-based through `getAuthToken`; this package does
not own auth storage or integrate with a provider.

```ts
import { createApiClient } from "@synapse/api-client";

const api = createApiClient({
  baseUrl: "http://localhost:8000/v1",
  getAuthToken: () => null,
});

const health = await api.health();
const notes = await api.notes.list({ page: 1, per_page: 20 });
```
