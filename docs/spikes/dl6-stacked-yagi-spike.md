# DL6 — Stacked Yagi architecture note

**Date:** 2026-11-20.
**Status:** design note; implementation not started.
**Question:** how should AntennaDesk compose two to four Yagis into a stack
without hiding the feed network or claiming unvalidated gain?

## Why this is not a simple `stack_count` field

A stack is not just the same Yagi copied at two heights:

- each Yagi has its own feedpoint and mutual coupling;
- the feed splitter and phasing lines change the impedance at every port;
- the lower and upper Yagis do not see the same environment;
- the stack gain depends on spacing, phase, and the feed network;
- per-port impedance and the combined pattern are different results.

Adding a `stack_count` field to `YagiParameters` would create a second feed
without a feed-network model. That is not acceptable as a validated result.

## Recommended architecture

Treat the stack as a **composed family**, not a new wire primitive:

1. Reuse the existing `YagiParameters` for each element.
2. Store count (2–4), vertical spacing, phase step, and amplitude ratio.
3. Build the canonical model with one Yagi per level.
4. Use the existing multi-source model for the first slice, with an **ideal**
   phase/amplitude progression. This is the same experimental approach already
   used by the phased vertical family.
5. Add a real feed network (splitter plus `TransmissionLine` phase lines) as a
   second slice. Until then, label the ideal source progression explicitly.
6. Expose per-port impedance and the combined pattern. The current primary
   feed remains the SWR reference port; additional ports are reported in the
   **Sources** tab.

## First slice

- Two identical Yagis.
- Fixed vertical spacing and 0°/180° phase.
- Ideal equal-amplitude feed, no splitter loss.
- No optimizer; spacing and phase remain context.
- Experimental C: mutual coupling and feed hardware are modeled only as ideal
  sources.
- Schema/ADR before code.
- Scene, reports, construction notes, and a visible limitation row.

## Risks

| Risk | Mitigation |
|---|---|
| Feed split is not physical | Label ideal; add real splitter/TL in the next slice |
| Per-port impedance vs primary SWR | Report both; never call the primary port the whole stack |
| Mutual coupling | Structural and solver tests; compare single vs stack |
| Optimizer scope | No optimizer until the feed model and per-port results are stable |
| Evidence | No gain claim; B/C until a published stack or measurement exists |
| Existing Yagi behavior | Keep stack disabled by default; no change when count=1 |

## Acceptance for the first slice

- A two-level stack builds and runs with two driven sources.
- The primary port still reports SWR; each port reports R/X/power.
- The combined pattern and single-Yagi pattern are inspectable.
- The report states that the feed split is ideal.
- A count=1 design is byte-for-byte the existing Yagi model.
- No optimizer claim and no unvalidated gain claim.

## Recommendation

Do not start with a `stack_count` field in `YagiParameters`. Write the stack ADR
and implement the composed family with an ideal two-source first slice. Add the
real splitter/phase-line model only after the per-port and pattern behavior is
stable.
