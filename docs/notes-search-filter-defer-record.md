# Notes Search / Filter Defer Record

**Slice:** 10A-R
**Date:** 2026-06-08
**Status:** Deferred
**Decision:** Do not implement Notes search/filter now.

## Decision Summary

Notes search/filter is deferred. The current Notes API already has enough list
controls for the portfolio demo, and adding text search now would create broad
cross-layer churn for a small demo gain.

The repository should stay in portfolio/review mode unless a new product goal is
explicitly chosen.

## Existing Note List Capabilities

`GET /v1/notes` already supports:

- pagination via `page` and `per_page`
- sorting via `sort` and `order`
- archive filtering via `is_archived`
- deleted-note inclusion via `include_deleted`

These capabilities are already represented across the backend route,
repositories, shared contracts, API client, and mobile list query plumbing.

## Why Not `/search`

The `/search` router is mounted, but it is empty. Using it for this slice would
imply a new product surface and a new search system rather than extending an
existing implemented path.

That would be larger than the current portfolio/review need, especially while
OpenAI, embeddings, vector search, Supabase persistence, and rendered mobile UI
remain out of scope.

## Why Not `q` Now

Adding a `q` text query to `GET /v1/notes` would require coordinated changes
across:

- backend route, service, repository protocol, and repository implementations
- shared Zod contracts and schema registry validation
- API client query serialization and tests
- backend route/repository tests
- possible demo and documentation updates

The implementation would still be limited to a dependency-free substring filter.
There is no rendered UI, no production persistence, and no search index. The
portfolio/demo value is therefore modest, while the contract and test churn is
broad.

## Future Reopen Criteria

Reopen this decision only when there is:

- a real UX need for users to find notes by text or filter state
- an approved API contract change
- clear demo value that improves the portfolio story
- a planned test path across backend, shared contracts, and API client
- explicit approval before adding OpenAI, embeddings, vector search, indexing,
  Supabase persistence, or any external service

## Current Recommendation

Pause feature work and use the current repository for portfolio/release review.
Do not open OpenAI, Supabase/RLS, Docker, Expo/React Native, rendered UI, SQL, or
migration gates as part of this decision.

Next recommended task:

> Pause feature work — use current repo for portfolio/review.

If development resumes later, start only after a new product goal is explicitly
chosen.
