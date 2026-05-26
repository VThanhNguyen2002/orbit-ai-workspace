import { describe, expect, it } from "vitest";

import {
  CreateNoteRequestSchema,
  DeleteNoteRequestSchema,
  ListNotesRequestSchema,
  ListNotesResponseSchema,
  NoteSchema,
  UpdateNoteRequestSchema,
} from "./index";
import {
  note_id,
  operation_id,
  request_id,
  timestamp,
  user_id,
  validNote,
} from "./__fixtures__/contracts";

describe("Notes contract schemas", () => {
  it("parses a valid snake_case note with nested sync metadata", () => {
    expect(NoteSchema.parse(validNote)).toEqual(validNote);
  });

  it("rejects an equivalent camelCase note payload", () => {
    const result = NoteSchema.safeParse({
      id: note_id,
      userId: user_id,
      title: "Planning note",
      content: "Decisions and follow-up items from the planning session.",
      contentType: "markdown",
      isArchived: false,
      isDeleted: false,
      createdAt: timestamp,
      updatedAt: timestamp,
      deletedAt: null,
      version: 1,
      syncMetadata: {
        lastSyncedAt: timestamp,
        pendingOperationIds: [operation_id],
        conflictIds: [],
      },
    });

    expect(result.success).toBe(false);
  });

  it("rejects an invalid note", () => {
    const result = NoteSchema.safeParse({
      ...validNote,
      title: "",
      version: -1,
    });

    expect(result.success).toBe(false);
  });

  it("parses a valid create note request with defaults", () => {
    expect(
      CreateNoteRequestSchema.parse({
        title: "Planning note",
      }),
    ).toEqual({
      title: "Planning note",
      content: "",
      content_type: "plain",
    });

    expect(
      CreateNoteRequestSchema.parse({
        title: "Planning note",
        content: "Decisions and follow-up items.",
        content_type: "markdown",
      }),
    ).toEqual({
      title: "Planning note",
      content: "Decisions and follow-up items.",
      content_type: "markdown",
    });
  });

  it("rejects server-controlled fields in create note requests", () => {
    const result = CreateNoteRequestSchema.safeParse({
      id: note_id,
      user_id,
      title: "Planning note",
      content: "Decisions and follow-up items.",
      content_type: "markdown",
      is_archived: false,
      is_deleted: false,
      created_at: timestamp,
      updated_at: timestamp,
      deleted_at: null,
      version: 1,
    });

    expect(result.success).toBe(false);
  });

  it("requires version for update note requests", () => {
    expect(
      UpdateNoteRequestSchema.parse({
        title: "Updated title",
        version: 1,
      }),
    ).toEqual({
      title: "Updated title",
      version: 1,
    });

    expect(
      UpdateNoteRequestSchema.safeParse({
        title: "Updated title",
      }).success,
    ).toBe(false);
  });

  it("requires version for delete note requests", () => {
    expect(DeleteNoteRequestSchema.parse({ version: 1 })).toEqual({
      version: 1,
    });

    expect(DeleteNoteRequestSchema.safeParse({}).success).toBe(false);
  });

  it("parses note list pagination and filters", () => {
    expect(ListNotesRequestSchema.parse({})).toEqual({
      page: 1,
      per_page: 20,
      sort: "updated_at",
      order: "desc",
      include_deleted: false,
    });

    expect(
      ListNotesRequestSchema.parse({
        page: 2,
        per_page: 25,
        sort: "title",
        order: "asc",
        is_archived: true,
        include_deleted: true,
      }),
    ).toEqual({
      page: 2,
      per_page: 25,
      sort: "title",
      order: "asc",
      is_archived: true,
      include_deleted: true,
    });
  });

  it("parses a snake_case list notes response", () => {
    const response = {
      data: {
        items: [validNote],
        pagination: {
          page: 1,
          per_page: 20,
          total: 1,
          has_next: false,
        },
      },
      meta: { request_id },
    };

    expect(ListNotesResponseSchema.parse(response)).toEqual(response);
  });

  it("rejects camelCase note CRUD contracts", () => {
    expect(
      CreateNoteRequestSchema.safeParse({
        title: "Planning note",
        contentType: "markdown",
      }).success,
    ).toBe(false);

    expect(
      ListNotesRequestSchema.safeParse({
        includeDeleted: true,
      }).success,
    ).toBe(false);

    expect(
      ListNotesResponseSchema.safeParse({
        data: {
          items: [validNote],
          pagination: {
            page: 1,
            perPage: 20,
            total: 1,
            hasNext: false,
          },
        },
        meta: { requestId: request_id },
      }).success,
    ).toBe(false);
  });
});
