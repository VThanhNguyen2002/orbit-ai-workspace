-- Slice 6E draft migration for Notes persistence.
-- This file is committed as a schema/RLS draft and is not executed by CI.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title text NOT NULL CHECK (char_length(title) BETWEEN 1 AND 500),
  content text NOT NULL DEFAULT '' CHECK (char_length(content) <= 50000),
  content_type text NOT NULL DEFAULT 'plain'
    CHECK (content_type IN ('plain', 'markdown')),
  is_archived boolean NOT NULL DEFAULT false,
  is_deleted boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz NULL,
  version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  CHECK (
    (is_deleted = false AND deleted_at IS NULL)
    OR (is_deleted = true AND deleted_at IS NOT NULL)
  )
);

COMMENT ON TABLE public.notes IS
  'User-owned notes. Request-path deletes are soft deletes implemented by UPDATE.';
COMMENT ON COLUMN public.notes.version IS
  'Server-side sync metadata for optimistic concurrency.';
COMMENT ON COLUMN public.notes.updated_at IS
  'Server-side sync metadata for ordering and future pull sync.';
COMMENT ON COLUMN public.notes.is_deleted IS
  'Server-side sync metadata for soft delete propagation.';
COMMENT ON COLUMN public.notes.deleted_at IS
  'Server-side sync metadata for soft delete time and cleanup eligibility.';

CREATE INDEX IF NOT EXISTS notes_user_visible_updated_idx
  ON public.notes (user_id, is_deleted, updated_at DESC, id);

CREATE INDEX IF NOT EXISTS notes_user_archive_visible_updated_idx
  ON public.notes (user_id, is_archived, is_deleted, updated_at DESC, id);

CREATE INDEX IF NOT EXISTS notes_user_updated_idx
  ON public.notes (user_id, updated_at DESC, id);

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS notes_set_updated_at ON public.notes;

CREATE TRIGGER notes_set_updated_at
BEFORE UPDATE ON public.notes
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own notes" ON public.notes;
CREATE POLICY "Users can view own notes"
  ON public.notes FOR SELECT
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can create own notes" ON public.notes;
CREATE POLICY "Users can create own notes"
  ON public.notes FOR INSERT
  WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own notes" ON public.notes;
CREATE POLICY "Users can update own notes"
  ON public.notes FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- No request-path physical DELETE policy is created for Notes.
-- HTTP DELETE /v1/notes/{note_id} is implemented as a soft-delete UPDATE.
