import { describe, expect, it } from "vitest";

import {
  AiStreamDoneEventSchema,
  AiStreamEventSchema,
  SemanticSearchRequestSchema,
  SemanticSearchResponseSchema,
} from "./index";
import { note_id, request_id, timestamp } from "./__fixtures__/contracts";

describe("AI contract schemas", () => {
  it("parses a snake_case semantic search contract", () => {
    const request = {
      query: "planning follow up",
      source_types: ["note", "transcript"],
    };
    const response = {
      data: {
        results: [
          {
            source_type: "note",
            source_id: note_id,
            title: "Planning note",
            snippet: "follow-up items",
            similarity: 0.91,
            chunk_index: 0,
            updated_at: timestamp,
          },
        ],
      },
      meta: {
        request_id,
        query_embedding_ms: 45,
        search_ms: 12,
      },
    };

    expect(SemanticSearchRequestSchema.parse(request)).toEqual({
      ...request,
      limit: 10,
      threshold: 0.7,
    });
    expect(SemanticSearchResponseSchema.parse(response)).toEqual(response);
  });

  it("rejects camelCase semantic search contracts", () => {
    expect(
      SemanticSearchRequestSchema.safeParse({
        query: "planning follow up",
        sourceTypes: ["note", "transcript"],
      }).success,
    ).toBe(false);

    expect(
      SemanticSearchResponseSchema.safeParse({
        data: {
          results: [
            {
              sourceType: "note",
              sourceId: note_id,
              title: "Planning note",
              snippet: "follow-up items",
              similarity: 0.91,
              chunkIndex: 0,
              updatedAt: timestamp,
            },
          ],
        },
        meta: { requestId: request_id },
      }).success,
    ).toBe(false);
  });

  it("parses AI streaming events with snake_case payload fields", () => {
    const event = {
      event: "token",
      data: {
        text: "The meeting covered ",
        index: 0,
      },
    };

    expect(AiStreamEventSchema.parse(event)).toEqual(event);

    const actionItemsEvent = {
      event: "action_items",
      data: {
        items: [{ text: "Schedule follow-up", priority: "high" }],
      },
    };

    expect(AiStreamEventSchema.parse(actionItemsEvent)).toEqual(
      actionItemsEvent,
    );

    const doneEvent = {
      event: "done",
      data: {
        summary_id: note_id,
        usage: {
          provider: "openai",
          model: "gpt-example",
          input_tokens: 120,
          output_tokens: 40,
          estimated_cost_usd: 0.01,
          operation: "summarize",
        },
      },
    };

    expect(AiStreamDoneEventSchema.parse(doneEvent)).toEqual(doneEvent);
  });

  it("rejects camelCase AI streaming event payload fields", () => {
    const result = AiStreamDoneEventSchema.safeParse({
      event: "done",
      data: {
        summaryId: note_id,
        usage: {
          provider: "openai",
          model: "gpt-example",
          inputTokens: 120,
          outputTokens: 40,
          estimatedCostUsd: 0.01,
          operation: "summarize",
        },
      },
    });

    expect(result.success).toBe(false);
  });
});
