# @synapse/api-client

Typed API client baseline for Synapse HTTP calls.

## Baseline Surface

- `createApiClient({ baseUrl, fetch, getAuthToken })`
- `client.request(path, options)` for typed envelope-aware requests
- `client.health()` for `GET /v1/health`
- `client.version()` for `GET /v1/version`

The client validates shared success and error envelopes from `@synapse/shared`.
HTTP error envelopes throw `ApiClientError`, network failures throw
`ApiNetworkError`, and malformed API responses throw `ApiInvalidResponseError`.

Auth is intentionally callback-based through `getAuthToken`; this package does
not own auth storage or integrate with a provider.

```ts
import { createApiClient } from "@synapse/api-client";

const api = createApiClient({
  baseUrl: "http://localhost:8000/v1",
  getAuthToken: () => null,
});

const health = await api.health();
```
