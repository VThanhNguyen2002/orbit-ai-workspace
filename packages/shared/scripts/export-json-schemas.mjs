import { mkdir, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { toJSONSchema } from "zod";

import {
  ContractSchemaDefinitions,
  ContractSchemaManifest,
  contractSchemaFile,
  contractSchemaId,
} from "../dist/schema-registry.js";

const packageRoot = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));
const schemasDir = join(packageRoot, "dist", "schemas");

const stableJson = (value) => `${JSON.stringify(value, null, 2)}\n`;

await rm(schemasDir, { force: true, recursive: true });
await mkdir(schemasDir, { recursive: true });

for (const definition of ContractSchemaDefinitions) {
  const schema = toJSONSchema(definition.schema, { target: "draft-7" });
  const { $schema: _zodSchemaDraft, ...schemaBody } = schema;
  const artifact = {
    $schema: "http://json-schema.org/draft-07/schema#",
    $id: contractSchemaId(definition),
    title: definition.title,
    description: definition.description,
    ...schemaBody,
  };
  const outputFile = join(schemasDir, contractSchemaFile(definition));

  await mkdir(dirname(outputFile), { recursive: true });
  await writeFile(outputFile, stableJson(artifact), "utf8");
}

const manifest = {
  schema_version: 1,
  source_package: "@synapse/shared",
  generated_by: "packages/shared/scripts/export-json-schemas.mjs",
  contract_count: ContractSchemaManifest.length,
  schemas: ContractSchemaManifest,
};

await writeFile(join(schemasDir, "manifest.json"), stableJson(manifest), "utf8");
