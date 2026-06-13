# 0012. Add query_format to the flag schema

**Status:** Accepted, 2026-06-13

## Context

ADR-0005 shipped a deliberately narrow `KleeFlags` (`max_time`, `max_memory`) and deferred any expansion until a concrete request appeared. Surfacing each test case's path constraint, KLEE's `--write-kqueries` output in KQuery format, is that request: it lets users see why KLEE took a given path.

## Decision

Add one typed field, `query_format: "none" | "kquery"` (default `none`), to `KleeFlags`. The runner maps `kquery` to `--write-kqueries`; `none` writes nothing. KQuery only for now. SMT-LIBv2 is a future enum value.

## Consequences

- Safe by construction still holds: an enum, not a free-form string, so no user text reaches the KLEE invocation (the property ADR-0005 protected).
- Default `none` leaves the common case unchanged: no query files, no UI noise.
- This is a scoped, feature-driven addition, not the general flag broadening still deferred to its own issue.

## References

- ADR-0005: narrow KleeFlags schema (the narrow stance this extends).
