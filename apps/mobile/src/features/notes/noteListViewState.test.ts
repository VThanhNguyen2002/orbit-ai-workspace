import {
  createIdleNoteListViewState,
  createLoadingNoteListViewState,
  loadNoteListViewState,
  mapNoteListDataToViewState,
  mapNoteListErrorToViewState,
  NOTE_LIST_EMPTY_MESSAGE,
  NOTE_LIST_INVALID_RESPONSE_MESSAGE,
  NOTE_LIST_LOADING_MESSAGE,
  NOTE_LIST_UNAVAILABLE_MESSAGE,
} from "./noteListViewState";
import { createInvalidResponseError, createNote } from "./testFixtures";
import { describe, expect, it } from "./testGlobals";

describe("note list view-state", () => {
  it("creates an idle state", () => {
    expect(createIdleNoteListViewState()).toEqual({
      status: "idle",
      items: [],
      pagination: null,
      message: "",
      isLoading: false,
      canRetry: false,
      errorReason: null,
    });
  });

  it("creates a loading state", () => {
    expect(createLoadingNoteListViewState()).toMatchObject({
      status: "loading",
      items: [],
      pagination: null,
      message: NOTE_LIST_LOADING_MESSAGE,
      isLoading: true,
      canRetry: false,
      errorReason: null,
    });
  });

  it("maps an empty response to a UI-safe empty state", () => {
    const state = mapNoteListDataToViewState({
      items: [],
      pagination: {
        page: 1,
        per_page: 20,
        total: 0,
        has_next: false,
      },
    });

    expect(state).toMatchObject({
      status: "empty",
      items: [],
      message: NOTE_LIST_EMPTY_MESSAGE,
      isLoading: false,
      canRetry: false,
      errorReason: null,
    });
    expect(state.pagination).toEqual({
      page: 1,
      perPage: 20,
      total: 0,
      hasNext: false,
    });
  });

  it("maps a success response while preserving API ordering", () => {
    const firstNote = createNote({
      id: "22222222-2222-4222-8222-222222222222",
      title: "First note",
      content: " First note body with extra whitespace. ",
      updated_at: "2026-05-19T13:00:00.000Z",
    });
    const secondNote = createNote({
      id: "33333333-3333-4333-8333-333333333333",
      title: "Second note",
      content: "Second note body.",
      updated_at: "2026-05-19T12:00:00.000Z",
    });

    const state = mapNoteListDataToViewState({
      items: [firstNote, secondNote],
      pagination: {
        page: 1,
        per_page: 20,
        total: 2,
        has_next: false,
      },
    });

    expect(state.status).toBe("success");
    expect(state.message).toBe("2 notes available.");
    expect(state.items.map((item) => item.id)).toEqual([
      firstNote.id,
      secondNote.id,
    ]);
    expect(state.items[0]).toMatchObject({
      id: firstNote.id,
      title: "First note",
      contentPreview: "First note body with extra whitespace.",
      contentType: "markdown",
      isArchived: false,
      isDeleted: false,
      createdAt: firstNote.created_at,
      updatedAt: firstNote.updated_at,
      deletedAt: null,
      version: 1,
    });
  });

  it("maps errors to UI-safe messages without raw diagnostics", () => {
    const unavailable = mapNoteListErrorToViewState(
      new Error("Synthetic backend detail for tests"),
    );
    const invalidResponse = mapNoteListErrorToViewState(
      createInvalidResponseError(),
    );

    expect(unavailable).toMatchObject({
      status: "error",
      items: [],
      pagination: null,
      message: NOTE_LIST_UNAVAILABLE_MESSAGE,
      isLoading: false,
      canRetry: true,
      errorReason: "unavailable",
    });
    expect(invalidResponse).toMatchObject({
      status: "error",
      message: NOTE_LIST_INVALID_RESPONSE_MESSAGE,
      canRetry: false,
      errorReason: "invalid_response",
    });
    expect(unavailable.message).not.toContain("Synthetic backend detail");
    expect(invalidResponse.message).not.toContain("Synthetic invalid response");
  });

  it("loads state through the injected API", async () => {
    const calls: unknown[] = [];
    const api = {
      listNotes: async (query?: unknown) => {
        calls.push(query);
        return {
          items: [createNote()],
          pagination: {
            page: 2,
            per_page: 10,
            total: 1,
            has_next: false,
          },
        };
      },
    };

    const state = await loadNoteListViewState(api, { page: 2, per_page: 10 });

    expect(calls).toEqual([{ page: 2, per_page: 10 }]);
    expect(state.status).toBe("success");
    expect(state.items).toHaveLength(1);
  });
});
