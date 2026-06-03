# Next Action

## Objective

Recommended next task: **Slice 7M-A — OpenAI SDK dependency review packet (docs-only)**.

Slice 7M is complete. The
[OpenAI SDK adapter plan](openai-sdk-adapter-plan.md)
was added as a docs-only planning document.

## Slice 7M Result

Slice 7M adds `docs/openai-sdk-adapter-plan.md`. The plan covers:

- Future SDK adapter boundary and injectable transport design.
- Credential constraints and runtime selection rules.
- Test strategy (mocked SDK client, fake transport, no-network, no-credential).
- Failure modes and cost/token guardrails.
- Approval gates required before any implementation begins.
- Recommended follow-up slices (7M-A, 7M-B, 7M-C, 7N).

No SDK installation, credential use, OpenAI API call, live harness execution,
WIF runtime, token exchange, route behavior switch, API client change,
SSE/frontend work, SQL, migration, Supabase work, or generated state was added.
Approval remains **DENIED / NOT GRANTED**. Fake provider remains the default.

## Slice 7M-A Scope

Docs-only dependency review packet for the OpenAI Python SDK. This slice does
not install anything, add dependencies, or change runtime behavior.

Recommended scope:

- Research the `openai` Python SDK: current stable version, license, transitive
  dependencies, size, security advisories.
- Produce a dependency review packet documenting findings and reviewer
  placeholders.
- Identify which transitive dependencies introduce network or crypto requirements.
- Document the dependency approval gate required before any `pip install openai`
  is authorized.
- Do not install `openai`, add SDK imports, change any `pyproject.toml` or
  lockfile, or add `.env` values.
- Do not add runtime code.
- Do not unblock the live harness path.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

To reopen:

1. Named security/privacy reviewer → sign-off per evidence packet section 5.1.
2. Named cost/budget reviewer → approve numeric budget values per section 5.2.
3. Named credential-mode reviewer → select a mode per section 5.3.
4. Named fixture reviewer → approve a synthetic fixture per section 5.4.
5. Named rollback reviewer → approve a plan with named owner per section 5.5.
6. Named CI reviewer → record explicit proof artifact per section 5.6.
7. Named boundary reviewer → approve a runbook per section 5.7.
8. External reviewer → provide explicit sign-off per section 5.8.

All 8 must be present before any live harness implementation is authorized.

## Definition Of Done

- The SDK adapter plan is documented.
- No live harness, SDK, credentials, or real API calls are added.
- Approval remains denied/not granted.

Do NOT proceed to Slice 7M-A automatically.
