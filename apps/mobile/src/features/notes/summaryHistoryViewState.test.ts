import {
  appendSummaryHistoryItemToViewState,
  createIdleSummaryHistoryViewState,
  createLoadingSummaryHistoryViewState,
  createSummarizingSummaryHistoryViewState,
  loadSummaryHistoryViewState,
  mapSummaryHistoryDataToViewState,
  mapSummaryHistoryErrorToViewState,
  summarizeNoteAndMapSummaryHistoryViewState,
  SUMMARY_HISTORY_EMPTY_MESSAGE,
  SUMMARY_HISTORY_INVALID_RESPONSE_MESSAGE,
  SUMMARY_HISTORY_LOADING_MESSAGE,
  SUMMARY_HISTORY_MEMORY_NOTICE,
  SUMMARY_HISTORY_NOT_FOUND_MESSAGE,
  SUMMARY_HISTORY_SUMMARIZING_MESSAGE,
  SUMMARY_HISTORY_UNAVAILABLE_MESSAGE,
} from "./summaryHistoryViewState";
import {
  createInvalidResponseError,
  createSummary,
  noteId,
} from "./testFixtures";
import { describe, expect, it } from "./testGlobals";

describe("summary history view-state", () => {
  it("creates loading and summarizing states with the memory-only notice", () => {
    const loading = createLoadingSummaryHistoryViewState(noteId);
    const current = mapSummaryHistoryDataToViewState(noteId, {
      items: [createSummary()],
    });
    const summarizing = createSummarizingSummaryHistoryViewState(
      noteId,
      current,
    );

    expect(loading).toMatchObject({
      status: "loading",
      noteId,
      items: [],
      message: SUMMARY_HISTORY_LOADING_MESSAGE,
      memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
      isLoading: true,
      isSummarizing: false,
      canRetry: false,
      errorReason: null,
    });
    expect(summarizing).toMatchObject({
      status: "summarizing",
      noteId,
      message: SUMMARY_HISTORY_SUMMARIZING_MESSAGE,
      memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
      isLoading: false,
      isSummarizing: true,
      canRetry: false,
      errorReason: null,
    });
    expect(summarizing.items).toEqual(current.items);
  });

  it("maps an empty response and keeps the memory-only notice available", () => {
    const state = mapSummaryHistoryDataToViewState(noteId, { items: [] });

    expect(state).toEqual({
      status: "empty",
      noteId,
      items: [],
      message: SUMMARY_HISTORY_EMPTY_MESSAGE,
      memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
      isLoading: false,
      isSummarizing: false,
      canRetry: false,
      errorReason: null,
    });
  });

  it("maps success responses newest first", () => {
    const older = createSummary({
      id: "44444444-4444-4444-8444-444444444444",
      created_at: "2026-05-19T12:00:00.000Z",
    });
    const newer = createSummary({
      id: "55555555-5555-4555-8555-555555555555",
      content: "This is the newer summary.",
      created_at: "2026-05-19T13:00:00.000Z",
    });

    const state = mapSummaryHistoryDataToViewState(noteId, {
      items: [older, newer],
    });

    expect(state.status).toBe("success");
    expect(state.message).toBe("2 summaries available.");
    expect(state.memoryNotice).toBe(SUMMARY_HISTORY_MEMORY_NOTICE);
    expect(state.items.map((item) => item.id)).toEqual([newer.id, older.id]);
    expect(state.items[0]).toMatchObject({
      id: newer.id,
      content: "This is the newer summary.",
      createdAt: newer.created_at,
      actionItems: [
        {
          text: "Follow up on the planning decision.",
          priority: "medium",
        },
      ],
    });
  });

  it("appends summaries with newest-first dedupe behavior", () => {
    const existing = createSummary({
      id: "44444444-4444-4444-8444-444444444444",
      content: "Original summary content.",
      created_at: "2026-05-19T12:00:00.000Z",
    });
    const current = mapSummaryHistoryDataToViewState(noteId, {
      items: [existing],
    });
    const replacement = createSummary({
      id: existing.id,
      content: "Replacement summary content.",
      created_at: "2026-05-19T14:00:00.000Z",
    });
    const newest = createSummary({
      id: "66666666-6666-4666-8666-666666666666",
      content: "Newest summary content.",
      created_at: "2026-05-19T15:00:00.000Z",
    });

    const deduped = appendSummaryHistoryItemToViewState(
      noteId,
      current,
      replacement,
    );
    const appended = appendSummaryHistoryItemToViewState(
      noteId,
      deduped,
      newest,
    );

    expect(deduped.items).toHaveLength(1);
    expect(deduped.items[0]).toMatchObject({
      id: existing.id,
      content: "Replacement summary content.",
      createdAt: replacement.created_at,
    });
    expect(appended.items.map((item) => item.id)).toEqual([
      newest.id,
      existing.id,
    ]);
  });

  it("maps errors to UI-safe messages", () => {
    const notFound = mapSummaryHistoryErrorToViewState(noteId, {
      status: 404,
      code: "NOT_FOUND",
      message: "Synthetic missing note detail",
    });
    const invalidResponse = mapSummaryHistoryErrorToViewState(
      noteId,
      createInvalidResponseError(),
    );
    const unavailable = mapSummaryHistoryErrorToViewState(
      noteId,
      new Error("Synthetic service diagnostic"),
    );

    expect(notFound).toMatchObject({
      status: "error",
      noteId,
      items: [],
      message: SUMMARY_HISTORY_NOT_FOUND_MESSAGE,
      memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
      canRetry: false,
      errorReason: "not_found",
    });
    expect(invalidResponse).toMatchObject({
      status: "error",
      message: SUMMARY_HISTORY_INVALID_RESPONSE_MESSAGE,
      canRetry: false,
      errorReason: "invalid_response",
    });
    expect(unavailable).toMatchObject({
      status: "error",
      message: SUMMARY_HISTORY_UNAVAILABLE_MESSAGE,
      canRetry: true,
      errorReason: "unavailable",
    });
    expect(notFound.message).not.toContain("Synthetic missing note detail");
    expect(invalidResponse.message).not.toContain("Synthetic invalid response");
    expect(unavailable.message).not.toContain("Synthetic service diagnostic");
  });

  it("loads and summarizes through injected APIs", async () => {
    const listCalls: string[] = [];
    const summarizeCalls: string[] = [];
    const summary = createSummary();
    const api = {
      listForNote: async (id: string) => {
        listCalls.push(id);
        return { items: [] };
      },
      summarizeForNote: async (id: string) => {
        summarizeCalls.push(id);
        return summary;
      },
    };

    const emptyState = await loadSummaryHistoryViewState(api, noteId);
    const summarizedState = await summarizeNoteAndMapSummaryHistoryViewState(
      api,
      noteId,
      createIdleSummaryHistoryViewState(noteId),
    );

    expect(listCalls).toEqual([noteId]);
    expect(summarizeCalls).toEqual([noteId]);
    expect(emptyState.status).toBe("empty");
    expect(summarizedState.status).toBe("success");
    expect(summarizedState.items.map((item) => item.id)).toEqual([summary.id]);
  });
});
