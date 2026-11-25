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
- an optional splitter + phase-line feed: a reference line length, a line
  increment per level, velocity factor, characteristic impedance, and splitter
  excess loss; the phase step is derived from the increment;
- a co-simulated network mode that adds a 1 cm numerical splitter node, a
  lossless reference line to level 1, lossless NEC TL cards to every higher
  level, and reports each network connection point;
- a bounded spacing/phase optimizer inside a user-set maximum top-height
  envelope; in phase-line mode the search moves the line increment;
- real `nec2c` tests for an ideal two-level stack and a co-simulated
  three-level network.

The base Yagi editor in the stack disables folded/matched driven elements,
per-level feed transformers, mast, and guy wires. Those geometries remain
unavailable until the feed network and one shared support model exist.

## Why

A stack has a separate feedpoint at every level and mutual coupling between
levels. Adding a counter to a single Yagi would create a second feed without a
feed-network model or a per-port result. The composed family makes that
distinction explicit and made room for the splitter/phase-line and network
slices.

## Consequences

- The family now covers form, schema, catalog, per-port results, scene,
  reports, solver coverage, the splitter/phase-line specification, and the
  co-simulated network. Line loss is a user-entered matched-loss value; the
  hardware, splitter internal mismatch, and per-level matching remain out.
- Evidence is C until a published stack or measurement is available; no
  stacking gain is claimed.
- The ideal source progression is visible as a limitation.
- A count of one is not a stack; use `YagiParameters` directly. The family
  accepts two to four levels.
- A Yagi with a mast, guy wires, folded/matched driven element, or per-level
  feed transformer is rejected until the stack owns one shared support and
  feed model; copying them per level would create floating or double-counted
  hardware.
- The feed network is a specification layer, not a full N-port co-simulation:
  phase-line mode keeps ideal voltage sources and a fixed design-frequency
  phase; network mode co-simulates lossless NEC TLs with frequency-dependent
  electrical length, the reference line, and its differential impedance
  transformation. A matched line-loss value is applied to realized gain; the
  primary SWR remains the lossless network input, so mismatch-dependent line
  loss is not captured. Splitter internal mismatch, per-level matching, and a
  shared mast remain follow-ups. The splitter excess loss is applied to
  realized gain. The
  spacing/phase optimizer is available once a maximum top height is set and
  makes no gain claim.
