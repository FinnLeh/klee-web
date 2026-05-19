import asyncio
from uuid import uuid4

import pytest

from klee_web.jobs.store import JobNotFound
from klee_web.models import Job, JobStatus


async def test_create_then_get_returns_same_job(store):
    job = Job()
    await store.create(job)
    retrieved = await store.get(job.id)
    assert retrieved == job


async def test_get_unknown_id_returns_none(store):
    assert await store.get(uuid4()) is None


async def test_two_distinct_jobs_can_coexist(store):
    a, b = Job(), Job()
    await store.create(a)
    await store.create(b)
    assert (await store.get(a.id)) == a
    assert (await store.get(b.id)) == b


async def test_update_status_changes_status(store):
    job = Job()
    await store.create(job)
    await store.update_status(job.id, JobStatus.running)
    retrieved = await store.get(job.id)
    assert retrieved is not None
    assert retrieved.status == JobStatus.running


async def test_update_status_on_unknown_id_raises_job_not_found(store):
    with pytest.raises(JobNotFound):
        await store.update_status(uuid4(), JobStatus.running)


async def test_set_result_stores_result_and_advances_status_to_done(store, sample_result):
    job = Job()
    await store.create(job)
    await store.set_result(job.id, sample_result)
    retrieved = await store.get(job.id)
    assert retrieved is not None
    assert retrieved.status == JobStatus.done
    assert retrieved.result == sample_result


async def test_set_result_on_unknown_id_raises_job_not_found(store, sample_result):
    with pytest.raises(JobNotFound):
        await store.set_result(uuid4(), sample_result)


async def test_concurrent_creates_dont_lose_jobs(store):
    jobs = [Job() for _ in range(50)]
    await asyncio.gather(*(store.create(j) for j in jobs))
    for job in jobs:
        retrieved = await store.get(job.id)
        assert retrieved == job
