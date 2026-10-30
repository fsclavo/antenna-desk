# AntennaDesk roadmap and backlog

**Updated:** 2026-10-30  
**Status:** active roadmap after the catalog/experimentation decision.

## Product direction

AntennaDesk is a design and experimentation tool for radio amateurs, not a
catalog of reference-approved antennas. The solver must remain trustworthy, but
users must be able to create, modify, and simulate geometries that have never
been built and therefore have no external reference.

Validation therefore applies at two different levels:

1. **Solver validation:** the NEC adapter and normalization must match
   independent references. This remains strict.
2. **Template/generator validation:** a template is not blocked because no
   independent result exists. It must be labeled with its evidence level and
   must not claim more accuracy than it has.

## Evidence levels

| Level | Meaning | Required evidence |
|---|---|---|
| A. Reference-backed | Compared with an independent source | Traceable source, metric, tolerance |
| B. Published or heuristic | Based on a published design rule or starting point | Source or documented heuristic |
| C. Experimental | Arbitrary geometry or unverified generator | Structural tests and visible warning |

A 10% tolerance is acceptable for many dimension/heuristic comparisons. It is
not a universal rule for gain, nulls, or impedance; each metric keeps its own
tolerance.

## Current state

Completed:

- Solver adapter, normalized results, persistence, imports, and reports.
- Guided dipole, folded dipole, vertical loop, and custom wires.
- Series/parallel loads, optimization objectives, feed line, pattern resolution.
- A/B comparison, construction sheets, CSV/HTML/PDF exports.
- Reference anchors for NEC examples and selected ARRL dipole/folded/loop
  properties.

Completed in M1:

- Parametric Yagi generator with editable element table and NBS preset.

In progress:

- Broad parametric catalog with explicit evidence levels; next is inverted-V.

Deferred:

- VNA import, measurement records, and hardware control.
- Advanced full-wave engines.

## Milestones

### M1 — Parametric Yagi generator (completed)

- Element table: position along boom, total length, radius.
- Add/remove elements and arbitrary driven-element index.
- NBS 0.8λ five-element starting preset.
- Generate an editable custom-wire design.
- Structural tests plus a reference-backed NEC check for the NBS preset.
- UI: **File → New Yagi...**, validation badge/notes in the generated design.

### M2 — Inverted-V generator

- Apex height, included angle, leg length, azimuth, wire radius, ground.
- Free-space and ground simulations.
- Structural and scaling tests; reference only when a primary numeric source is
  available.

### M3 — Catalog expansion

- Delta loop and quad presets.
- Moxon rectangle.
- Off-center-fed dipole and fan dipole.
- Vertical with radial ground-screen options.
- Each entry records evidence level and limitations.

### M4 — Advanced design and measurement

- Multi-element optimization and constrained geometry.
- VNA CSV import and measurement comparison.
- Measurement conditions and reference-plane metadata.

## Backlog

| Priority | Item | Evidence | Status |
|---|---|---|---|
| P0 | Parametric Yagi generator | B/C | done |
| P0 | Inverted-V generator | C | next |
| P1 | Catalog metadata and validation badge | A/B/C | pending |
| P1 | Delta loop / quad / Moxon generators | B/C | pending |
| P1 | OCFD and fan dipole generators | B/C | pending |
| P1 | Vertical with radial screen | B/C | pending |
| P2 | VNA CSV and measurement records | A | deferred |
| P2 | Multi-element optimization | n/a | pending |
| P2 | Packaging and release hardening | n/a | pending |

## Definition of done for a generator

- Domain generator is independent of Qt and the solver.
- Geometry invariants and feed connectivity are tested.
- Scaling with frequency is tested.
- Presets identify their source or heuristic.
- Experimental generators show a visible limitation/warning.
- A reference test is added when a traceable numeric oracle exists.
- Documentation and changelog are updated.
