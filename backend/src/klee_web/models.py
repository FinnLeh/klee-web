from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class KleeFlags(BaseModel):
    max_time: Annotated[int, Field(ge=1, le=300)] = 60
    max_memory: Annotated[int, Field(ge=64, le=2048)] = 512


class JobRequest(BaseModel):
    source: Annotated[str, Field(min_length=1, max_length=64_000)]
    flags: KleeFlags = Field(default_factory=KleeFlags)


class TestCase(BaseModel):
    name: str
    inputs: dict[str, str]


class JobResult(BaseModel):
    test_cases: list[TestCase]
    messages: str
    warnings: str
    errors: list[str]
    stats: dict[str, int]


class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: JobStatus = JobStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result: JobResult | None = None
