# KLEE Web

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
└── docker-compose.yml   Local dev orchestration (added once components exist).
```

## Running locally

The backend, frontend, and runner pieces run independently. End-to-end
execution requires Docker plus the locally-built runner image.

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

### Runner image

Build the runner image once before booting the backend, and rebuild after any
change to `runner/Dockerfile` or `runner/entrypoint.py`:

```bash
docker build -t klee-web-runner ./runner
```

### Backend

```bash
cd backend
uv sync
uv run uvicorn klee_web.main:app --port 8000
```

OpenAPI surface at <http://localhost:8000/docs>. `POST /jobs` compiles and
runs the submitted C source via the runner image and returns a `job_id`;
`GET /jobs/{id}` returns the parsed result with test cases, errors, and stats.
The backend assumes the `klee-web-runner` image is built; without it, `POST
/jobs` returns 500 with a runner error.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite dev server at <http://localhost:5173>.

## Design

Architecture is documented in `docs/adr/`, one ADR per major decision.
