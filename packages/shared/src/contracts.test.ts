import { describe, expect, it } from "vitest";

import {
  ApiErrorEnvelopeSchema,
  ConflictResolutionStrategySchema,
  PaginationRequestSchema,
  SyncEntityTypeSchema,
  SyncOperationStatusSchema,
  TaskStatusSchema,
} from "./index";
import { note_id, request_id } from "./__fixtures__/contracts";

describe("common contract schemas", () => {
  it("parses an API error envelope", () => {
    const envelope = {
      error: {
        code: "VALIDATION_ERROR",
        message: "Invalid request body",
        details: [
          {
            field: "title",
            message: "Required",
            server_data: { id: note_id, version: 2 },
          },
        ],
      },
      meta: { request_id },
    };

    expect(ApiErrorEnvelopeSchema.parse(envelope)).toEqual(envelope);
  });

  it("rejects a camelCase API error envelope", () => {
    const result = ApiErrorEnvelopeSchema.safeParse({
      error: {
        code: "VALIDATION_ERROR",
        message: "Invalid request body",
        details: [{ field: "title", serverData: { id: note_id } }],
      },
      meta: { requestId: request_id },
    });

    expect(result.success).toBe(false);
  });

  it("parses pagination defaults", () => {
    expect(PaginationRequestSchema.parse({})).toEqual({
      page: 1,
      per_page: 20,
      sort: "updated_at",
      order: "desc",
    });
  });

  it("parses snake_case pagination input and rejects camelCase input", () => {
    expect(
      PaginationRequestSchema.parse({
        page: 2,
        per_page: 50,
        sort: "created_at",
        order: "asc",
      }),
    ).toEqual({
      page: 2,
      per_page: 50,
      sort: "created_at",
      order: "asc",
    });

    expect(
      PaginationRequestSchema.safeParse({ page: 2, perPage: 50 }).success,
    ).toBe(false);
  });

  it("keeps enum values API-friendly and rejects former camelCase values", () => {
    expect(TaskStatusSchema.parse("in_progress")).toBe("in_progress");
    expect(SyncEntityTypeSchema.parse("voice_memo")).toBe("voice_memo");
    expect(SyncOperationStatusSchema.parse("in_flight")).toBe("in_flight");
    expect(ConflictResolutionStrategySchema.parse("local_wins")).toBe(
      "local_wins",
    );

    expect(TaskStatusSchema.safeParse("inProgress").success).toBe(false);
    expect(SyncEntityTypeSchema.safeParse("voiceMemo").success).toBe(false);
    expect(SyncOperationStatusSchema.safeParse("inFlight").success).toBe(false);
    expect(
      ConflictResolutionStrategySchema.safeParse("localWins").success,
    ).toBe(false);
  });
});
