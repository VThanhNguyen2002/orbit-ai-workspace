# Privacy and Data Handling

## Threat Model

Synapse handles sensitive personal data: notes, tasks, voice recordings, AI-generated summaries. Even as a portfolio project, the architecture must demonstrate production-grade data handling.

### Data Classification

| Category | Examples | Sensitivity | Storage |
|----------|----------|-------------|---------|
| Identity | Email, display name | Medium | Supabase Auth |
| Content | Notes, tasks | High | Supabase PostgreSQL |
| Audio | Voice memos | High | Supabase Storage |
| AI-derived | Transcripts, summaries | High | Supabase PostgreSQL |
| Vectors | Embeddings | Low-Medium | Supabase pgvector |
| Sync metadata | Queue operations, conflict records | Low | Local device only |

## User Isolation

### Supabase Row Level Security (RLS)

Every table with user data has RLS enabled. Policies enforce:

```sql
-- Example: notes table
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access own notes"
  ON notes FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**Rules:**
- RLS is enabled on every user-data table — no exceptions
- The API cannot bypass RLS (uses standard Supabase client, not service role key for user operations)
- Service role key is used only for system operations (embedding generation, scheduled cleanup)
- Service role key never leaves the backend environment

Slice 6E adds the first Notes RLS draft in
`supabase/migrations/20260522000000_create_notes.sql`. The API still defaults to
the memory repository for local/test determinism, and the Supabase request path
will require an injected user-scoped client before live use. No service-role key
is used by Notes request handlers.

### API-Level Isolation

Even though RLS handles authorization, the API adds defense-in-depth:

```python
async def get_note(note_id: UUID, user: User = Depends(get_current_user)):
    note = await db.fetch_note(note_id)
    if note is None or note.user_id != user.id:
        raise HTTPException(404)  # 404, not 403 — don't leak existence
    return note
```

404 for unauthorized access (not 403) — prevents entity enumeration.

## Voice Memo Security

### Storage

- Voice memos stored in Supabase Storage bucket: `voice-memos`
- Path format: `voice-memos/{user_id}/{memo_id}.{ext}`
- Bucket is **private** — no public URLs
- Access via signed URLs with short TTL (5 minutes)

### Signed URL Generation

```python
def get_voice_memo_url(user_id: str, memo_id: str, ext: str) -> str:
    path = f"voice-memos/{user_id}/{memo_id}.{ext}"
    return supabase.storage.from_("voice-memos").create_signed_url(
        path, expires_in=300  # 5 minutes
    )
```

- Signed URLs are generated server-side only
- Client requests a signed URL via API, never constructs storage paths directly
- URLs expire — no permanent access links

### Storage Bucket Policy

```sql
CREATE POLICY "Users can manage own voice memos"
  ON storage.objects FOR ALL
  USING (
    bucket_id = 'voice-memos' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );
```

## AI Provider Data Exposure

### What AI providers see

| Provider | Data Sent | Risk | Mitigation |
|----------|-----------|------|------------|
| OpenAI/Groq/Gemini | Note content, transcript text | Content exposure to third party | Use providers with data retention opt-out; no fine-tuning on user data |
| Whisper | Audio binary | Voice biometric exposure | Use providers with zero-retention API policies |
| Embedding API | Text chunks | Content exposure | Same as LLM — use zero-retention policies |

### What AI providers do NOT see

- User identity (no email/name sent)
- Entity IDs or metadata
- Other users' data
- Authentication tokens

### Mitigation Strategy

1. **OpenAI API data policy**: Opt out of data usage for training via API settings
2. **No PII in prompts**: System prompts never include user identity
3. **Provider abstraction**: Can switch to self-hosted models (Ollama) in future without client changes
4. **Audit logging**: All AI calls logged with timestamp, model, and token count (not content)

## API Key Management

### Backend API Keys

```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
GOOGLE_AI_KEY=...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=...
```

**Rules:**
- All API keys stored as environment variables
- Never committed to git (enforced via `.gitignore` and CI checks)
- In production: injected via deployment platform secrets (Render environment variables)
- In development: `.env` file, gitignored
- Service role key used only for server-side operations, never exposed to clients

### Client-Side Keys

The client only holds:
- `SUPABASE_URL` — public, safe to embed
- `SUPABASE_ANON_KEY` — public, safe to embed (RLS protects data)

No other secrets on the client. All AI operations go through the backend.

## Offline Storage Security

### Local Persistence Threat Model

Data stored locally in WatermelonDB (SQLite on mobile, web adapter storage in the browser) is not encrypted at rest by default.

**Accepted risk for Phase 1:** Local storage relies on OS-level device security (device lock, encryption). This is the same security model as most mobile apps (including banking apps).

**Phase 2 consideration:** Encrypt sensitive fields (note content, task descriptions) before writing to local persistence using a key derived from the user's auth session.

### What's Stored Locally

| Data | Stored Locally | Reason |
|------|---------------|--------|
| Notes (content) | Yes | Offline reading/editing |
| Tasks | Yes | Offline viewing/editing |
| Voice memo metadata | Yes | Title, duration, status for offline display |
| Voice memo audio files | No (temporary cache only) | Held in temp cache until uploaded; deleted after upload |
| Transcripts | Yes (text only) | Offline reading |
| Summaries | Yes (text only) | Offline reading |
| Embeddings | No | Only needed server-side for search |
| Sync queue | Yes | Offline operation tracking |
| Auth token | Yes (secure storage) | Session persistence |

### Auth Token Storage

- **Mobile:** `expo-secure-store` (Keychain on iOS, Keystore on Android)
- **Web:** `httpOnly` cookie or in-memory (Supabase handles this)
- Never in localStorage, browser persistence, key-value stores, or WatermelonDB entity tables

## Data Deletion

### Soft Delete

All entity deletions are soft deletes (`is_deleted = true`). Physical deletion occurs via scheduled cleanup:

```sql
-- Runs weekly via Supabase scheduled function
DELETE FROM notes WHERE is_deleted = true AND updated_at < now() - interval '30 days';
DELETE FROM tasks WHERE is_deleted = true AND updated_at < now() - interval '30 days';
-- Cascade: embeddings, summaries deleted via FK cascade
```

### Account Deletion

If implemented:
1. Delete all user data from all tables (cascade from user_id FK)
2. Delete all files in `voice-memos/{user_id}/` from Storage
3. Delete Supabase Auth user
4. Clear local storage on device

This is a Phase 3 consideration.

## Transport Security

- All API communication over HTTPS (enforced by Vercel and Render)
- Supabase connections use TLS
- WebSocket (Realtime) uses WSS
- No HTTP fallback in production

## Assumptions

1. OS-level device security is the baseline for local data protection
2. AI providers honor their data retention policies
3. Supabase RLS is correctly configured and tested (verified via integration tests)
4. Single-user system — no need for inter-user access control in Phase 1
5. GDPR/compliance is out of scope for portfolio project, but architecture supports eventual compliance
