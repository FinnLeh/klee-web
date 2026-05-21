# KLEE output sample fixtures

Captured runner output directories consumed by the parser tests in `tests/unit/test_klee_output.py`. Each subdirectory pairs the `input.c` that was run with the `output/` directory the runner produced.

## Scenarios

- `happy_path/`: canonical KLEE tutorial program (`get_sign`), three paths, three test cases, no errors.
- `compile_error/`: same program with `#include <klee/klee.h>` removed. Entrypoint writes `compile_error.txt` and exits 0; `output/` contains only that file.
- `runtime_error/`: divide-by-zero with `x` symbolic. KLEE emits `test000001.div.err` alongside the `.ktest` files.

## Files in each `output/`

- `messages.txt`, `warnings.txt`: KLEE text logs.
- `info`: invocation, PID, timing, exploration summary.
- `run.stats`: SQLite3 with KLEE's statistics. Final row is totals.
- `test*.ktest`: binary test case files. Decode with `ktest-tool` inside the runner image.
- `test*.*.err`: error report. Extension encodes error type (e.g. `.div.err`, `.ptr.err`).
- `test*.kquery`: constraint query that produced the failing input. Emitted alongside `.err`.
- `compile_error.txt`: clang stderr. Present only when compilation failed.

## Excluded from the captured output

- `assembly.ll`: LLVM IR dump in text. KLEE-internal debugging artefact.
- `run.istats`: per-instruction profiling data for kcachegrind / `klee-stats`.

Both are large and KLEE Web never surfaces them. The parser ignores files it does not recognise.