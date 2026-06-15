#!/usr/bin/env python3
"""Compile /work/input.c with clang, run KLEE on it, write outputs to /work/output/.

Reads max_time and max_memory from KLEE_MAX_TIME and KLEE_MAX_MEMORY env vars.
On compile failure, writes clang stderr to /work/output/compile_error.txt and
exits 0: the runner did its job, the user's code is what didn't compile, and the
backend distinguishes this from a runner crash via the presence of that file.

KLEE's stdout carries the user program's own output (its printf/cout), so we
capture it and write it to /work/output/program_output.txt. KLEE's stderr (its
own diagnostics) is left to flow to the container so the backend still sees it.

When KLEE_QUERY_FORMAT=kquery, pass --write-kqueries so KLEE emits a .kquery
(path constraint) file per test case.

A SIGTERM to this process (how the backend cancels a job) is translated into a
SIGINT to KLEE, the signal KLEE halts gracefully on: KLEE stops exploring and
dumps the test cases found so far, the same partial result a --max-time expiry
produces.
"""
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

INPUT = Path("/work/input.c")
BITCODE = Path("/work/code.bc")
OUTPUT_DIR = Path("/work/output")
KLEE_INCLUDE = "/home/klee/klee_src/include"
GRACE_SECONDS = 10  # after forwarding the halt, SIGKILL KLEE if it has not flushed and exited


def main() -> int:
    max_time = os.environ.get("KLEE_MAX_TIME", "60")
    max_memory = os.environ.get("KLEE_MAX_MEMORY", "512")
    query_format = os.environ.get("KLEE_QUERY_FORMAT", "none")

    compile_proc = subprocess.run(
        [
            "clang",
            "-I", KLEE_INCLUDE,
            "-emit-llvm",
            "-c",
            "-g",
            "-O0",
            str(INPUT),
            "-o", str(BITCODE),
        ],
        capture_output=True,
        text=True,
    )
    if compile_proc.returncode != 0:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "compile_error.txt").write_text(compile_proc.stderr)
        return 0

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    klee_cmd = [
        "klee",
        "--libc=uclibc",
        "--posix-runtime",
        f"--max-time={max_time}",
        f"--max-memory={max_memory}",
        f"--output-dir={OUTPUT_DIR}",
    ]
    if query_format == "kquery":
        klee_cmd.append("--write-kqueries")
    klee_cmd.append(str(BITCODE))

    proc = subprocess.Popen(klee_cmd, stdout=subprocess.PIPE, text=True)
    halted = False

    def _force_kill(signum, frame):
        proc.kill()

    def _forward_halt(signum, frame):
        nonlocal halted
        halted = True
        proc.send_signal(signal.SIGINT)
        signal.signal(signal.SIGALRM, _force_kill)
        signal.alarm(GRACE_SECONDS)

    signal.signal(signal.SIGTERM, _forward_halt)
    signal.signal(signal.SIGINT, _forward_halt)

    stdout, _ = proc.communicate()
    signal.alarm(0)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "program_output.txt").write_text(stdout or "")
    return 0 if halted else proc.returncode


if __name__ == "__main__":
    sys.exit(main())
