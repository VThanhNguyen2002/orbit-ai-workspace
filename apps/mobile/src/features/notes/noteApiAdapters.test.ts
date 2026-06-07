import { createNoteDetailApi } from "./noteDetailApi";
import { createNoteListApi } from "./noteListApi";
import { createSummaryHistoryApi } from "./summaryHistoryApi";
import { createNote, createSummary, noteId } from "./testFixtures";
import { describe, expect, it } from "./testGlobals";

describe("mobile note API adapters", () => {
  it("uses the injected note list client method and validates shared schemas", async () => {
    const calls: unknown[] = [];
    const note = createNote();
    const api = createNoteListApi({
      notes: {
        list: async (query) => {
          calls.push(query);
          return {
            data: {
              items: [note],
              pagination: {
                page: 1,
                per_page: 20,
                total: 1,
                has_next: false,
              },
            },
            meta: {
              request_id: "req_mobile_list",
            },
          };
        },
      },
    });

    const data = await api.listNotes({ page: 1 });

    expect(data).toEqual({
      items: [note],
      pagination: {
        page: 1,
        per_page: 20,
        total: 1,
        has_next: false,
      },
    });
    expect(calls).toEqual([{ page: 1 }]);
  });

  it("uses the injected note detail client method and rejects invalid data", async () => {
    const calls: string[] = [];
    const api = createNoteDetailApi({
      notes: {
        get: async (id) => {
          calls.push(id);
          return {
            data: {
              ...createNote({ id }),
              title: "",
            },
            meta: {
              request_id: "req_mobile_detail",
            },
          };
        },
      },
    });

    try {
      await api.getNote(noteId);
      throw new Error("Expected shared schema validation to reject");
    } catch (error) {
      expect(error).toMatchObject({
        name: "ZodError",
      });
    }
    expect(calls).toEqual([noteId]);
  });

  it("uses injected summary history client methods and validates summary data", async () => {
    const listCalls: string[] = [];
    const summarizeCalls: string[] = [];
    const summary = createSummary();
    const api = createSummaryHistoryApi({
      ai: {
        listNoteSummaries: async (id) => {
          listCalls.push(id);
          return {
            data: {
              items: [summary],
            },
            meta: {
              request_id: "req_mobile_history",
            },
          };
        },
        summarizeNote: async (id) => {
          summarizeCalls.push(id);
          return {
            data: summary,
            meta: {
              request_id: "req_mobile_summarize",
            },
          };
        },
      },
    });

    expect(await api.listForNote(noteId)).toEqual({ items: [summary] });
    expect(await api.summarizeForNote(noteId)).toEqual(summary);
    expect(listCalls).toEqual([noteId]);
    expect(summarizeCalls).toEqual([noteId]);
  });
});
