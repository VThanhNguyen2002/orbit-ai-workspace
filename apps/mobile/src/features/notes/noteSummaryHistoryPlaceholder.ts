import {
  SUMMARY_HISTORY_MEMORY_NOTICE,
  createIdleSummaryHistoryViewState,
  type SummaryHistoryViewState,
} from "./summaryHistoryViewState";

export const NOTE_SUMMARY_HISTORY_PLACEHOLDER_REGIONS = [
  "summary-history-status",
  "summary-history-list",
  "summary-history-generate-action",
  "summary-history-reset-notice",
] as const;

export const NOTE_SUMMARY_HISTORY_PLACEHOLDER_NON_GOALS = [
  "No rendered mobile UI while Expo initialization is deferred.",
  "No direct network calls from future screen modules.",
  "No credential, prompt, diagnostic, or provider-specific display data.",
] as const;

export type NoteSummaryHistoryPlaceholder = {
  readonly name: "NoteSummaryHistory";
  readonly noteId: string;
  readonly state: SummaryHistoryViewState;
  readonly regions: typeof NOTE_SUMMARY_HISTORY_PLACEHOLDER_REGIONS;
  readonly memoryNotice: string;
  readonly nonGoals: typeof NOTE_SUMMARY_HISTORY_PLACEHOLDER_NON_GOALS;
};

export function createNoteSummaryHistoryPlaceholder(
  noteId: string,
  state: SummaryHistoryViewState = createIdleSummaryHistoryViewState(noteId),
): NoteSummaryHistoryPlaceholder {
  return {
    name: "NoteSummaryHistory",
    noteId,
    state,
    regions: NOTE_SUMMARY_HISTORY_PLACEHOLDER_REGIONS,
    memoryNotice: SUMMARY_HISTORY_MEMORY_NOTICE,
    nonGoals: NOTE_SUMMARY_HISTORY_PLACEHOLDER_NON_GOALS,
  };
}
