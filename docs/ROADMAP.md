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

Completed:

- M1: parametric Yagi generator with editable element table and NBS preset.
- M2: inverted-V generator.
- Single **New Antenna** catalog with search, Antenna Type selection, and
  family grouping.
- Explicit antenna family/template mapping in the domain and design panel.
- Generated-design metadata (`generator_id` / `generator_name`) persisted in
  legacy custom designs.
- All current generators (Yagi, inverted-V, vertical, OCFD) are first-class
  templates with inline editors and native persistence.

In progress:

- M3 catalog expansion complete: delta/quad loops, Moxon, OCFD, vertical with
  radials, and fan dipole are available.
- M4 measurement support: VNA CSV import, measurement conditions/reference
  plane, project measurements, and measured/simulated SWR comparison.

Deferred:

- VNA import, measurement records, and hardware control.
- Advanced full-wave engines.

## Milestones

### M1 — Parametric Yagi generator (completed)

- Element table: position along boom, total length, radius.
- Add/remove elements and arbitrary driven-element index.
- NBS 0.8λ five-element starting preset.
- Generate a first-class editable Yagi design.
- Structural tests plus a reference-backed NEC check for the NBS preset.
- UI: Yagi entry in the **New Antenna** catalog with an inline element editor.

### M2 — Inverted-V generator (completed)

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
| P0 | Inverted-V generator | C | done |
| P1 | Catalog metadata and validation badge | A/B/C | done |
| P1 | Delta loop / quad presets | B/C | done |
| P1 | Moxon generator | B/C | done |
| P1 | OCFD generator | B/C | done |
| P1 | Fan dipole generator | B/C | done |
| P1 | Vertical with radial screen | B/C | done |
| P2 | VNA CSV and measurement records | A | in progress |
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
