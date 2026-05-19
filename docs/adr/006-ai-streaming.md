# ADR-006: Server-Sent Events for AI Streaming

**Status:** Accepted
**Date:** 2025-05-18
**Author:** Viet Thanh Nguyen

## Context

AI operations (summarization, Q&A) take 2–10 seconds to complete. Showing a spinner for the entire duration is a poor UX. Users expect ChatGPT-style progressive token rendering — text appearing word-by-word as the LLM generates it.

We need a streaming protocol from backend to client.

## Decision

Use **Server-Sent Events (SSE)** for streaming AI responses from FastAPI to the client.

## Rationale

### Why SSE over WebSocket

| Factor | SSE | WebSocket |
|--------|-----|-----------|
| Direction | Server → Client (unidirectional) | Bidirectional |
| Protocol | HTTP/1.1 | Custom protocol upgrade |
| Reconnection | Built-in auto-reconnect | Must implement manually |
| Complexity | Simple — standard HTTP response | Connection management, heartbeats |
| Load balancers | Works with any HTTP proxy | Requires WebSocket-aware proxy |
| Browser support | Native `EventSource` API | Native `WebSocket` API |

AI streaming is inherently unidirectional (server → client). WebSocket's bidirectional capability is unnecessary overhead. SSE works over standard HTTP — simpler deployment, simpler debugging.

### Why not long polling

- Higher latency per token (new request per update)
- More server resources (connection setup per poll)
- SSE is strictly superior for server→client streaming

### Why not WebSocket (used by Supabase Realtime)

Supabase Realtime already uses WebSocket for database change subscriptions. Adding another WebSocket for AI streaming would mean two persistent connections per client. SSE keeps AI streaming on standard HTTP, separating concerns cleanly:

- **WebSocket** → Supabase Realtime (database changes)
- **SSE** → AI response streaming (from our FastAPI backend)

## Implementation

### Backend (FastAPI)

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/notes/{note_id}/summarize")
async def summarize_note(note_id: str, user = Depends(get_current_user)):
    note = await note_service.get(note_id, user.id)

    async def event_stream():
        full_text = ""
        async for token in ai_provider.stream(prompt=note.content, system=SUMMARIZE_SYSTEM):
            full_text += token
            yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"

        action_items = extract_action_items(full_text)
        yield f"event: action_items\ndata: {json.dumps({'items': action_items})}\n\n"

        summary = await summary_service.save(note_id, user.id, full_text, action_items)
        yield f"event: done\ndata: {json.dumps({'summary_id': str(summary.id)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### Client (React Native)

```typescript
async function streamSummary(noteId: string, onToken: (text: string) => void): Promise<string> {
  const response = await fetch(`${API_URL}/v1/notes/${noteId}/summarize`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let summaryId = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    for (const line of text.split('\n')) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.text) onToken(data.text);
        if (data.summary_id) summaryId = data.summary_id;
      }
    }
  }

  return summaryId;
}
```

**Note:** React Native doesn't support `EventSource` natively. We use `fetch` with `ReadableStream` (polyfilled via `react-native-fetch-api` if needed) or a lightweight SSE parser.

## Event Protocol

```
event: token
data: {"text": "The "}

event: token
data: {"text": "meeting "}

event: action_items
data: {"items": [{"text": "Follow up with team", "priority": "high"}]}

event: done
data: {"summary_id": "uuid-here"}

event: error
data: {"code": "PROVIDER_ERROR", "message": "LLM timeout"}
```

| Event | When | Client Action |
|-------|------|--------------|
| `token` | Each generated token/chunk | Append to displayed text |
| `action_items` | After full text generated | Display extracted tasks |
| `done` | Operation complete, data persisted | Clear loading state, show final result |
| `error` | Provider failure | Show error toast, enable retry |

## Consequences

### Positive
- Token-by-token rendering gives perceived instant response
- Standard HTTP — works through any proxy, CDN, or load balancer
- Simple implementation on both ends
- Auto-reconnect (if using EventSource on web)

### Negative
- React Native needs SSE polyfill or manual stream parsing
- No client→server streaming (not needed for current use cases)
- Connection timeout handling needed for long operations

### Mitigations
- Custom SSE parser is < 50 lines of code
- Backend sets keep-alive to prevent proxy timeouts
- Client sets 60-second timeout, shows retry option on timeout
