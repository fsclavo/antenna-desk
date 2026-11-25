# ADR-0049 — Stacked Yagi as a composed family

**Status:** accepted 2026-11-20; first slice implemented 2026-11-25.
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

## Implementation (2026-11-25)

The first slice is implemented with these boundaries:

- `StackedYagiParameters` and a two-to-four-level canonical model;
- schema 62 with a metadata-only 61→62 migration;
- a stacked-Yagi form and catalog routes for **New Antenna** and **Change
  Template**;
- the generic **Sources** results table reports every driven level, while the
  primary port remains the SWR reference;
- a front-elevation scene contract, design summary, construction sheet, and a
  multi-boom BOM;
- an explicit optimizer-unavailable reason because the feed split and
  mechanical envelope are not validated;
- a real `nec2c` two-level, two-source test.

The base Yagi editor in the stack disables folded/matched driven elements,
per-level feed transformers, mast, and guy wires. Those geometries remain
unavailable until the feed network and one shared support model exist.

## Why

A stack has a separate feedpoint at every level and mutual coupling between
levels. Adding a counter to a single Yagi would create a second feed without a
feed-network model or a per-port result. The composed family makes that
distinction explicit and leaves room for a real splitter/phase-line slice.

## Consequences

- The first slice is form, schema, catalog, per-port results, scene, reports,
  and solver coverage; the splitter loss and phase-line hardware remain out.
- Evidence is C until a published stack or measurement is available; no
  stacking gain is claimed.
- The ideal source progression is visible as a limitation.
- A count of one is not a stack; use `YagiParameters` directly. The family
  accepts two to four levels.
- A Yagi with a mast, guy wires, folded/matched driven element, or per-level
  feed transformer is rejected until the stack owns one shared support and
  feed model; copying them per level would create floating or double-counted
  hardware.
- Optimizer, splitter loss, phase lines, and a shared mast are follow-ups.
