import {
  createIdleNoteMutationViewState,
  createNoteAndMapMutationViewState,
  createSubmittingNoteMutationViewState,
  deleteNoteAndMapMutationViewState,
  mapNoteMutationDataToViewState,
  mapNoteMutationErrorToViewState,
  NOTE_MUTATION_CONFLICT_MESSAGE,
  NOTE_MUTATION_CREATE_SUBMITTING_MESSAGE,
  NOTE_MUTATION_CREATE_SUCCESS_MESSAGE,
  NOTE_MUTATION_DELETE_SUBMITTING_MESSAGE,
  NOTE_MUTATION_DELETE_SUCCESS_MESSAGE,
  NOTE_MUTATION_INVALID_RESPONSE_MESSAGE,
  NOTE_MUTATION_NOT_FOUND_MESSAGE,
  NOTE_MUTATION_UNAVAILABLE_MESSAGE,
  NOTE_MUTATION_UPDATE_SUBMITTING_MESSAGE,
  NOTE_MUTATION_UPDATE_SUCCESS_MESSAGE,
  updateNoteAndMapMutationViewState,
} from "./noteMutationViewState";
import { createInvalidResponseError, createNote, noteId } from "./testFixtures";
import { describe, expect, it } from "./testGlobals";

describe("note mutation view-state", () => {
  it("creates idle and submitting states for note mutations", () => {
    expect(createIdleNoteMutationViewState()).toEqual({
      status: "idle",
      operation: null,
      noteId: null,
      note: null,
      message: "",
      isSubmitting: false,
      canRetry: false,
      errorReason: null,
    });
    expect(createIdleNoteMutationViewState("update", noteId)).toMatchObject({
      status: "idle",
      operation: "update",
      noteId,
      isSubmitting: false,
    });
    expect(createSubmittingNoteMutationViewState("create")).toMatchObject({
      status: "submitting",
      operation: "create",
      noteId: null,
      message: NOTE_MUTATION_CREATE_SUBMITTING_MESSAGE,
      isSubmitting: true,
    });
    expect(createSubmittingNoteMutationViewState("update", noteId)).toMatchObject({
      status: "submitting",
      operation: "update",
      noteId,
      message: NOTE_MUTATION_UPDATE_SUBMITTING_MESSAGE,
      isSubmitting: true,
    });
    expect(createSubmittingNoteMutationViewState("delete", noteId)).toMatchObject({
      status: "submitting",
      operation: "delete",
      noteId,
      message: NOTE_MUTATION_DELETE_SUBMITTING_MESSAGE,
      isSubmitting: true,
    });
  });

  it("maps create success into a future-screen-ready state", async () => {
    const calls: unknown[] = [];
    const note = createNote({
      content: "",
      content_type: "plain",
    });
    const api = {
      createNote: async (payload: unknown) => {
        calls.push(payload);
        return note;
      },
    };

    const state = await createNoteAndMapMutationViewState(api, {
      title: "Planning note",
      content: "",
      content_type: "plain",
    });

    expect(calls).toEqual([
      {
        title: "Planning note",
        content: "",
        content_type: "plain",
      },
    ]);
    expect(state).toEqual({
      status: "success",
      operation: "create",
      noteId: note.id,
      note: {
        id: note.id,
        title: note.title,
        content: "",
        contentType: "plain",
        isArchived: false,
        isDeleted: false,
        createdAt: note.created_at,
        updatedAt: note.updated_at,
        deletedAt: null,
        version: 1,
      },
      message: NOTE_MUTATION_CREATE_SUCCESS_MESSAGE,
      isSubmitting: false,
      canRetry: false,
      errorReason: null,
    });
  });

  it("maps update success and version conflicts to UI-safe states", async () => {
    const calls: unknown[] = [];
    const updatedNote = createNote({
      title: "Updated planning note",
      is_archived: true,
      version: 2,
    });
    const successApi = {
      updateNote: async (id: string, payload: unknown) => {
        calls.push({ id, payload });
        return updatedNote;
      },
    };
    const conflictApi = {
      updateNote: async () => {
        throw {
          status: 409,
          code: "CONFLICT",
          message: "Synthetic conflict detail with raw credential marker",
        };
      },
    };

    const success = await updateNoteAndMapMutationViewState(successApi, noteId, {
      title: "Updated planning note",
      version: 1,
    });
    const conflict = await updateNoteAndMapMutationViewState(
      conflictApi,
      noteId,
      {
        title: "Updated planning note",
        version: 0,
      },
    );

    expect(calls).toEqual([
      {
        id: noteId,
        payload: {
          title: "Updated planning note",
          version: 1,
        },
      },
    ]);
    expect(success).toMatchObject({
      status: "success",
      operation: "update",
      noteId,
      message: NOTE_MUTATION_UPDATE_SUCCESS_MESSAGE,
      errorReason: null,
    });
    expect(success.note).toMatchObject({
      title: "Updated planning note",
      isArchived: true,
      version: 2,
    });
    expect(conflict).toMatchObject({
      status: "error",
      operation: "update",
      noteId,
      note: null,
      message: NOTE_MUTATION_CONFLICT_MESSAGE,
      isSubmitting: false,
      canRetry: false,
      errorReason: "conflict",
    });
    expect(JSON.stringify(conflict)).not.toContain("Synthetic conflict detail");
    expect(JSON.stringify(conflict)).not.toContain("credential marker");
  });

  it("maps delete success and errors without raw diagnostics", async () => {
    const calls: unknown[] = [];
    const deletedNote = createNote({
      is_deleted: true,
      deleted_at: "2026-05-19T12:30:00.000Z",
      version: 2,
    });
    const successApi = {
      deleteNote: async (id: string, payload: unknown) => {
        calls.push({ id, payload });
        return deletedNote;
      },
    };
    const unavailableApi = {
      deleteNote: async () => {
        throw new Error("Synthetic delete backend diagnostic");
      },
    };

    const success = await deleteNoteAndMapMutationViewState(
      successApi,
      noteId,
      {
        version: 1,
      },
    );
    const unavailable = await deleteNoteAndMapMutationViewState(
      unavailableApi,
      noteId,
      {
        version: 1,
      },
    );

    expect(calls).toEqual([
      {
        id: noteId,
        payload: {
          version: 1,
        },
      },
    ]);
    expect(success).toMatchObject({
      status: "success",
      operation: "delete",
      noteId,
      message: NOTE_MUTATION_DELETE_SUCCESS_MESSAGE,
      errorReason: null,
    });
    expect(success.note).toMatchObject({
      isDeleted: true,
      deletedAt: "2026-05-19T12:30:00.000Z",
      version: 2,
    });
    expect(unavailable).toMatchObject({
      status: "error",
      operation: "delete",
      noteId,
      message: NOTE_MUTATION_UNAVAILABLE_MESSAGE,
      canRetry: true,
      errorReason: "unavailable",
    });
    expect(JSON.stringify(unavailable)).not.toContain(
      "Synthetic delete backend diagnostic",
    );
  });

  it("maps invalid-response and not-found mutation errors safely", () => {
    const invalidResponse = mapNoteMutationErrorToViewState(
      "create",
      null,
      createInvalidResponseError(),
    );
    const notFound = mapNoteMutationErrorToViewState("delete", noteId, {
      status: 404,
      code: "NOT_FOUND",
      message: "Synthetic missing-note backend detail",
    });

    expect(invalidResponse).toMatchObject({
      status: "error",
      operation: "create",
      noteId: null,
      message: NOTE_MUTATION_INVALID_RESPONSE_MESSAGE,
      canRetry: false,
      errorReason: "invalid_response",
    });
    expect(notFound).toMatchObject({
      status: "error",
      operation: "delete",
      noteId,
      message: NOTE_MUTATION_NOT_FOUND_MESSAGE,
      canRetry: false,
      errorReason: "not_found",
    });
    expect(JSON.stringify(invalidResponse)).not.toContain(
      "Synthetic invalid response",
    );
    expect(JSON.stringify(notFound)).not.toContain(
      "Synthetic missing-note backend detail",
    );
  });

  it("maps mutation data consistently for all operations", () => {
    const note = createNote({
      content_type: "plain",
      version: 4,
    });

    expect(mapNoteMutationDataToViewState("update", note)).toMatchObject({
      status: "success",
      operation: "update",
      noteId: note.id,
      message: NOTE_MUTATION_UPDATE_SUCCESS_MESSAGE,
      note: {
        id: note.id,
        contentType: "plain",
        version: 4,
      },
    });
  });
});
