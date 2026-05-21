import { z } from "zod";

import { JsonValueSchema, RequestIdSchema } from "../common/index.js";

export const ApiErrorCodeSchema = z.enum([
  "VALIDATION_ERROR",
  "UNAUTHORIZED",
  "FORBIDDEN",
  "NOT_FOUND",
  "CONFLICT",
  "UNPROCESSABLE",
  "RATE_LIMITED",
  "INTERNAL_ERROR",
]);

export const ApiErrorDetailSchema = z.strictObject({
  field: z.string().min(1).optional(),
  message: z.string().min(1).optional(),
  expected: JsonValueSchema.optional(),
  actual: JsonValueSchema.optional(),
  server_data: JsonValueSchema.optional(),
});

export const ApiErrorPayloadSchema = z.strictObject({
  code: ApiErrorCodeSchema,
  message: z.string().min(1),
  details: z.array(ApiErrorDetailSchema).optional(),
});

export const ApiErrorMetaSchema = z.strictObject({
  request_id: RequestIdSchema,
});

export const ApiErrorEnvelopeSchema = z.strictObject({
  error: ApiErrorPayloadSchema,
  meta: ApiErrorMetaSchema,
});

export type ApiErrorCode = z.infer<typeof ApiErrorCodeSchema>;
export type ApiErrorDetail = z.infer<typeof ApiErrorDetailSchema>;
export type ApiErrorPayload = z.infer<typeof ApiErrorPayloadSchema>;
export type ApiErrorEnvelope = z.infer<typeof ApiErrorEnvelopeSchema>;
