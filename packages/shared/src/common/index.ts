import { z } from "zod";

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export const JsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(JsonValueSchema),
    z.record(z.string(), JsonValueSchema),
  ]),
);

export const JsonObjectSchema = z.record(z.string(), JsonValueSchema);

export const EntityIdSchema = z.string().uuid();
export const RequestIdSchema = z.string().min(1).max(128);
export const IsoTimestampSchema = z.string().datetime({ offset: true });
export const NullableIsoTimestampSchema = IsoTimestampSchema.nullable();
export const EpochMillisSchema = z.number().int().nonnegative();
export const NonNegativeIntegerSchema = z.number().int().nonnegative();
export const PositiveIntegerSchema = z.number().int().positive();

export const SortOrderSchema = z.enum(["asc", "desc"]);
export const PaginationSortSchema = z.enum([
  "created_at",
  "updated_at",
  "title",
]);

export const PaginationRequestSchema = z.strictObject({
  page: z.number().int().min(1).default(1),
  per_page: z.number().int().min(1).max(100).default(20),
  sort: PaginationSortSchema.default("updated_at"),
  order: SortOrderSchema.default("desc"),
});

export const PaginationMetaSchema = z.strictObject({
  page: z.number().int().min(1),
  per_page: z.number().int().min(1).max(100),
  total: NonNegativeIntegerSchema,
  has_next: z.boolean(),
});

export const ApiMetaSchema = z.strictObject({
  request_id: RequestIdSchema,
  pagination: PaginationMetaSchema.optional(),
});

export const ApiSuccessEnvelopeSchema = z.strictObject({
  data: z.unknown(),
  meta: ApiMetaSchema,
});

export const createApiSuccessEnvelopeSchema = (
  dataSchema: z.ZodType,
  metaSchema: z.ZodType = ApiMetaSchema,
) =>
  z.strictObject({
    data: dataSchema,
    meta: metaSchema,
  });

export type EntityId = z.infer<typeof EntityIdSchema>;
export type RequestId = z.infer<typeof RequestIdSchema>;
export type IsoTimestamp = z.infer<typeof IsoTimestampSchema>;
export type EpochMillis = z.infer<typeof EpochMillisSchema>;
export type PaginationRequest = z.infer<typeof PaginationRequestSchema>;
export type PaginationMeta = z.infer<typeof PaginationMetaSchema>;
export type ApiMeta = z.infer<typeof ApiMetaSchema>;
export type ApiSuccessEnvelope = z.infer<typeof ApiSuccessEnvelopeSchema>;
