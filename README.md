# KLEE Web

[![CI](https://github.com/FinnLeh/klee-web/actions/workflows/ci.yml/badge.svg)](https://github.com/FinnLeh/klee-web/actions/workflows/ci.yml)

Browser-accessible interface for the [KLEE](https://klee.llvm.org/) symbolic execution engine. MSc thesis project, Imperial College London, supervised by Prof. Cristian Cadar.

## Goal

KLEE today requires users to build LLVM, STP, and a chain of other dependencies before running a single test. Many give up. KLEE Web removes that barrier: write C in a browser, get test cases back.

## Current stage

**Stage 1: synchronous monolith.** React frontend, FastAPI backend, Docker runner. No queue, no cache. Runs locally via the steps below. Target: end of May 2026.

Stages 2 (Celery + Redis + cache) and 3 (nginx + gVisor + admin UI) follow over the summer.

## Layout

```
klee-web/
├── backend/        FastAPI + Pydantic. Job submission, status, result API.
├── frontend/       React + TypeScript + Vite. Editor and results UI.
├── runner/         Docker image and entrypoint that actually runs KLEE.
├── docs/adr/       Architecture Decision Records.
└── Makefile        `make up` builds the runner image and runs backend + frontend dev servers.
```

## Running locally

Requires `uv` and `node` on the host.

```bash
make up
```

`make up` builds the `klee-web-runner` Docker image (idempotent), then starts
uvicorn (`localhost:8000`, `--reload`) and the Vite dev server
(`localhost:5173`) as background processes. Both hot-reload on file changes.
Ctrl+C stops both.

OpenAPI surface at <http://localhost:8000/docs>. App at <http://localhost:5173>.

The frontend is functional end-to-end. The page loads with a demo C program in
a Monaco editor; the top bar carries the KLEE wordmark, inline flag inputs for
`max_time` and `max_memory`, a Run button, and a settings cog. Run posts to the
backend and the results panel polls and renders pending, running (with a
curated live-stats grid: instructions, active states, full branches, wall
time), done (test cases plus a KLEE messages and warnings collapsible), and
compile-error states. A timeout reads as an amber `Stopped at max time` badge
under the tab bar; a clean run reads `Explored all paths`. The bottom status
bar shows a backend-connected indicator (5 s poll of `/openapi.json`), the
current source byte count, and the pinned KLEE version. Theme (system / light /
dark) and results-position (right / below) settings persist across reloads via
the settings popover.

## Regenerating the API contract

The backend emits its OpenAPI spec from the Pydantic models. The frontend's
TypeScript types live in `frontend/src/types/api.ts`, generated from that spec
and committed to the repo. They do not regenerate on their own.

After any backend change that alters the contract (a renamed field, a new
endpoint, a changed shape), regenerate the types:

```bash
cd frontend && npm run gen:types
```

The script reads the live `/openapi.json`, so the backend must already be
running (`make up`, or uvicorn on `localhost:8000`). Commit the updated
`api.ts` alongside the backend change. A stale `api.ts` surfaces as a frontend
type error against the new contract, which is the point: drift fails at compile
time instead of silently.

## Pre-commit hooks

One-time per clone:

```bash
uv tool install pre-commit
pre-commit install
```

After that, `git commit` runs ruff (backend), eslint (frontend), and whitespace / end-of-file checks. The eslint hook needs `frontend/node_modules`, so run `npm install` in `frontend/` once before the first commit.

## Design

Architecture is documented in `docs/adr/`, one ADR per major decision.
