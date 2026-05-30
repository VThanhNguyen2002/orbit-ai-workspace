# Notes Local RLS Dry-Run Blocker Resolution

## 1. Objective

Slice 6H-3B-4C-B3 records a new blocker encountered during the B2 manual
setup attempt: `npx supabase start` failed during Docker image pull/inspect
from `public.ecr.aws`. The local Supabase stack did not start. Cleanup was
performed (`supabase stop --no-backup`). No SQL was executed.

This document now covers all known blockers from E, E2, and E3/B3 attempts.
The Docker startup failure must be fixed before any future dry-run can proceed.

This document defines the exact manual setup a human operator must complete
outside git before any future dry-run attempt. It does not execute SQL, create
SQL files, add migrations, start Supabase locally, connect to hosted Supabase,
run RLS validation, add credentials, use service-role request-path behavior,
enable live Notes persistence, change public Notes API behavior, or add any
runtime, package, or dependency.

The blocked attempts are recorded in
[notes-local-rls-dry-run-blocked-report.md](notes-local-rls-dry-run-blocked-report.md).
Any future attempt must follow
[notes-local-rls-dry-run-execution-runbook.md](notes-local-rls-dry-run-execution-runbook.md)
and stop at any failed preflight or stop condition.

## 2. Blocked Reasons Summary

### From E / E2 (Resolved In Part By B2 Manual Setup)

- ~~Supabase CLI not on PATH~~ — resolved: `npx supabase` 2.102.0 available.
- ~~`supabase init` not run~~ — resolved: `init` succeeded in
  `/tmp/synapse-supabase-dryrun`.
- All required env vars still absent (depends on running local stack).
- Synthetic users still absent (depends on running local stack).

### From E3 / B3 (Partially Addressed By B4)

- ~~`supabase start` Docker image pull failed~~ — images now pull successfully.
- Container startup: **failed due to disk full (ENOSPC)**.
- Root cause: Supabase images (~4.9 GB total) consumed all remaining free disk
  space on `/` during pull and container layer writes.
- `supabase stop --no-backup` also failed with ENOSPC during the B4 attempt.
- Cleanup: all Supabase images removed via `docker rmi` (~4.9 GB reclaimed).
- Disk after cleanup: ~3.9 GB free (86% used) — still insufficient for a
  successful `supabase start` (requires ~8–10 GB free headroom).
- All env vars, synthetic users, and tokens still absent.

Repository safety checks all passed (clean working tree, no tracked `.env`,
`.sql`, `supabase/migrations/*`; `SUPABASE_SERVICE_ROLE_KEY` absent; no
`node-actionlint` in manifests; `.codegraph/` already gitignored).

No operator should retry the dry-run until the Docker startup failure is fixed
and each missing item is resolved outside git.

## 3. Local-Only Target Requirements

An acceptable target must satisfy every requirement below:

- The target is a disposable local Supabase project only. It must not be
  hosted, staging, production, shared QA, or any other persistent remote
  Supabase project.
- The target contains no real users, real emails, real Notes rows, imported
  production data, staging data, dumps, backups, snapshots, or realistic
  personal content.
- The target uses only synthetic users and synthetic Notes rows prepared for
  the dry-run.
- Request-path validation does not require or use service-role credentials.
- Cleanup or full disposal/reset is possible before, during, and after
  execution.

If locality, data safety, request-path credential boundaries, or cleanup
cannot be proven, the target is not ready.

## 4. Manual Setup Sequence (Operator Only, Outside Git)

Complete the following steps in a local shell. Do not commit any file produced
by this setup.

### Step 1 — Install Supabase CLI

Install the Supabase CLI using your platform package manager or npm:

```text
npm install -g supabase
# or: brew install supabase/tap/supabase  (macOS)
# or: see https://supabase.com/docs/guides/cli
```

Confirm installation:

```text
supabase --version
```

### Step 2 — Initialize And Start A Disposable Local Project

In a temporary directory outside this git repository:

```text
mkdir /tmp/synapse-rls-local && cd /tmp/synapse-rls-local
supabase init
supabase start
```

Record the output anon/publishable key and API URL. Do not commit them.
Confirm the project is local-only (URL matches `http://127.0.0.1:<port>`).

### Step 3 — Confirm No Real Data

The freshly started local project contains no real users or Notes rows by
design. Confirm this is a fresh local instance, not a project restored from a
dump, backup, snapshot, or production data export.

### Step 4 — Create Synthetic Users A And B

Use the Supabase Dashboard UI at `http://127.0.0.1:<studio-port>` or the
local CLI to create two disposable synthetic users:

- Synthetic user A: use a placeholder email such as
  `synapse-test-user-a@local.invalid`.
- Synthetic user B: use a placeholder email such as
  `synapse-test-user-b@local.invalid`.

Obtain short-lived access tokens for each user by exchanging credentials
against the local Auth endpoint. Keep tokens in the shell only. Do not
commit them.

### Step 5 — Set Required Environment Variables (Local Shell Only)

Export values into the shell that will run the harness. Do not write these
to any committed file:

```text
export SYNAPSE_SUPABASE_INTEGRATION_TESTS=1
export SYNAPSE_SUPABASE_TEST_MODE=local
export SUPABASE_URL='<local-api-url-from-step-2>'
export SUPABASE_PUBLISHABLE_KEY='<local-anon-key-from-step-2>'
export SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN='<user-a-token>'
export SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN='<user-b-token>'
unset SUPABASE_SERVICE_ROLE_KEY
```

Acceptable alternatives:

- Write to a gitignored local file (e.g. `apps/api/.env.local`) and source it.
  Confirm the file path is covered by `.gitignore` before writing.
- Use an approved local secret store.

Do not write values to any tracked file. Do not print raw values to logs,
screenshots, evidence docs, or terminal sessions that persist.

### Step 6 — Verify Presence Without Printing Values

Run this check to confirm all required names are set:

```text
python3 - <<'PY'
import os
required = (
    "SYNAPSE_SUPABASE_INTEGRATION_TESTS",
    "SYNAPSE_SUPABASE_TEST_MODE",
    "SUPABASE_URL",
    "SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN",
    "SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN",
)
public_key_names = ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY")
for name in required:
    print(f"{name}: {'set' if os.getenv(name) else 'missing'}")
print("public key:", "set" if any(os.getenv(n) for n in public_key_names) else "missing")
print("SUPABASE_SERVICE_ROLE_KEY:", "set - STOP" if os.getenv("SUPABASE_SERVICE_ROLE_KEY") else "absent")
PY
```

Expected output: all required names show `set`, public key shows `set`,
SERVICE_ROLE_KEY shows `absent`. No raw values are printed.

### Step 7 — Prepare Cleanup Plan

Before running the dry-run, confirm you can clean up:

- Synthetic Notes rows: delete via owner-scoped API, deterministic synthetic
  prefix predicates, or full local project disposal (`supabase stop --no-backup`
  in the project directory).
- Synthetic Auth users: remove via Dashboard UI or CLI, or dispose the
  entire local project.
- Local shell values: `unset` all exported env vars after the run.
- Gitignored local env file: delete or scrub after the run.

If cleanup cannot be guaranteed before execution starts, do not proceed.

### Step 8 — Confirm Redacted Evidence Location

Choose a location to capture evidence that is either gitignored or outside
the git repository. The location must not accept raw keys, tokens, Auth
payloads, emails, user identifiers, note identifiers, or note content.
Acceptable content: coarse pass/fail/skip, synthetic user labels
(e.g. `user-a`, `user-b`), synthetic prefixes, coarse cleanup counts,
run date.

## 5. Required Env Shape (Names Only)

| Env Var Name | Required | Source |
|---|---|---|
| `SYNAPSE_SUPABASE_INTEGRATION_TESTS` | yes, must be `1` | local shell / gitignored file |
| `SYNAPSE_SUPABASE_TEST_MODE` | yes, must be `local` | local shell / gitignored file |
| `SUPABASE_URL` | yes | local shell / gitignored file |
| `SUPABASE_PUBLISHABLE_KEY` | one of these two | local shell / gitignored file |
| `SUPABASE_ANON_KEY` | one of these two | local shell / gitignored file |
| `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` | yes | local shell / gitignored file |
| `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN` | yes | local shell / gitignored file |
| `SUPABASE_SERVICE_ROLE_KEY` | **must be absent** | must not be set |

## 6. Synthetic User And Data Requirements

Synthetic user requirements:

- Use disposable local-only accounts or local-only placeholder aliases.
- Do not use real emails unless they are disposable aliases created solely for
  the local target.
- Do not include raw emails, user ids, Auth payloads, refresh tokens, or access
  tokens in evidence.
- Use pseudonyms (`user-a`, `user-b`) throughout evidence and logs.

Synthetic Notes requirements:

- Use synthetic Notes rows only.
- Use a deterministic test prefix such as
  `synapse-live-harness-<user-label>-<run-id>`.
- Keep the run id non-sensitive and compatible with the harness `_SAFE_COMPONENT_RE`
  pattern (`^[a-z0-9][a-z0-9_-]{0,63}$`).
- Do not print note content in logs, evidence, screenshots, or docs.
- Ensure all rows can be cleaned by owner-scoped predicates, deterministic
  synthetic prefixes, or full local project disposal.

## 7. Cleanup Proof Requirements

Cleanup must be provable before execution starts:

- Synthetic Notes rows: owner-scoped cleanup, synthetic prefix predicates, or
  local project disposal (`supabase stop --no-backup`).
- Synthetic Auth users: Dashboard/CLI removal or local project disposal.
- Local env values: `unset` all exported vars or delete the gitignored local
  env file.
- Temporary logs and evidence captures: stored only in gitignored or
  out-of-repo locations.
- Post-run git hygiene: `git status --short` confirms no `.env`, `.sql`,
  `supabase/migrations/*`, generated Supabase state, credential, or sensitive
  evidence artifact is staged.

## 8. Redacted Evidence Requirements

After the dry-run (if executed), create or update
`docs/notes-local-rls-dry-run-evidence.md` using the template in the runbook.
The evidence must include only:

- run date;
- local-only environment confirmation;
- artifact path and commit/blob SHA;
- harness mode (`local`);
- synthetic user aliases only, no raw IDs, emails, or tokens;
- RLS matrix results (pass/fail/skip, no raw response bodies);
- cleanup result (coarse counts only);
- redaction confirmation;
- no service-role request-path confirmation; and
- no staged artifact confirmation.

## 9. Local Tooling Notes

These tools are local-only. None should be added as a repo dependency.

| Tool | Correct Usage | Do Not |
|---|---|---|
| `supabase` CLI | Install globally or via platform package; use outside this git repo for dry-run setup | Add to `package.json` / `pnpm-lock.yaml` |
| `node-actionlint` | Run via `pnpm dlx node-actionlint .github/workflows/ci.yml` | Add as a repo dependency |
| `gitleaks` | Run as local binary: `gitleaks detect --source=. --redact` | Add to `package.json` |
| `CodeGraph` | Local-only code discovery; `.codegraph/` is already gitignored | Commit `.codegraph/` contents |
| `MarkItDown` | Local-only trusted doc conversion | Add to server/runtime dependencies |

## 10. Stop Conditions

Stop immediately and do not execute the dry-run if any of these occur:

- Hosted, staging, production, shared QA, or any non-disposable target is
  detected.
- Real data, real users, real emails, real Notes content, production data,
  staging data, imports, dumps, backups, snapshots, or realistic personal
  content are detected.
- Service-role credentials are required for request-path behavior.
- Cleanup cannot be guaranteed before execution starts.
- Secrets, tokens, authorization headers, Auth payloads, URLs with secrets,
  emails, raw user identifiers, note identifiers, note content, or local env
  values would be printed, shared, captured, or committed.
- SQL differs from the reviewed Markdown artifact without separate approval.
- Any `.env`, `.sql`, `supabase/migrations/*`, generated Supabase state, dump,
  backup, snapshot, database file, credential, or sensitive evidence artifact
  would be staged or committed.
- Default CI would need to set live/local Supabase harness values.

## 11. Preflight Checklist For Next Attempt (Slice 6H-3B-4C-E3)

Before retrying, confirm all items below:

- [ ] Working tree is clean (`git status --short` prints nothing).
- [ ] No `.env` or `.env.*` file is staged or tracked.
- [ ] No `.sql` file is staged or tracked.
- [ ] No `supabase/migrations/*` file is staged or tracked.
- [ ] No generated Supabase state, dump, backup, snapshot, or database file is
      staged.
- [ ] `node-actionlint` is absent from `package.json` and `pnpm-lock.yaml`.
- [ ] Supabase CLI is installed and confirms a running local project
      (`supabase status` returns a local URL, not hosted/staging/production).
- [ ] The target is confirmed as disposable local Supabase only.
- [ ] The target contains no real users, real data, staging data, production
      data, imports, dumps, backups, snapshots, or realistic personal content.
- [ ] `SYNAPSE_SUPABASE_INTEGRATION_TESTS=1` is present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_MODE=local` is present locally only.
- [ ] `SUPABASE_URL` is present locally only and points to the disposable local
      target (URL begins with `http://127.0.0.1`).
- [ ] `SUPABASE_PUBLISHABLE_KEY` or reviewed legacy `SUPABASE_ANON_KEY` is
      present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_USER_A_ACCESS_TOKEN` is present locally only.
- [ ] `SYNAPSE_SUPABASE_TEST_USER_B_ACCESS_TOKEN` is present locally only.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is absent.
- [ ] Synthetic user A and synthetic user B are ready.
- [ ] Synthetic Notes data can be created and cleaned up.
- [ ] Cleanup is actionable: Notes rows, Auth users, local env values, and
      generated local state.
- [ ] Redacted evidence capture destination is ready and will not include raw
      values.
- [ ] The reviewed Markdown artifact identity is unchanged from the recorded
      blob SHA `8376735329234cf4838d6344b5a0757fdeeb8828`.

## 12. Definition Of Ready

Slice 6H-3B-4C-E3 may be attempted only when:

- every blocked reason in section 2 is resolved locally outside git;
- the manual setup sequence in section 4 is fully completed;
- the preflight checklist in section 11 is confirmed without printing raw
  values;
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

Recommended next task: **Slice 6H-3B-4C-B4 — Troubleshoot local Supabase
Docker startup**.

Only re-attempt the dry-run after the Docker startup blocker in section 13 is
resolved and this full checklist is satisfied locally. Do not execute
automatically because this document exists, the approval record exists, or the
runbook exists.

## 13. Docker / Supabase Local Start Troubleshooting

`supabase start` pulls images from `public.ecr.aws`. If that step fails, the
local stack cannot start and no API URL or keys can be obtained. All of the
following must be confirmed outside git before retrying `supabase start`.

### Check Docker Daemon

```text
docker info
```

Expected: docker daemon running, no error. If not running, start Docker Desktop
or the Docker daemon for your platform.

### Check Disk Space

```text
df -h
docker system df
```

Supabase images total approximately 4.9 GB. The full local stack (images plus
container layer writes) requires ample free space. **Minimum recommended free
space before retrying: 8–10 GB on `/`**.

**B4 confirmed root cause: ENOSPC.** Images pulled successfully but container
startup wrote layers that exhausted the disk. All Supabase images were
removed post-B4 to recover ~4.9 GB.

#### Free Disk Space Before Retrying

Check what is consuming space:

```text
du -sh /var/log/* /tmp/* /home/vietthanh/.npm /home/vietthanh/.cache 2>/dev/null | sort -rh | head -20
```

Then free space using one or more of:

```text
# Remove npm cache (safe, will be rebuilt):
npm cache clean --force

# Remove apt caches:
sudo apt-get clean

# Remove Docker build cache and unused images (confirm none are needed):
docker system prune -f
docker image prune -a -f

# Remove large unneded files in /tmp:
rm -rf /tmp/synapse-supabase-dryrun
mkdir /tmp/synapse-supabase-dryrun
cd /tmp/synapse-supabase-dryrun && npx supabase init
```

Verify at least 8 GB free before retrying:

```text
df -h /
```

### Check Registry / Network Access

```text
curl -I https://public.ecr.aws/v2/
```

Expected: HTTP 200 or 401 (registry reachable). If connection fails or times
out, troubleshoot DNS, firewall, proxy, or VPN settings. Do not paste the full
output of `supabase status` into docs or evidence if it contains API keys or
JWT secrets.

### Retry Outside Repo

Retry only in `/tmp/synapse-supabase-dryrun` or another temporary directory
outside this git repository:

```text
cd /tmp/synapse-supabase-dryrun
npx supabase start
```

Confirm the local URL begins with `http://127.0.0.1`. Do not commit any file
produced by this step.

### Redaction Rule

Never paste raw `supabase status` output into committed docs, evidence files,
screenshots, or pull-request comments. That output contains the `anon` key,
`service_role` key, and other secrets. Record only the presence/absence of a
local URL and truncated port number.

### After Successful Start

Once `supabase start` succeeds:

1. Note the local API URL and anon key in your local shell only.
2. Continue with the manual setup sequence in section 4, starting at step 4
   (create synthetic users).
3. Do not commit the URL or key.
4. Do not paste the full `supabase status` output anywhere.

## 14. B4 / B4-D Troubleshooting Summary

Date: 2026-05-30

### B4 — Docker Startup Attempt

| Check | Result |
|---|---|
| Docker daemon | Running (v29.1.3, 7.7 GiB RAM, overlayfs) |
| Registry `public.ecr.aws` | Reachable (HTTP 401 — normal) |
| Disk before retry | 87% full, ~3.8 GB free |
| Image pull | **Succeeded** (all images downloaded) |
| Container startup | **Failed** — `error running container: exit 1` |
| `supabase stop` | **Failed** — `ENOSPC: no space left on device` |
| Disk after retry | **100% full**, 0 bytes free |
| Root cause | **Disk exhausted** during image pull + container layer writes |

### B4-D — Post-Cleanup State

| Cleanup Action | Result |
|---|---|
| Supabase images removed (`docker rmi`) | ~4.9 GB reclaimed |
| Snap cache cleared (`/var/lib/snapd/cache`) | 3.7 GB → 4 KB reclaimed |
| Disk after all cleanup | ~7.2–7.3 GB free (74% used) |
| Safe retry threshold | ≥10 GB free (minimum 8 GB) |
| Retry blocked | **Yes** — below threshold |
| No Supabase containers remain | Confirmed |
| No raw secrets pasted | Confirmed |

Next recommended task: **Slice 6H-3B-4C-P** — pause local Supabase validation
until disk is expanded or sufficient space is freed.
