import { describe, expect, it } from "vitest";

import {
  ApiInvalidResponseError,
  ApiNetworkError,
  type FetchLike,
  type FetchRequestInit,
  type FetchResponseLike,
  buildUrl,
  createApiClient,
} from "./index";

const successMeta = {
  request_id: "req_test",
};

describe("@synapse/api-client", () => {
  it("builds URLs from the configured base URL", () => {
    expect(
      buildUrl("https://api.example.test/v1/", "/health", {
        page: 1,
        include: ["notes", "tasks"],
        empty: undefined,
      }),
    ).toBe("https://api.example.test/v1/health?page=1&include=notes&include=tasks");
  });

  it("fetches the health endpoint through a shared success envelope", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: {
          status: "ok",
          service: "synapse-api",
        },
        meta: successMeta,
      })),
    });

    await expect(client.health()).resolves.toEqual({
      data: {
        status: "ok",
        service: "synapse-api",
      },
      meta: successMeta,
    });
    expect(requests).toEqual([
      {
        input: "https://api.example.test/v1/health",
        init: {
          headers: {
            Accept: "application/json",
          },
          method: "GET",
        },
      },
    ]);
  });

  it("fetches version metadata and injects auth headers without owning auth state", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: {
          service: "synapse-api",
          version: "0.0.0",
          api_version: "v1",
        },
        meta: successMeta,
      })),
      getAuthToken: () => "token_test",
    });

    await expect(client.version()).resolves.toEqual({
      data: {
        service: "synapse-api",
        version: "0.0.0",
        api_version: "v1",
      },
      meta: successMeta,
    });
    expect(requests[0]?.init.headers).toEqual({
      Accept: "application/json",
      Authorization: "Bearer token_test",
    });
  });

  it("throws typed API errors from shared error envelopes", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch([], jsonResponse(409, {
        error: {
          code: "CONFLICT",
          message: "Entity has been modified",
          details: [
            {
              field: "version",
              expected: 3,
              actual: 4,
            },
          ],
        },
        meta: {
          request_id: "req_conflict",
        },
      })),
    });

    await expect(client.request("/notes/note-id")).rejects.toMatchObject({
      name: "ApiClientError",
      code: "CONFLICT",
      requestId: "req_conflict",
      status: 409,
    });
  });

  it("throws a network error when fetch fails before a response arrives", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: async () => {
        throw new Error("offline");
      },
    });

    await expect(client.health()).rejects.toBeInstanceOf(ApiNetworkError);
  });

  it("rejects malformed API envelopes", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch([], jsonResponse(200, {
        status: "ok",
      })),
    });

    await expect(client.health()).rejects.toBeInstanceOf(ApiInvalidResponseError);
  });
});

type CapturedRequest = {
  init: FetchRequestInit;
  input: string;
};

function captureFetch(
  requests: CapturedRequest[],
  response: FetchResponseLike,
): FetchLike {
  return async (input, init = {}) => {
    requests.push({ input, init });
    return response;
  };
}

function jsonResponse(status: number, body: unknown): FetchResponseLike {
  return {
    json: async () => body,
    ok: status >= 200 && status < 300,
    status,
  };
}
