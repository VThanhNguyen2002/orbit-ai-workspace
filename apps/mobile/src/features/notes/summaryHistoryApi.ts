import type { AiApi } from "@synapse/api-client";
import {
  ListSummariesDataSchema,
  type ListSummariesData,
} from "@synapse/shared";

export type SummaryHistoryData = ListSummariesData;
export type SummaryHistoryItem = ListSummariesData["items"][number];

export type SummaryHistoryApiClient = {
  readonly ai: Pick<AiApi, "listNoteSummaries">;
};

export type SummaryHistoryApi = {
  readonly listForNote: (noteId: string) => Promise<SummaryHistoryData>;
};

export function createSummaryHistoryApi(
  client: SummaryHistoryApiClient,
): SummaryHistoryApi {
  return {
    listForNote: async (noteId) => {
      const response = await client.ai.listNoteSummaries(noteId);
      return ListSummariesDataSchema.parse(response.data);
    },
  };
}
