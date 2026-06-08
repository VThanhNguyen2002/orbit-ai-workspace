import type {
  NoteListApi,
  NoteListData,
  NoteListItemData,
  NoteListPaginationData,
  NoteListQuery,
} from "./noteListApi";
import { toErrorRecord } from "./viewStateError";

export const NOTE_LIST_EMPTY_MESSAGE = "No notes yet.";
export const NOTE_LIST_LOADING_MESSAGE = "Loading notes.";
export const NOTE_LIST_UNAVAILABLE_MESSAGE = "Notes are unavailable right now.";
export const NOTE_LIST_INVALID_RESPONSE_MESSAGE =
  "Notes could not be displayed because the response was not recognized.";
export const NOTE_LIST_CONTENT_PREVIEW_MAX_LENGTH = 160;

export type NoteListStatus =
  | "idle"
  | "loading"
  | "empty"
  | "success"
  | "error";

export type NoteListErrorReason = "invalid_response" | "unavailable";

export type NoteListItem = {
  readonly id: NoteListItemData["id"];
  readonly title: NoteListItemData["title"];
  readonly contentPreview: string;
  readonly contentType: NoteListItemData["content_type"];
  readonly isArchived: NoteListItemData["is_archived"];
  readonly isDeleted: NoteListItemData["is_deleted"];
  readonly createdAt: NoteListItemData["created_at"];
  readonly updatedAt: NoteListItemData["updated_at"];
  readonly deletedAt: NoteListItemData["deleted_at"];
  readonly version: NoteListItemData["version"];
};

export type NoteListPagination = {
  readonly page: NoteListPaginationData["page"];
  readonly perPage: NoteListPaginationData["per_page"];
  readonly total: NoteListPaginationData["total"];
  readonly hasNext: NoteListPaginationData["has_next"];
};

export type NoteListViewState = {
  readonly status: NoteListStatus;
  readonly items: readonly NoteListItem[];
  readonly pagination: NoteListPagination | null;
  readonly message: string;
  readonly isLoading: boolean;
  readonly canRetry: boolean;
  readonly errorReason: NoteListErrorReason | null;
};

export function createIdleNoteListViewState(): NoteListViewState {
  return {
    status: "idle",
    items: [],
    pagination: null,
    message: "",
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function createLoadingNoteListViewState(): NoteListViewState {
  return {
    status: "loading",
    items: [],
    pagination: null,
    message: NOTE_LIST_LOADING_MESSAGE,
    isLoading: true,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteListDataToViewState(
  data: NoteListData,
): NoteListViewState {
  const items = data.items.map(toNoteListItem);
  const pagination = toNoteListPagination(data.pagination);

  if (items.length === 0) {
    return {
      status: "empty",
      items,
      pagination,
      message: NOTE_LIST_EMPTY_MESSAGE,
      isLoading: false,
      canRetry: false,
      errorReason: null,
    };
  }

  return {
    status: "success",
    items,
    pagination,
    message: noteCountMessage(pagination.total),
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function mapNoteListErrorToViewState(error: unknown): NoteListViewState {
  const errorRecord = toErrorRecord(error);

  if (errorRecord.name === "ApiInvalidResponseError") {
    return createErrorNoteListViewState(
      "invalid_response",
      NOTE_LIST_INVALID_RESPONSE_MESSAGE,
      false,
    );
  }

  return createErrorNoteListViewState(
    "unavailable",
    NOTE_LIST_UNAVAILABLE_MESSAGE,
    true,
  );
}

export async function loadNoteListViewState(
  api: Pick<NoteListApi, "listNotes">,
  query?: NoteListQuery,
): Promise<NoteListViewState> {
  try {
    const data = await api.listNotes(query);
    return mapNoteListDataToViewState(data);
  } catch (error) {
    return mapNoteListErrorToViewState(error);
  }
}

function createErrorNoteListViewState(
  errorReason: NoteListErrorReason,
  message: string,
  canRetry: boolean,
): NoteListViewState {
  return {
    status: "error",
    items: [],
    pagination: null,
    message,
    isLoading: false,
    canRetry,
    errorReason,
  };
}

function toNoteListItem(note: NoteListItemData): NoteListItem {
  return {
    id: note.id,
    title: note.title,
    contentPreview: toContentPreview(note.content),
    contentType: note.content_type,
    isArchived: note.is_archived,
    isDeleted: note.is_deleted,
    createdAt: note.created_at,
    updatedAt: note.updated_at,
    deletedAt: note.deleted_at,
    version: note.version,
  };
}

function toNoteListPagination(
  pagination: NoteListPaginationData,
): NoteListPagination {
  return {
    page: pagination.page,
    perPage: pagination.per_page,
    total: pagination.total,
    hasNext: pagination.has_next,
  };
}

function toContentPreview(content: string): string {
  const normalized = content.replace(/\s+/g, " ").trim();

  if (normalized.length <= NOTE_LIST_CONTENT_PREVIEW_MAX_LENGTH) {
    return normalized;
  }

  return `${normalized
    .slice(0, NOTE_LIST_CONTENT_PREVIEW_MAX_LENGTH - 3)
    .trimEnd()}...`;
}

function noteCountMessage(total: number): string {
  return total === 1 ? "1 note available." : `${total} notes available.`;
}
