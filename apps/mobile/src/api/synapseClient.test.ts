import type { FetchLike, FetchRequestInit } from "@synapse/api-client";

import { createNoteDetailApi } from "../features/notes/noteDetailApi";
import { createNoteListApi } from "../features/notes/noteListApi";
import { createSummaryHistoryApi } from "../features/notes/summaryHistoryApi";
import {
  createNote,
  createSummary,
  noteId,
} from "../features/notes/testFixtures";
import { describe, expect, it } from "../features/notes/testGlobals";
import { createMobileSynapseClient } from "./synapseClient";

type RecordedRequest = {
  readonly input: string;
  readonly method: string | undefined;
};

function createSuccessResponse(data: unknown, requestId: string) {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      data,
      meta: {
        request_id: requestId,
      },
    }),
  };
}

describe("createMobileSynapseClient", () => {
  it("composes with note list, note detail, and summary history adapters", async () => {
    const note = createNote();
    const summary = createSummary();
    const requests: RecordedRequest[] = [];
    const fetch: FetchLike = async (
      input: string,
      init?: FetchRequestInit,
    ) => {
      requests.push({
        input,
        method: init?.method,
      });

      if (input.endsWith("/notes?page=1&per_page=20")) {
        return createSuccessResponse(
          {
            items: [note],
            pagination: {
              page: 1,
              per_page: 20,
              total: 1,
              has_next: false,
            },
          },
          "req_mobile_client_list",
        );
      }

      if (input.endsWith(`/notes/${noteId}`)) {
        return createSuccessResponse(note, "req_mobile_client_detail");
      }

      if (input.endsWith(`/ai/notes/${noteId}/summaries`)) {
        return createSuccessResponse(
          {
            items: [summary],
          },
          "req_mobile_client_history",
        );
      }

      if (input.endsWith(`/ai/notes/${noteId}/summarize`)) {
        return createSuccessResponse(summary, "req_mobile_client_summarize");
      }

      throw new Error(`Unexpected mobile API request: ${input}`);
    };
    const client = createMobileSynapseClient({ fetch });
    const noteListApi = createNoteListApi(client);
    const noteDetailApi = createNoteDetailApi(client);
    const summaryHistoryApi = createSummaryHistoryApi(client);

    const noteList = await noteListApi.listNotes({ page: 1, per_page: 20 });
    const noteDetail = await noteDetailApi.getNote(noteId);
    const summaryHistory = await summaryHistoryApi.listForNote(noteId);
    const generatedSummary = await summaryHistoryApi.summarizeForNote(noteId);

    expect(noteList).toEqual({
      items: [note],
      pagination: {
        page: 1,
        per_page: 20,
        total: 1,
        has_next: false,
      },
    });
    expect(noteDetail).toEqual(note);
    expect(summaryHistory).toEqual({
      items: [summary],
    });
    expect(generatedSummary).toEqual(summary);

    expect(requests).toEqual([
      {
        input: "http://localhost:8000/v1/notes?page=1&per_page=20",
        method: "GET",
      },
      {
        input: `http://localhost:8000/v1/notes/${noteId}`,
        method: "GET",
      },
      {
        input: `http://localhost:8000/v1/ai/notes/${noteId}/summaries`,
        method: "GET",
      },
      {
        input: `http://localhost:8000/v1/ai/notes/${noteId}/summarize`,
        method: "POST",
      },
    ]);
  });
});
