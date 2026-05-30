import { describe, expect, it } from "vitest";
import { toJSONSchema } from "zod";

import {
  ContractSchemaDefinitions,
  ContractSchemaManifest,
  contractSchemaFile,
  contractSchemaId,
} from "./schema-registry";

const camelCasePattern = /^[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*$/;

const collectObjectPropertyKeys = (value: unknown, keys: string[] = []) => {
  if (Array.isArray(value)) {
    for (const item of value) {
      collectObjectPropertyKeys(item, keys);
    }
    return keys;
  }

  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;

    if (record.properties && typeof record.properties === "object") {
      keys.push(...Object.keys(record.properties));
    }

    for (const nested of Object.values(record)) {
      collectObjectPropertyKeys(nested, keys);
    }
  }

  return keys;
};

describe("contract schema registry", () => {
  it("has a one-to-one deterministic manifest entry for every registered schema", () => {
    expect(ContractSchemaManifest).toHaveLength(ContractSchemaDefinitions.length);

    const keys = new Set<string>();
    for (const definition of ContractSchemaDefinitions) {
      const key = `${definition.group}/${definition.name}`;
      expect(keys.has(key)).toBe(false);
      keys.add(key);

      expect(contractSchemaId(definition)).toBe(
        `urn:synapse:contract:${definition.group}:${definition.name}`,
      );
      expect(contractSchemaFile(definition)).toBe(
        `${definition.group}/${definition.name}.schema.json`,
      );
    }
  });

  it("converts every registered Zod contract to draft-07 JSON Schema", () => {
    for (const definition of ContractSchemaDefinitions) {
      const jsonSchema = toJSONSchema(definition.schema, { target: "draft-7" });
      expect(jsonSchema).toHaveProperty(
        "$schema",
        "http://json-schema.org/draft-07/schema#",
      );
    }
  });

  it("does not export camelCase object property names", () => {
    for (const definition of ContractSchemaDefinitions) {
      const jsonSchema = toJSONSchema(definition.schema, { target: "draft-7" });
      const camelCaseKeys = collectObjectPropertyKeys(jsonSchema).filter((key) =>
        camelCasePattern.test(key),
      );

      expect(camelCaseKeys, definition.name).toEqual([]);
    }
  });

  it("includes representative backend-facing contracts", () => {
    const files = new Set(ContractSchemaManifest.map((entry) => entry.file));

    expect(files.has("domain/note.schema.json")).toBe(true);
    expect(files.has("domain/create_note_request.schema.json")).toBe(true);
    expect(files.has("domain/update_note_request.schema.json")).toBe(true);
    expect(files.has("domain/delete_note_request.schema.json")).toBe(true);
    expect(files.has("domain/get_note_response.schema.json")).toBe(true);
    expect(files.has("domain/list_notes_request.schema.json")).toBe(true);
    expect(files.has("domain/list_notes_response.schema.json")).toBe(true);
    expect(files.has("sync/sync_push_request.schema.json")).toBe(true);
    expect(files.has("sync/sync_pull_response.schema.json")).toBe(true);
    expect(files.has("ai/semantic_search_response.schema.json")).toBe(true);
    expect(files.has("ai/ai_stream_event.schema.json")).toBe(true);
    expect(files.has("ai/get_summary_response.schema.json")).toBe(true);
    expect(files.has("errors/api_error_envelope.schema.json")).toBe(true);
  });
});
