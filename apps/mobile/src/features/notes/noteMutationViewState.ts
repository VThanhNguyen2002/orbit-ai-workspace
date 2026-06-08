import type {
  CreateNoteMutationPayload,
  DeleteNoteMutationPayload,
  NoteMutationApi,
  NoteMutationData,
  UpdateNoteMutationPayload,
} from "./noteMutationApi";
import { toErrorRecord } from "./viewStateError";

export const NOTE_MUTATION_CREATE_SUBMITTING_MESSAGE = "Creating note.";
export const NOTE_MUTATION_CREATE_SUCCESS_MESSAGE = "Note created.";
export const NOTE_MUTATION_UPDATE_SUBMITTING_MESSAGE = "Saving note.";
export const NOTE_MUTATION_UPDATE_SUCCESS_MESSAGE = "Note updated.";
export const NOTE_MUTATION_DELETE_SUBMITTING_MESSAGE = "Deleting note.";
export const NOTE_MUTATION_DELETE_SUCCESS_MESSAGE = "Note deleted.";
export const NOTE_MUTATION_CONFLICT_MESSAGE =
  "This note changed elsewhere. Reload it before saving.";
export const NOTE_MUTATION_NOT_FOUND_MESSAGE = "We could not find that note.";
export const NOTE_MUTATION_UNAVAILABLE_MESSAGE =
  "Note changes are unavailable right now.";
export const NOTE_MUTATION_INVALID_RESPONSE_MESSAGE =
  "Note changes could not be saved because the response was not recognized.";

export type NoteMutationOperation = "create" | "update" | "delete";
export type NoteMutationStatus = "idle" | "submitting" | "success" | "error";
export type NoteMutationErrorReason =
  | "conflict"
  | "not_found"
  | "invalid_response"
  | "unavailable";

export type NoteMutationResult = {
  readonly id: NoteMutationData["id"];
  readonly title: NoteMutationData["title"];
  readonly content: NoteMutationData["content"];
  readonly contentType: NoteMutationData["content_type"];
  readonly isArchived: NoteMutationData["is_archived"];
  readonly isDeleted: NoteMutationData["is_deleted"];
  readonly createdAt: NoteMutationData["created_at"];
  readonly updatedAt: NoteMutationData["updated_at"];
  readonly deletedAt: NoteMutationData["deleted_at"];
  readonly version: NoteMutationData["version"];
};

export type NoteMutationViewState = {
  readonly status: NoteMutationStatus;
  readonly operation: NoteMutationOperation | null;
  readonly noteId: string | null;
  readonly note: NoteMutationResult | null;
  readonly message: string;
  readonly isSubmitting: boolean;
  readonly canRetry: boolean;
  readonly errorReason: NoteMutationErrorReason | null;
};

export function createIdleNoteMutationViewState(
  operation: NoteMutationOperation | null = null,
  noteId: string | null = null,
): NoteMutationViewState {
  return {
    status: "idle",
    operation,
    noteId,
    note: null,
    message: "",
    isSubmitting: false,
    canRetry: false,
    errorReason: null,
  };
}

export function createSubmittingNoteMutationViewState(
  operation: NoteMutationOperation,
  noteId: string | null = null,
): NoteMutationViewState {
  return {
    status: "submitting",
    operation,
    noteId,
    note: null,
    message: submittingMessage(operation),
    isSubmitting: true,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteMutationDataToViewState(
  operation: NoteMutationOperation,
  note: NoteMutationData,
): NoteMutationViewState {
  return {
    status: "success",
    operation,
    noteId: note.id,
    note: toNoteMutationResult(note),
    message: successMessage(operation),
    isSubmitting: false,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteMutationErrorToViewState(
  operation: NoteMutationOperation,
  noteId: string | null,
  error: unknown,
): NoteMutationViewState {
  const errorRecord = toErrorRecord(error);

  if (errorRecord.name === "ApiInvalidResponseError") {
    return createErrorNoteMutationViewState(
      operation,
      noteId,
      "invalid_response",
      NOTE_MUTATION_INVALID_RESPONSE_MESSAGE,
      false,
    );
  }

  if (errorRecord.status === 409 || errorRecord.code === "CONFLICT") {
    return createErrorNoteMutationViewState(
      operation,
      noteId,
      "conflict",
      NOTE_MUTATION_CONFLICT_MESSAGE,
      false,
    );
  }

  if (errorRecord.status === 404 || errorRecord.code === "NOT_FOUND") {
    return createErrorNoteMutationViewState(
      operation,
      noteId,
      "not_found",
      NOTE_MUTATION_NOT_FOUND_MESSAGE,
      false,
    );
  }

  return createErrorNoteMutationViewState(
    operation,
    noteId,
    "unavailable",
    NOTE_MUTATION_UNAVAILABLE_MESSAGE,
    true,
  );
}

export async function createNoteAndMapMutationViewState(
  api: Pick<NoteMutationApi, "createNote">,
  payload: CreateNoteMutationPayload,
): Promise<NoteMutationViewState> {
  try {
    const note = await api.createNote(payload);
    return mapNoteMutationDataToViewState("create", note);
  } catch (error) {
    return mapNoteMutationErrorToViewState("create", null, error);
  }
}

export async function updateNoteAndMapMutationViewState(
  api: Pick<NoteMutationApi, "updateNote">,
  noteId: string,
  payload: UpdateNoteMutationPayload,
): Promise<NoteMutationViewState> {
  try {
    const note = await api.updateNote(noteId, payload);
    return mapNoteMutationDataToViewState("update", note);
  } catch (error) {
    return mapNoteMutationErrorToViewState("update", noteId, error);
  }
}

export async function deleteNoteAndMapMutationViewState(
  api: Pick<NoteMutationApi, "deleteNote">,
  noteId: string,
  payload: DeleteNoteMutationPayload,
): Promise<NoteMutationViewState> {
  try {
    const note = await api.deleteNote(noteId, payload);
    return mapNoteMutationDataToViewState("delete", note);
  } catch (error) {
    return mapNoteMutationErrorToViewState("delete", noteId, error);
  }
}

function createErrorNoteMutationViewState(
  operation: NoteMutationOperation,
  noteId: string | null,
  errorReason: NoteMutationErrorReason,
  message: string,
  canRetry: boolean,
): NoteMutationViewState {
  return {
    status: "error",
    operation,
    noteId,
    note: null,
    message,
    isSubmitting: false,
    canRetry,
    errorReason,
  };
}

function toNoteMutationResult(note: NoteMutationData): NoteMutationResult {
  return {
    id: note.id,
    title: note.title,
    content: note.content,
    contentType: note.content_type,
    isArchived: note.is_archived,
    isDeleted: note.is_deleted,
    createdAt: note.created_at,
    updatedAt: note.updated_at,
    deletedAt: note.deleted_at,
    version: note.version,
  };
}

function submittingMessage(operation: NoteMutationOperation): string {
  if (operation === "create") {
    return NOTE_MUTATION_CREATE_SUBMITTING_MESSAGE;
  }

  if (operation === "update") {
    return NOTE_MUTATION_UPDATE_SUBMITTING_MESSAGE;
  }

  return NOTE_MUTATION_DELETE_SUBMITTING_MESSAGE;
}

function successMessage(operation: NoteMutationOperation): string {
  if (operation === "create") {
    return NOTE_MUTATION_CREATE_SUCCESS_MESSAGE;
  }

  if (operation === "update") {
    return NOTE_MUTATION_UPDATE_SUCCESS_MESSAGE;
  }

  return NOTE_MUTATION_DELETE_SUCCESS_MESSAGE;
}
