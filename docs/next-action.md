# Next Action

## Objective

Recommended next task: **Slice 7M-B — Mocked SDK adapter interface tests
without SDK dependency**.

Slice 7M-A is complete. The
[OpenAI SDK dependency review packet](openai-sdk-dependency-review-packet.md)
was added as a docs-only planning document.

## Slice 7M-A Result

Slice 7M-A adds `docs/openai-sdk-dependency-review-packet.md`. The packet
covers:

- Candidate dependency fields (all `TO_BE_*` placeholder, not yet selected).
- 8 dependency approval gates (all required before any install).
- Supply-chain risk checklist (source verification, version pinning,
  transitive deps, vulnerability scan, update policy, rollback path).
- Runtime risk checklist (import failure, API shape drift, retry/timeout,
  response validation, error mapping).
- Credential/security checklist (no committed keys, no auth header logging,
  API key mode and WIF both not approved).
- Testing plan (dependency-free mocked interface tests remain default).
- CI/build impact checklist (install time, lockfile diff, Python compat,
  no default live tests, no workflow secret changes).

No SDK installation, dependency manifest change, lockfile change, credential
use, live API call, runtime import, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED.**

## Slice 7M-B Scope

Add test coverage for the future SDK adapter using only fake/mocked SDK clients.
No real SDK install, no network, no credentials.

Recommended scope:

- Implement mocked SDK client tests for the `openai_provider.py` adapter
  boundary using `unittest.mock`.
- Cover success mapping, failure mapping, timeout, retry, malformed response,
  and redaction paths.
- Implement no-network proof via `socket.socket` patch.
- Implement no-credential proof.
- Keep tests default-CI-safe: no live network, no SDK install required.
- Do not install `openai`, change any dependency manifest, add credentials,
  change runtime code, or modify route behavior.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED.** All 8 dependency approval gates must
be satisfied before any `pip install openai` is authorized.

## Definition Of Done

- The dependency review packet is documented.
- No SDK, live harness, credentials, or real API calls are added.
- Approval remains denied/not granted.
- SDK dependency remains NOT APPROVED.

Do NOT proceed to Slice 7M-B automatically.
