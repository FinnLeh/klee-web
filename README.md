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

The frontend renders the layout chassis (top bar, editor area, results area,
status bar) with placeholder slot content. Theme and layout-position settings
are wired and persist across reloads. The components inside each slot land over
the next few frontend sessions; until they do, end-to-end traffic against the
backend is exercised through the Swagger UI.

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
