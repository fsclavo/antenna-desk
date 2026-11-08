# Autonomous execution backlog

**Date:** 2026-11-08
**Status:** active queue after the loaded/linked dipole, wire sag, tapered Yagi
tips, space constraints, and PyNEC validation work.

This is the ordered queue for continuing without waiting for new product
decisions. Each item is independently shippable and must leave the full gate
green. Items marked **blocked** require a measurement, a traceable source, or an
external service and must not be invented or simulated into existence.

## Rules

- One coherent milestone per change set.
- Run `ruff check`, `ruff format --check`, both `mypy` passes, and the full
  `NEC2C=... uv run pytest` before declaring an item complete.
- Add domain, persistence, UI, scene, reporting, optimizer, migration, and
  documentation coverage proportional to the item.
- No new numerical reference without a traceable source.
- Do not commit or push unless explicitly requested.

## Queue

| ID | Task | Size | Depends on | Acceptance |
|---|---|---|---|---|
| ~~A1~~ | ~~Decide the boom-correction policy~~ | S | traceable source | **Done 2026-11-08:** the Yagi dialog, evidence registry, and user guide state that boom mounting is not modeled |
| ~~A2~~ | ~~Export optimization evaluation/Pareto data~~ | S–M | none | **Done 2026-11-08:** UTF-8 CSV export with a stable schema, Pareto flags, and tests |
| B1 | Promote `inverted_l` evidence if a source exists | M | independent source | Published dimensions and a numeric metric are tested; otherwise the audit keeps it C |
| B2 | Improve the Ringo matching-ring model | M | manufacturer data or measurement | Matching-ring geometry and impedance are traceable; evidence can move beyond C |
| B3 | Add independent checks for biquad/double biquad/Beverage/loaded dipole | M–L | source or measurement | At least one numeric metric per family is validated or the limitation stays explicit |
| B4 | Fan-dipole coupling calibration | M | measurement | A coupled-fan measurement is reproduced; no scalar correction is invented |
| C1 | **Phased verticals / arrays** | XL | multi-source architecture | See the detailed breakdown below |
| C2 | Quad beam / hexbeam | L | C1 lessons optional | New family with full DoD, scene contract, persistence, optimizer, and evidence |
| C3 | Log-periodic | L | none | Multi-element feed and geometry, full DoD, optimizer, and evidence |
| C4 | Discone | L | none | Broadband multi-wire geometry, full DoD, scene, persistence, optimizer, and evidence |
| C5 | Trapped / multiband Yagi | L | trap model reuse | Trap-loaded elements, feed/matching, full DoD, and evidence |
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |
| D4 | Segmented frequency plan in one NEC deck | M | solver benchmark | Deferred; current per-band batching is intentional |

## C1 — Phased verticals / arrays (largest item)

**Why it is the largest:** the current canonical model has exactly one feed
(`AntennaModel.feed`), and the NEC adapter emits exactly one `EX` source. A
phased array needs multiple driven elements, per-source amplitude and phase,
and a feed/combining model. That crosses the domain model, solver port, NEC
deck, persistence, scene presentation, optimization, reports, and validation.

Proposed slices:

1. **Model and solver**
   - introduce a `Source` value (wire, offset, amplitude, phase) and allow an
     antenna model to carry multiple sources while preserving the single-source
     API for every existing family;
   - update segmentation and the NEC input writer to emit one `EX` card per
     source;
   - normalize per-source currents/patterns in the result;
   - test with two equal in-phase sources and a known two-element spacing.
2. **Family**
   - `PhasedVerticalParameters`: count, spacing, height, base height, radial
     system, amplitude taper, phase progression, azimuth, radius, material,
     ground;
   - feed network is an explicit ideal combining model, not a hidden loss;
   - topology (count, radial system) remains a user choice.
3. **Persistence**
   - schema migration; validate source indices and phase range;
   - round-trip and migration tests.
4. **Presentation**
   - scene dimensions for spacing, height, and phase direction;
   - pattern/current views and reports.
5. **Optimizer**
   - family descriptor for geometry and phase/amplitude variables;
   - constraints for spacing, turning radius, and feed feasibility;
   - NEC2C integration and determinism tests.
6. **Evidence**
   - a traceable two-element published array or measurement; otherwise keep the
     family experimental and state the limitations.

Do not start C1 by cloning a vertical N times inside a widget. The multi-source
model and solver contract must land first.

## Recommended order

1. ~~A1 and A2~~ (done 2026-11-08).
2. C1 in the slices above (largest user-visible and architectural gain).
3. C3 or C2 (next large families).
4. B1–B3 whenever a source or measurement becomes available.
5. C4, C5, and the deferred items.

## Current baseline

- Schema: **23**.
- Full gate: **1,801 passed, 0 skipped** with `NEC2C` and the optional
  `cross-engine` group; **1,798 passed, 1 skipped** without PyNEC.
- Last commits: loaded/linked dipole, wire sag, tapered Yagi tips, space
  constraints, and the optional PyNEC validation cleanup.
