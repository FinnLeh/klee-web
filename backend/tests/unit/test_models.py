from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from klee_web.models import Job, JobRequest, JobStatus, KleeFlags


def test_klee_flags_defaults():
    flags = KleeFlags()
    assert flags.max_time == 60
    assert flags.max_memory == 512


def test_klee_flags_max_time_below_min_rejected():
    with pytest.raises(ValidationError):
        KleeFlags(max_time=0)


def test_klee_flags_max_time_above_max_rejected():
    with pytest.raises(ValidationError):
        KleeFlags(max_time=301)


def test_klee_flags_max_memory_below_min_rejected():
    with pytest.raises(ValidationError):
        KleeFlags(max_memory=32)


def test_klee_flags_max_memory_above_max_rejected():
    with pytest.raises(ValidationError):
        KleeFlags(max_memory=4096)


def test_job_request_minimal_valid():
    req = JobRequest(source="int main() { return 0; }")
    assert req.source == "int main() { return 0; }"
    assert req.flags.max_time == 60


def test_job_request_empty_source_rejected():
    with pytest.raises(ValidationError):
        JobRequest(source="")


def test_job_request_oversized_source_rejected():
    with pytest.raises(ValidationError):
        JobRequest(source="a" * 64_001)


def test_job_request_accepts_custom_flags():
    req = JobRequest(source="int main() {}", flags=KleeFlags(max_time=120, max_memory=1024))
    assert req.flags.max_time == 120
    assert req.flags.max_memory == 1024


def test_job_defaults():
    job = Job()
    assert job.status == JobStatus.pending
    assert job.result is None


def test_job_instances_have_unique_ids():
    a, b = Job(), Job()
    assert a.id != b.id


def test_job_created_at_is_timezone_aware_and_recent():
    job = Job()
    assert job.created_at.tzinfo is not None
    assert (datetime.now(UTC) - job.created_at).total_seconds() < 1.0


def test_job_status_serialises_as_plain_string():
    job = Job(status=JobStatus.running)
    dumped = job.model_dump(mode="json")
    assert dumped["status"] == "running"
