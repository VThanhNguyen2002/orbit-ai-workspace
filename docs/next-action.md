# Next Action

## Objective

Recommended next task: **Slice 7M-C — SDK dependency approval or denial
record**.

Slice 7M-B is complete. The mocked SDK adapter boundary and tests were added
without installing or importing the real OpenAI SDK and without wiring any live
runtime path.

## Slice 7M-B Result

Slice 7M-B adds:

- `apps/api/app/services/openai_sdk_adapter.py` — typed SDK-like messages,
  requests, responses, usage metadata, injected client protocol, adapter, and
  safe redacted adapter errors.
- `apps/api/tests/test_openai_sdk_adapter.py` — fake SDK client tests covering
  request construction, success mapping, no SDK import, no environment
  credential lookup, no network use, timeout/rate-limit/unavailable mapping,
  malformed response handling, empty/unsafe output handling, and redaction.

No real SDK dependency, dependency manifest change, lockfile change,
credential, `.env` file, OpenAI API call, WIF runtime, token exchange, backend
route change, API client change, SSE/frontend work, SQL, migration, Supabase
work, or generated state was added.

**OpenAI SDK dependency decision: NOT APPROVED.**

## Slice 7M-C Scope

Record an explicit approval or denial decision for the OpenAI SDK dependency.
Named reviewers must complete the dependency gates before any install is
authorized.

Recommended scope:

- Record dependency owner, security/privacy, license, supply-chain, CI/build,
  rollback, no-default-live-run, and external review decisions.
- Keep all candidate version, license, vulnerability, transitive dependency,
  and lockfile-impact fields evidence-backed.
- Keep the decision separate from implementation. Approval, if granted later,
  only authorizes a future dependency install slice.
- If approval is denied or incomplete, keep the OpenAI SDK dependency blocked.

## Live Harness Path Status

The live harness approval path remains **CLOSED / BLOCKED UNTIL NAMED APPROVALS
EXIST** (Slice 7L-G — 0 of 8 named reviewer approvals).

## Dependency Status

**OpenAI SDK dependency: NOT APPROVED.** All dependency approval gates must be
satisfied before any SDK install is authorized.

## Definition Of Done

- A dependency approval or denial record exists.
- Named reviewer decisions are explicit and evidence-backed.
- No SDK install, dependency manifest change, lockfile change, credential,
  `.env` file, live API call, WIF runtime, token exchange, live harness, route
  behavior change, API client change, SSE/frontend work, SQL, migration,
  Supabase work, or generated state is added.
- Fake provider remains the default.

Do NOT proceed to Slice 7M-C automatically.
