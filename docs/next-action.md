# Next Action

## Objective

Recommended next task: **Slice 7M — OpenAI SDK adapter planning (docs-only)**.

Slice 7L-G is complete. The
[OpenAI live harness approval evidence packet](openai-live-harness-approval-evidence-packet.md)
was reviewed for named reviewer approvals.

## Slice 7L-G Result

**Named reviewer approvals found: 0 of 8 required.**

All eight `TBD_*` reviewer slots remain placeholder-only.

**Decision: CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**

| Evidence item | Status |
|---|---|
| Security/privacy approval | CLOSED / BLOCKED |
| Cost/budget approval | CLOSED / BLOCKED |
| Credential-mode decision | CLOSED / BLOCKED |
| Synthetic prompt fixture | CLOSED / BLOCKED |
| Redacted evidence template | PRESENT |
| Rollback/disable plan | CLOSED / BLOCKED |
| No-default-CI proof | CLOSED / BLOCKED |
| Fail-closed config proof | PRESENT |
| Local-only boundary | CLOSED / BLOCKED |
| External review sign-off | CLOSED / BLOCKED |

Approval remains **DENIED / NOT GRANTED**. The live harness approval path
is **CLOSED / BLOCKED** until all 8 named reviewers provide explicit sign-off
per sections 5.1–5.8 of the evidence packet.

No OpenAI SDK, provider credential, `.env` file, real provider call, live
harness code, WIF runtime, token exchange, GitHub Actions WIF setup, frontend
work, SSE streaming, SQL, migration, Supabase generated state, API client
change, route behavior change, or live execution approval has been added.

## Slice 7M Scope

Docs-only planning for a future OpenAI SDK adapter. This slice does not
implement the adapter, install SDK packages, add credentials, or change
runtime behavior.

Recommended scope:

- Document the SDK adapter boundary (types, interface, transport protocol).
- Document the request/response safety rules.
- Document how the adapter will be gated behind the credential-mode approval
  (which remains blocked).
- Document how tests will use the existing fake transport without the SDK.
- Do not install `openai`, add SDK imports, or add `.env` values.
- Do not add runtime code.
- Do not unblock the live harness path.

## Reopening the Live Harness Path

To reopen the live harness approval path the following must occur:

1. A named security/privacy reviewer must sign off per section 5.1.
2. A named cost/budget reviewer must approve numeric budget values per section 5.2.
3. A named credential-mode reviewer must select a mode per section 5.3.
4. A named fixture reviewer must approve a synthetic fixture per section 5.4.
5. A named rollback reviewer must approve a plan with named owner per section 5.5.
6. A named CI reviewer must record explicit proof artifact per section 5.6.
7. A named boundary reviewer must approve a runbook per section 5.7.
8. An external reviewer must provide explicit sign-off per section 5.8.

All 8 must be present before any live harness implementation is authorized.

## Definition Of Done

- The live harness path remains closed/blocked.
- No live harness, SDK, credentials, or real API calls are added.
- Approval remains denied/not granted.

Do NOT proceed to Slice 7M automatically.
