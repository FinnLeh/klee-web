# 0006. Frontend tooling stack

**Status:** Accepted, 2026-05-15

## Context

Stage 1 needs a frontend build chain. Four choices are bundled here because they were considered together: build tool, framework, type system, CSS approach. Splitting them across four ADRs would obscure that each choice is partly justified by the others (e.g. Tailwind's Vite plugin only matters if Vite is the bundler).

The frontend is the only user-facing surface of KLEE Web. Build speed, contract enforcement against the backend, and zero-friction styling all directly affect how fast Stage 1 can ship and how fast Stages 2 and 3 can iterate.

## Decision

- **Vite** as dev server and bundler. Native ESM during development (fast HMR), Rollup-based production build.
- **React 19** as UI framework. Hooks support the polling-loop pattern Stage 1 needs.
- **TypeScript** for compile-time contract enforcement against the backend, via OpenAPI-generated types.
- **Tailwind v4** for styling, through the `@tailwindcss/vite` plugin. CSS-first config: no `postcss.config.js`, no `tailwind.config.js` for the default setup.

## Consequences

**Positive**

- Vite HMR plus React Fast Refresh keep save-to-screen latency under a second during development.
- TypeScript catches backend-frontend contract drift at compile time: renaming a field in a Pydantic model surfaces as a TS error in the consumer after `openapi-typescript` regeneration.
- Tailwind v4's Vite plugin removes the v3 ceremony (no `postcss.config.js`, no `tailwind.config.js` for the default setup), so no extra config files land in the repo.

**Negative**

- TypeScript adds a compile step and syntax overhead compared with plain JavaScript. Worth it for the contract enforcement against the backend, but the cost is real, particularly for a developer whose primary language is not JavaScript.

## References

- ADR-0004: Monaco for the in-browser editor (a concrete consumer of this stack).
