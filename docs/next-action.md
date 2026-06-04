# Next Action

## Objective

Recommended next task: **Slice 8F — Dependency-free demo walkthrough/runbook for the fake-provider note detail flow**.

Create a concise demo runbook that shows the backend-only product flow now supported by Slice 8E:

1. Create or fetch a note through the existing notes endpoints.
2. List empty summary history for that note.
3. Generate one or more fake summaries.
4. List generated summaries newest first.
5. Confirm the response/log surfaces avoid prompt text, raw diagnostics, raw note content, placeholder key names, bearer-like values, and token-like strings.

Keep the work dependency-free and backend/fake-provider-only.

## Slice 8E Result

Slice 8E completed backend/product demo polish using the existing fake-provider flow:

- Summary history now lists generated fake summaries newest first.
- Backend tests cover note detail fetch, empty history, repeated fake summary generation, newest-first listing, and AI surface/log redaction.
- `apps/mobile/src/features/notes/summaryHistoryApi.ts` can list summaries and request fake summary generation through the injected API boundary.
- `apps/mobile/src/features/notes/summaryHistoryViewState.ts` models `summarizing`, append, dedupe, newest-first ordering, and safe error states without rendered UI.
- `docs/backend-product-demo-polish-record.md` records the Slice 8E result.

## Slice 8F Gate

- Do not install dependencies, modify package manifests, or modify lockfiles.
- Do not initialize Expo, React Native runtime UI, routers, or native files.
- Do not introduce a live provider, OpenAI SDK, credentials, `.env`, WIF runtime, SSE streaming, SQL, migrations, Supabase state, Docker work, or generated state.
- Use only the existing fake-provider endpoints and memory-only backend state.

## Definition Of Done

- The runbook documents the exact backend demo sequence and expected response shapes.
- The runbook names the memory-only reset limitation.
- The runbook includes verification commands that remain safe for local/CI use.
- Security/privacy constraints remain unchanged and fast checks pass.
