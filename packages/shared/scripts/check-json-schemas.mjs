import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  ContractSchemaDefinitions,
  ContractSchemaManifest,
} from "../dist/schema-registry.js";

const packageRoot = fileURLToPath(new URL("..", import.meta.url));
const schemasDir = join(packageRoot, "dist", "schemas");
const camelCasePattern = /^[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*$/;

const readJson = async (path) => JSON.parse(await readFile(path, "utf8"));

const collectObjectPropertyKeys = (value, keys = []) => {
  if (Array.isArray(value)) {
    for (const item of value) {
      collectObjectPropertyKeys(item, keys);
    }
    return keys;
  }

  if (value && typeof value === "object") {
    if (value.properties && typeof value.properties === "object") {
      keys.push(...Object.keys(value.properties));
    }

    for (const nested of Object.values(value)) {
      collectObjectPropertyKeys(nested, keys);
    }
  }

  return keys;
};

const errors = [];
const manifestPath = join(schemasDir, "manifest.json");
const manifest = await readJson(manifestPath);

if (manifest.schema_version !== 1) {
  errors.push("manifest.schema_version must be 1");
}

if (manifest.source_package !== "@synapse/shared") {
  errors.push("manifest.source_package must be @synapse/shared");
}

if (manifest.contract_count !== ContractSchemaDefinitions.length) {
  errors.push(
    `manifest.contract_count ${manifest.contract_count} does not match registry ${ContractSchemaDefinitions.length}`,
  );
}

const manifestFiles = new Set(manifest.schemas?.map((entry) => entry.file));
const expectedFiles = new Set(ContractSchemaManifest.map((entry) => entry.file));

for (const expected of ContractSchemaManifest) {
  if (!manifestFiles.has(expected.file)) {
    errors.push(`manifest is missing ${expected.file}`);
    continue;
  }

  const schema = await readJson(join(schemasDir, expected.file));
  if (schema.$schema !== "http://json-schema.org/draft-07/schema#") {
    errors.push(`${expected.file} has unexpected $schema ${schema.$schema}`);
  }
  if (schema.$id !== expected.id) {
    errors.push(`${expected.file} has unexpected $id ${schema.$id}`);
  }
  if (schema.title !== expected.title) {
    errors.push(`${expected.file} has unexpected title ${schema.title}`);
  }

  const camelCaseKeys = collectObjectPropertyKeys(schema).filter((key) =>
    camelCasePattern.test(key),
  );
  if (camelCaseKeys.length > 0) {
    errors.push(
      `${expected.file} contains camelCase wire keys: ${[...new Set(camelCaseKeys)].join(", ")}`,
    );
  }
}

for (const file of manifestFiles) {
  if (!expectedFiles.has(file)) {
    errors.push(`manifest contains unregistered schema file ${file}`);
  }
}

if (errors.length > 0) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
}
