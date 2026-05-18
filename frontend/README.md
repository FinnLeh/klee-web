# frontend/

React + TypeScript single-page app. Editor for C source, submit button, results pane.

## Stage 1 contents (planned)

- `package.json`: React 19, TypeScript, Vite, React Query, Tailwind, an editor library (Monaco or CodeMirror 6, undecided)
- `vite.config.ts`: build / dev server config
- `tsconfig.json`: strict TypeScript
- `index.html`: entry HTML
- `src/main.tsx`: React mount point
- `src/App.tsx`: top-level layout
- `src/components/Editor.tsx`: code editor wrapper
- `src/components/Results.tsx`: results pane
- `src/api/jobs.ts`: `POST /jobs`, `GET /jobs/{id}` client, polls via React Query
- `src/types/api.ts`: types generated from the backend OpenAPI spec, committed

## Editor choice (undecided)

Monaco (VS Code's editor) vs CodeMirror 6. Tradeoff is in the architecture slides. Will decide before frontend work starts in earnest.

## Why types are generated, not hand-written

The backend emits an OpenAPI spec from Pydantic models. `openapi-typescript` consumes that spec and emits TypeScript types. A rename on the backend, after regenerating, fails the frontend at compile time. Contract drift becomes impossible.
