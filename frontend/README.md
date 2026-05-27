# frontend/

React + TypeScript single-page app. Editor for C source, submit button, results pane.

## Stage 1 contents

- `package.json`: React 19, TypeScript, Vite, Tailwind v4, React Query, React Router, Monaco editor, openapi-fetch, openapi-typescript
- `.npmrc`: `legacy-peer-deps=true` so clones do not trip on openapi-typescript's stale `typescript: ^5.x` peer-dep range while we are on TS 6
- `vite.config.ts`: build / dev server config
- `tsconfig.json`: strict TypeScript
- `index.html`: entry HTML
- `src/main.tsx`: React mount point, wraps `<App />` in `QueryClientProvider`
- `src/App.tsx`: route index (`SettingsProvider` + `BrowserRouter` + `Route` at `/`)
- `src/api/client.ts`: typed `apiClient` over openapi-fetch; also exports `BASE_URL` for callers that need the backend origin outside the typed routes (e.g., the status bar pinging `/openapi.json`)
- `src/api/jobs.ts`: `submitJob`, `getJob`, re-exported schema aliases
- `src/hooks/useSubmitJob.ts`: React Query mutation over `submitJob`
- `src/hooks/useJob.ts`: React Query polling query over `getJob`, 1000 ms cadence, stops on terminal status
- `src/types/api.ts`: types generated from the backend OpenAPI spec, committed
- `src/context/SettingsContext.tsx`: theme (system/dark/light, default system) and results-position (right/below), localStorage-backed
- `src/components/Workspace.tsx`: layout chassis with five slot props (`topBar`, `sidebar?`, `main`, `results`, `statusBar`); `resultsPosition` flips main/results between row and column
- `src/components/TopBar.tsx`: KLEE wordmark, inline `FlagBar`, Run button, settings cog. Owns the local `settingsOpen` state and the document `pointerdown` / `keydown` listeners that dismiss the popover
- `src/components/FlagBar.tsx`: inline number inputs for `max_time` and `max_memory` with valid / empty / invalid discriminated-union validation. Empty snaps to default on blur; invalid shows a floating rose-bordered explanation and snaps back to the last valid value
- `src/components/Editor.tsx`: `@monaco-editor/react` wrapper. C language, controlled `value` / `onChange`, theme from `useSettings().resolvedTheme` mapped to `vs-dark` / `vs-light`
- `src/components/Results.tsx`: dispatch on job status with eight branches (empty / loading / connection error / pending / running / compile error / done / failed). Running state surfaces a curated 2x2 stat grid; DoneView holds local tab state (Test cases / Stats) and renders a `HaltBadge` between TabBar and scroll area
- `src/components/SettingsPopover.tsx`: panel with two segmented controls (theme: system / light / dark; results position: right / below). Pure presentational, reads and writes `useSettings()`
- `src/components/StatusBar.tsx`: bottom strip with backend-connected indicator (polls `/openapi.json` every 5 s via React Query, two-state connected/disconnected derived from `data` + `isError`), source byte count, pinned KLEE version
- `src/pages/HomePage.tsx`: composes Workspace at route `/`. Owns `source`, `flags`, and `jobId` state. `handleRun` posts via `useSubmitJob` and sets `jobId` on success; `useJob(jobId)` inside `Results` drives the polling

## Editor

Monaco, the editor that powers VS Code. CodeMirror 6 was the alternative considered. See `../docs/adr/0004-monaco-editor.md`.

## Why types are generated, not hand-written

The backend emits an OpenAPI spec from Pydantic models. `openapi-typescript` consumes that spec and emits TypeScript types. A rename on the backend, after regenerating, fails the frontend at compile time. Contract drift becomes impossible.

Regenerate when the backend schema changes:

```bash
npm run gen:types
```

The script expects the backend running on `http://localhost:8000`.
