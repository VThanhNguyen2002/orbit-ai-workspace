import { z } from "zod";

import {
  createApiSuccessEnvelopeSchema,
  EntityIdSchema,
  IsoTimestampSchema,
  NonNegativeIntegerSchema,
  PositiveIntegerSchema,
  RequestIdSchema,
} from "../common";
import {
  SummaryActionItemSchema,
  SummarySchema,
  SummarySourceTypeSchema,
} from "../domain";

export const AiProviderSchema = z.string().min(1).max(100);
export const AiModelSchema = z.string().min(1).max(200);

export const SummarizeRequestSchema = z.strictObject({
  source_id: EntityIdSchema,
  source_type: SummarySourceTypeSchema,
  content: z.string().min(1).max(50_000),
  max_sentences: z.number().int().min(1).max(10).optional(),
});

export const SummarizeResponseSchema = z.strictObject({
  summary: SummarySchema,
  action_items: z.array(SummaryActionItemSchema),
});

export const SemanticSearchSourceTypeSchema = z.enum(["note", "transcript"]);

export const SemanticSearchRequestSchema = z.strictObject({
  query: z.string().min(3).max(1_000),
  limit: z.number().int().min(1).max(50).default(10),
  threshold: z.number().min(0).max(1).default(0.7),
  source_types: z.array(SemanticSearchSourceTypeSchema).optional(),
});

export const SemanticSearchResultSchema = z.strictObject({
  source_type: SemanticSearchSourceTypeSchema,
  source_id: EntityIdSchema,
  title: z.string().min(1).max(500),
  snippet: z.string().min(1),
  similarity: z.number().min(0).max(1),
  chunk_index: NonNegativeIntegerSchema,
  updated_at: IsoTimestampSchema,
});

export const SemanticSearchDataSchema = z.strictObject({
  results: z.array(SemanticSearchResultSchema),
});

export const SemanticSearchMetaSchema = z.strictObject({
  request_id: RequestIdSchema,
  query_embedding_ms: NonNegativeIntegerSchema.optional(),
  search_ms: NonNegativeIntegerSchema.optional(),
});

export const SemanticSearchResponseSchema = createApiSuccessEnvelopeSchema(
  SemanticSearchDataSchema,
  SemanticSearchMetaSchema,
);

export const EmbeddingMetadataSchema = z.strictObject({
  provider: AiProviderSchema,
  model: AiModelSchema,
  dimensions: PositiveIntegerSchema,
  source_type: SemanticSearchSourceTypeSchema,
  source_id: EntityIdSchema,
  chunk_index: NonNegativeIntegerSchema,
});

export const AiUsageSchema = z.strictObject({
  provider: AiProviderSchema,
  model: AiModelSchema,
  input_tokens: NonNegativeIntegerSchema,
  output_tokens: NonNegativeIntegerSchema,
  estimated_cost_usd: z.number().nonnegative(),
  operation: z.enum(["summarize", "embed", "transcribe"]),
});

export const AiStreamTokenEventSchema = z.strictObject({
  event: z.literal("token"),
  data: z.strictObject({
    text: z.string().min(1),
    index: NonNegativeIntegerSchema.optional(),
  }),
});

export const AiStreamActionItemsEventSchema = z.strictObject({
  event: z.literal("action_items"),
  data: z.strictObject({
    items: z.array(SummaryActionItemSchema),
  }),
});

export const AiStreamDoneEventSchema = z.strictObject({
  event: z.literal("done"),
  data: z.strictObject({
    summary_id: EntityIdSchema.optional(),
    transcript_id: EntityIdSchema.optional(),
    usage: AiUsageSchema.optional(),
  }),
});

export const AiStreamErrorEventSchema = z.strictObject({
  event: z.literal("error"),
  data: z.strictObject({
    code: z.string().min(1).max(100),
    message: z.string().min(1),
    retryable: z.boolean().optional(),
  }),
});

export const AiStreamEventSchema = z.discriminatedUnion("event", [
  AiStreamTokenEventSchema,
  AiStreamActionItemsEventSchema,
  AiStreamDoneEventSchema,
  AiStreamErrorEventSchema,
]);

export type AiProvider = z.infer<typeof AiProviderSchema>;
export type AiModel = z.infer<typeof AiModelSchema>;
export type SummarizeRequest = z.infer<typeof SummarizeRequestSchema>;
export type SummarizeResponse = z.infer<typeof SummarizeResponseSchema>;
export type SemanticSearchSourceType = z.infer<
  typeof SemanticSearchSourceTypeSchema
>;
export type SemanticSearchRequest = z.infer<
  typeof SemanticSearchRequestSchema
>;
export type SemanticSearchResult = z.infer<typeof SemanticSearchResultSchema>;
export type SemanticSearchData = z.infer<typeof SemanticSearchDataSchema>;
export type SemanticSearchMeta = z.infer<typeof SemanticSearchMetaSchema>;
export type SemanticSearchResponse = z.infer<
  typeof SemanticSearchResponseSchema
>;
export type EmbeddingMetadata = z.infer<typeof EmbeddingMetadataSchema>;
export type AiUsage = z.infer<typeof AiUsageSchema>;
export type AiStreamTokenEvent = z.infer<typeof AiStreamTokenEventSchema>;
export type AiStreamActionItemsEvent = z.infer<
  typeof AiStreamActionItemsEventSchema
>;
export type AiStreamDoneEvent = z.infer<typeof AiStreamDoneEventSchema>;
export type AiStreamErrorEvent = z.infer<typeof AiStreamErrorEventSchema>;
export type AiStreamEvent = z.infer<typeof AiStreamEventSchema>;
