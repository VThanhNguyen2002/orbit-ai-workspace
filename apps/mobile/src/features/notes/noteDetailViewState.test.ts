import {
  createIdleNoteDetailViewState,
  createLoadingNoteDetailViewState,
  loadNoteDetailViewState,
  mapNoteDetailDataToViewState,
  mapNoteDetailErrorToViewState,
  NOTE_DETAIL_INVALID_RESPONSE_MESSAGE,
  NOTE_DETAIL_LOADING_MESSAGE,
  NOTE_DETAIL_NOT_FOUND_MESSAGE,
  NOTE_DETAIL_SUCCESS_MESSAGE,
  NOTE_DETAIL_UNAVAILABLE_MESSAGE,
} from "./noteDetailViewState";
import { createInvalidResponseError, createNote, noteId } from "./testFixtures";
import { describe, expect, it } from "./testGlobals";

describe("note detail view-state", () => {
  it("creates an idle state", () => {
    expect(createIdleNoteDetailViewState(noteId)).toEqual({
      status: "idle",
      noteId,
      note: null,
      message: "",
      isLoading: false,
      canRetry: false,
      errorReason: null,
    });
  });

  it("creates a loading state", () => {
    expect(createLoadingNoteDetailViewState(noteId)).toEqual({
      status: "loading",
      noteId,
      note: null,
      message: NOTE_DETAIL_LOADING_MESSAGE,
      isLoading: true,
      canRetry: false,
      errorReason: null,
    });
  });

  it("maps a note safely for display", () => {
    const note = createNote({
      content_type: "plain",
      is_archived: true,
      version: 3,
    });

    const state = mapNoteDetailDataToViewState(note);

    expect(state).toEqual({
      status: "success",
      noteId: note.id,
      note: {
        id: note.id,
        title: note.title,
        content: note.content,
        contentType: "plain",
        isArchived: true,
        isDeleted: false,
        createdAt: note.created_at,
        updatedAt: note.updated_at,
        deletedAt: null,
        version: 3,
      },
      message: NOTE_DETAIL_SUCCESS_MESSAGE,
      isLoading: false,
      canRetry: false,
      errorReason: null,
    });
  });

  it("maps not-found and unavailable errors to UI-safe states", () => {
    const notFound = mapNoteDetailErrorToViewState(noteId, {
      status: 404,
      code: "NOT_FOUND",
      message: "Synthetic missing note diagnostic",
    });
    const unavailable = mapNoteDetailErrorToViewState(
      noteId,
      new Error("Synthetic backend stack detail"),
    );

    expect(notFound).toMatchObject({
      status: "error",
      noteId,
      note: null,
      message: NOTE_DETAIL_NOT_FOUND_MESSAGE,
      canRetry: false,
      errorReason: "not_found",
    });
    expect(unavailable).toMatchObject({
      status: "error",
      noteId,
      note: null,
      message: NOTE_DETAIL_UNAVAILABLE_MESSAGE,
      canRetry: true,
      errorReason: "unavailable",
    });
    expect(notFound.message).not.toContain("Synthetic missing note diagnostic");
    expect(unavailable.message).not.toContain("Synthetic backend stack detail");
  });

  it("maps invalid responses without exposing raw backend diagnostics", () => {
    const state = mapNoteDetailErrorToViewState(
      noteId,
      createInvalidResponseError(),
    );

    expect(state).toMatchObject({
      status: "error",
      noteId,
      note: null,
      message: NOTE_DETAIL_INVALID_RESPONSE_MESSAGE,
      canRetry: false,
      errorReason: "invalid_response",
    });
    expect(state.message).not.toContain("Synthetic invalid response");
  });

  it("loads state through the injected API", async () => {
    const calls: string[] = [];
    const api = {
      getNote: async (id: string) => {
        calls.push(id);
        return createNote({ id });
      },
    };

    const state = await loadNoteDetailViewState(api, noteId);

    expect(calls).toEqual([noteId]);
    expect(state.status).toBe("success");
    expect(state.note?.id).toBe(noteId);
  });
});
