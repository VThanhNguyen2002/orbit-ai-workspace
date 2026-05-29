# Notes Migration/RLS Draft Review Packet

## Status

Slice 6H-3B-4A prepares the security review packet for a future Notes
table/RLS migration. This packet is sanitized, non-executable documentation
only. It does not approve, add, or apply SQL.

The next implementation slice is **Slice 6H-3B-4B - Approved local-only
migration artifact**, but that slice must not start until this review packet is
accepted and the required approvals are recorded.

## 1. Objective

Provide reviewers with the proposed Notes table and RLS behavior for a future
migration artifact before any executable SQL exists in the repository.

The packet should let engineering and security/privacy reviewers decide whether
the future artifact is safe to draft, approve, and validate in a local-only
environment with synthetic data.

This is not executable SQL, not a migration, and not permission to commit a
database artifact.

## 2. Non-Goals

- Do not commit SQL.
- Do not add Supabase migration files.
- Do not apply migrations.
- Do not run Supabase locally.
- Do not connect to hosted Supabase.
- Do not validate live RLS.
- Do not add real credentials, `.env` files, tokens, keys, or connection
  strings.
- Do not change runtime code, tests, repository wiring, SDK adapters, or
  settings.
- Do not change public Notes API behavior or shared contract behavior.
- Do not add service-role use to any Notes request path.
- Do not add frontend/UI, Expo, AI, or offline sync behavior.

## 3. Current Source-Of-Truth Contracts

Current Notes behavior is defined by the backend Pydantic models in
`apps/api/app/schemas/notes.py`, the shared Zod contracts in
`packages/shared/src/domain/index.ts`, and the existing Notes repository
contract.

Current shared/backend Note fields in prose:

- `id`: stable note identifier. Shared Zod uses the shared entity-id shape;
  backend Pydantic currently validates only a non-empty string.
- `user_id`: authenticated owner identifier. It must come from the auth context
  in API/repository calls, not from client create/update input.
- `title`: required note title, bounded by the current contract.
- `content`: note body text, bounded by the current contract and allowed to be
  empty on create through the default.
- `content_type`: current content format, either plain text or markdown.
- `is_archived`: archive state controlled by create defaults and update input.
- `created_at`: server-set creation timestamp. Shared Zod models this as an ISO
  timestamp; backend Pydantic currently validates a non-empty string.
- `updated_at`: server-set update timestamp. Shared Zod models this as an ISO
  timestamp; backend Pydantic currently validates a non-empty string.
- `deleted_at`: nullable soft-delete timestamp.
- `is_deleted`: soft-delete flag in both shared and backend note models.
- `version`: non-negative optimistic concurrency counter.
- `sync_metadata`: optional field in the shared Zod Note contract. The current
  backend Pydantic Note model does not include or emit this field, and the
  contract drift guard explicitly treats it as a shared optional extension.

Important contract differences:

- Shared Zod contracts are stricter about entity-id and timestamp formats than
  the current backend Pydantic models.
- Shared `sync_metadata` is optional and currently not emitted by backend Notes
  routes.
- Shared request defaults can appear as required in generated JSON Schema, while
  runtime parsing and backend inputs allow omission and apply defaults.
- This packet must preserve current public API behavior; format tightening or
  server-emitted `sync_metadata` would require separate contract review.

## 4. Proposed Table Design

This section is sanitized prose only and must not be copied into an executable
SQL file.

Proposed future Notes persistence shape:

- Primary key concept: every note has one stable server identifier suitable for
  lookup, sorting tie-breakers, conflict responses, and client references.
- Owner field: every note stores one authenticated owner identifier. The owner
  is derived from the verified caller context and must be the basis for
  application predicates and RLS ownership checks.
- Text fields: title and content store user-authored note text; content type
  stores the current plain/markdown format.
- Archive field: archive state remains mutable by the owner and defaults to not
  archived on create.
- Timestamp fields: creation and update timestamps are server-selected; deleted
  timestamp is nullable and set only on soft delete.
- Soft-delete fields: `is_deleted` marks request-path deletion, while
  `deleted_at` records when the soft delete occurred.
- Version field: version starts at the server-selected initial value and
  increments on owner-scoped update and soft delete.
- Sync metadata field: initial migration review should decide whether this is
  omitted from the physical server table, because the current backend does not
  emit it. If a future approved artifact includes server-side sync metadata, it
  must remain optional, owner-scoped, non-sensitive, and compatible with the
  shared optional contract.
- Indexing intent: future indexes should support owner-scoped list/get/update
  flows, default non-deleted filtering, archive filtering, deterministic
  ordering by requested sort plus identifier tie-breaker, and version-gated
  writes. Indexing must not create any public read path or cross-user access.

## 5. Proposed RLS Behavior

This section is sanitized prose only and must not be copied into an executable
SQL policy statement.

Required future RLS behavior:

- SELECT own notes only: authenticated callers can read only rows whose owner
  matches their authenticated identity.
- INSERT own notes only: authenticated callers can insert only rows owned by
  their authenticated identity. Attempts to spoof another owner must fail.
- UPDATE own notes only: authenticated callers can update only rows they own.
- Soft delete as owner-scoped update: the public Notes delete path remains an
  update that marks the owner row deleted and advances version/timestamps.
- No request-path physical delete: public Notes CRUD must not physically remove
  rows.
- No cross-user visibility: reads, conflict lookups, and write outcomes must not
  reveal whether another user's note exists.
- Include-deleted remains owner-scoped: an explicit include-deleted path may
  expose deleted rows only to the authenticated owner.

Application-level `user_id` predicates remain mandatory after RLS exists. RLS
is a database enforcement boundary, not a replacement for repository scoping.

## 6. Security Review Checklist

Reviewers must confirm before any SQL approval:

- No production data, production schema dump, seed with real data, backup, or
  snapshot is part of the packet or future artifact.
- No credentials, passwords, JWT secrets, service-role keys, access tokens,
  refresh tokens, private keys, project identifiers, or connection strings are
  present.
- No service-role credential is used for Notes request-path behavior or future
  RLS validation.
- No broad grants or broad table access are proposed.
- No unsafe privileged functions are proposed. Any privileged function requires
  explicit justification and separate review.
- No public read policy is proposed.
- Cross-user reads, updates, soft deletes, conflict lookups, and include-deleted
  paths remain blocked or non-disclosing.
- Ownership is bound to the authenticated user, not to caller-supplied owner
  fields.
- Soft delete remains an owner-scoped update and does not become physical
  request-path deletion.
- Rollback and cleanup considerations are documented before execution.
- Synthetic validation evidence is required later before RLS coverage can be
  claimed.
- Logs, errors, assertions, and review evidence redact note content, user
  emails, Auth payloads, keys, and tokens.

## 7. Risk Analysis

| Risk | Review concern | Required control |
|---|---|---|
| RLS bypass | A request path could reach data with a privileged credential or missing caller identity | Use public key plus verified caller token; keep service role outside request path |
| User-id spoofing | A caller could insert or mutate a row owned by another user | Bind ownership to authenticated identity and reject owner mismatch |
| Service-role misuse | A service-role key could make tests pass while bypassing RLS | Reject service-role env in harness inputs and keep admin work separate |
| Migration rollback error | A bad rollback could leave partial tables, grants, or policies | Require rollback notes and local-only trial evidence before approval |
| Accidental broad access | Grants or policy scope could expose all rows | Review grants/policies for least privilege and no public read path |
| Soft-delete leakage | Deleted rows could be visible to other users or by default | Keep default reads non-deleted and include-deleted owner-scoped |
| Sync metadata leakage | Optional sync metadata could expose local operation/conflict details | Keep it absent from initial server emission unless explicitly approved; if added, keep it owner-scoped and non-sensitive |
| Note content exposure | Logs or validation evidence could reveal user note text | Use synthetic content only and redact returned row content in evidence |
| Test cleanup failure | Synthetic rows could accumulate or affect later validations | Use deterministic prefixes, owner-scoped cleanup, and coarse cleanup reporting |

## 8. Review Questions

Reviewers must answer these before executable SQL approval:

- Is `user_id` derived only from verified auth context for request-path writes?
- Can insert spoof another user's owner identifier?
- Can update or soft delete affect another user's row?
- Can a stale-version conflict lookup reveal another user's row?
- Are deleted notes hidden by default unless explicitly requested?
- Is include-deleted still scoped to the authenticated owner?
- Is physical delete excluded from public request-path CRUD?
- Are indexes sufficient for owner-scoped list/get/update/delete flows without
  creating broader access?
- Is `sync_metadata` omitted from the initial server table, or explicitly
  justified if included?
- Are rollback and cleanup steps safe for local-only synthetic validation?
- Is any privileged function absent, or explicitly justified and reviewed?
- Is any service-role use limited to separately approved migration/admin work
  outside request-path validation?
- Is the validation evidence plan synthetic, redacted, and default-CI disabled?

## 9. Approval Gate

Executable migration work may begin only after all approvals are recorded:

- Engineering approval for the proposed table shape, owner predicates,
  soft-delete/version semantics, and compatibility with current Notes behavior.
- Security/privacy approval for RLS ownership behavior, credential handling,
  redaction requirements, and absence of real data.
- Database artifact policy exception for the specific future migration file.
- Synthetic validation plan covering local-only or approved non-production
  users, data, cleanup, and expected evidence.
- Rollback/cleanup plan for local-only validation and any later staging
  validation.

Approval must be artifact-specific. Accepting this review packet is a
prerequisite for Slice 6H-3B-4B, but it is not itself executable migration
approval.

## 10. Future Implementation Slices

1. **Slice 6H-3B-4B - Approved local-only migration artifact**
   Add the minimal environment-independent migration artifact only after this
   packet is accepted and the required approvals are recorded.
2. **Slice 6H-3B-4C - RLS validation tests behind opt-in harness**
   Add skipped-by-default user A/B validation tests gated by the explicit
   Supabase harness environment.
3. **Slice 6H-3B-4D - Hosted staging validation plan**
   Document controlled non-production hosted validation, secret-store handling,
   workflow separation, redaction, rollback, and evidence requirements.

## 11. Definition Of Done

Slice 6H-3B-4A is complete when:

- This review packet exists.
- No executable SQL, migration file, `.env` file, credential, generated
  Supabase state, live Supabase execution, live repository mode, or RLS test is
  added.
- Current schema and proposed RLS behavior are documented in sanitized prose.
- Current shared/backend contract differences are called out.
- The security review checklist exists.
- The approval gate exists and blocks Slice 6H-3B-4B until the packet is
  accepted.
- Verification passes locally.
- CI passes after the docs-only commit is pushed.
