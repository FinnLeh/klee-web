from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from klee_web.deps import get_job_store, get_runner
from klee_web.jobs.runner import KleeRunner, KleeRunnerError
from klee_web.jobs.store import JobStore
from klee_web.models import Job, JobCreated, JobRequest, JobStatus

router = APIRouter()


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreated)
async def create_job(
    request: JobRequest,
    store: Annotated[JobStore, Depends(get_job_store)],
    runner: Annotated[KleeRunner, Depends(get_runner)],
) -> JobCreated:
    job = Job()
    await store.create(job)
    await store.update_status(job.id, JobStatus.running)
    try:
        result = await runner.execute(request.source, request.flags)
        await store.set_result(job.id, result)
    except KleeRunnerError:
        await store.update_status(job.id, JobStatus.failed)
    return JobCreated(job_id=job.id)


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(
    job_id: UUID,
    store: Annotated[JobStore, Depends(get_job_store)],
) -> Job:
    job = await store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
