import type { NoteDetailApi, NoteDetailData } from "./noteDetailApi";
import { toErrorRecord } from "./viewStateError";

export const NOTE_DETAIL_LOADING_MESSAGE = "Loading note.";
export const NOTE_DETAIL_SUCCESS_MESSAGE = "Note loaded.";
export const NOTE_DETAIL_UNAVAILABLE_MESSAGE =
  "Note detail is unavailable right now.";
export const NOTE_DETAIL_NOT_FOUND_MESSAGE = "We could not find that note.";
export const NOTE_DETAIL_INVALID_RESPONSE_MESSAGE =
  "Note detail could not be displayed because the response was not recognized.";

export type NoteDetailStatus = "idle" | "loading" | "success" | "error";

export type NoteDetailErrorReason =
  | "not_found"
  | "invalid_response"
  | "unavailable";

export type NoteDetail = {
  readonly id: NoteDetailData["id"];
  readonly title: NoteDetailData["title"];
  readonly content: NoteDetailData["content"];
  readonly contentType: NoteDetailData["content_type"];
  readonly isArchived: NoteDetailData["is_archived"];
  readonly isDeleted: NoteDetailData["is_deleted"];
  readonly createdAt: NoteDetailData["created_at"];
  readonly updatedAt: NoteDetailData["updated_at"];
  readonly deletedAt: NoteDetailData["deleted_at"];
  readonly version: NoteDetailData["version"];
};

export type NoteDetailViewState = {
  readonly status: NoteDetailStatus;
  readonly noteId: string | null;
  readonly note: NoteDetail | null;
  readonly message: string;
  readonly isLoading: boolean;
  readonly canRetry: boolean;
  readonly errorReason: NoteDetailErrorReason | null;
};

export function createIdleNoteDetailViewState(
  noteId: string | null = null,
): NoteDetailViewState {
  return {
    status: "idle",
    noteId,
    note: null,
    message: "",
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function createLoadingNoteDetailViewState(
  noteId: string,
): NoteDetailViewState {
  return {
    status: "loading",
    noteId,
    note: null,
    message: NOTE_DETAIL_LOADING_MESSAGE,
    isLoading: true,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteDetailDataToViewState(
  note: NoteDetailData,
): NoteDetailViewState {
  return {
    status: "success",
    noteId: note.id,
    note: toNoteDetail(note),
    message: NOTE_DETAIL_SUCCESS_MESSAGE,
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteDetailErrorToViewState(
  noteId: string,
  error: unknown,
): NoteDetailViewState {
  const errorRecord = toErrorRecord(error);

  if (errorRecord.name === "ApiInvalidResponseError") {
    return createErrorNoteDetailViewState(
      noteId,
      "invalid_response",
      NOTE_DETAIL_INVALID_RESPONSE_MESSAGE,
      false,
    );
  }

  if (errorRecord.status === 404 || errorRecord.code === "NOT_FOUND") {
    return createErrorNoteDetailViewState(
      noteId,
      "not_found",
      NOTE_DETAIL_NOT_FOUND_MESSAGE,
      false,
    );
  }

  return createErrorNoteDetailViewState(
    noteId,
    "unavailable",
    NOTE_DETAIL_UNAVAILABLE_MESSAGE,
    true,
  );
}

export async function loadNoteDetailViewState(
  api: Pick<NoteDetailApi, "getNote">,
  noteId: string,
): Promise<NoteDetailViewState> {
  try {
    const note = await api.getNote(noteId);
    return mapNoteDetailDataToViewState(note);
  } catch (error) {
    return mapNoteDetailErrorToViewState(noteId, error);
  }
}

function createErrorNoteDetailViewState(
  noteId: string,
  errorReason: NoteDetailErrorReason,
  message: string,
  canRetry: boolean,
): NoteDetailViewState {
  return {
    status: "error",
    noteId,
    note: null,
    message,
    isLoading: false,
    canRetry,
    errorReason,
  };
}

function toNoteDetail(note: NoteDetailData): NoteDetail {
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
