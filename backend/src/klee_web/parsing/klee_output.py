import sqlite3
import struct
from pathlib import Path

from klee_web.models import HaltReason, JobResult, TestCase
from klee_web.parsing.ktest import KTest


def parse_output_dir(output_dir: Path) -> JobResult:
    compile_error_path = output_dir / "compile_error.txt"
    if compile_error_path.exists():
        return JobResult(
            test_cases=[],
            messages="",
            warnings="",
            stats={},
            compile_error=compile_error_path.read_text(),
        )

    test_cases: list[TestCase] = []
    for p in sorted(output_dir.glob("*.ktest")):
        try:
            test_cases.append(_test_case_from_ktest(p))
        except (OSError, ValueError, EOFError, struct.error):
            # Mid-write ktest; the watcher will see the finished file on a later tick.
            continue

    messages = _read_or_empty(output_dir / "messages.txt")
    info = _read_or_empty(output_dir / "info")
    return JobResult(
        test_cases=test_cases,
        messages=messages,
        warnings=_read_or_empty(output_dir / "warnings.txt"),
        stats=_read_stats(output_dir / "run.stats"),
        halt_reason=_detect_halt_reason(messages, info),
    )


def _detect_halt_reason(messages: str, info: str) -> HaltReason | None:
    # KLEE writes the HaltTimer marker to messages.txt when --max-time fires,
    # and its "KLEE: done:" summary lines to info only at termination. Absence of
    # both means KLEE is still running, so we report None rather than guessing.
    if "HaltTimer invoked" in messages:
        return HaltReason.max_time
    if "KLEE: done:" in info:
        return HaltReason.completed
    return None


def _read_or_empty(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def _read_stats(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        con = sqlite3.connect(path)
        try:
            # run.stats is a time series of snapshots written every --stats-write-interval.
            # KLEE counters are monotonic, so the last row is the cumulative totals.
            cur = con.execute("SELECT * FROM stats ORDER BY rowid DESC LIMIT 1;")
            cols = [str(d[0]) for d in cur.description]
            row = cur.fetchone()
        finally:
            con.close()
    except sqlite3.Error:
        # Mid-write or locked DB; next watcher tick will retry.
        return {}
    if row is None:
        return {}
    return {c: int(v) for c, v in zip(cols, row, strict=True) if v is not None}


_INT_SIZE_FORMATS = {1: "<b", 2: "<h", 4: "<i", 8: "<q"}


def _test_case_from_ktest(path: Path) -> TestCase:
    ktest = KTest.fromfile(str(path))
    inputs = {name: _decode_object_value(data) for name, data in ktest.objects}
    # KLEE names error files <test_stem>.<errortype>.err next to the .ktest.
    err_files = sorted(path.parent.glob(f"{path.stem}.*.err"))
    error = "\n".join(p.read_text() for p in err_files) if err_files else None
    return TestCase(name=path.stem, inputs=inputs, error=error)


def _decode_object_value(data: bytes) -> str:
    fmt = _INT_SIZE_FORMATS.get(len(data))
    if fmt is not None:
        return str(struct.unpack(fmt, data)[0])
    return data.hex()
