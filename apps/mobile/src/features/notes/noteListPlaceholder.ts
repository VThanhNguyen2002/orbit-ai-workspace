import {
  createIdleNoteListViewState,
  type NoteListViewState,
} from "./noteListViewState";

export const NOTE_LIST_PLACEHOLDER_REGIONS = [
  "note-list-status",
  "note-list-filter-summary",
  "note-list-items",
  "note-list-pagination-boundary",
  "note-list-empty-state",
] as const;

export const NOTE_LIST_PLACEHOLDER_NON_GOALS = [
  "No rendered mobile UI while Expo initialization is deferred.",
  "No direct network calls from future screen modules.",
  "No credential, diagnostic, provider-specific, or backend-specific display data.",
] as const;

export type NoteListPlaceholder = {
  readonly name: "NoteList";
  readonly state: NoteListViewState;
  readonly regions: typeof NOTE_LIST_PLACEHOLDER_REGIONS;
  readonly nonGoals: typeof NOTE_LIST_PLACEHOLDER_NON_GOALS;
};

export function createNoteListPlaceholder(
  state: NoteListViewState = createIdleNoteListViewState(),
): NoteListPlaceholder {
  return {
    name: "NoteList",
    state,
    regions: NOTE_LIST_PLACEHOLDER_REGIONS,
    nonGoals: NOTE_LIST_PLACEHOLDER_NON_GOALS,
  };
}
