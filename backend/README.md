# backend/

FastAPI service. Receives job submissions, runs KLEE through the runner, returns results.

## Stage 1 contents (planned)

- `pyproject.toml`: dependencies and tooling config
- `src/klee_web/main.py`: FastAPI app
- `src/klee_web/api/jobs.py`: `POST /jobs`, `GET /jobs/{id}`
- `src/klee_web/models.py`: Pydantic schemas (`JobRequest`, `Job`, `JobResult`, `JobStatus`)
- `src/klee_web/jobs/store.py`: `JobStore` protocol + `InMemoryJobStore`
- `src/klee_web/jobs/runner.py`: `KleeRunner` protocol + `DockerKleeRunner`
- `src/klee_web/parsing/klee_output.py`: parse KLEE output dir into a `JobResult`
- `src/klee_web/deps.py`: dependency providers (`get_job_store`, `get_runner`)
- `tests/unit/`: handler tests, parser tests with golden fixtures
- `tests/integration/`: end-to-end with real Docker

## Why `JobStore` and `KleeRunner` are protocols

Stage 1 ships in-memory and direct-Docker implementations. Stage 2 swaps in `RedisJobStore` and a Celery-driven runner. The endpoints depend on the protocols via `Depends`, never on the concrete classes. One file (`deps.py`) changes at the stage boundary; everything else is untouched. See `../docs/adr/0001-stage-based-additive-architecture.md`.
