import {
  DEFAULT_API_BASE_URL,
  createApiClient,
  type ApiClientConfig,
  type SynapseApiClient,
} from "@synapse/api-client";

export const MOBILE_API_BASE_URL = DEFAULT_API_BASE_URL;

export type MobileSynapseClient = Pick<SynapseApiClient, "ai">;
export type MobileSynapseClientConfig = ApiClientConfig;

export function createMobileSynapseClient(
  config: MobileSynapseClientConfig = {},
): MobileSynapseClient {
  const clientConfig: ApiClientConfig = {
    baseUrl: config.baseUrl ?? MOBILE_API_BASE_URL,
  };

  if (config.fetch !== undefined) {
    clientConfig.fetch = config.fetch;
  }

  if (config.getAuthToken !== undefined) {
    clientConfig.getAuthToken = config.getAuthToken;
  }

  return createApiClient(clientConfig);
}
