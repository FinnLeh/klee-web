from functools import lru_cache

from klee_web.jobs.runner import DockerKleeRunner, KleeRunner
from klee_web.jobs.store import InMemoryJobStore, JobStore


@lru_cache
def get_job_store() -> JobStore:
    return InMemoryJobStore()


@lru_cache
def get_runner() -> KleeRunner:
    return DockerKleeRunner()
