# runner/

Docker image and entrypoint that actually runs KLEE on user-submitted C code. Top-level sibling of `backend/` deliberately: in Stage 2 this is what lives on separate worker VMs, and the separation stops backend code from accidentally reaching into runner internals.

## Stage 1 contents

- `Dockerfile`: pinned `klee/klee:v3.2` base, copies in the entrypoint, sets the working user
- `entrypoint.py`: compile C to LLVM bitcode with clang, run KLEE with bounded flags, exit. Output files land in a mounted volume the backend reads back.

## Why a separate image per job, not a long-lived process

Per-job containers give cgroup isolation, easy resource accounting (memory, CPU, pids), and trivial cleanup with `docker rm`. A long-lived KLEE process accumulates state: leaked fds, fragmented memory, half-cleaned tmp dirs. Per-job means every run starts from a known clean state. See `../docs/adr/0008-kleerunner-protocol-surface.md` and `../docs/adr/0009-per-job-containers.md`.

## Known working invocation (reference)

- `clang -I /home/klee/klee_src/include -emit-llvm -c -g -O0 input.c -o code.bc`
- `klee --libc=uclibc --posix-runtime --max-time=60 --max-memory=512 --output-dir=/tmp/klee-out code.bc`
- Output dir contains `messages.txt`, `warnings.txt`, `*.ktest`, `*.err`, `run.stats` (SQLite3 in KLEE 3.x).
