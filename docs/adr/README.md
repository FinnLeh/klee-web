# Architecture Decision Records

One sequentially-numbered markdown per major design decision. The slides (`~/Documents/MSc_Computing/Thesis/`, source of truth) are distilled here into single-decision documents that live with the code.

## Format

[Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) style. Each ADR has:

1. **Title** (`0007-pick-database.md`, short kebab-case)
2. **Status** (Proposed / Accepted / Superseded by NNNN / Deprecated)
3. **Context** What forces are at play, what constraints exist
4. **Decision** What we chose
5. **Consequences** What becomes easier, what becomes harder, what's now load-bearing

Keep them short. One page is enough for almost every decision. If it needs more, split it.

## Numbering

Sequential, four-digit, never reused. If an ADR is superseded, the new one references the old one and the old one's status flips to `Superseded by NNNN`. Old ADRs stay in the repo as history.

## When to write one

Write an ADR when:

- A decision constrains future choices (picking React over Vue; Redis over RabbitMQ; gVisor over Firecracker).
- A choice is non-obvious enough that a future reader, or future me, will ask "why this?".
- A decision is reversed (write a new ADR explaining the reversal, supersede the old).

Don't write ADRs for:

- Bug fixes.
- Local tactical choices that don't constrain the rest of the system.
- Anything where the answer is obviously the only sensible option.

## Index

| # | Title | Status |
|---|-------|--------|
| 0001 | Stage-based additive architecture | Accepted |
