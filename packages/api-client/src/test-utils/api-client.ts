import type { FetchLike, FetchRequestInit, FetchResponseLike } from "../index";

export const successMeta = {
  request_id: "req_test",
};

export const note = {
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

export type CapturedRequest = {
  init: FetchRequestInit;
  input: string;
};

export function captureFetch(
  requests: CapturedRequest[],
  response: FetchResponseLike,
): FetchLike {
  return async (input, init = {}) => {
    requests.push({ input, init });
    return response;
  };
}

export function jsonResponse(status: number, body: unknown): FetchResponseLike {
  return {
    json: async () => body,
    ok: status >= 200 && status < 300,
    status,
  };
}

export function parseRequestBody(request: CapturedRequest | undefined): unknown {
  if (request?.init.body === undefined) {
    return undefined;
  }

  return JSON.parse(request.init.body);
}
