import {
  createIdleNoteDetailViewState,
  type NoteDetailViewState,
} from "./noteDetailViewState";

export const NOTE_DETAIL_PLACEHOLDER_REGIONS = [
  "note-detail-status",
  "note-detail-title",
  "note-detail-content",
  "note-detail-metadata",
  "note-detail-actions",
  "note-detail-summary-entry-point",
] as const;

export const NOTE_DETAIL_PLACEHOLDER_NON_GOALS = [
  "No rendered mobile UI while Expo initialization is deferred.",
  "No direct network calls from future screen modules.",
  "No credential, diagnostic, provider-specific, or backend-specific display data.",
] as const;

export type NoteDetailPlaceholder = {
  readonly name: "NoteDetail";
  readonly noteId: string;
  readonly state: NoteDetailViewState;
  readonly regions: typeof NOTE_DETAIL_PLACEHOLDER_REGIONS;
  readonly nonGoals: typeof NOTE_DETAIL_PLACEHOLDER_NON_GOALS;
};

export function createNoteDetailPlaceholder(
  noteId: string,
  state: NoteDetailViewState = createIdleNoteDetailViewState(noteId),
): NoteDetailPlaceholder {
  return {
    name: "NoteDetail",
    noteId,
    state,
    regions: NOTE_DETAIL_PLACEHOLDER_REGIONS,
    nonGoals: NOTE_DETAIL_PLACEHOLDER_NON_GOALS,
  };
}
