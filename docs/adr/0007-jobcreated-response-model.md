# 0007. POST /jobs returns JobCreated, not full Job

**Status:** Accepted, 2026-05-19

## Context

`POST /jobs` creates a job. Two response shapes are possible:

1. Return the full `Job` (including `status` and, in Stage 1, the populated `result`).
2. Return a narrow `JobCreated{job_id}`.

In Stage 1 the handler runs synchronously: it blocks on the runner and the full `Job` is available by the time the response is sent. The full-`Job` response would technically work.

In Stage 2 the handler returns before any worker touches the job. Only `job_id` is known at that point. The full-`Job` response is structurally impossible.

The choice is therefore not between two equally valid options; it is between a Stage-1-only shape and a shape that survives both stages.

## Decision

Always return `JobCreated{job_id}`.

## Consequences

**Positive**

- The HTTP contract is identical across stages. Frontend code is unchanged at the Stage 1 to Stage 2 boundary.
- Forces the frontend into the polling discipline (`GET /jobs/{id}`) that Stage 2 will require, from day one. If Stage 1 returned the full Job, the frontend would learn to read `status=done` directly from the POST response, and Stage 2 would silently break that path.
- Aligns with REST convention: create operations return the minimum identification of the new resource, not its full state.

**Negative**

- In Stage 1, the frontend performs one extra HTTP round-trip (the first GET) to learn what the POST response could have included. The cost is one request on a localhost loopback, paid in service of Stage 2 contract stability.

## References

- ADR-0001: stage-based additive architecture (the principle this ADR instantiates at the API contract layer).
- ADR-0002: JobStore protocol surface (same staging discipline applied to storage).
