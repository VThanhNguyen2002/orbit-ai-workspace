import { describe, expect, it } from "vitest";

import { SyncPullResponseSchema, SyncPushRequestSchema } from "./index";
import {
  note_id,
  operation_id,
  request_id,
  validNote,
} from "./__fixtures__/contracts";

describe("sync contract schemas", () => {
  it("parses a snake_case sync push request", () => {
    const request = {
      operations: [
        {
          id: operation_id,
          entity_type: "note",
          entity_id: note_id,
          operation: "update",
          payload: { title: "Planning note" },
          created_at: 1_700_003_300_000,
          retry_count: 0,
          status: "pending",
        },
      ],
    };

    expect(SyncPushRequestSchema.parse(request)).toEqual(request);
  });

  it("rejects a camelCase sync push request", () => {
    const result = SyncPushRequestSchema.safeParse({
      operations: [
        {
          id: operation_id,
          entityType: "note",
          entityId: note_id,
          operation: "update",
          payload: { title: "Planning note" },
          createdAt: 1_700_003_300_000,
          retryCount: 0,
          status: "pending",
        },
      ],
    });

    expect(result.success).toBe(false);
  });

  it("parses a sync pull response", () => {
    const response = {
      data: {
        notes: [validNote],
        tasks: [],
        voice_memos: [],
        summaries: [],
        transcripts: [],
      },
      meta: {
        request_id,
        sync_timestamp: 1_700_003_400_000,
        has_more: false,
      },
    };

    expect(SyncPullResponseSchema.parse(response)).toEqual(response);
  });

  it("rejects a camelCase sync pull response", () => {
    const result = SyncPullResponseSchema.safeParse({
      data: {
        notes: [validNote],
        tasks: [],
        voiceMemos: [],
        summaries: [],
        transcripts: [],
      },
      meta: {
        requestId: request_id,
        syncTimestamp: 1_700_003_400_000,
        hasMore: false,
      },
    });

    expect(result.success).toBe(false);
  });
});
