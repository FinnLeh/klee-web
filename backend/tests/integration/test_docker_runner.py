import asyncio
import shutil
import subprocess

import pytest

from klee_web.jobs.runner import IMAGE_TAG, DockerKleeRunner
from klee_web.models import KleeFlags


def _runner_environment_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    result = subprocess.run(
        ["docker", "image", "inspect", IMAGE_TAG],
        capture_output=True,
    )
    return result.returncode == 0


pytestmark = pytest.mark.skipif(
    not _runner_environment_ready(),
    reason=f"docker CLI or {IMAGE_TAG} image not available",
)


GET_SIGN_SOURCE = """\
#include <klee/klee.h>

int get_sign(int x) {
    if (x == 0) return 0;
    if (x < 0) return -1;
    else return 1;
}

int main() {
    int a;
    klee_make_symbolic(&a, sizeof(a), "a");
    return get_sign(a);
}
"""


SOURCE_MISSING_INCLUDE = """\
int get_sign(int x) {
    if (x == 0) return 0;
    if (x < 0) return -1;
    else return 1;
}

int main() {
    int a;
    klee_make_symbolic(&a, sizeof(a), "a");
    return get_sign(a);
}
"""


DIV_BY_ZERO_SOURCE = """\
#include <klee/klee.h>

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    return 10 / x;
}
"""


async def test_docker_runner_runs_get_sign_end_to_end():
    runner = DockerKleeRunner()
    result = await asyncio.wait_for(
        runner.execute(GET_SIGN_SOURCE, KleeFlags(max_time=10, max_memory=256)),
        timeout=30,
    )
    assert len(result.test_cases) == 3
    assert {tc.inputs["a"] for tc in result.test_cases} == {
        "0",
        "16843009",
        "-2147483648",
    }
    assert result.compile_error is None
    assert all(tc.error is None for tc in result.test_cases)
    assert result.stats["Instructions"] > 0


async def test_docker_runner_surfaces_compile_error_from_missing_include():
    runner = DockerKleeRunner()
    result = await asyncio.wait_for(
        runner.execute(SOURCE_MISSING_INCLUDE, KleeFlags(max_time=10, max_memory=256)),
        timeout=30,
    )
    assert result.compile_error is not None
    assert "klee_make_symbolic" in result.compile_error or "undeclared" in result.compile_error
    assert result.test_cases == []
    assert result.stats == {}


async def test_docker_runner_pairs_div_err_with_failing_test_case():
    runner = DockerKleeRunner()
    result = await asyncio.wait_for(
        runner.execute(DIV_BY_ZERO_SOURCE, KleeFlags(max_time=10, max_memory=256)),
        timeout=30,
    )
    assert len(result.test_cases) == 2
    assert sum(tc.error is not None for tc in result.test_cases) == 1
    failing = next(tc for tc in result.test_cases if tc.error is not None)
    assert failing.error is not None
    assert failing.inputs == {"x": "0"}
    assert "divide by zero" in failing.error
    assert result.compile_error is None
