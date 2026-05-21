import asyncio
import tempfile
from pathlib import Path
from typing import Protocol

from klee_web.models import JobResult, KleeFlags
from klee_web.parsing.klee_output import parse_output_dir


IMAGE_TAG = "klee-web-runner"


class KleeRunnerError(Exception):
    """Raised when the runner itself fails: docker missing, image missing, container crash, no output dir.

    User-code compile errors are NOT raised here; they flow through JobResult.compile_error.
    """


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
    """Runs the klee-web-runner container per job and parses /work/output back into a JobResult."""

    async def execute(self, source: str, flags: KleeFlags) -> JobResult:
        with tempfile.TemporaryDirectory(prefix="klee-job-") as tmpdir_str:
            tmpdir = Path(tmpdir_str)
            (tmpdir / "input.c").write_text(source)

            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker", "run", "--rm",
                    "-v", f"{tmpdir}:/work",
                    "-e", f"KLEE_MAX_TIME={flags.max_time}",
                    "-e", f"KLEE_MAX_MEMORY={flags.max_memory}",
                    IMAGE_TAG,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            except FileNotFoundError as e:
                raise KleeRunnerError("docker CLI not found on PATH") from e

            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise KleeRunnerError(
                    f"docker run exited with {proc.returncode}: "
                    f"{stderr.decode(errors='replace').strip()}"
                )

            output_dir = tmpdir / "output"
            if not output_dir.exists():
                raise KleeRunnerError("runner produced no output directory")

            return parse_output_dir(output_dir)