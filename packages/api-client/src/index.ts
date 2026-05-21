import {
  ApiErrorEnvelopeSchema,
  ApiSuccessEnvelopeSchema,
  type ApiErrorCode,
  type ApiErrorEnvelope,
  type ApiMeta,
  type ApiSuccessEnvelope,
  type JsonValue,
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
  private readonly baseUrl: string;
  private readonly fetcher: FetchLike;
  private readonly getAuthToken?: ApiClientConfig["getAuthToken"];

  constructor(config: ApiClientConfig = {}) {
    this.baseUrl = normalizeBaseUrl(config.baseUrl ?? DEFAULT_API_BASE_URL);
    this.fetcher = config.fetch ?? getDefaultFetch();
    this.getAuthToken = config.getAuthToken;
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
