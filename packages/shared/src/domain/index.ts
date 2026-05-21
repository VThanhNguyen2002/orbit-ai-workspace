import { z } from "zod";

import {
  EntityIdSchema,
  IsoTimestampSchema,
  JsonObjectSchema,
  NonNegativeIntegerSchema,
  NullableIsoTimestampSchema,
} from "../common/index.js";

export const SyncMetadataSchema = z.strictObject({
  last_synced_at: NullableIsoTimestampSchema,
  pending_operation_ids: z.array(EntityIdSchema),
  conflict_ids: z.array(EntityIdSchema),
});

const MutableEntityFields = {
  id: EntityIdSchema,
  user_id: EntityIdSchema,
  created_at: IsoTimestampSchema,
  updated_at: IsoTimestampSchema,
  deleted_at: NullableIsoTimestampSchema,
  version: NonNegativeIntegerSchema,
  sync_metadata: SyncMetadataSchema.optional(),
};

export const UserSchema = z.strictObject({
  id: EntityIdSchema,
  email: z.string().email(),
  display_name: z.string().min(1).max(200).nullable(),
  created_at: IsoTimestampSchema,
  updated_at: IsoTimestampSchema,
});

export const NoteContentTypeSchema = z.enum(["plain", "markdown"]);

export const NoteSchema = z.strictObject({
  ...MutableEntityFields,
  title: z.string().min(1).max(500),
  content: z.string().max(50_000),
  content_type: NoteContentTypeSchema,
  is_archived: z.boolean(),
  is_deleted: z.boolean(),
});

export const TaskStatusSchema = z.enum([
  "todo",
  "in_progress",
  "done",
  "cancelled",
]);

export const TaskPrioritySchema = z.enum(["low", "medium", "high", "urgent"]);

export const TaskSchema = z.strictObject({
  ...MutableEntityFields,
  note_id: EntityIdSchema.nullable(),
  title: z.string().min(1).max(500),
  description: z.string().max(5_000).nullable(),
  status: TaskStatusSchema,
  priority: TaskPrioritySchema,
  due_date: NullableIsoTimestampSchema,
  is_deleted: z.boolean(),
});

export const VoiceMemoStatusSchema = z.enum([
  "recording",
  "uploaded",
  "transcribing",
  "transcribed",
  "failed",
]);

export const VoiceMemoSchema = z.strictObject({
  ...MutableEntityFields,
  storage_path: z.string().min(1).max(1_000),
  duration_seconds: NonNegativeIntegerSchema,
  mime_type: z.string().min(1).max(100),
  file_size_bytes: NonNegativeIntegerSchema,
  status: VoiceMemoStatusSchema,
  is_deleted: z.boolean(),
});

export const TranscriptSchema = z.strictObject({
  id: EntityIdSchema,
  voice_memo_id: EntityIdSchema,
  user_id: EntityIdSchema,
  content: z.string().min(1),
  language: z.string().min(2).max(16).nullable(),
  provider: z.string().min(1).max(100),
  confidence: z.number().min(0).max(1).nullable(),
  created_at: IsoTimestampSchema,
});

export const SummarySourceTypeSchema = z.enum(["note", "transcript"]);

export const SummaryActionItemSchema = z.strictObject({
  text: z.string().min(1).max(1_000),
  priority: TaskPrioritySchema,
});

export const SummarySchema = z.strictObject({
  id: EntityIdSchema,
  user_id: EntityIdSchema,
  source_id: EntityIdSchema,
  source_type: SummarySourceTypeSchema,
  content: z.string().min(1),
  action_items: z.array(SummaryActionItemSchema),
  provider: z.string().min(1).max(100),
  model: z.string().min(1).max(200),
  created_at: IsoTimestampSchema,
});

export const EmbeddingSourceTypeSchema = SummarySourceTypeSchema;

export const EmbeddingSchema = z.strictObject({
  id: EntityIdSchema,
  user_id: EntityIdSchema,
  source_id: EntityIdSchema,
  source_type: EmbeddingSourceTypeSchema,
  vector: z.array(z.number()).min(1),
  model: z.string().min(1).max(200),
  chunk_text: z.string().min(1),
  chunk_index: NonNegativeIntegerSchema,
  metadata: JsonObjectSchema.optional(),
  created_at: IsoTimestampSchema,
});

export type SyncMetadata = z.infer<typeof SyncMetadataSchema>;
export type User = z.infer<typeof UserSchema>;
export type NoteContentType = z.infer<typeof NoteContentTypeSchema>;
export type Note = z.infer<typeof NoteSchema>;
export type TaskStatus = z.infer<typeof TaskStatusSchema>;
export type TaskPriority = z.infer<typeof TaskPrioritySchema>;
export type Task = z.infer<typeof TaskSchema>;
export type VoiceMemoStatus = z.infer<typeof VoiceMemoStatusSchema>;
export type VoiceMemo = z.infer<typeof VoiceMemoSchema>;
export type Transcript = z.infer<typeof TranscriptSchema>;
export type SummarySourceType = z.infer<typeof SummarySourceTypeSchema>;
export type SummaryActionItem = z.infer<typeof SummaryActionItemSchema>;
export type Summary = z.infer<typeof SummarySchema>;
export type EmbeddingSourceType = z.infer<typeof EmbeddingSourceTypeSchema>;
export type Embedding = z.infer<typeof EmbeddingSchema>;
