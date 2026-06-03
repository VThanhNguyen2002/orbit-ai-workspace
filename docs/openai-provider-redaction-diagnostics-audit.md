# OpenAI Provider Redaction Diagnostics Audit

## 1. Objective

Audit and harden redaction and diagnostics behavior across the AI provider
boundary without adding dependencies, credentials, live calls, route behavior
changes, or runtime provider changes.

This slice verifies that prompt text, note content, credential-like fields,
auth headers, token-shaped values, provider payloads, SDK-like raw bodies, and
WIF fake assertion/token placeholders do not appear in safe diagnostics,
`repr()` output, `str()` output, or public error surfaces.

## 2. Scope

Audited surfaces:

- Prompt builder and redaction helper:
  `apps/api/app/services/ai_prompting.py`
- Summarization service and fake provider default:
  `apps/api/app/services/ai_summarization.py`
- OpenAI provider transport and provider-safe errors:
  `apps/api/app/services/openai_provider.py`
- Dependency-free SDK adapter diagnostics:
  `apps/api/app/services/openai_sdk_adapter.py`
- Mocked WIF exchange diagnostics:
  `apps/api/app/services/openai_workload_identity.py`
- Config fail-closed errors:
  `apps/api/app/core/config.py`
- Existing and new focused tests under `apps/api/tests/`
- `.gitleaksignore` exact-fingerprint posture

## 3. Audit Findings

- Prompt objects intentionally contain provider-facing prompt text, but their
  `repr()` and `log_safe_metadata()` surfaces expose only metadata and counts.
- `redact_diagnostic()` already masked sensitive keys, explicit prompt/content
  terms, bearer-style values, compact JWT-shaped values, and OpenAI-key-shaped
  values.
- The audit identified a hardening gap for raw payload and token/assertion
  field names such as `access_token`, `identity_assertion`, `raw_response`,
  `raw_body`, `provider_payload`, and `sdk_response`. These are now treated as
  sensitive diagnostic keys.
- `OpenAIProviderError` stores only redacted diagnostics and uses safe
  `str()`/`repr()` messages.
- `OpenAISDKAdapterError` stores only redacted diagnostics and preserves the
  dependency-free injected-client boundary.
- WIF fake exchange errors redact assertion/access-token placeholders and do
  not expose raw token values through request/result/error reprs.
- Config fail-closed errors continue to return coarse messages without
  echoing unsupported values or credential placeholders.
- Fake provider remains the runtime default.

## 4. Tests Added Or Extended

- `tests/test_ai_prompting.py`
  - raw provider/SDK payload keys are fully redacted
  - access-token, id-token, OIDC-token, identity assertion, and auth-header
    diagnostic fields are redacted
- `tests/test_openai_provider.py`
  - OpenAI provider transport diagnostics redact raw provider payloads,
    access-token fields, identity assertion fields, auth headers, prompt text,
    and note content
- `tests/test_openai_sdk_adapter.py`
  - SDK adapter diagnostics redact raw SDK response/body fields, access-token
    fields, identity assertion fields, provider payloads, prompt text, and note
    content
  - synthetic placeholder hygiene now covers the API-key and token placeholder
    output strings added by Slice 7M-J
- `tests/test_openai_workload_identity.py`
  - WIF error diagnostics redact raw response, identity assertion, access-token,
    and provider payload fields without requiring real-looking tokens

## 5. Security Guardrails Confirmed

- No raw prompt logging.
- No raw note title/content logging.
- No auth header/API key/access token/identity assertion logging.
- No provider raw payload or SDK-like raw response body in safe diagnostics.
- No real-looking JWT/OIDC/API-key fixtures were added.
- Synthetic placeholders remain `gitleaks`-safe.
- `.gitleaksignore` remains exact-fingerprint only.
- Fake provider remains the default runtime provider.
- OpenAI SDK dependency remains **NOT APPROVED / DENIED**.

## 6. Non-goals

This audit does not approve or add:

- OpenAI SDK dependency installation.
- Dependency manifest or lockfile changes.
- Credentials or `.env` files.
- OpenAI API calls.
- WIF runtime or real token exchange.
- Live harness implementation or execution.
- Route/API client behavior changes.
- SSE/frontend/Supabase/SQL/migration/generated-state work.
- `.gitleaksignore` broadening.

## 7. Approval Boundaries

- This audit does not approve refactor implementation.
- This audit does not approve SDK dependency use.
- This audit does not approve credentials.
- This audit does not approve live API calls.
- This audit does not reopen the live harness path.
- The live harness path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**.

## 8. Future Slices

Recommended next task:

- **Slice 7M-L — Provider boundary cleanup/refactor implementation** *(Complete — provider request sensitive-term derivation now feeds provider and SDK adapter diagnostics.)*

Later work remains blocked from live execution unless the live path is reopened
and approved by the required named reviewers.

## 9. Slice 7M-L Follow-up

Slice 7M-L kept the redaction behavior unchanged while clarifying ownership:
`OpenAIProviderRequest` now owns provider-facing sensitive-term derivation, and
both `OpenAISummarizationProvider` and the dependency-free `OpenAISDKAdapter`
use that request-owned list when creating safe errors.

No SDK dependency/import, credential, `.env` file, live call, WIF runtime, live
harness, route/API client change, SQL, migration, Supabase state,
`.gitleaksignore` broadening, or generated state was added.

## 10. Definition Of Done

- Redaction/diagnostics audit record exists.
- Focused tests cover prompt/content, credential-like fields, raw payloads,
  provider diagnostics, SDK diagnostics, WIF fake diagnostics, and fixture
  hygiene.
- Verification passes.
- Security checks confirm no `.env`, SDK dependency, credentials, SQL,
  migrations, Supabase state, route/client/live runtime changes, real-looking
  token examples, or `.gitleaksignore` broadening.
