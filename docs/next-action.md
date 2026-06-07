# Next Action

## Objective

Recommended next task: **Slice 8P — Demo script validation / README walkthrough
alignment**.

Slice 8O is complete: the repository now has a dependency-free local API demo
script for the current fake-provider flow, plus matching README and demo docs.
Do not proceed to Slice 8P automatically.

See
[`docs/rendered-mobile-demo-unblock-decision-packet.md`](rendered-mobile-demo-unblock-decision-packet.md)
for the rendered mobile gate status. See
[`docs/api-demo-walkthrough.md`](api-demo-walkthrough.md) for the API-level demo
script and mobile view-state surface.

## Slice 8O Result

Slice 8O adds `scripts/demo-api.sh`, a local-only API walkthrough script that
exercises the current backend fake-provider demo flow.

Changes:

- `scripts/demo-api.sh` — dependency-free `bash` script using `curl` and
  `python3`; defaults to `http://127.0.0.1:8000`; refuses non-local URLs.
- `README.md` — demo section now points to the script after local backend
  startup.
- `docs/api-demo-walkthrough.md` — scripted demo instructions, behavior, and
  syntax check added.
- `docs/backend-product-demo-polish-record.md` — Slice 8O result recorded.
- `docs/security/privacy-and-data-handling.md` — script security boundary
  recorded.
- `docs/next-action.md` — updated to Slice 8O result and Slice 8P next task.

Script behavior:

- health check
- synthetic note create
- note list
- note detail
- empty summary history
- fake summarize
- summary history list
- fake summarize again
- final newest-first append verification

Auth/demo assumptions:

- Uses the backend's default local `dev` auth mode.
- Sends no auth header and uses no credential example.
- Requires the backend to be running locally with
  `SYNAPSE_AI_SUMMARIZATION_ENABLED=true`.
- Stops clearly if the backend is unreachable, AI is disabled, or local dev
  auth is not active.

## Slice 8P Candidate

Validate the scripted walkthrough against a clean local backend start and align
README/docs wording if the observed terminal transcript suggests clearer
instructions. Keep this dependency-free and local-only.

## Slice 8P Gate

- Do not install dependencies, modify package manifests, or modify lockfiles.
- Do not initialize Expo, React Native runtime UI, routers, native files, JSX,
  or TSX.
- Do not introduce a live provider, OpenAI SDK, credentials, `.env`, WIF
  runtime, SSE streaming, SQL, migrations, Supabase state, Docker work, or
  generated state.
- Do not call external network services from the demo script.
- If rendered mobile demo work is reconsidered, first satisfy the approval
  gates in `docs/rendered-mobile-demo-unblock-decision-packet.md`.

## Definition Of Done

- Demo script behavior and docs remain aligned.
- All targeted checks pass.
- No dependency, lockfile, rendered UI, live provider, credential, SQL,
  migration, Supabase, Docker, or production persistence change is made.
- Fake-provider-only demo constraints remain unchanged.
- Security/privacy constraints remain unchanged.
