import type {
  SummaryHistoryApi,
  SummaryHistoryData,
  SummaryHistoryItem,
} from "./summaryHistoryApi";

export const SUMMARY_HISTORY_EMPTY_MESSAGE = "No summaries generated yet.";
export const SUMMARY_HISTORY_LOADING_MESSAGE = "Loading summary history.";
export const SUMMARY_HISTORY_MEMORY_NOTICE =
  "Summary history is temporary in this demo and may clear when the development server restarts.";
export const SUMMARY_HISTORY_UNAVAILABLE_MESSAGE =
  "Summary history is unavailable right now.";
export const SUMMARY_HISTORY_NOT_FOUND_MESSAGE = "We could not find that note.";
export const SUMMARY_HISTORY_INVALID_RESPONSE_MESSAGE =
  "Summary history could not be displayed because the response was not recognized.";

export type SummaryHistoryStatus =
  | "idle"
  | "loading"
  | "empty"
  | "success"
  | "error";

export type SummaryHistoryErrorReason =
  | "not_found"
  | "invalid_response"
  | "unavailable";

export type SummaryHistoryActionItem = {
  readonly text: SummaryHistoryItem["action_items"][number]["text"];
  readonly priority: SummaryHistoryItem["action_items"][number]["priority"];
};

export type SummaryHistoryListItem = {
  readonly id: SummaryHistoryItem["id"];
  readonly content: SummaryHistoryItem["content"];
  readonly createdAt: SummaryHistoryItem["created_at"];
  readonly actionItems: readonly SummaryHistoryActionItem[];
};

export type SummaryHistoryViewState = {
  readonly status: SummaryHistoryStatus;
  readonly noteId: string | null;
  readonly items: readonly SummaryHistoryListItem[];
  readonly message: string;
  readonly memoryNotice: string;
  readonly isLoading: boolean;
  readonly canRetry: boolean;
  readonly errorReason: SummaryHistoryErrorReason | null;
};

export function createIdleSummaryHistoryViewState(
  noteId: string | null = null,
): SummaryHistoryViewState {
  return {
    status: "idle",
    noteId,
    items: [],
    message: "",
    memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function createLoadingSummaryHistoryViewState(
  noteId: string,
): SummaryHistoryViewState {
  return {
    status: "loading",
    noteId,
    items: [],
    message: SUMMARY_HISTORY_LOADING_MESSAGE,
    memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
    isLoading: true,
    canRetry: false,
    errorReason: null,
  };
}

export function mapSummaryHistoryDataToViewState(
  noteId: string,
  data: SummaryHistoryData,
): SummaryHistoryViewState {
  const items = sortSummariesNewestFirst(data.items).map(
    toSummaryHistoryListItem,
  );

  if (items.length === 0) {
    return {
      status: "empty",
      noteId,
      items,
      message: SUMMARY_HISTORY_EMPTY_MESSAGE,
      memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
      isLoading: false,
      canRetry: false,
      errorReason: null,
    };
  }

  return {
    status: "success",
    noteId,
    items,
    message: summaryCountMessage(items.length),
    memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
    isLoading: false,
    canRetry: false,
    errorReason: null,
  };
}

export function mapSummaryHistoryErrorToViewState(
  noteId: string,
  error: unknown,
): SummaryHistoryViewState {
  const errorRecord = toErrorRecord(error);

  if (errorRecord.name === "ApiInvalidResponseError") {
    return createErrorSummaryHistoryViewState(
      noteId,
      "invalid_response",
      SUMMARY_HISTORY_INVALID_RESPONSE_MESSAGE,
      false,
    );
  }

  if (errorRecord.status === 404 || errorRecord.code === "NOT_FOUND") {
    return createErrorSummaryHistoryViewState(
      noteId,
      "not_found",
      SUMMARY_HISTORY_NOT_FOUND_MESSAGE,
      false,
    );
  }

  return createErrorSummaryHistoryViewState(
    noteId,
    "unavailable",
    SUMMARY_HISTORY_UNAVAILABLE_MESSAGE,
    true,
  );
}

export async function loadSummaryHistoryViewState(
  api: Pick<SummaryHistoryApi, "listForNote">,
  noteId: string,
): Promise<SummaryHistoryViewState> {
  try {
    const data = await api.listForNote(noteId);
    return mapSummaryHistoryDataToViewState(noteId, data);
  } catch (error) {
    return mapSummaryHistoryErrorToViewState(noteId, error);
  }
}

function createErrorSummaryHistoryViewState(
  noteId: string,
  errorReason: SummaryHistoryErrorReason,
  message: string,
  canRetry: boolean,
): SummaryHistoryViewState {
  return {
    status: "error",
    noteId,
    items: [],
    message,
    memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
    isLoading: false,
    canRetry,
    errorReason,
  };
}

function toSummaryHistoryListItem(
  summary: SummaryHistoryItem,
): SummaryHistoryListItem {
  return {
    id: summary.id,
    content: summary.content,
    createdAt: summary.created_at,
    actionItems: summary.action_items.map((actionItem) => ({
      text: actionItem.text,
      priority: actionItem.priority,
    })),
  };
}

function sortSummariesNewestFirst(
  summaries: readonly SummaryHistoryItem[],
): SummaryHistoryItem[] {
  return [...summaries].sort((left, right) => {
    const createdAtDifference =
      toTimestamp(right.created_at) - toTimestamp(left.created_at);

    if (createdAtDifference !== 0) {
      return createdAtDifference;
    }

    return right.id.localeCompare(left.id);
  });
}

function toTimestamp(value: string): number {
  const parsed = Date.parse(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function summaryCountMessage(count: number): string {
  return count === 1 ? "1 summary available." : `${count} summaries available.`;
}

function toErrorRecord(error: unknown): Record<string, unknown> {
  return typeof error === "object" && error !== null
    ? (error as Record<string, unknown>)
    : {};
}
