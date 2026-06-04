import {
  ApiErrorEnvelopeSchema,
  ApiSuccessEnvelopeSchema,
  CreateNoteRequestSchema,
  DeleteNoteRequestSchema,
  ListSummariesDataSchema,
  SummarySchema,
  UpdateNoteRequestSchema,
  type ApiErrorCode,
  type ApiErrorEnvelope,
  type ApiMeta,
  type ApiSuccessEnvelope,
  type CreateNoteRequest,
  type DeleteNoteRequest,
  type JsonValue,
  type ListNotesRequest,
  type ListNotesResponse,
  type ListSummariesResponse,
  type Note,
  type NoteContentType,
  type PaginationMeta,
  type Summary,
  type SyncMetadata,
  type UpdateNoteRequest,
} from "@synapse/shared";

export const DEFAULT_API_BASE_URL = "http://localhost:8000/v1";

export type ApiSuccessResponse<TData> = Omit<ApiSuccessEnvelope, "data"> & {
  data: TData;
};

export type HealthData = {
  status: "ok";
  service: string;
};

export type VersionData = {
  service: string;
  version: string;
  api_version: string;
};

export type ListNotesData = ListNotesResponse["data"];
export type ListNotesQuery = Partial<ListNotesRequest>;
export type ListSummariesData = ListSummariesResponse["data"];

export type NotesApi = {
  list: (query?: ListNotesQuery) => Promise<ApiSuccessResponse<ListNotesData>>;
  create: (payload: CreateNoteRequest) => Promise<ApiSuccessResponse<Note>>;
  get: (note_id: string) => Promise<ApiSuccessResponse<Note>>;
  update: (
    note_id: string,
    payload: UpdateNoteRequest,
  ) => Promise<ApiSuccessResponse<Note>>;
  delete: (
    note_id: string,
    payload: DeleteNoteRequest,
  ) => Promise<ApiSuccessResponse<Note>>;
};

/** AI feature namespace on {@link SynapseApiClient}.
 *
 * NOTE: SSE streaming is deferred to Slice 7E.
 */
export type AiApi = {
  summarizeNote: (note_id: string) => Promise<ApiSuccessResponse<Summary>>;
  listNoteSummaries: (
    note_id: string,
  ) => Promise<ApiSuccessResponse<ListSummariesData>>;
};

export type QueryValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | readonly (string | number | boolean | null | undefined)[];

export type ApiRequestOptions<TData> = {
  body?: JsonValue;
  headers?: Record<string, string>;
  method?: HttpMethod;
  parseData?: (data: unknown) => TData;
  query?: Record<string, QueryValue>;
  signal?: unknown;
};

export type ApiClientConfig = {
  baseUrl?: string;
  fetch?: FetchLike;
  getAuthToken?: () => Promise<string | null | undefined> | string | null | undefined;
};

export type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export type FetchRequestInit = {
  body?: string | undefined;
  headers?: Record<string, string>;
  method?: string;
  signal?: unknown | undefined;
};

export type FetchResponseLike = {
  json: () => Promise<unknown>;
  ok: boolean;
  status: number;
};

export type FetchLike = (
  input: string,
  init?: FetchRequestInit,
) => Promise<FetchResponseLike>;

type UnknownRecord = Record<string, unknown>;

export class ApiClientError extends Error {
  readonly code: ApiErrorCode;
  readonly envelope: ApiErrorEnvelope;
  readonly requestId: string;
  readonly status: number;

  constructor(status: number, envelope: ApiErrorEnvelope) {
    super(envelope.error.message);
    this.name = "ApiClientError";
    this.code = envelope.error.code;
    this.envelope = envelope;
    this.requestId = envelope.meta.request_id;
    this.status = status;
  }
}

export class ApiNetworkError extends Error {
  readonly cause: unknown;

  constructor(cause: unknown) {
    super("Network request failed");
    this.name = "ApiNetworkError";
    this.cause = cause;
  }
}

export class ApiInvalidResponseError extends Error {
  readonly responseBody: unknown;
  readonly status: number;

  constructor(status: number, responseBody: unknown, message: string) {
    super(message);
    this.name = "ApiInvalidResponseError";
    this.responseBody = responseBody;
    this.status = status;
  }
}

export class SynapseApiClient {
  readonly notes: NotesApi;
  readonly ai: AiApi;

  private readonly baseUrl: string;
  private readonly fetcher: FetchLike;
  private readonly getAuthToken?: ApiClientConfig["getAuthToken"];

  constructor(config: ApiClientConfig = {}) {
    this.baseUrl = normalizeBaseUrl(config.baseUrl ?? DEFAULT_API_BASE_URL);
    this.fetcher = config.fetch ?? getDefaultFetch();
    this.getAuthToken = config.getAuthToken;
    this.notes = {
      list: (query) => this.listNotes(query),
      create: (payload) => this.createNote(payload),
      get: (note_id) => this.getNote(note_id),
      update: (note_id, payload) => this.updateNote(note_id, payload),
      delete: (note_id, payload) => this.deleteNote(note_id, payload),
    };
    this.ai = {
      summarizeNote: (note_id) => this.doSummarizeNote(note_id),
      listNoteSummaries: (note_id) => this.listNoteSummaries(note_id),
    };
  }

  async request<TData = unknown>(
    path: string,
    options: ApiRequestOptions<TData> = {},
  ): Promise<ApiSuccessResponse<TData>> {
    const response = await this.fetch(path, options);
    const responseBody = await readJson(response);

    if (!response.ok) {
      const errorEnvelope = ApiErrorEnvelopeSchema.safeParse(responseBody);

      if (!errorEnvelope.success) {
        throw new ApiInvalidResponseError(
          response.status,
          responseBody,
          "API error response did not match the shared error envelope",
        );
      }

      throw new ApiClientError(response.status, errorEnvelope.data);
    }

    const successEnvelope = ApiSuccessEnvelopeSchema.safeParse(responseBody);

    if (!successEnvelope.success) {
      throw new ApiInvalidResponseError(
        response.status,
        responseBody,
        "API success response did not match the shared success envelope",
      );
    }

    const data = options.parseData
      ? options.parseData(successEnvelope.data.data)
      : (successEnvelope.data.data as TData);

    return {
      data,
      meta: successEnvelope.data.meta as ApiMeta,
    };
  }

  health(): Promise<ApiSuccessResponse<HealthData>> {
    return this.request("/health", {
      parseData: parseHealthData,
    });
  }

  version(): Promise<ApiSuccessResponse<VersionData>> {
    return this.request("/version", {
      parseData: parseVersionData,
    });
  }

  private listNotes(
    query: ListNotesQuery = {},
  ): Promise<ApiSuccessResponse<ListNotesData>> {
    return this.request("/notes", {
      parseData: parseListNotesData,
      query: notesListQuery(query),
    });
  }

  private createNote(
    payload: CreateNoteRequest,
  ): Promise<ApiSuccessResponse<Note>> {
    return this.request("/notes", {
      body: CreateNoteRequestSchema.parse(payload) as JsonValue,
      method: "POST",
      parseData: parseNoteData,
    });
  }

  private getNote(note_id: string): Promise<ApiSuccessResponse<Note>> {
    return this.request(`/notes/${encodeURIComponent(note_id)}`, {
      parseData: parseNoteData,
    });
  }

  private updateNote(
    note_id: string,
    payload: UpdateNoteRequest,
  ): Promise<ApiSuccessResponse<Note>> {
    return this.request(`/notes/${encodeURIComponent(note_id)}`, {
      body: UpdateNoteRequestSchema.parse(payload) as JsonValue,
      method: "PATCH",
      parseData: parseNoteData,
    });
  }

  private deleteNote(
    note_id: string,
    payload: DeleteNoteRequest,
  ): Promise<ApiSuccessResponse<Note>> {
    return this.request(`/notes/${encodeURIComponent(note_id)}`, {
      body: DeleteNoteRequestSchema.parse(payload) as JsonValue,
      method: "DELETE",
      parseData: parseNoteData,
    });
  }

  private doSummarizeNote(
    note_id: string,
  ): Promise<ApiSuccessResponse<Summary>> {
    return this.request(`/ai/notes/${encodeURIComponent(note_id)}/summarize`, {
      method: "POST",
      parseData: parseSummaryData,
    });
  }

  private listNoteSummaries(
    note_id: string,
  ): Promise<ApiSuccessResponse<ListSummariesData>> {
    return this.request(`/ai/notes/${encodeURIComponent(note_id)}/summaries`, {
      parseData: parseListSummariesData,
    });
  }

  private async fetch<TData>(
    path: string,
    options: ApiRequestOptions<TData>,
  ): Promise<FetchResponseLike> {
    const requestInit: FetchRequestInit = {
      headers: await this.createHeaders(options),
      method: options.method ?? (options.body === undefined ? "GET" : "POST"),
    };

    if (options.body !== undefined) {
      requestInit.body = JSON.stringify(options.body);
    }

    if (options.signal !== undefined) {
      requestInit.signal = options.signal;
    }

    try {
      return await this.fetcher(
        buildUrl(this.baseUrl, path, options.query),
        requestInit,
      );
    } catch (error) {
      throw new ApiNetworkError(error);
    }
  }

  private async createHeaders<TData>(
    options: ApiRequestOptions<TData>,
  ): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      Accept: "application/json",
      ...options.headers,
    };

    if (options.body !== undefined && headers["Content-Type"] === undefined) {
      headers["Content-Type"] = "application/json";
    }

    const authToken = await this.getAuthToken?.();

    if (authToken) {
      headers.Authorization = `Bearer ${authToken}`;
    }

    return headers;
  }
}

export function createApiClient(config: ApiClientConfig = {}): SynapseApiClient {
  return new SynapseApiClient(config);
}

export function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

export function buildUrl(
  baseUrl: string,
  path: string,
  query?: Record<string, QueryValue>,
): string {
  const resolvedPath = path.startsWith("/") ? path : `/${path}`;
  const searchParams: string[] = [];

  for (const [key, value] of Object.entries(query ?? {})) {
    appendQueryValue(searchParams, key, value);
  }

  const queryString = searchParams.join("&");
  return `${normalizeBaseUrl(baseUrl)}${resolvedPath}${
    queryString ? `?${queryString}` : ""
  }`;
}

function appendQueryValue(
  searchParams: string[],
  key: string,
  value: QueryValue,
): void {
  if (Array.isArray(value)) {
    for (const item of value) {
      appendQueryValue(searchParams, key, item);
    }

    return;
  }

  if (value === undefined || value === null) {
    return;
  }

  searchParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
}

async function readJson(response: FetchResponseLike): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    throw new ApiInvalidResponseError(
      response.status,
      undefined,
      "API response was not valid JSON",
    );
  }
}

function getDefaultFetch(): FetchLike {
  const fetcher = (globalThis as { fetch?: FetchLike }).fetch;

  if (fetcher === undefined) {
    throw new ApiNetworkError("No fetch implementation is available");
  }

  return fetcher.bind(globalThis);
}

function parseHealthData(data: unknown): HealthData {
  const record = parseRecord(data, "Health response data did not match contract");

  if (record.status !== "ok") {
    throw new ApiInvalidResponseError(
      200,
      data,
      "Health response status did not match contract",
    );
  }

  return {
    status: "ok",
    service: parseString(record.service, data, "Health service"),
  };
}

function parseVersionData(data: unknown): VersionData {
  const record = parseRecord(data, "Version response data did not match contract");

  return {
    service: parseString(record.service, data, "Version service"),
    version: parseString(record.version, data, "Version value"),
    api_version: parseString(record.api_version, data, "API version value"),
  };
}

function parseListNotesData(data: unknown): ListNotesData {
  const record = parseRecord(data, "List notes response data did not match contract");
  assertOnlyFields(
    record,
    ["items", "pagination"],
    data,
    "List notes response data did not match contract",
  );

  if (!Array.isArray(record.items)) {
    throw new ApiInvalidResponseError(
      200,
      data,
      "List notes items did not match contract",
    );
  }

  return {
    items: record.items.map((item) => parseNoteData(item)),
    pagination: parsePaginationMeta(record.pagination, data),
  };
}

function parseNoteData(data: unknown): Note {
  const record = parseRecord(data, "Note response data did not match contract");
  assertOnlyFields(
    record,
    [
      "id",
      "user_id",
      "title",
      "content",
      "content_type",
      "is_archived",
      "is_deleted",
      "created_at",
      "updated_at",
      "deleted_at",
      "version",
      "sync_metadata",
    ],
    data,
    "Note response data did not match contract",
  );

  const note = {
    id: parseString(record.id, data, "Note id"),
    user_id: parseString(record.user_id, data, "Note user_id"),
    title: parseString(record.title, data, "Note title"),
    content: parseStringValue(record.content, data, "Note content"),
    content_type: parseNoteContentType(record.content_type, data),
    is_archived: parseBoolean(record.is_archived, data, "Note is_archived"),
    is_deleted: parseBoolean(record.is_deleted, data, "Note is_deleted"),
    created_at: parseString(record.created_at, data, "Note created_at"),
    updated_at: parseString(record.updated_at, data, "Note updated_at"),
    deleted_at: parseNullableString(record.deleted_at, data, "Note deleted_at"),
    version: parseNonNegativeInteger(record.version, data, "Note version"),
  };

  if (record.sync_metadata === undefined) {
    return note;
  }

  return {
    ...note,
    sync_metadata: parseSyncMetadata(record.sync_metadata, data),
  };
}

function parsePaginationMeta(value: unknown, body: unknown): PaginationMeta {
  const record = parseRecord(value, "Pagination metadata did not match contract");
  assertOnlyFields(
    record,
    ["page", "per_page", "total", "has_next"],
    body,
    "Pagination metadata did not match contract",
  );

  return {
    page: parsePositiveInteger(record.page, body, "Pagination page"),
    per_page: parsePositiveInteger(record.per_page, body, "Pagination per_page"),
    total: parseNonNegativeInteger(record.total, body, "Pagination total"),
    has_next: parseBoolean(record.has_next, body, "Pagination has_next"),
  };
}

function parseSyncMetadata(value: unknown, body: unknown): SyncMetadata {
  const record = parseRecord(value, "Note sync_metadata did not match contract");
  assertOnlyFields(
    record,
    ["last_synced_at", "pending_operation_ids", "conflict_ids"],
    body,
    "Note sync_metadata did not match contract",
  );

  return {
    last_synced_at: parseNullableString(
      record.last_synced_at,
      body,
      "Sync metadata last_synced_at",
    ),
    pending_operation_ids: parseStringArray(
      record.pending_operation_ids,
      body,
      "Sync metadata pending_operation_ids",
    ),
    conflict_ids: parseStringArray(
      record.conflict_ids,
      body,
      "Sync metadata conflict_ids",
    ),
  };
}

function parseRecord(data: unknown, message: string): UnknownRecord {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new ApiInvalidResponseError(200, data, message);
  }

  return data as UnknownRecord;
}

function parseString(value: unknown, body: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parseStringValue(value: unknown, body: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parseNullableString(
  value: unknown,
  body: unknown,
  label: string,
): string | null {
  if (value === null) {
    return null;
  }

  return parseString(value, body, label);
}

function parseBoolean(value: unknown, body: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parseNonNegativeInteger(
  value: unknown,
  body: unknown,
  label: string,
): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < 0) {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parsePositiveInteger(value: unknown, body: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value < 1) {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parseStringArray(value: unknown, body: unknown, label: string): string[] {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    throw new ApiInvalidResponseError(200, body, `${label} did not match contract`);
  }

  return value;
}

function parseNoteContentType(value: unknown, body: unknown): NoteContentType {
  if (value !== "plain" && value !== "markdown") {
    throw new ApiInvalidResponseError(
      200,
      body,
      "Note content_type did not match contract",
    );
  }

  return value;
}

function assertOnlyFields(
  record: UnknownRecord,
  allowedFields: readonly string[],
  body: unknown,
  message: string,
): void {
  const allowed = new Set(allowedFields);

  for (const field of Object.keys(record)) {
    if (!allowed.has(field)) {
      throw new ApiInvalidResponseError(200, body, message);
    }
  }
}

function notesListQuery(query: ListNotesQuery): Record<string, QueryValue> {
  return {
    page: query.page,
    per_page: query.per_page,
    sort: query.sort,
    order: query.order,
    is_archived: query.is_archived,
    include_deleted: query.include_deleted,
  };
}

/**
 * Validates the `data` field of a summarize-note success response using the
 * shared {@link GetSummaryResponseSchema}.
 *
 * Uses Zod schema validation directly — no `any`, no manual field checks.
 * ZodErrors are surfaced as {@link ApiInvalidResponseError} to match the
 * existing error-handling contract.
 */
function parseSummaryData(data: unknown): Summary {
  const result = SummarySchema.safeParse(data);

  if (!result.success) {
    throw new ApiInvalidResponseError(
      200,
      data,
      `Summary response data did not match contract: ${result.error.message}`,
    );
  }

  return result.data;
}

function parseListSummariesData(data: unknown): ListSummariesData {
  const result = ListSummariesDataSchema.safeParse(data);

  if (!result.success) {
    throw new ApiInvalidResponseError(
      200,
      data,
      `List summaries response data did not match contract: ${result.error.message}`,
    );
  }

  return result.data;
}
