# backend/

FastAPI service. Receives job submissions, runs KLEE through the runner, returns results.

## Stage 1 contents

- `pyproject.toml`: dependencies and tooling config
- `src/klee_web/main.py`: FastAPI app
- `src/klee_web/api/jobs.py`: `POST /jobs`, `GET /jobs/{id}`. POST returns immediately and schedules the runner on `asyncio.create_task`; GET polls the store
- `src/klee_web/models.py`: Pydantic schemas (`JobRequest`, `Job`, `JobResult`, `JobStatus`, `KleeFlags`, `TestCase`, `HaltReason`)
- `src/klee_web/jobs/store.py`: `JobStore` protocol + `InMemoryJobStore`. `set_partial_result` for mid-flight progress writes; `set_result` flips status to `done`
- `src/klee_web/jobs/runner.py`: `KleeRunner` protocol + `DockerKleeRunner`. Spawns a watcher coroutine that polls the output dir every second and emits partials via an `on_progress` callback
- `src/klee_web/parsing/klee_output.py`: parse KLEE output dir into a `JobResult`. Detects halt reason from `HaltTimer invoked` in `messages.txt` (`max_time`) or `KLEE: done:` in `info` (`completed`)
- `src/klee_web/parsing/ktest.py`: vendored KLEE ktest reader (NCSA, trimmed to `KTest.fromfile`)
- `src/klee_web/deps.py`: dependency providers (`get_job_store`, `get_runner`)
- `tests/unit/`: handler tests, parser tests with golden fixtures (`happy_path`, `compile_error`, `runtime_error`, `max_time`)
- `tests/integration/`: end-to-end with real Docker

## Why `JobStore` and `KleeRunner` are protocols

Stage 1 ships in-memory and direct-Docker implementations. Stage 2 swaps in `RedisJobStore` and a Celery-driven runner. The endpoints depend on the protocols via `Depends`, never on the concrete classes. One file (`deps.py`) changes at the stage boundary; everything else is untouched. See `../docs/adr/0001-stage-based-additive-architecture.md`.
