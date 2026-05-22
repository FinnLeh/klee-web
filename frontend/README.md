# frontend/

React + TypeScript single-page app. Editor for C source, submit button, results pane.

## Stage 1 contents

- `package.json`: React 19, TypeScript, Vite, Tailwind v4, React Query, React Router, Monaco editor, openapi-fetch, openapi-typescript
- `.npmrc`: `legacy-peer-deps=true` so clones do not trip on openapi-typescript's stale `typescript: ^5.x` peer-dep range while we are on TS 6
- `vite.config.ts`: build / dev server config
- `tsconfig.json`: strict TypeScript
- `index.html`: entry HTML
- `src/main.tsx`: React mount point, wraps `<App />` in `QueryClientProvider`
- `src/App.tsx`: top-level layout (currently the Vite scaffold placeholder; rewrite arrives in the next frontend session)
- `src/api/client.ts`: typed `apiClient` over openapi-fetch
- `src/api/jobs.ts`: `submitJob`, `getJob`, re-exported schema aliases
- `src/hooks/useSubmitJob.ts`: React Query mutation over `submitJob`
- `src/hooks/useJob.ts`: React Query polling query over `getJob`, 1000 ms cadence, stops on terminal status
- `src/types/api.ts`: types generated from the backend OpenAPI spec, committed
- `src/components/`: editor, results, top bar, status bar, flag bar, settings popover (arrive in the next session)

## Editor

Monaco, the editor that powers VS Code. CodeMirror 6 was the alternative considered. See `../docs/adr/0004-monaco-editor.md`.

## Why types are generated, not hand-written

The backend emits an OpenAPI spec from Pydantic models. `openapi-typescript` consumes that spec and emits TypeScript types. A rename on the backend, after regenerating, fails the frontend at compile time. Contract drift becomes impossible.

Regenerate when the backend schema changes:

```bash
npm run gen:types
```

The script expects the backend running on `http://localhost:8000`.
