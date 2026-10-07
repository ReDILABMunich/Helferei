// The layer rules from docs/architecture.md. Imports only go downwards:
// app -> components / hooks / content -> api -> types.
// Each rule lists what a layer may import; anything else inside src/ is an error.

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "app-only-to-allowed-layers",
      comment:
        "App.tsx and main.tsx may import components, hooks, content and types. They never call the api directly (decision 002).",
      severity: "error",
      from: { path: "^src/(main|App)\\.tsx$" },
      to: {
        path: "^src/",
        pathNot: "^src/(App\\.tsx|components/|hooks/|content/|assets/|types\\.ts|[^/]+\\.css)$",
      },
    },
    {
      name: "components-only-to-content-and-types",
      comment:
        "Components get data through props. They never import api or hooks (decision 002).",
      severity: "error",
      from: { path: "^src/components/" },
      to: {
        path: "^src/",
        pathNot: "^src/(components/|content/|assets/|types\\.ts$)",
      },
    },
    {
      name: "hooks-only-to-api-and-types",
      comment: "Hooks hold the conversation state. They may call the api and use types.",
      severity: "error",
      from: { path: "^src/hooks/" },
      to: {
        path: "^src/",
        pathNot: "^src/(hooks/|api/|types\\.ts$)",
      },
    },
    {
      name: "api-only-to-types",
      comment: "The api layer sends requests. It knows nothing about the interface.",
      severity: "error",
      from: { path: "^src/api/" },
      to: {
        path: "^src/",
        pathNot: "^src/(api/|types\\.ts$)",
      },
    },
    {
      name: "content-only-to-types",
      comment: "Interface text, one file per language. It imports nothing but types.",
      severity: "error",
      from: { path: "^src/content/" },
      to: {
        path: "^src/",
        pathNot: "^src/(content/|types\\.ts$)",
      },
    },
    {
      name: "types-import-nothing",
      comment: "types.ts is the bottom layer and imports nothing from the project.",
      severity: "error",
      from: { path: "^src/types\\.ts$" },
      to: { path: "^src/" },
    },
    {
      name: "no-circular",
      comment: "Two files must not import each other, directly or through others.",
      severity: "error",
      from: {},
      to: { circular: true },
    },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: "tsconfig.app.json" },
  },
};
