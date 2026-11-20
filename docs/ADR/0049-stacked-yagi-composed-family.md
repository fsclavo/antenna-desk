# ADR-0049 — Stacked Yagi as a composed family

**Status:** accepted for a domain prototype, 2026-11-20.
**Scope:** DL6 first slice.

## Decision

A stacked Yagi is a composed family, not a `stack_count` field on
`YagiParameters`. The first slice keeps one `YagiParameters` per level and
builds a canonical `AntennaModel` with:

- two to four identical Yagis at a fixed vertical spacing;
- one primary feed on level 1;
- additional ideal sources on levels 2–4 with a fixed amplitude ratio and phase
  step;
- no power splitter, phase-line hardware, or splitter loss.

The primary port remains the reported SWR reference. Per-port results are
reported through the existing multi-source model.

## Why

A stack has a separate feedpoint at every level and mutual coupling between
levels. Adding a counter to a single Yagi would create a second feed without a
feed-network model or a per-port result. The composed family makes that
distinction explicit and leaves room for a real splitter/phase-line slice.

## Consequences

- The prototype is domain-only; no form, schema, or catalog route yet.
- Evidence is C until a published stack or measurement is available.
- The ideal source progression is visible as a limitation.
- A count of one remains a normal Yagi; no existing Yagi behavior changes.
- Optimizer, splitter loss, phase lines, and per-port UI are follow-ups.
