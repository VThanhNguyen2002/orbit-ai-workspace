export const user_id = "11111111-1111-4111-8111-111111111111";
export const note_id = "22222222-2222-4222-8222-222222222222";
export const operation_id = "33333333-3333-4333-8333-333333333333";
export const request_id = "req_contract_test";
export const timestamp = "2026-05-19T10:30:00.000Z";

export const validNote = {
  id: note_id,
  user_id,
  title: "Planning note",
  content: "Decisions and follow-up items from the planning session.",
  content_type: "markdown",
  is_archived: false,
  is_deleted: false,
  created_at: timestamp,
  updated_at: timestamp,
  deleted_at: null,
  version: 1,
  sync_metadata: {
    last_synced_at: timestamp,
    pending_operation_ids: [operation_id],
    conflict_ids: [],
  },
};
