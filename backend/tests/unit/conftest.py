import asyncio

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from klee_web.api.jobs import _background_tasks
from klee_web.api.jobs import router as jobs_router
from klee_web.deps import get_job_store, get_runner
from klee_web.jobs.runner import FakeKleeRunner
from klee_web.jobs.store import InMemoryJobStore
from klee_web.models import JobResult, TestCase


@pytest.fixture
def sample_result() -> JobResult:
    return JobResult(
        test_cases=[TestCase(name="test1", inputs={"x": "0"})],
        messages="ok",
        warnings="",
        stats={"paths": 1, "instructions": 100},
    )


@pytest.fixture
def store() -> InMemoryJobStore:
    return InMemoryJobStore()


@pytest.fixture
def runner(sample_result) -> FakeKleeRunner:
    return FakeKleeRunner(canned_result=sample_result)


@pytest.fixture
def app(store, runner) -> FastAPI:
    app = FastAPI()
    app.include_router(jobs_router)
    app.dependency_overrides[get_job_store] = lambda: store
    app.dependency_overrides[get_runner] = lambda: runner
    return app


async def _drain_background_jobs() -> None:
    if _background_tasks:
        await asyncio.gather(*list(_background_tasks), return_exceptions=True)


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    # Drain background job tasks so state from one test cannot bleed into the next.
    await _drain_background_jobs()


@pytest.fixture
def wait_for_jobs():
    return _drain_background_jobs
