import { z } from "zod";

import {
  createApiSuccessEnvelopeSchema,
  EntityIdSchema,
  EpochMillisSchema,
  JsonObjectSchema,
  NonNegativeIntegerSchema,
  RequestIdSchema,
} from "../common";
import {
  NoteSchema,
  SummarySchema,
  TaskSchema,
  TranscriptSchema,
  VoiceMemoSchema,
} from "../domain";

export const SyncEntityTypeSchema = z.enum(["note", "task", "voice_memo"]);
export const SyncOperationTypeSchema = z.enum(["create", "update", "delete"]);
export const SyncOperationStatusSchema = z.enum([
  "pending",
  "in_flight",
  "failed",
  "resolved",
]);
export const ConflictResolutionStrategySchema = z.enum([
  "pending",
  "local_wins",
  "server_wins",
  "merged",
]);

export const SyncCursorSchema = z.strictObject({
  since: EpochMillisSchema,
  entity_types: z.array(SyncEntityTypeSchema).optional(),
});

export const SyncOperationSchema = z.strictObject({
  id: EntityIdSchema,
  entity_type: SyncEntityTypeSchema,
  entity_id: EntityIdSchema,
  operation: SyncOperationTypeSchema,
  payload: JsonObjectSchema,
  created_at: EpochMillisSchema,
  retry_count: NonNegativeIntegerSchema,
  status: SyncOperationStatusSchema,
  error: z.string().min(1).optional(),
});

export const ConflictRecordSchema = z.strictObject({
  id: EntityIdSchema,
  sync_operation_id: EntityIdSchema,
  entity_type: SyncEntityTypeSchema,
  entity_id: EntityIdSchema,
  local_version: NonNegativeIntegerSchema,
  server_version: NonNegativeIntegerSchema,
  local_data: JsonObjectSchema,
  server_data: JsonObjectSchema,
  resolution: ConflictResolutionStrategySchema,
  resolved_at: EpochMillisSchema.nullable(),
});

export const SyncPushRequestSchema = z.strictObject({
  operations: z.array(SyncOperationSchema).min(1).max(500),
});

export const SyncPushResultStatusSchema = z.enum([
  "applied",
  "conflict",
  "rejected",
]);

export const SyncPushResultSchema = z.strictObject({
  operation_id: EntityIdSchema,
  status: SyncPushResultStatusSchema,
  entity: JsonObjectSchema.optional(),
  server_data: JsonObjectSchema.optional(),
  reason: z.string().min(1).optional(),
});

export const SyncPushDataSchema = z.strictObject({
  results: z.array(SyncPushResultSchema),
});

export const SyncPushResponseSchema =
  createApiSuccessEnvelopeSchema(SyncPushDataSchema);

export const SyncPullRequestSchema = SyncCursorSchema;

export const SyncPullDataSchema = z.strictObject({
  notes: z.array(NoteSchema),
  tasks: z.array(TaskSchema),
  voice_memos: z.array(VoiceMemoSchema),
  summaries: z.array(SummarySchema),
  transcripts: z.array(TranscriptSchema),
});

export const SyncPullMetaSchema = z.strictObject({
  request_id: RequestIdSchema,
  sync_timestamp: EpochMillisSchema,
  has_more: z.boolean(),
});

export const SyncPullResponseSchema = createApiSuccessEnvelopeSchema(
  SyncPullDataSchema,
  SyncPullMetaSchema,
);

export type SyncEntityType = z.infer<typeof SyncEntityTypeSchema>;
export type SyncOperationType = z.infer<typeof SyncOperationTypeSchema>;
export type SyncOperationStatus = z.infer<typeof SyncOperationStatusSchema>;
export type ConflictResolutionStrategy = z.infer<
  typeof ConflictResolutionStrategySchema
>;
export type SyncCursor = z.infer<typeof SyncCursorSchema>;
export type SyncOperation = z.infer<typeof SyncOperationSchema>;
export type ConflictRecord = z.infer<typeof ConflictRecordSchema>;
export type SyncPushRequest = z.infer<typeof SyncPushRequestSchema>;
export type SyncPushResultStatus = z.infer<typeof SyncPushResultStatusSchema>;
export type SyncPushResult = z.infer<typeof SyncPushResultSchema>;
export type SyncPushResponse = z.infer<typeof SyncPushResponseSchema>;
export type SyncPullRequest = z.infer<typeof SyncPullRequestSchema>;
export type SyncPullData = z.infer<typeof SyncPullDataSchema>;
export type SyncPullResponse = z.infer<typeof SyncPullResponseSchema>;
