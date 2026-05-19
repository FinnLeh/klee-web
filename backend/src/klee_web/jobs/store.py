import asyncio
from typing import Protocol
from uuid import UUID

from klee_web.models import Job, JobResult, JobStatus


class JobNotFound(Exception):
    """Raised when an operation references a UUID that is not in the store."""


class JobStore(Protocol):
    async def create(self, job: Job) -> None: ...
    async def get(self, job_id: UUID) -> Job | None: ...
    async def update_status(self, job_id: UUID, status: JobStatus) -> None: ...
    async def set_result(self, job_id: UUID, result: JobResult) -> None: ...


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[UUID, Job] = {}
        self._lock = asyncio.Lock()

    async def create(self, job: Job) -> None:
        async with self._lock:
            self._jobs[job.id] = job

    async def get(self, job_id: UUID) -> Job | None:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_status(self, job_id: UUID, status: JobStatus) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise JobNotFound(job_id)
            job.status = status

    async def set_result(self, job_id: UUID, result: JobResult) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise JobNotFound(job_id)
            job.result = result
            job.status = JobStatus.done
