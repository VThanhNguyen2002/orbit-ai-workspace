import { describe, expect, it } from "vitest";

import {
  ApiClientError,
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

const note = {
  id: "note_test",
  user_id: "dev_user",
  title: "Planning note",
  content: "Decisions and follow-up items.",
  content_type: "markdown",
  is_archived: false,
  is_deleted: false,
  created_at: "2026-05-22T03:00:00.000Z",
  updated_at: "2026-05-22T03:00:00.000Z",
  deleted_at: null,
  version: 1,
} as const;

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

  it("lists notes with snake_case query parameters", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: {
          items: [note],
          pagination: {
            page: 2,
            per_page: 10,
            total: 11,
            has_next: true,
          },
        },
        meta: successMeta,
      })),
    });

    await expect(
      client.notes.list({
        page: 2,
        per_page: 10,
        sort: "title",
        order: "asc",
        is_archived: false,
        include_deleted: true,
      }),
    ).resolves.toEqual({
      data: {
        items: [note],
        pagination: {
          page: 2,
          per_page: 10,
          total: 11,
          has_next: true,
        },
      },
      meta: successMeta,
    });
    expect(requests[0]).toEqual({
      input:
        "https://api.example.test/v1/notes?page=2&per_page=10&sort=title&order=asc&is_archived=false&include_deleted=true",
      init: {
        headers: {
          Accept: "application/json",
        },
        method: "GET",
      },
    });
  });

  it("creates notes with shared request defaults", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(201, {
        data: {
          ...note,
          content: "",
          content_type: "plain",
        },
        meta: successMeta,
      })),
      getAuthToken: () => "token_notes",
    });

    await expect(client.notes.create({ title: "Planning note" })).resolves.toEqual({
      data: {
        ...note,
        content: "",
        content_type: "plain",
      },
      meta: successMeta,
    });
    expect(requests[0]?.input).toBe("https://api.example.test/v1/notes");
    expect(requests[0]?.init.method).toBe("POST");
    expect(requests[0]?.init.headers).toEqual({
      Accept: "application/json",
      Authorization: "Bearer token_notes",
      "Content-Type": "application/json",
    });
    expect(parseRequestBody(requests[0])).toEqual({
      title: "Planning note",
      content: "",
      content_type: "plain",
    });
  });

  it("gets a note by id", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: note,
        meta: successMeta,
      })),
    });

    await expect(client.notes.get("note/id")).resolves.toEqual({
      data: note,
      meta: successMeta,
    });
    expect(requests[0]?.input).toBe("https://api.example.test/v1/notes/note%2Fid");
    expect(requests[0]?.init.method).toBe("GET");
  });

  it("updates notes with versioned PATCH payloads", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: {
          ...note,
          title: "Updated note",
          version: 2,
        },
        meta: successMeta,
      })),
    });

    await expect(
      client.notes.update(note.id, {
        title: "Updated note",
        is_archived: true,
        version: 1,
      }),
    ).resolves.toMatchObject({
      data: {
        title: "Updated note",
        version: 2,
      },
      meta: successMeta,
    });
    expect(requests[0]?.input).toBe(`https://api.example.test/v1/notes/${note.id}`);
    expect(requests[0]?.init.method).toBe("PATCH");
    expect(parseRequestBody(requests[0])).toEqual({
      title: "Updated note",
      is_archived: true,
      version: 1,
    });
  });

  it("soft deletes notes with versioned DELETE payloads", async () => {
    const requests: CapturedRequest[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch(requests, jsonResponse(200, {
        data: {
          ...note,
          is_deleted: true,
          deleted_at: "2026-05-22T03:01:00.000Z",
          version: 2,
        },
        meta: successMeta,
      })),
    });

    await expect(client.notes.delete(note.id, { version: 1 })).resolves.toMatchObject({
      data: {
        id: note.id,
        is_deleted: true,
        deleted_at: "2026-05-22T03:01:00.000Z",
        version: 2,
      },
      meta: successMeta,
    });
    expect(requests[0]?.input).toBe(`https://api.example.test/v1/notes/${note.id}`);
    expect(requests[0]?.init.method).toBe("DELETE");
    expect(parseRequestBody(requests[0])).toEqual({ version: 1 });
  });

  it("maps missing note responses to ApiClientError", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch([], jsonResponse(404, {
        error: {
          code: "NOT_FOUND",
          message: "Note not found",
          details: [
            {
              field: "note_id",
              message: "note_not_found",
            },
          ],
        },
        meta: {
          request_id: "req_missing",
        },
      })),
    });

    await expect(client.notes.get(note.id)).rejects.toMatchObject({
      name: "ApiClientError",
      code: "NOT_FOUND",
      requestId: "req_missing",
      status: 404,
    });
  });

  it("maps note version conflicts to ApiClientError with server data", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch([], jsonResponse(409, {
        error: {
          code: "CONFLICT",
          message: "Note version conflict",
          details: [
            {
              field: "version",
              message: "version_conflict",
              expected: 0,
              actual: 1,
              server_data: note,
            },
          ],
        },
        meta: {
          request_id: "req_conflict",
        },
      })),
    });

    await expect(
      client.notes.update(note.id, {
        title: "Updated note",
        version: 0,
      }),
    ).rejects.toMatchObject({
      name: "ApiClientError",
      code: "CONFLICT",
      requestId: "req_conflict",
      status: 409,
      envelope: {
        error: {
          details: [
            {
              server_data: note,
            },
          ],
        },
      },
    } satisfies Partial<ApiClientError>);
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

  it("rejects malformed note data in success envelopes", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test/v1",
      fetch: captureFetch([], jsonResponse(200, {
        data: {
          ...note,
          contentType: "markdown",
        },
        meta: successMeta,
      })),
    });

    await expect(client.notes.get(note.id)).rejects.toBeInstanceOf(
      ApiInvalidResponseError,
    );
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

function parseRequestBody(request: CapturedRequest | undefined): unknown {
  if (request?.init.body === undefined) {
    return undefined;
  }

  return JSON.parse(request.init.body);
}
