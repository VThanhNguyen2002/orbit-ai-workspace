# OpenAI SDK Dependency Review Packet

## Status

Slice 7M-A is a documentation-only dependency review slice. It reviews the
future OpenAI SDK dependency decision without installing or approving the
dependency.

**OpenAI SDK dependency decision: NOT APPROVED.**

This packet does not install the SDK, add any package manifest entry, change
any lockfile, add credentials, perform API calls, or change runtime behavior.

## 1. Objective

Prepare a dependency review packet for a future decision on adding the OpenAI
Python SDK as a backend dependency. The packet evaluates supply-chain risk,
runtime risk, credential/security constraints, testing requirements, and CI
impact so that named reviewers can make an informed approval or denial decision.

This is evidence preparation only. It is not installation permission.

## 2. Non-Goals

This slice explicitly excludes:

- OpenAI SDK installation (`pip install openai` or equivalent).
- Any `pyproject.toml`, `requirements.txt`, `poetry.lock`, or lockfile change.
- SDK import in runtime code, tests, or scripts.
- Real OpenAI API calls.
- Provider credentials of any kind.
- `.env` files or committed credential values.
- WIF runtime implementation.
- Token exchange implementation.
- Live harness execution.
- Backend route changes or route behavior switches.
- API client method changes.
- SSE streaming implementation.
- Frontend, Expo, or UI work.
- Supabase/RLS work, SQL, migrations, or generated Supabase state.
- Any `.gitleaksignore` changes.

## 3. Current Baseline

- `docs/openai-sdk-adapter-plan.md` exists: future adapter boundary,
  injectable transport, credential constraints, and test strategy are planned.
- `FakeSummarizationProvider` is the only runtime-enabled provider.
- `apps/api/app/services/openai_provider.py` defines a network-free adapter
  boundary with injected transport. It imports no OpenAI SDK.
- `apps/api/app/core/config.py` fails closed for `ai_provider=openai` and all
  live auth modes.
- Live harness path: **CLOSED / BLOCKED UNTIL NAMED APPROVALS EXIST**
  (Slice 7L-G — 0 of 8 named reviewer approvals).
- **No OpenAI SDK dependency exists in the repository.**

## 4. Official Dependency Direction To Review Before Coding

A future implementer must review official OpenAI documentation before any
dependency decision is made. This packet does not reproduce official docs or
paste install commands as executable instructions.

| Topic | What to review |
|---|---|
| Official SDKs and libraries page | Confirm the current supported Python SDK name, current stable version, and official install path. |
| Server-side API key handling | Confirm that keys must be loaded server-side only, never committed, never logged, never sent to clients. |
| Responses API direction | OpenAI has indicated the Responses API is the direction for new projects. Confirm whether this changes the request shape required by the adapter. |
| Production best practices | Review guidance on project separation, spend limits, rate limits, and key rotation policy. |
| Changelog and release notes | Review the SDK changelog for the candidate version to identify breaking changes, removed features, or security advisories. |

No install commands, curl commands, or bearer token examples may be included
in docs or committed to the repository.

## 5. Candidate Dependency

| Field | Value |
|---|---|
| Package name | `openai` (Python SDK) |
| Candidate version | `TO_BE_SELECTED` — not yet chosen |
| Version constraint | `TO_BE_PINNED` — exact version or bounded range required |
| License | `TO_BE_REVIEWED` — must confirm OSI-compatible before approval |
| Security advisory status | `TO_BE_CHECKED` — must confirm no open critical CVEs |
| Changelog review | `TO_BE_REVIEWED` — must review since the version pinned in the plan |
| Transitive dependencies | `TO_BE_ENUMERATED` — must list and review each |

No placeholder above constitutes approval. Named reviewers must replace each
`TO_BE_*` field with actual verified values before any install is authorized.

## 6. Dependency Approval Gates

No SDK dependency installation may begin until all of the following are
approved and recorded:

| Gate | Required approver | Record location |
|---|---|---|
| Dependency owner approval | Named dependency owner | New dependency approval record (future slice) |
| Security/privacy approval | `TBD_SECURITY_PRIVACY_REVIEWER` | Evidence packet section 5.1 / new record |
| License approval | Named license reviewer | Dependency approval record |
| Supply-chain risk approval | Named supply-chain reviewer | Dependency approval record |
| CI/build impact approval | Named CI reviewer | Dependency approval record |
| Rollback plan approval | Named rollback owner | Dependency approval record |
| No-default-live-run confirmation | Named CI reviewer | Dependency approval record |
| External review gate | `TBD_EXTERNAL_REVIEWER` | Evidence packet section 5.8 / new record |

All gates must be recorded before `pip install openai` or any equivalent
dependency add is authorized. This packet does not satisfy any gate.

## 7. Supply-Chain Risk Checklist

A future dependency approval must address every item in this checklist:

| Item | Required evidence |
|---|---|
| Package source verification | Confirm package is from PyPI and matches the official OpenAI SDK repository. |
| Pinned version | Exact version or bounded range approved and pinned before install. |
| Lockfile impact | Lockfile diff reviewed and approved before merging. |
| Transitive dependencies | All transitive deps enumerated; each reviewed for license, security, and size. |
| Vulnerability scan | `pip-audit` or equivalent run against the candidate version; no open critical CVEs. |
| Update policy | Explicit policy for reviewing SDK updates before applying them. |
| Rollback path | Explicit step to remove the dependency if it must be reverted. |
| No unreviewed postinstall | Confirm no postinstall scripts run on `pip install openai`. |
| No broad dependency additions | Confirm only the minimum required packages are added. |

Any unchecked item blocks dependency approval.

## 8. Runtime Risk Checklist

A future SDK adapter implementation must address every item:

| Risk | Required mitigation |
|---|---|
| SDK import failure | Fail closed at provider construction; never propagate `ImportError` to routers. |
| Unsupported SDK version | Fail closed at config validation startup; log only coarse version metadata. |
| API shape drift | Validate SDK response shape before constructing any internal domain object. |
| Retry behavior | Bound retry attempts within approved `TO_BE_APPROVED_MAX_RETRIES` limit. |
| Timeout behavior | Bound request duration within approved `TO_BE_APPROVED_MAX_TIMEOUT` limit. |
| Streaming behavior | Deferred — SSE streaming implementation is out of scope until a separate approved slice. |
| Response shape validation | Reject unvalidated or malformed SDK responses before returning public responses. |
| Safe error mapping | Map all SDK errors to coarse public errors; never expose raw SDK error body. |
| No router SDK calls | Routers must never import or call the SDK directly. |

## 9. Credential/Security Checklist

The following constraints apply regardless of which approval decision is made:

| Constraint | Status |
|---|---|
| No committed credentials | Required — no key, token, or secret may be committed. |
| No `.env` commit | Required — `.env` files must remain gitignored. |
| No API key logging | Required — `OPENAI_API_KEY` or equivalent must never appear in logs. |
| No `Authorization` header logging | Required — raw auth header values must be redacted before logging. |
| No prompt/content logging | Required — note content, prompt text must not appear in logs. |
| No raw provider body logging | Required — raw SDK response body must not appear in logs. |
| API key mode not approved for production | Confirmed — local API-key candidate requires credential-mode reviewer sign-off per evidence packet section 5.3. |
| WIF preferred for CI/cloud | Confirmed — WIF is preferred where supported, but WIF runtime is not implemented and not approved. |
| Credential source outside git only | Required — any future credential must be stored in gitignored local env, local secret manager, or deployment platform secret manager. |

## 10. Testing Plan Before Dependency Approval

All tests must remain dependency-free until dependency approval exists:

| Test type | Approach |
|---|---|
| Default mocked interface tests | Continue to use injected fake transport; no SDK import required. |
| Future SDK adapter tests | Must use mocked SDK client (e.g., `unittest.mock`); never require real SDK install for test runs. |
| No live tests by default | Live tests are skipped unless explicit opt-in flags are set. |
| No credentials required | Tests must pass with no credentials present. |
| No-network proof | `socket.socket` patched at test level to block any accidental network attempt. |
| Malformed SDK response tests | Inject synthetic malformed response objects; confirm adapter rejects them. |
| SDK error redaction tests | Inject synthetic SDK errors; confirm redaction helper strips sensitive fields. |
| Import-unavailable tests | Confirm provider construction fails closed if SDK module is not importable. |

## 11. CI/Build Impact Checklist

A future dependency approval must address every item:

| Item | Required evidence |
|---|---|
| Install time impact | Measure `pip install` time impact on CI baseline. |
| Package size impact | Confirm total installed size (SDK + transitive deps) is acceptable. |
| Lockfile diff review | Lockfile changes reviewed and approved before merging. |
| Python version compatibility | Confirm SDK version supports all Python versions used in CI. |
| No default live tests | CI remains fake-only, credential-free, and network-free after dependency install. |
| No workflow secret changes | CI workflow files are not modified in the dependency install slice. |
| No `workflow_dispatch` live job | No live provider workflow job is added in this slice or the dependency install slice. |

## 12. Decision Status

**OpenAI SDK dependency decision: NOT APPROVED.**

| Item | Status |
|---|---|
| OpenAI SDK dependency install | NOT APPROVED |
| Runtime SDK import | NOT APPROVED |
| Credential or API call use | NOT APPROVED |
| Any `pyproject.toml` / lockfile change | NOT APPROVED |
| Live harness path | CLOSED / BLOCKED (0 of 8 live harness approvals) |

Approval requires named reviewer sign-off on every gate in section 6. No
placeholder, checklist, or planning document constitutes approval.

## 13. Future Slices

Recommended follow-up slices:

- **Slice 7M-B — Mocked SDK adapter interface tests without SDK dependency.**
  Add test coverage for the future adapter using only fake/mocked SDK clients
  (no real SDK install). *Recommended immediate next step.*
- **Slice 7M-C — SDK dependency approval or denial record.** Named reviewers
  complete every approval gate in section 6 and record their decision. Only
  after this record is complete may the dependency be installed.
- **Slice 7M-D — Optional SDK dependency install.** Only reachable after Slice
  7M-C records explicit named approval for every gate.
- **Slice 7N — Opt-in live provider harness skeleton.** Only reachable after
  all 8 live harness approvals exist and a separate implementation slice is
  approved. Not authorized by this packet.

Do not proceed to any of the above automatically.

## 14. Definition of Done

This slice is complete when:

- `docs/openai-sdk-dependency-review-packet.md` exists.
- Referenced docs are minimally updated to point to this packet.
- `docs/next-action.md` recommends Slice 7M-B.
- No runtime code, tests, SDK, credential, `.env` file, API call, token
  exchange, WIF runtime, backend route, API client method, SSE/frontend,
  Supabase, SQL, migration, lockfile, or generated state is added.
- Fake provider remains the default.
- Default CI remains fake-only and network-free.
- `.gitleaksignore` remains exact-fingerprint only.
- OpenAI SDK dependency decision remains NOT APPROVED.
- Verification passes or any blocked verification is explicitly reported.
