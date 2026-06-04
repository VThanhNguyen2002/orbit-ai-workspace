import { describe, expect, it } from "vitest";

import {
  ApiClientError,
  ApiInvalidResponseError,
  createApiClient,
} from "./index";
import {
  type CapturedRequest,
  captureFetch,
  jsonResponse,
  successMeta,
} from "./test-utils/api-client";

/** Minimal valid Summary fixture matching SummarySchema (EntityIdSchema requires UUIDs). */
const summary = {
  id: "11111111-1111-4111-8111-111111111111",
  user_id: "22222222-2222-4222-8222-222222222222",
  source_id: "33333333-3333-4333-8333-333333333333",
  source_type: "note" as const,
  content: "This note covers key decisions and follow-up items.",
  action_items: [
    { text: "Review key decisions", priority: "high" as const },
    { text: "Schedule follow-up", priority: "medium" as const },
  ],
  provider: "fake",
  model: "fake-model-v1",
  created_at: "2026-05-30T11:00:00.000Z",
} as const;

describe("@synapse/api-client ai", () => {
  it("posts to the correct summarize path", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        requests,
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
    });

    await client.ai.summarizeNote("note_test_id");

    expect(requests[0]?.input).toBe(
      "https://api.example.test/v1/ai/notes/note_test_id/summarize",
    );
    expect(requests[0]?.init.method).toBe("POST");
  });

  it("url-encodes the note_id in the summarize path", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        requests,
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
    });

    await client.ai.summarizeNote("note/with/slashes");

    expect(requests[0]?.input).toBe(
      "https://api.example.test/v1/ai/notes/note%2Fwith%2Fslashes/summarize",
    );
  });

  it("includes auth header when getAuthToken returns a token", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        requests,
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
      getAuthToken: () => "tok_ai_test",
    });

    await client.ai.summarizeNote(summary.source_id);

    expect(requests[0]?.init.headers).toEqual({
      Accept: "application/json",
      Authorization: "Bearer tok_ai_test",
    });
  });

  it("omits auth header when getAuthToken is not configured", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        requests,
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
    });

    await client.ai.summarizeNote(summary.source_id);

    expect(requests[0]?.init.headers).toEqual({
      Accept: "application/json",
    });
    expect(requests[0]?.init.headers).not.toHaveProperty("Authorization");
  });

  it("returns the validated summary and meta on success", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
    });

    await expect(
      client.ai.summarizeNote(summary.source_id),
    ).resolves.toEqual({ data: summary, meta: successMeta });
  });

  it("preserves snake_case fields in the summary response", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(200, { data: summary, meta: successMeta }),
      ),
    });

    const { data } = await client.ai.summarizeNote(summary.source_id);

    expect(data).toHaveProperty("source_id");
    expect(data).toHaveProperty("source_type");
    expect(data).toHaveProperty("action_items");
    expect(data).toHaveProperty("created_at");
    expect(data).not.toHaveProperty("sourceId");
    expect(data).not.toHaveProperty("sourceType");
    expect(data).not.toHaveProperty("actionItems");
    expect(data).not.toHaveProperty("createdAt");
  });

  it("maps 503 feature_disabled to ApiClientError", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(503, {
          error: {
            code: "UNPROCESSABLE",
            message: "AI summarization is not enabled",
            details: [
              {
                field: "ai_summarization_enabled",
                message: "feature_disabled",
              },
            ],
          },
          meta: { request_id: "req_disabled" },
        }),
      ),
    });

    await expect(
      client.ai.summarizeNote(summary.source_id),
    ).rejects.toMatchObject({
      name: "ApiClientError",
      code: "UNPROCESSABLE",
      requestId: "req_disabled",
      status: 503,
    } satisfies Partial<ApiClientError>);
  });

  it("maps 404 note_not_found to ApiClientError", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(404, {
          error: {
            code: "NOT_FOUND",
            message: "Note not found",
            details: [{ field: "note_id", message: "note_not_found" }],
          },
          meta: { request_id: "req_missing" },
        }),
      ),
    });

    await expect(
      client.ai.summarizeNote("no-such-note"),
    ).rejects.toMatchObject({
      name: "ApiClientError",
      code: "NOT_FOUND",
      requestId: "req_missing",
      status: 404,
    } satisfies Partial<ApiClientError>);
  });

  it("rejects a response where summary data does not match the shared contract", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        // action_items missing; should fail SummarySchema validation
        jsonResponse(200, {
          data: {
            id: "sum_bad",
            user_id: "dev_user",
            source_id: "note_id",
            source_type: "note",
            content: "Some summary content.",
            provider: "fake",
            model: "fake-model-v1",
            created_at: "2026-05-30T11:00:00.000Z",
            // 'action_items' intentionally omitted to trigger validation failure
          },
          meta: successMeta,
        }),
      ),
    });

    await expect(
      client.ai.summarizeNote(summary.source_id),
    ).rejects.toBeInstanceOf(ApiInvalidResponseError);
  });

  it("rejects a response with camelCase fields in summary data", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(200, {
          data: {
            ...summary,
            actionItems: summary.action_items, // camelCase alias
          },
          meta: successMeta,
        }),
      ),
    });

    // strictObject in SummarySchema rejects unknown keys → ApiInvalidResponseError
    await expect(
      client.ai.summarizeNote(summary.source_id),
    ).rejects.toBeInstanceOf(ApiInvalidResponseError);
  });

  it("gets summary history from the correct encoded path", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        requests,
        jsonResponse(200, {
          data: { items: [summary] },
          meta: successMeta,
        }),
      ),
    });

    await client.ai.listNoteSummaries("note/with/slashes");

    expect(requests[0]).toEqual({
      input:
        "https://api.example.test/v1/ai/notes/note%2Fwith%2Fslashes/summaries",
      init: {
        headers: {
          Accept: "application/json",
        },
        method: "GET",
      },
    });
  });

  it("returns validated snake_case summary history data and meta", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(200, {
          data: { items: [summary] },
          meta: successMeta,
        }),
      ),
    });

    await expect(
      client.ai.listNoteSummaries(summary.source_id),
    ).resolves.toEqual({
      data: { items: [summary] },
      meta: successMeta,
    });
  });

  it("maps 404 summary history responses to ApiClientError", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(404, {
          error: {
            code: "NOT_FOUND",
            message: "Note not found",
            details: [{ field: "note_id", message: "note_not_found" }],
          },
          meta: { request_id: "req_history_missing" },
        }),
      ),
    });

    await expect(
      client.ai.listNoteSummaries("no-such-note"),
    ).rejects.toMatchObject({
      name: "ApiClientError",
      code: "NOT_FOUND",
      requestId: "req_history_missing",
      status: 404,
    } satisfies Partial<ApiClientError>);
  });

  it("rejects camelCase fields in summary history data", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(
        [],
        jsonResponse(200, {
          data: {
            items: [
              {
                ...summary,
                actionItems: summary.action_items,
              },
            ],
          },
          meta: successMeta,
        }),
      ),
    });

    await expect(
      client.ai.listNoteSummaries(summary.source_id),
    ).rejects.toBeInstanceOf(ApiInvalidResponseError);
  });

  // SSE streaming is intentionally not tested here — deferred to Slice 7E.
  it("does not include any SSE or streaming behavior", () => {
    const client = createApiClient({ baseUrl: "https://api.example.test/v1" });
    // The method returns a plain Promise, not a ReadableStream or EventSource.
    const returnValue = client.ai.summarizeNote(summary.source_id).catch(
      () => undefined,
    );
    expect(returnValue).toBeInstanceOf(Promise);
    expect(returnValue).not.toHaveProperty("getReader");
  });
});
