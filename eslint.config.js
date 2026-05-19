const js = require("@eslint/js");
const tseslint = require("typescript-eslint");

const appImportPatterns = [
  "apps/*",
  "apps/**",
  "../apps/**",
  "../../apps/**",
  "../../../apps/**",
  "../../../../apps/**",
];

const nodeBuiltinPaths = [
  "fs",
  "node:fs",
  "path",
  "node:path",
  "crypto",
  "node:crypto",
  "process",
  "node:process",
];

const restrictedGlobalsForShared = [
  "window",
  "document",
  "localStorage",
  "crypto",
  "process",
  "AsyncStorage",
].map((name) => ({
  name,
  message: "@synapse/shared must stay platform-agnostic.",
}));

module.exports = tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/build/**",
      "**/coverage/**",
      "**/.turbo/**",
      "**/node_modules/**",
      "**/*.tsbuildinfo",
      "apps/api/**",
    ],
  },
  {
    ...js.configs.recommended,
    files: ["**/*.{js,cjs,mjs}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
    },
  },
  ...tseslint.configs.recommended,
  {
    files: ["packages/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: appImportPatterns,
              message: "Packages and apps must not import through apps/* paths.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["packages/shared/src/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-globals": ["error", ...restrictedGlobalsForShared],
      "no-restricted-imports": [
        "error",
        {
          paths: [
            ...nodeBuiltinPaths.map((name) => ({
              name,
              message: "@synapse/shared must not import Node-only APIs.",
            })),
            {
              name: "react",
              message: "@synapse/shared must not import React.",
            },
            {
              name: "react-native",
              message: "@synapse/shared must not import React Native.",
            },
            {
              name: "expo",
              message: "@synapse/shared must not import Expo.",
            },
            {
              name: "next",
              message: "@synapse/shared must not import Next.js.",
            },
            {
              name: "vite",
              message: "@synapse/shared must not import Vite.",
            },
            {
              name: "@react-native-async-storage/async-storage",
              message: "@synapse/shared must not import AsyncStorage.",
            },
            {
              name: "@synapse/ui",
              message: "@synapse/shared must not depend on @synapse/ui.",
            },
            {
              name: "@synapse/api-client",
              message: "@synapse/shared must not depend on @synapse/api-client.",
            },
          ],
          patterns: [
            {
              group: [
                "expo-*",
                "@synapse/ui/*",
                "@synapse/api-client/*",
                ...appImportPatterns,
              ],
              message: "@synapse/shared must stay platform-agnostic.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["packages/api-client/src/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            {
              name: "@synapse/ui",
              message: "@synapse/api-client must not depend on @synapse/ui.",
            },
          ],
          patterns: [
            {
              group: ["@synapse/ui/*", ...appImportPatterns],
              message: "@synapse/api-client must stay independent of UI and apps.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["packages/ui/src/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            ...nodeBuiltinPaths.map((name) => ({
              name,
              message: "@synapse/ui must not import Node-only APIs.",
            })),
            {
              name: "@synapse/api-client",
              message: "@synapse/ui must not depend on @synapse/api-client.",
            },
          ],
          patterns: [
            {
              group: ["@synapse/api-client/*", ...appImportPatterns],
              message: "@synapse/ui must stay independent of apps and data clients.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["packages/config/src/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-globals": ["error", ...restrictedGlobalsForShared],
      "no-restricted-imports": [
        "error",
        {
          paths: [
            ...nodeBuiltinPaths.map((name) => ({
              name,
              message: "@synapse/config must not import Node-only APIs.",
            })),
            {
              name: "react",
              message: "@synapse/config must not import React.",
            },
            {
              name: "react-native",
              message: "@synapse/config must not import React Native.",
            },
            {
              name: "@synapse/ui",
              message: "@synapse/config must not depend on UI.",
            },
            {
              name: "@synapse/api-client",
              message: "@synapse/config must not depend on API client.",
            },
          ],
          patterns: [
            {
              group: [
                "expo-*",
                "@synapse/ui/*",
                "@synapse/api-client/*",
                ...appImportPatterns,
              ],
              message: "@synapse/config must stay runtime-agnostic.",
            },
          ],
        },
      ],
    },
  },
  {
    files: ["apps/mobile/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["apps/api", "apps/api/**", "../api/**", "../../api/**"],
              message: "apps/mobile must not import backend internals.",
            },
          ],
        },
      ],
    },
  }
);
