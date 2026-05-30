# Notes Local RLS Dry-Run Blocker Resolution

## 1. Objective

Slice 6H-3B-4C-B resolves the missing setup preconditions that blocked the
first local-only Notes RLS dry-run attempt at planning and documentation level.

This document defines the exact local-only checklist and the evidence that must
exist before another dry-run attempt. It does not execute SQL, create SQL
files, add migrations, start Supabase locally, connect to hosted Supabase, run
RLS validation, add credentials, use service-role request-path behavior, enable
live Notes persistence, or change public Notes API behavior.

The blocked attempt is recorded in
[notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md).
The next attempt must still follow
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
and stop at any failed preflight or stop condition.

## 2. Current Blocked Reasons

The first dry-run attempt stopped before execution because all of the following
preconditions were missing or unproven:

- missing `SYNAPSE_SUPABASE_INTEGRATION_TESTS`;
- missing `SYNAPSE_SUPABASE_TEST_MODE`;
- missing `SUPABASE_URL`;
- missing public key source through `SUPABASE_PUBLISHABLE_KEY` or reviewed
  legacy `SUPABASE_ANON_KEY`;
- missing synthetic user A and user B token sources through
  `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` and
  `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN`;
- missing confirmed disposable local target;
- missing synthetic users and synthetic Notes data; and
- missing actionable cleanup proof.

No operator should retry the dry-run until each item has been resolved outside
git and can be verified without printing raw values.

## 3. Local-Only Target Requirements

An acceptable target must satisfy every requirement below:

- The target is a disposable local Supabase project only.
- The target is not hosted, staging, production, shared QA, or any other
  persistent remote Supabase project.
- The target contains no real users, real emails, real Notes rows, imported
  production data, staging data, dumps, backups, snapshots, or realistic
  personal content.
- The target uses only synthetic users and synthetic Notes rows prepared for
  the dry-run.
- Request-path validation does not require or use service-role credentials.
- Cleanup or full disposal/reset is possible before execution starts.

If locality, data safety, request-path credential boundaries, or cleanup cannot
be proven, the target is not ready.

## 4. Local Env Setup Rules

The next attempt may use these placeholder-only environment names:

```text
SYNAPSE_SUPABASE_INTEGRATION_TESTS=1
SYNAPSE_SUPABASE_TEST_MODE=local
SUPABASE_URL=<disposable-local-supabase-url>
SUPABASE_PUBLISHABLE_KEY=<local-public-publishable-key>
SUPABASE_ANON_KEY=<reviewed-legacy-public-anon-key-fallback>
SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN=<synthetic-user-a-token>
SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN=<synthetic-user-b-token>
```

Use either `SUPABASE_PUBLISHABLE_KEY` or the deliberately reviewed legacy
`SUPABASE_ANON_KEY` fallback. Do not require both.

Rules:

- Real values belong only in an ignored local environment file, local shell, or
  approved secret store.
- Never commit `.env` files or copied shell transcripts containing real values.
- Never print raw URLs, keys, access tokens, authorization headers, Auth
  payloads, user identifiers, note identifiers, emails, or note content.
- Never include token values in evidence.
- Never set `SUPABASE_SERVICE_ROLE_KEY` for request-path harness validation.
- Clear temporary local shell values or scrub temporary ignored local files
  after the attempt.

## 5. Synthetic User/Data Requirements

The dry-run may use only synthetic user A and synthetic user B.

Synthetic user requirements:

- Use disposable local-only accounts or local-only aliases.
- Do not use real emails unless they are disposable aliases created solely for
  the local target.
- Do not include raw emails, user ids, Auth payloads, refresh tokens, or access
  tokens in evidence.

Synthetic Notes requirements:

- Use synthetic Notes rows only.
- Use a deterministic test prefix such as
  `synapse-live-harness-<user-label>-<run-id>`.
- Keep the run id non-sensitive and compatible with the harness safe-component
  rules.
- Do not print note content in logs, evidence, screenshots, or docs.
- Ensure all rows can be cleaned by owner-scoped predicates, deterministic
  synthetic prefixes, or full local project disposal/reset.

## 6. Cleanup Proof Requirements

Before execution, the operator must be able to prove each cleanup path without
revealing secrets or real data:

- the synthetic note cleanup path, using owner-scoped cleanup, deterministic
  synthetic prefixes, or local project disposal/reset;
- the synthetic Auth user cleanup path, or a full disposable local project
  disposal/reset path;
- the local environment cleanup path for shell values, ignored local env files,
  temporary logs, and evidence captures;
- the post-run git hygiene path proving no `.env`, `.sql`,
  `supabase/migrations/*`, generated Supabase state, credential, or sensitive
  evidence artifact is staged; and
- the redacted evidence output location, with an explicit rule that it contains
  only coarse pass/fail/skip results, pseudonyms, synthetic prefixes, and
  coarse cleanup counts.

If cleanup proof depends on an unreviewed admin or service-role request path,
the dry-run must stop until that setup path is separately reviewed and kept
outside request-path validation.

## 7. Preflight Checklist For Next Attempt

Before retrying Slice 6H-3B-4C-E, confirm all of the following:

- [ ] Working tree is clean.
- [ ] No `.env` or `.env.*` file is staged or tracked.
- [ ] No `.sql` file is staged.
- [ ] No `supabase/migrations/*` file is staged.
- [ ] No generated Supabase state, dump, backup, snapshot, database file, or
      local runtime artifact is staged.
- [ ] The target is confirmed as disposable local Supabase only.
- [ ] The target contains no real users, real data, staging data, production
      data, imports, dumps, backups, snapshots, or realistic personal content.
- [ ] `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` is present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_MODE=local` is present locally only.
- [ ] `SUPABASE_URL` is present locally only and points to the disposable local
      target.
- [ ] `SUPABASE_PUBLISHABLE_KEY` or reviewed legacy `SUPABASE_ANON_KEY` is
      present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` is present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN` is present locally only.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is absent from request-path harness
      configuration.
- [ ] Synthetic user A, synthetic user B, and synthetic Notes data are ready.
- [ ] Cleanup is actionable for Notes rows, Auth users, local env values, and
      generated local state.
- [ ] Redacted evidence capture is ready and will not include raw values.
- [ ] The reviewed Markdown artifact identity is unchanged, or separate review
      has approved any change before execution.

## 8. Stop Conditions

Stop immediately and do not execute the dry-run if any of these occur:

- hosted, staging, production, shared QA, or any non-disposable target is
  detected;
- real data, real users, real emails, real Notes content, production data,
  staging data, imports, dumps, backups, snapshots, or realistic personal
  content are detected;
- service-role credentials are required for request-path behavior;
- cleanup cannot be guaranteed before execution starts;
- secrets, tokens, authorization headers, Auth payloads, URLs with secrets,
  emails, raw user identifiers, note identifiers, note content, or local env
  values would be printed, shared, captured, or committed;
- SQL differs from the reviewed Markdown artifact without separate approval;
- any `.env`, `.sql`, `supabase/migrations/*`, generated Supabase state, dump,
  backup, snapshot, database file, credential, or sensitive evidence artifact
  would be staged or committed; or
- default CI would need to set live/local Supabase harness values.

## 9. Definition Of Ready

Slice 6H-3B-4C-E may be re-attempted only when:

- every blocked reason in this document is resolved locally outside git;
- the disposable local target is confirmed and contains only synthetic users
  and synthetic Notes data;
- all required local env names are present without printing or committing raw
  values;
- service-role request-path usage is absent;
- cleanup proof exists for synthetic Notes rows, synthetic Auth users or full
  project disposal, local env values, and generated local state;
- the reviewed Markdown artifact identity is known and unchanged, or any
  change has separate approval;
- redacted evidence capture is ready; and
- final preflight git hygiene confirms no prohibited artifact is staged.

Recommended next task: **Slice 6H-3B-4C-E2 - Re-attempt local-only RLS
dry-run**.

Only re-attempt after this blocker-resolution checklist is satisfied locally.
Do not execute automatically because this document exists, the approval record
exists, or the runbook exists.
