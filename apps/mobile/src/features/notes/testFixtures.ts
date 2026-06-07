import type { Note } from "@synapse/shared";

import type { SummaryHistoryItem } from "./summaryHistoryApi";

export const noteId = "22222222-2222-4222-8222-222222222222";
export const otherNoteId = "33333333-3333-4333-8333-333333333333";
export const userId = "11111111-1111-4111-8111-111111111111";
export const createdAt = "2026-05-19T10:30:00.000Z";
export const updatedAt = "2026-05-19T11:30:00.000Z";

export function createNote(overrides: Partial<Note> = {}): Note {
  return {
    id: noteId,
    user_id: userId,
    title: "Planning note",
    content: "Decisions and follow-up items from the planning session.",
    content_type: "markdown",
    is_archived: false,
    is_deleted: false,
    created_at: createdAt,
    updated_at: updatedAt,
    deleted_at: null,
    version: 1,
    ...overrides,
  };
}

export function createSummary(
  overrides: Partial<SummaryHistoryItem> = {},
): SummaryHistoryItem {
  return {
    id: "44444444-4444-4444-8444-444444444444",
    user_id: userId,
    source_id: noteId,
    source_type: "note",
    content: "This note summarizes planning decisions.",
    action_items: [
      {
        text: "Follow up on the planning decision.",
        priority: "medium",
      },
    ],
    provider: "fake",
    model: "fake-summary-model",
    created_at: "2026-05-19T12:00:00.000Z",
    ...overrides,
  };
}

export function createInvalidResponseError(): Error {
  const error = new Error("Synthetic invalid response");
  error.name = "ApiInvalidResponseError";
  return error;
}
