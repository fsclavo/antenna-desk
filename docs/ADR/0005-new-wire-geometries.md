# ADR-0005 — Folded dipole and loop templates

- **Status:** Accepted
- **Date:** 2026-10-29
- **Supersedes:** none

## Context

Phase 6 started with a vertical center-fed dipole in the existing single-wire
`wire_dipole` model. The next useful geometries are a folded dipole and a
simple loop. Both are naturally represented by the existing `AntennaModel`
with multiple wires, so the solver adapter should not need geometry-specific
branches.

The application also needs to keep project files compatible. Schema version 3
already persists simulation runs, and changing the `wire_dipole` payload would
break existing files. The new geometries must be an additive extension.

## Decision

1. Add two frozen parameter dataclasses:
   - `FoldedDipoleParameters`: two parallel elements, two end connectors, and
     a center feed on the driven element.
   - `LoopParameters`: a vertical regular polygon with 3–128 sides, a bottom
     height above ground, and a feed at the midpoint of the first side.
2. Define `AntennaDesignParameters` as the union of the dipole, folded-dipole,
   and loop parameter types. `antenna_type_for()` maps parameters to the
   stable type identifiers `wire_dipole`, `folded_dipole`, and `loop`.
3. Store the union in `DesignVariant`, validate that `antenna_type` matches the
   parameters, and update both the type and derived model in
   `with_parameters()`.
4. Keep schema version 3. Add `FoldedDipoleParametersPayload` and
   `LoopParametersPayload`, select the payload class from `antenna_type`, and
   leave existing `wire_dipole` payloads unchanged.
5. Expose an antenna-type selector in the design form. Show spacing for folded
   dipoles and side count for loops. Convert the current design when the user
   applies or simulates.
6. Use the shared multi-wire `AntennaModel` directly in the NEC adapter. Do not
   add folded/loop-specific calculations to the adapter.
7. Switch multi-wire designs to Plan view. Put construction dimensions in Plan
   for every geometry; use Elevation for installation and position above
   ground (height, feed height, ground line, and a folded-conductor section).
8. Limit `EditDipoleLength` to `DipoleParameters`. Optimize the primary
   dimension for all three templates: total length for wire and folded
   dipoles, circumference for loops.
9. Treat folded and loop solver runs as topology and sanity coverage until
   traceable independent impedance references are added. Do not invent
   expected values.

## Consequences

Positive:

- The solver adapter remains geometry-agnostic and already supports multiple
  wires.
- Existing project files remain valid; the schema change is additive.
- Reports, construction sheets, and comparison can share type-aware summaries.
- The UI can convert designs without duplicating the whole project.

Negative and limitations:

- A loop is a polygon approximation; a larger side count is more circular and
  more expensive to segment.
- Folded-dipole end connectors are short wires; segmentation warnings may
  appear unless they are modeled with appropriate segment counts.
- The application does not yet edit free-form wire coordinates.
- Folded and loop templates need independent published references and
  measurement validation.

## Follow-ups

- Add traceable independent reference cases from MMANA-GAL or the ARRL Antenna
  Book, including engine version, configuration, and tolerances.
- Per-wire segmentation and feed-aligned counts are implemented; keep
  monitoring short-connector warnings.
- Add VNA CSV import and measurement records separately; they are not part of
  this decision.
