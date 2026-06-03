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

Every live table with user data must have RLS enabled. For Notes, the intended
policy outcome is that an authenticated user may create, read, update, and
soft-delete only rows they own. This is a sanitized design statement, not an
executable database artifact.

**Rules:**
- RLS is enabled on every user-data table — no exceptions
- The API cannot bypass RLS (uses standard Supabase client, not service role key for user operations)
- Service role key is used only for system operations (embedding generation, scheduled cleanup)
- Service role key never leaves the backend environment

The executable Notes migration draft was removed from the current repository.
Only sanitized Notes/RLS design documentation remains; future migration files
require explicit approval and security review under
[database-migration-policy.md](database-migration-policy.md). Private repository
status does not reduce this review requirement. The API still defaults to the
memory repository, and no service-role key is used by Notes request handlers.

Slice 6G hardens the API auth mode boundary. `SYNAPSE_AUTH_MODE=dev` remains a
local/test-only deterministic path, while `SYNAPSE_AUTH_MODE=jwt` fails closed
for missing, malformed, unconfigured, or unverified bearer tokens. Unknown auth
modes also fail closed instead of silently becoming dev auth.

Slice 6H-1 implements an injected JWT verifier and a configured RS256 adapter.
It verifies signature, expiry, issuer, audience, UUID subject, and authenticated
role; `AuthContext.user_id` is derived only from verified `sub`. Deterministic
tests generate local RSA keys at runtime, never call Supabase, and assert that
token values do not appear in authorization error responses.

Asymmetric Supabase JWT verification through JWKS remains the normal live target
but is not wired yet; shared-secret verification is limited to a future explicit
legacy deployment if required. Future request-path Data API clients must use a
public publishable key (or a documented legacy anon key) plus the verified
caller JWT; they must never use a service-role credential.

Slice 6H-2 adds the request-scoped client factory boundary as an inert
descriptor. It accepts JWT auth context only, stores the caller token and public
Data API key as redacted values, prefers `SUPABASE_PUBLISHABLE_KEY`, and never
selects `SUPABASE_SERVICE_ROLE_KEY`. Its tests make no network requests. Live
repository wiring and RLS validation remain deferred.

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

### Prompt and Diagnostic Boundaries

Slice 7E adds a backend prompt builder for note summarization. The provider
prompt is assembled only from explicit note `title`, note `content`, and bounded
metadata such as content type and character counts. Prompt object reprs and
log-safe metadata exclude raw title, raw content, user identity, auth headers,
tokens, provider keys, and internal IDs.

Diagnostics for AI summarization must pass through the redaction helper before
they are logged or returned from public error paths. The helper masks sensitive
diagnostic keys, note title/content terms, prompt text, bearer/JWT-like values,
OpenAI-style API keys, Supabase key names, and raw auth header values. The fake
provider remains the only runtime provider; no live provider secret is required
or wired by this boundary.

### OpenAI Provider Credential Planning

Slice 7F keeps OpenAI provider integration docs-only. Future provider runtime
work must keep the fake provider as the default for local tests and CI, keep
live provider tests explicitly opt-in, and isolate any SDK or HTTP provider
calls inside a backend provider adapter.

Workload Identity Federation is the preferred future CI/cloud direction where a
secure token exchange is supported. Any future WIF slice must validate issuer,
audience, repository/ref/workflow subject constraints, avoid printing raw
OIDC/JWT/token values, and redact token-exchange diagnostics. A long-lived
provider API key may be documented only as an explicit fallback stored in a
deployment secret manager or gitignored local environment, never in source,
logs, CI output, public errors, or client bundles.

Slice 7G adds only the adapter interface boundary and fake transport tests. The
adapter accepts an injected transport, reads no credentials, imports no provider
SDK, and exposes only redacted diagnostics for timeout, unavailable, and
malformed-response cases. It is not wired into request handling; the fake
provider remains the default runtime provider.

Slice 7H adds config shape and fail-closed validation only. OpenAI `api_key` and
`workload_identity` modes are accepted as future configuration names but rejected
by runtime validation because no credential boundary or WIF runtime exists yet.
Default config remains fake, disabled, credential-free, and network-free.

Slice 7I adds the
[OpenAI Workload Identity approval record](../openai-workload-identity-approval-record.md).
WIF remains a preferred future direction where supported, but runtime token
exchange is not approved. Any future WIF work must satisfy issuer, audience,
subject, repository/ref/workflow, service-account mapping, rollback, CI
permission, and redaction requirements before implementation.

Slice 7J adds a mocked WIF token exchange boundary and fake-only tests. It is
not live runtime wiring: it performs no real token exchange, reads no
environment credentials, imports no OpenAI SDK, requests no GitHub OIDC token,
and creates no network clients. The boundary keeps raw identity assertion and
fake access-token placeholder values out of reprs, error strings, and safe
diagnostics.

Slice 7K adds the docs-only
[OpenAI live provider harness plan](../openai-live-provider-harness-plan.md).
Any future live provider harness must be skipped by default, use only synthetic
prompt content, keep fake provider as the default local/test/CI path, require
explicit opt-in gates, stop on missing budget or credential configuration, and
record only coarse redacted diagnostics. It must not log note content, prompt
text, raw provider response bodies, auth headers, API keys, OIDC/JWT values,
access tokens, or raw user payloads.

Slice 7L adds the docs-only
[OpenAI live harness approval record](../openai-live-harness-approval-record.md).
Approval status remains pending/not granted. No live OpenAI API call, SDK
implementation, credential use, WIF runtime, default CI live test, GitHub
Actions WIF wiring, route behavior switch, background summarization, or
persisted live provider output is approved.

Slice 7L-A keeps local-only live harness approval not granted until prerequisites
exist. Required evidence includes security/privacy approval, cost/budget
ceiling, credential-mode decision, synthetic prompt fixture, redacted evidence
template, no-default-CI proof, fail-closed config proof, local-only execution
boundary, rollback/disable plan, and external review gate.

Slice 7L-B adds the docs-only
[OpenAI live harness prerequisites](../openai-live-harness-prerequisites.md)
packet. It prepares checklists and a redacted evidence template only; it does
not approve credentials, SDK/runtime work, WIF runtime, live API calls, or live
harness execution.

Slice 7L-C denies local-only live harness approval because explicit approval
evidence is missing or insufficient. No credential use, OpenAI API call, SDK
runtime, WIF runtime, default CI live test, route behavior switch, background
summarization, or persisted live provider output is approved.

Slice 7L-D adds the docs-only
[OpenAI live harness approval evidence packet](../openai-live-harness-approval-evidence-packet.md).
The packet prepares reviewer placeholders and evidence requirements for
security/privacy, cost/budget, credential mode, synthetic fixture review,
rollback/disable, no-default-CI proof, and local-only boundary review. Approval
remains denied/not granted, and no live execution or credential use is approved.

Slice 7L-E fills the
[OpenAI live harness approval evidence packet](../openai-live-harness-approval-evidence-packet.md)
with explicit reviewer decision sections and a final evidence decision matrix.
2 of 10 evidence items are PRESENT; 4 are MISSING; 4 are INSUFFICIENT; 0 have
been approved by a named reviewer. Approval remains denied/not granted, and no
live execution or credential use is approved.

Slice 7L-F converts each MISSING and INSUFFICIENT evidence item into a concrete
required-action record. 8 items are now `PREPARED / STILL NOT APPROVED`. This
is not an approval state. Approval remains denied/not granted, and no live
execution or credential use is approved.

Slice 7L-G reviewed all named reviewer slots. 0 of 8 required named reviewer
approvals exist. Decision: CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST.
Approval remains denied/not granted, and no live execution or credential use
is approved.

Slice 7M adds the docs-only
[OpenAI SDK adapter plan](../openai-sdk-adapter-plan.md). The plan documents
the future adapter boundary, injectable transport design, credential constraints,
runtime selection rules, test strategy, failure modes, cost/token guardrails,
and approval gates. No SDK installation, credential use, live API call, route
behavior switch, or live harness execution is approved or added. Approval
remains denied/not granted. Fake provider remains the default.

Slice 7M-A adds the docs-only
[OpenAI SDK dependency review packet](../openai-sdk-dependency-review-packet.md).
The packet evaluates supply-chain risk, runtime risk, credential/security
constraints, testing requirements, and CI impact for a future OpenAI Python SDK
dependency decision. No SDK installation, dependency manifest change, credential
use, live API call, or runtime code is approved or added. OpenAI SDK dependency
decision remains **NOT APPROVED**. Fake provider remains the default.

Slice 7M-B adds a mocked SDK adapter boundary and fake-only tests. The boundary
accepts an injected SDK-like client, builds typed SDK-like requests, validates
typed SDK-like responses, and maps timeout, rate-limit, unavailable, malformed,
empty, or unsafe output cases to redacted safe errors. It imports no real SDK,
reads no environment credentials, creates no network clients, logs no prompt or
note content, renders no raw SDK body, and is not wired into runtime provider
selection. The OpenAI SDK dependency remains **NOT APPROVED**.

Slice 7M-C adds the docs-only
[OpenAI SDK dependency approval record](../openai-sdk-dependency-approval-record.md).
The record explicitly denies the `openai` Python SDK dependency. All 12 required
approval gates (dependency owner, security/privacy, license, supply-chain, CI
impact, rollback, no-default-live-run, external review, pinned version,
transitive dep review, vulnerability scan plan, update policy) are MISSING.
Decision: **NOT APPROVED / DENIED**. No install, manifest change, runtime
import, credential use, or live API call is approved. Fake provider remains the
default.

Slice 7M-D adds the docs-only
[OpenAI SDK dependency prerequisites](../openai-sdk-dependency-prerequisites.md).
The document prepares required-action checklists for all 12 missing approval
gates. All gates move from MISSING to PREPARED / STILL NOT APPROVED. PREPARED /
STILL NOT APPROVED is not an approval state. Dependency decision remains **NOT
APPROVED / DENIED**. No install, manifest change, runtime import, credential use,
or live API call is approved. Fake provider remains the default.

Slice 7M-E adds the docs-only
[OpenAI SDK dependency re-evaluation record](../openai-sdk-dependency-reevaluation-record.md).
The record formally re-evaluates the dependency decision. All 12 approval gates
remain MISSING since no named reviewer has provided concrete sign-offs or evidence.
Decision remains **NOT APPROVED / DENIED**. No SDK install, dependency manifest
change, lockfile change, credential use, live API call, WIF runtime, token exchange,
or generated state is approved or added. Fake provider remains the default.
Slice 7M-G should document keeping the mocked adapter path dependency-free.


### Backend API Keys

Secret names are documented without example values:

- `OPENAI_API_KEY` — future provider fallback only; not approved or required.
- `GROQ_API_KEY` — future provider fallback only.
- `GOOGLE_AI_KEY` — future provider fallback only.
- `SUPABASE_SERVICE_ROLE_KEY` — backend system operations only.
- `SUPABASE_JWT_SECRET` — legacy JWT verification only if explicitly approved.

**Rules:**
- All API keys stored as environment variables
- Never committed to git (enforced via `.gitignore` and CI checks)
- In production: injected via deployment platform secrets (Render environment variables)
- In development: `.env` file, gitignored
- Service role key used only for server-side operations, never exposed to clients

### Client-Side Keys

The client only holds:
- `SUPABASE_URL` — public, safe to embed
- `SUPABASE_PUBLISHABLE_KEY` — preferred future public Data API key (RLS protects data)
- `SUPABASE_ANON_KEY` — legacy public key only when an existing deployment requires it

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
- The API must not log bearer token contents. Auth failures should report only
  coarse failure categories through the standard error envelope.

## Data Deletion

### Soft Delete

All entity deletions are intended to be soft deletes. Any future physical
cleanup or retention implementation requires a separately approved,
security-reviewed administrative path; no cleanup query is committed here.

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
