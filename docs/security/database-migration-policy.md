# Database Migration And Artifact Policy

## Status

This is an interim security gate. No executable Supabase migration is currently
approved for commit. Until an explicit policy change is reviewed and approved,
`supabase/migrations/*.sql` remains ignored.

## Current Posture

- Architecture documents may describe intended tables, ownership boundaries, and
  RLS outcomes as sanitized, non-deployable summaries.
- Planning work must not add executable migrations, generated database state, or
  environment-specific database artifacts.
- The repository being private does not make operational database artifacts safe
  to commit casually. Git history is durable and access can change over time.

## Prohibited Artifacts

Do not commit:

- live database dumps, production schema dumps, backups, snapshots, or exports;
- generated Supabase state, temporary runtime directories, or local metadata;
- `.env` files, connection strings, credentials, passwords, JWT secrets,
  service-role keys, refresh tokens, or access tokens;
- seed files containing real user, production, or otherwise sensitive data; or
- executable migration files before the approval gate below is completed.

## Future Migration Approval Gate

An executable migration may be introduced only after explicit approval for the
specific database change. Before commit, it must:

1. Be minimal and environment-independent, with no project identifiers,
   credentials, real data, or deployment-specific values.
2. Receive security review for privilege scope, RLS effects, data exposure,
   rollback considerations, and secret/data scanning.
3. Be accompanied by a clear execution and validation plan using synthetic data
   and an approved non-production environment first.
4. Change the ignore rule only as part of the explicitly approved migration
   review, not as a convenience during planning.

## Notes Design Handling

The intended Notes ownership and RLS behavior is documented in architecture
plans only. Those summaries are not a migration, have not been executed, and do
not authorize creation or deployment of database artifacts.

## Git History Posture

- Removed migration artifacts must not remain in `HEAD`.
- The removed Notes SQL draft contained no secrets, credentials, or production
  data; therefore this project will not rewrite Git history at this time.
- Historical removal requires explicit approval and coordination because it
  changes repository history for all collaborators.
- Reserve history rewriting for discovered secrets, credentials, production
  data, other sensitive exposure, or a reviewed cleanup before public release.
- Private repository status is not a substitute for review discipline or future
  public-release preparation.
