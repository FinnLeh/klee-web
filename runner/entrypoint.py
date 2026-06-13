#!/usr/bin/env python3
"""Compile /work/input.c with clang, run KLEE on it, write outputs to /work/output/.

Reads max_time and max_memory from KLEE_MAX_TIME and KLEE_MAX_MEMORY env vars.
On compile failure, writes clang stderr to /work/output/compile_error.txt and
exits 0: the runner did its job, the user's code is what didn't compile, and the
backend distinguishes this from a runner crash via the presence of that file.

KLEE's stdout carries the user program's own output (its printf/cout), so we
capture it and write it to /work/output/program_output.txt. KLEE's stderr (its
own diagnostics) is left to flow to the container so the backend still sees it.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

INPUT = Path("/work/input.c")
BITCODE = Path("/work/code.bc")
OUTPUT_DIR = Path("/work/output")
KLEE_INCLUDE = "/home/klee/klee_src/include"


def main() -> int:
    max_time = os.environ.get("KLEE_MAX_TIME", "60")
    max_memory = os.environ.get("KLEE_MAX_MEMORY", "512")

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

    klee_proc = subprocess.run(
        [
            "klee",
            "--libc=uclibc",
            "--posix-runtime",
            f"--max-time={max_time}",
            f"--max-memory={max_memory}",
            f"--output-dir={OUTPUT_DIR}",
            str(BITCODE),
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "program_output.txt").write_text(klee_proc.stdout or "")
    return klee_proc.returncode


if __name__ == "__main__":
    sys.exit(main())
