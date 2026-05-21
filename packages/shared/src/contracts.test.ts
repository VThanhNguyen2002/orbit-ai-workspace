import { describe, expect, it } from "vitest";

import {
  AiStreamDoneEventSchema,
  AiStreamEventSchema,
  ApiErrorEnvelopeSchema,
  ConflictResolutionStrategySchema,
  CreateNoteRequestSchema,
  DeleteNoteRequestSchema,
  ListNotesRequestSchema,
  ListNotesResponseSchema,
  NoteSchema,
  PaginationRequestSchema,
  SemanticSearchRequestSchema,
  SemanticSearchResponseSchema,
  SyncEntityTypeSchema,
  SyncOperationStatusSchema,
  SyncPushRequestSchema,
  SyncPullResponseSchema,
  TaskStatusSchema,
  UpdateNoteRequestSchema,
} from "./index";

const user_id = "11111111-1111-4111-8111-111111111111";
const note_id = "22222222-2222-4222-8222-222222222222";
const operation_id = "33333333-3333-4333-8333-333333333333";
const request_id = "req_contract_test";
const timestamp = "2026-05-19T10:30:00.000Z";

const validNote = {
  id: note_id,
  user_id,
  title: "Planning note",
  content: "Decisions and follow-up items from the planning session.",
  content_type: "markdown",
  is_archived: false,
  is_deleted: false,
  created_at: timestamp,
  updated_at: timestamp,
  deleted_at: null,
  version: 1,
  sync_metadata: {
    last_synced_at: timestamp,
    pending_operation_ids: [operation_id],
    conflict_ids: [],
  },
};

describe("shared contract schemas", () => {
  it("parses a valid snake_case note with nested sync metadata", () => {
    expect(NoteSchema.parse(validNote)).toEqual(validNote);
  });

  it("rejects an equivalent camelCase note payload", () => {
    const result = NoteSchema.safeParse({
      id: note_id,
      userId: user_id,
      title: "Planning note",
      content: "Decisions and follow-up items from the planning session.",
      contentType: "markdown",
      isArchived: false,
      isDeleted: false,
      createdAt: timestamp,
      updatedAt: timestamp,
      deletedAt: null,
      version: 1,
      syncMetadata: {
        lastSyncedAt: timestamp,
        pendingOperationIds: [operation_id],
        conflictIds: [],
      },
    });

    expect(result.success).toBe(false);
  });

  it("rejects an invalid note", () => {
    const result = NoteSchema.safeParse({
      ...validNote,
      title: "",
      version: -1,
    });

    expect(result.success).toBe(false);
  });

  it("parses a valid create note request with defaults", () => {
    expect(
      CreateNoteRequestSchema.parse({
        title: "Planning note",
      }),
    ).toEqual({
      title: "Planning note",
      content: "",
      content_type: "plain",
    });

    expect(
      CreateNoteRequestSchema.parse({
        title: "Planning note",
        content: "Decisions and follow-up items.",
        content_type: "markdown",
      }),
    ).toEqual({
      title: "Planning note",
      content: "Decisions and follow-up items.",
      content_type: "markdown",
    });
  });

  it("rejects server-controlled fields in create note requests", () => {
    const result = CreateNoteRequestSchema.safeParse({
      id: note_id,
      user_id,
      title: "Planning note",
      content: "Decisions and follow-up items.",
      content_type: "markdown",
      is_archived: false,
      is_deleted: false,
      created_at: timestamp,
      updated_at: timestamp,
      deleted_at: null,
      version: 1,
    });

    expect(result.success).toBe(false);
  });

  it("requires version for update note requests", () => {
    expect(
      UpdateNoteRequestSchema.parse({
        title: "Updated title",
        version: 1,
      }),
    ).toEqual({
      title: "Updated title",
      version: 1,
    });

    expect(
      UpdateNoteRequestSchema.safeParse({
        title: "Updated title",
      }).success,
    ).toBe(false);
  });

  it("requires version for delete note requests", () => {
    expect(DeleteNoteRequestSchema.parse({ version: 1 })).toEqual({
      version: 1,
    });

    expect(DeleteNoteRequestSchema.safeParse({}).success).toBe(false);
  });

  it("parses note list pagination and filters", () => {
    expect(ListNotesRequestSchema.parse({})).toEqual({
      page: 1,
      per_page: 20,
      sort: "updated_at",
      order: "desc",
      include_deleted: false,
    });

    expect(
      ListNotesRequestSchema.parse({
        page: 2,
        per_page: 25,
        sort: "title",
        order: "asc",
        is_archived: true,
        include_deleted: true,
      }),
    ).toEqual({
      page: 2,
      per_page: 25,
      sort: "title",
      order: "asc",
      is_archived: true,
      include_deleted: true,
    });
  });

  it("parses a snake_case list notes response", () => {
    const response = {
      data: {
        items: [validNote],
        pagination: {
          page: 1,
          per_page: 20,
          total: 1,
          has_next: false,
        },
      },
      meta: { request_id },
    };

    expect(ListNotesResponseSchema.parse(response)).toEqual(response);
  });

  it("rejects camelCase note CRUD contracts", () => {
    expect(
      CreateNoteRequestSchema.safeParse({
        title: "Planning note",
        contentType: "markdown",
      }).success,
    ).toBe(false);

    expect(
      ListNotesRequestSchema.safeParse({
        includeDeleted: true,
      }).success,
    ).toBe(false);

    expect(
      ListNotesResponseSchema.safeParse({
        data: {
          items: [validNote],
          pagination: {
            page: 1,
            perPage: 20,
            total: 1,
            hasNext: false,
          },
        },
        meta: { requestId: request_id },
      }).success,
    ).toBe(false);
  });

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
