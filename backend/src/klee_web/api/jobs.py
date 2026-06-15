import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from klee_web.deps import get_job_store, get_runner
from klee_web.jobs.runner import KleeRunner, KleeRunnerError
from klee_web.jobs.store import JobStore
from klee_web.models import HaltReason, Job, JobCreated, JobRequest, JobResult, JobStatus

router = APIRouter()

# Strong references to in-flight background tasks. Without this, asyncio may
# garbage-collect a task that has no other live reference, killing the job
# mid-execution. Tasks remove themselves via add_done_callback on completion.
_background_tasks: set[asyncio.Task[None]] = set()


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreated)
async def create_job(
    request: JobRequest,
    store: Annotated[JobStore, Depends(get_job_store)],
    runner: Annotated[KleeRunner, Depends(get_runner)],
) -> JobCreated:
    job = Job()
    await store.create(job)
    task = asyncio.create_task(_run_job_in_background(job.id, request, store, runner))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return JobCreated(job_id=job.id)


async def _run_job_in_background(
    job_id: UUID,
    request: JobRequest,
    store: JobStore,
    runner: KleeRunner,
) -> None:
    await store.update_status(job_id, JobStatus.running)

    async def on_progress(partial: JobResult) -> None:
        await store.set_partial_result(job_id, partial)

    async def on_parsing() -> None:
        await store.update_status(job_id, JobStatus.parsing)

    try:
        result = await runner.execute(
            request.source,
            request.flags,
            job_id,
            on_progress=on_progress,
            on_parsing=on_parsing,
        )
        job = await store.get(job_id)
        if job is not None and job.cancel_requested:
            result.halt_reason = HaltReason.cancelled
        await store.set_result(job_id, result)
    except KleeRunnerError:
        await store.update_status(job_id, JobStatus.failed)


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(
    job_id: UUID,
    store: Annotated[JobStore, Depends(get_job_store)],
) -> Job:
    job = await store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.post(
    "/jobs/{job_id}/cancel",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=Job,
)
async def cancel_job(
    job_id: UUID,
    store: Annotated[JobStore, Depends(get_job_store)],
    runner: Annotated[KleeRunner, Depends(get_runner)],
) -> Job:
    job = await store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    landed = await runner.cancel(job_id)
    if not landed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not running")
    await store.request_cancel(job_id)
    updated = await store.get(job_id)
    assert updated is not None  # store never drops a job that get() just returned
    return updated
