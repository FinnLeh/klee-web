from typing import Protocol

from klee_web.models import JobResult, KleeFlags


class KleeRunnerError(Exception):
    """Raised when KLEE execution fails: compile error, KLEE internal crash, timeout, OOM."""


class KleeRunner(Protocol):
    async def execute(self, source: str, flags: KleeFlags) -> JobResult: ...


class FakeKleeRunner:
    """Test double. Returns a canned result, or raises a canned exception. Records calls."""

    def __init__(
        self,
        canned_result: JobResult | None = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self._canned_result = canned_result
        self._raise_exc = raise_exc
        self.calls: list[tuple[str, KleeFlags]] = []

    async def execute(self, source: str, flags: KleeFlags) -> JobResult:
        self.calls.append((source, flags))
        if self._raise_exc is not None:
            raise self._raise_exc
        if self._canned_result is None:
            raise RuntimeError("FakeKleeRunner needs either canned_result or raise_exc")
        return self._canned_result


class DockerKleeRunner:
    """Stage 1 real implementation. Shells out to `docker run`. Implemented tomorrow."""

    async def execute(self, source: str, flags: KleeFlags) -> JobResult:
        raise NotImplementedError("DockerKleeRunner is implemented in tomorrow's runner work")
