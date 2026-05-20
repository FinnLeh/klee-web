# KLEE Web

Browser-accessible interface for the [KLEE](https://klee.llvm.org/) symbolic execution engine. MSc thesis project, Imperial College London, supervised by Prof. Cristian Cadar.

## Goal

KLEE today requires users to build LLVM, STP, and a chain of other dependencies before running a single test. Many give up. KLEE Web removes that barrier: write C in a browser, get test cases back.

## Current stage

**Stage 1: synchronous monolith.** React frontend, FastAPI backend, Docker runner. No queue, no cache. Runs locally with `docker compose up`. Target: end of May 2026.

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

The backend and frontend dev servers run independently. End-to-end execution
depends on the runner, which is still a stub: `POST /jobs` returns 500
(`NotImplementedError`) until the real `DockerKleeRunner` lands.

The frontend currently renders the Vite scaffold's placeholder, not a KLEE Web
UI. The submit-and-poll components arrive in the next frontend session.

### Backend

```bash
cd backend
uv sync
uv run uvicorn klee_web.main:app --port 8000
```

OpenAPI surface at <http://localhost:8000/docs>. Use the Swagger UI's
"Try it out" on `POST /jobs` to confirm the 500.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite dev server at <http://localhost:5173>.

## Design

Architecture is documented in `docs/adr/`, one ADR per major decision.
