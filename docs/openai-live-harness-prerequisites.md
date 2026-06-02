# OpenAI Live Harness Prerequisites

## 1. Objective

Prepare the documentation prerequisites for a future local-only OpenAI live
harness approval decision without granting approval, implementing a harness,
adding credentials, installing an SDK, or calling OpenAI.

This document is a checklist and evidence-template packet only. It does not
authorize live execution.

## 2. Current Decision Status

Approval remains **NOT GRANTED**.

This slice does not approve:

- Live harness execution.
- Provider credentials.
- OpenAI SDK implementation.
- OpenAI runtime wiring.
- WIF runtime.
- Token exchange.
- Live OpenAI API calls.
- Default CI live tests.

Fake provider remains the default for local development, tests, and normal CI.

## 3. Security/Privacy Prerequisite Checklist

Before any local-only approval can be reconsidered, the future approval record
must show that the live harness will enforce:

- Synthetic prompt only.
- No real note content.
- No user PII.
- No production data.
- No raw prompt logging.
- No provider raw body logging.
- No auth header logging.
- No token logging.
- No API-key logging.
- Redacted diagnostics only.
- External review before execution.

Missing any item keeps approval blocked.

## 4. Cost/Budget Prerequisite Checklist

Future limits must be approved with placeholder-only labels until a later
approval record chooses actual values:

| Future limit | Placeholder label |
|---|---|
| Max requests per run | `TO_BE_APPROVED_MAX_REQUESTS_PER_RUN` |
| Max prompt length | `TO_BE_APPROVED_MAX_PROMPT_LENGTH` |
| Max output tokens | `TO_BE_APPROVED_MAX_OUTPUT_TOKENS` |
| Max retry count | `TO_BE_APPROVED_MAX_RETRY_COUNT` |
| Max timeout | `TO_BE_APPROVED_MAX_TIMEOUT` |
| Max spend ceiling | `TO_BE_APPROVED_MAX_SPEND_CEILING` |

The future harness must fail closed if budget configuration is missing or
invalid. This document does not add provider config, defaults, credentials, or
environment reads.

## 5. Credential-Mode Decision Checklist

A later approval record must decide one credential mode and document its
constraints:

- Local-only API-key candidate: not approved yet.
- WIF candidate: preferred for CI/cloud, not approved yet.
- No production API-key fallback.
- Credentials must stay outside git.
- No committed `.env` files.
- No tokens, keys, OIDC values, or JWT values in logs.
- No tokens, keys, OIDC values, or JWT values in artifacts.
- Fake provider remains default.

This document does not approve credential use.

## 6. Redacted Evidence Template

A future live harness run report should use this template. It must contain
labels and coarse metadata only.

```text
Run mode:
Approval record commit:
Credential mode label:
Synthetic prompt description:
Coarse provider outcome:
Request count:
Cost estimate bucket:
Cleanup/no-artifact confirmation:
Redaction confirmation:
Stop condition if failed:
```

Rules for the future report:

- Describe the synthetic prompt; do not include prompt text.
- Record a credential mode label only; do not include credential values.
- Record a coarse provider outcome only; do not include raw provider body.
- Record request count and cost estimate bucket only.
- Confirm cleanup and no-artifact state.
- Confirm redaction.
- If execution stops, record only the stop condition.

## 7. Rollback/Disable Plan Checklist

A future approval must include a rollback and disable plan that preserves:

- Fake provider default.
- Disabled live flag.
- Removal of local environment value after the run.
- No route behavior switch.
- No default CI live test.
- No persisted live output.
- No committed evidence containing secrets.

## 8. No-Default-CI Proof Checklist

A future approval must include proof that:

- Normal push CI does not set live environment flags.
- Live tests are skipped by default.
- Workflow changes require separate review.
- `workflow_dispatch` live validation is not approved in this slice.
- Default CI remains fake-only, credential-free, and network-free.

## 9. Local-Only Execution Boundary

The future local-only boundary must be:

- Local developer machine only.
- Explicit opt-in flag required.
- Synthetic prompt only.
- No background summarization.
- No route default switch.
- No provider default switch.
- No shared credentials.
- No committed evidence containing secrets.
- No committed evidence containing prompt text.
- No committed evidence containing raw provider bodies.

## 10. Remaining Blockers

The following are still missing before local-only approval can be considered:

- Explicit approval decision.
- Actual credential-mode decision.
- Actual budget numbers.
- Approved evidence format.
- Local harness skeleton.
- Optional SDK planning.
- External review sign-off.

Until these blockers are resolved, approval remains **NOT GRANTED**.

## 11. Future Path

Recommended follow-up slices:

- **Slice 7L-C — Grant or deny local-only live harness approval with evidence.**
- **Slice 7M — OpenAI SDK adapter planning, still no credentials.**
- **Slice 7N — Opt-in live provider harness skeleton only after approval.**

Do not proceed to Slice 7L-C automatically from this prerequisite packet.
