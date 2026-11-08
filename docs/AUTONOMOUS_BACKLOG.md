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
| ~~C1~~ | ~~**Phased verticals / arrays**~~ | XL | multi-source architecture | **Done 2026-11-08:** multi-source model and schema 24, then the 2–4 element phased vertical family with ideal phase/amplitude progression, radial screens, schema 25, editor, scene markers, reports, construction notes, and family optimizer. Evidence remains C pending a traceable reference. |
| ~~C2~~ | ~~Quad beam / hexbeam~~ | L | C1 lessons optional | **Partially done 2026-11-08:** quad beam with 2–3 loops, reflector/driven/optional director, ideal single feed, schema 26, editor, scene, reports, construction notes, and optimizer. Hexbeam remains open; evidence stays C. |
| C3 | Log-periodic | L | transposed feed-line model | **Blocked 2026-11-08:** independent ideal voltage sources with alternating polarity produced a negative primary-feed resistance in NEC2C. A real transposed boom feed line must be modeled before this family can ship; do not approximate it with independent sources. |
| C4 | Discone | L | none | Broadband multi-wire geometry, full DoD, scene, persistence, optimizer, and evidence |
| C5 | Trapped / multiband Yagi | L | trap model reuse | Trap-loaded elements, feed/matching, full DoD, and evidence |
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |
| D4 | Segmented frequency plan in one NEC deck | M | solver benchmark | Deferred; current per-band batching is intentional |

## C1 — Phased verticals / arrays (completed)

**Status:** completed 2026-11-08. Evidence remains experimental pending a
traceable published array or measurement.

The original blocker was the single-feed model (`AntennaModel.feed`) and the
single `EX` source in the NEC adapter. The delivered work crosses the domain
model, solver port, NEC deck, persistence, scene presentation, optimization,
reports, and validation.

Completed slices:

1. **Model and solver — completed 2026-11-08**
   - `Source` value (wire, offset, amplitude, phase) and optional
     `AntennaModel.sources` with the primary feed as source 1;
   - segmentation locates each source independently;
   - the NEC input writer emits one `EX` card per effective source;
   - the primary feed remains the impedance/SWR reference; the total pattern
     and currents include all sources;
   - schema 24 persists the additional sources;
   - unit and real NEC2C two-source tests pass.
2. **Family — completed 2026-11-08**
   - `PhasedVerticalParameters`: count, spacing, height, base height, radial
     system, amplitude taper, phase progression, azimuth, radius, material,
     ground;
   - feed network is an explicit ideal combining model, not a hidden loss;
   - topology (count, radial system) remains a user choice.
3. **Persistence — completed 2026-11-08**
   - schema-25 migration; phase and element-count ranges are validated;
   - round-trip and migration tests.
4. **Presentation — completed 2026-11-08**
   - scene dimensions for spacing and height, and markers for additional
     sources;
   - pattern/current views and reports.
5. **Optimizer — completed 2026-11-08**
   - family descriptor for geometry and phase/amplitude variables;
   - constraints for spacing and phase/amplitude ranges;
   - NEC2C integration and Apply Best adapter.
6. **Evidence — open**
   - a traceable two-element published array or measurement; otherwise the
     family stays experimental with visible limitations.

Do not start C1 by cloning a vertical N times inside a widget. The multi-source
model and solver contract must land first.

## Recommended order

1. ~~A1, A2, and C1~~ (done 2026-11-08).
2. C2 quad beam (done 2026-11-08); hexbeam remains open.
3. C3 is blocked on a transposed boom feed-line model. Do not substitute
   independent ideal sources: NEC2C reported negative primary-feed resistance
   in the prototype.
4. B1–B3 whenever a source or measurement becomes available.
5. C4, C5, and the deferred items.

## Current baseline

- Schema: **26**.
- Full gate: **1,862 passed, 0 skipped** with `NEC2C` and the optional
  `cross-engine` group; rerun without PyNEC if the environment lacks it.
- Last commits: multi-source excitation, phased vertical array, and quad beam.
