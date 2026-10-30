# ADR-0007 — Custom straight-wire designs

- **Status:** Accepted
- **Date:** 2026-10-29
- **Supersedes:** none

## Context

The guided templates cover dipoles, folded dipoles, and regular-polygon loops.
Users need arbitrary straight-wire geometries that do not fit those templates.
The canonical `AntennaModel` already represents multiple wires, a feed,
environment, and loads, so the solver does not need a new geometry path.

## Decision

1. Add `CustomAntennaParameters` with frequency, wires, feed, ground, and loads.
   `to_antenna()` builds the same canonical model used by the templates.
2. Add the `custom` antenna type to `AntennaDesignParameters` and persistence.
   The custom payload stores the wire geometry explicitly; schema v3 remains
   additive.
3. Keep the guided design panel for template designs. Custom designs use a
   dedicated modal editor and a separate summary panel.
4. Disable primary-dimension optimization for custom designs. They have no
   single length/circumference.
5. Reuse the existing simulation, load, report, comparison, persistence, and
   export paths.
6. Add a practical NEC-2 subset importer (GW, EX, FR, GE/GN, LD 0/1) and a
   basic MMANA-GAL `.maa` geometry/source importer. Both create custom wire
   designs and report unsupported/omitted data.

## Consequences

Positive:

- Arbitrary straight-wire models can be simulated without changing the solver.
- The same project/report/load infrastructure applies to custom designs.
- The guided templates remain simple and validated.

Limitations:

- Wire editing is coordinate-based, not a 3D drawing tool.
- Geometry warnings cover short wires, overlaps, and crossings, but do not
  enforce electrical junctions or repair the geometry automatically.
- Custom designs cannot use length optimization.
- NEC import supports only a practical subset; unsupported cards are reported.
- MMANA import does not read ground, loads, segmentation, or calculated results.
- The radial generator adds geometry only; it is not a calibrated ground-screen
  model.

## Follow-ups

- Extend the NEC importer with GM/GR transformations and more source types.
- Extend MMANA import to ground/loads when the format is verified.
- Add wire/load selection in the geometry view.
- Add reference cases from imported models.
