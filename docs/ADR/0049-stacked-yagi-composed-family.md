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
  primary port remains the SWR reference (level 1, or the splitter node in
  network mode);
- a front-elevation scene contract, design summary, construction sheet, and a
  multi-boom BOM;
- an optional splitter + phase-line feed: a reference line length, a line
  increment per level, velocity factor, characteristic impedance, and splitter
  excess loss; the phase step is derived from the increment;
- a co-simulated network mode that adds a 1 cm numerical splitter node, a
  lossless reference line to level 1, lossless NEC TL cards to every higher
  level, and reports each network connection point;
- one shared mast and optional guy set across every level, built once at the
  top-boom height instead of copied per level;
- a Wilkinson divider mode solved by the N-port feed-network solver, with a
  declared design frequency, equal N-way quarter-wave branches, star isolation
  resistors, feed-line loss, optional per-level L/Pi/T matching networks, and a
  pattern reconstructed from the solved port voltages;
- a folded driven element or a beta/hairpin match at every driven element,
  built per level from the base Yagi's fields, plus optional ideal per-level
  transformer ratios, matched branch loss, and a deterministic
  component-tolerance corner check in Wilkinson mode;
- a bounded spacing/phase optimizer inside a user-set maximum top-height
  envelope; in phase-line mode the search moves the line increment;
- real `nec2c` tests for an ideal two-level stack, a co-simulated three-level
  network, one shared mast, a per-level beta match, and a folded driven
  element.

The base Yagi editor in the stack exposes folded driven elements. Wilkinson
mode adds optional ideal transformer ratios and matching networks per level;
the other modes use the feed network. A beta/hairpin match is available on
every driven element when the driven element is straight.
The mast and guy fields form one shared support model: a single mast runs from
ground through every level and one guy set attaches to its top. Copying a mast
per level is rejected.

## Why

A stack has a separate feedpoint at every level and mutual coupling between
levels. Adding a counter to a single Yagi would create a second feed without a
feed-network model or a per-port result. The composed family makes that
distinction explicit and made room for the splitter/phase-line and network
slices.

## Consequences

- The family now covers form, schema, catalog, per-port results, scene,
  reports, solver coverage, the splitter/phase-line specification, the
  co-simulated network, one shared mast/guy set, a beta/hairpin match, and the
  Wilkinson N-port feed mode. Line loss is a user-entered matched loss plus a
  per-port load-mismatch correction estimated from the solved port impedances;
  the loss-induced input-impedance shift and a frequency-dependent non-ideal
  splitter/isolation model remain out.
- Evidence is C until a published stack or measurement is available; no
  stacking gain is claimed.
- The ideal source progression is visible as a limitation.
- A count of one is not a stack; use `YagiParameters` directly. The family
  accepts two to four levels.
- A per-level ideal transformer is configured in the Wilkinson feed spec, not
  in the base Yagi. A folded driven element or a beta/hairpin match is copied to
  every level. The mast and guy fields are interpreted as one shared support
  for the whole stack; copying a mast per level would create floating or
  double-counted hardware.
- A [feed-network spike](../spikes/dl6-feed-network-spike.md) rejects scalar
  isolation post-processing; [ADR-0054](0054-bounded-multiport-feed-network.md)
  implements an explicit port/reference abstraction and a bounded Wilkinson
  splitter. Per-level L/Pi/T matching networks are available in Wilkinson
  mode; broadband component-tolerance guarantees remain out.
- The feed network is a bounded co-simulation, not a full N-port circuit model:
  phase-line mode keeps ideal voltage sources and a fixed design-frequency
  phase; network mode co-simulates lossless NEC TLs with frequency-dependent
  electrical length, the reference line, and its differential impedance
  transformation. A matched line-loss value is applied to realized gain; the
  primary SWR remains the lossless network input, so mismatch-dependent line
  loss is not captured. Splitter internal mismatch and per-level matching
  broadband component-tolerance guarantees remain follow-ups. The splitter excess loss is applied
  to realized gain. The spacing/phase optimizer is available once a maximum top
  height is set and makes no gain claim.
