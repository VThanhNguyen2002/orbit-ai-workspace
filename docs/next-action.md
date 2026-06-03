# Next Action

## Objective

Recommended next task: **Review gate for Slice 7M-L — Provider boundary
cleanup/refactor implementation**.

Slice 7M-L is complete. Do not proceed to Slice 7N or any live harness work
unless the live path is explicitly reopened with the required named approvals.

## Slice 7M-L Result

Slice 7M-L adds a narrow provider-boundary cleanup:

- `OpenAIProviderRequest` now owns provider-facing sensitive-term derivation for
  safe diagnostics.
- `OpenAISummarizationProvider` and the dependency-free `OpenAISDKAdapter` both
  use `OpenAIProviderRequest.sensitive_terms()` when creating safe errors.
- Duplicate prompt/request sensitive-term helpers were removed from the provider
  and SDK adapter modules.
- Focused tests cover request-owned sensitive-term redaction through
  provider-safe errors.

No SDK install, dependency manifest change, lockfile change, credential, `.env`
file, live API call, WIF runtime, token exchange, live harness, route behavior
change, API client change, SSE/frontend work, SQL, migration, Supabase work,
`.gitleaksignore` broadening, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED / DENIED.**

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED / DENIED.** All dependency approval gates
must be satisfied before any SDK install is authorized.

## Definition Of Done

- Review Slice 7M-L code, tests, docs, verification output, security check
  result, commit, push, and CI status.
- Confirm fake provider remains the default and OpenAI runtime remains
  fail-closed.
- Confirm no SDK dependency/import, credential, `.env` file, live runtime, route
  behavior, API client, SQL/migration, Supabase generated state, or
  `.gitleaksignore` broadening was introduced.
