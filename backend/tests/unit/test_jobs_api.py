import asyncio
from uuid import UUID, uuid4

from klee_web.deps import get_runner
from klee_web.jobs.runner import FakeKleeRunner, KleeRunnerError
from klee_web.models import JobResult, JobStatus, TestCase


async def test_post_jobs_returns_202_with_job_id(client):
    response = await client.post("/jobs", json={"source": "int main() { return 0; }"})
    assert response.status_code == 202
    body = response.json()
    assert "job_id" in body
    UUID(body["job_id"])  # raises if not a valid UUID


async def test_post_jobs_calls_runner_with_source_and_flags(client, runner, wait_for_jobs):
    payload = {
        "source": "int main() { return 0; }",
        "flags": {"max_time": 120, "max_memory": 256},
    }
    await client.post("/jobs", json=payload)
    await wait_for_jobs()
    assert len(runner.calls) == 1
    called_source, called_flags = runner.calls[0]
    assert called_source == payload["source"]
    assert called_flags.max_time == 120
    assert called_flags.max_memory == 256


async def test_post_jobs_happy_path_stores_result_and_advances_to_done(
    client, store, sample_result, wait_for_jobs,
):
    response = await client.post("/jobs", json={"source": "int main(){}"})
    job_id = UUID(response.json()["job_id"])
    await wait_for_jobs()
    job = await store.get(job_id)
    assert job is not None
    assert job.status == JobStatus.done
    assert job.result == sample_result


async def test_post_jobs_runner_failure_marks_job_failed(client, app, store, wait_for_jobs):
    failing_runner = FakeKleeRunner(raise_exc=KleeRunnerError("KLEE crashed"))
    app.dependency_overrides[get_runner] = lambda: failing_runner

    response = await client.post("/jobs", json={"source": "int main(){}"})
    assert response.status_code == 202
    job_id = UUID(response.json()["job_id"])
    await wait_for_jobs()
    job = await store.get(job_id)
    assert job is not None
    assert job.status == JobStatus.failed


async def test_post_jobs_rejects_empty_source(client):
    response = await client.post("/jobs", json={"source": ""})
    assert response.status_code == 422


async def test_post_jobs_rejects_oversized_source(client):
    response = await client.post("/jobs", json={"source": "a" * 64_001})
    assert response.status_code == 422


async def test_get_jobs_returns_completed_job(client, wait_for_jobs):
    post_response = await client.post("/jobs", json={"source": "int main(){}"})
    job_id = post_response.json()["job_id"]
    await wait_for_jobs()

    get_response = await client.get(f"/jobs/{job_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["status"] == "done"
    assert body["result"] is not None


async def test_get_jobs_returns_404_for_unknown_id(client):
    response = await client.get(f"/jobs/{uuid4()}")
    assert response.status_code == 404


async def test_post_runs_in_background_and_streams_partial_results(
    client, app, store, wait_for_jobs, sample_result,
):
    """POST returns immediately; partial lands while running; final lands at completion."""
    partial_emitted = asyncio.Event()
    finish_when = asyncio.Event()
    partial = JobResult(
        test_cases=[TestCase(name="test_partial", inputs={"x": "1"})],
        messages="",
        warnings="",
        stats={},
    )

    class BlockingStreamingRunner:
        async def execute(self, source, flags, on_progress=None):
            if on_progress is not None:
                await on_progress(partial)
            partial_emitted.set()
            await finish_when.wait()
            return sample_result

    app.dependency_overrides[get_runner] = lambda: BlockingStreamingRunner()

    response = await client.post("/jobs", json={"source": "int main(){}"})
    assert response.status_code == 202
    job_id = UUID(response.json()["job_id"])

    # Mid-execution: partial has landed, status is still running.
    await partial_emitted.wait()
    job = await store.get(job_id)
    assert job is not None
    assert job.status == JobStatus.running
    assert job.result == partial

    # Let the runner finish. Final state: done with the final result.
    finish_when.set()
    await wait_for_jobs()
    job = await store.get(job_id)
    assert job is not None
    assert job.status == JobStatus.done
    assert job.result == sample_result