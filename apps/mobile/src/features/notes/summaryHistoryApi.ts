import type { AiApi } from "@synapse/api-client";
import {
  ListSummariesDataSchema,
  SummarySchema,
  type ListSummariesData,
  type Summary,
} from "@synapse/shared";

export type SummaryHistoryData = ListSummariesData;
export type SummaryHistoryItem = ListSummariesData["items"][number];

export type SummaryHistoryApiClient = {
  readonly ai: Pick<AiApi, "listNoteSummaries" | "summarizeNote">;
};

export type SummaryHistoryApi = {
  readonly listForNote: (noteId: string) => Promise<SummaryHistoryData>;
  readonly summarizeForNote: (noteId: string) => Promise<Summary>;
};

export function createSummaryHistoryApi(
  client: SummaryHistoryApiClient,
): SummaryHistoryApi {
  return {
    listForNote: async (noteId) => {
      const response = await client.ai.listNoteSummaries(noteId);
      return ListSummariesDataSchema.parse(response.data);
    },
    summarizeForNote: async (noteId) => {
      const response = await client.ai.summarizeNote(noteId);
      return SummarySchema.parse(response.data);
    },
  };
}
