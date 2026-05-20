# 0004. Monaco for the in-browser editor

**Status:** Accepted, 2026-05-15

## Context

Stage 1 needs an in-browser editor for C source. Two candidates were considered: Monaco (the editor that powers VS Code, via `@monaco-editor/react`) and CodeMirror 6.

The editor sits in the central flow of the app: paste C, edit, submit. Its UX shapes how the project feels to a first-time user. The choice also affects bundle size, feature surface, and how much wiring per feature the frontend code has to carry.

## Decision

Use Monaco, via `@monaco-editor/react`.

## Consequences

**Positive**

- VS Code-familiar UX out of the box. The target audience (students, KLEE newcomers) overlaps heavily with VS Code users.
- Richer C language services without manual wiring: syntax highlighting, bracket matching, code folding, find-and-replace, multi-cursor. CodeMirror 6 would require each of these to be enabled and configured as a separate extension.

**Negative**

- Larger bundle: roughly 2 MB minified. Not a meaningful constraint for a dev tool delivered over broadband.
- Less flexible than CodeMirror 6 for deep editor customisation. Stage 1 needs none of that flexibility.
- Microsoft-controlled. Acceptable for a permissively licensed library; we are not locked into proprietary services.

## References

- ADR-0006: frontend tooling stack (where this fits in the wider frontend decision set).
