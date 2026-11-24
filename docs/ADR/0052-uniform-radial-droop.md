# ADR-0052 — Uniform radial droop for verticals

- **Status:** implemented 2026-11-24
- **Date:** 2026-11-24
- **Related:** VR1, `docs/AUTONOMOUS_BACKLOG.md` §VR1

## Context

The vertical and loaded-vertical templates generate every radial in the
horizontal plane at `base_height_m`. `radial_angle_deg` is the azimuth of the
first radial, not a droop angle. Sloped radials are common for elevated
quarter-wave verticals and radial skirts, and NEC-2 already supports them as
ordinary straight wires. What is missing is parametric geometry, validation,
persistence, presentation, and optimizer coverage.

## Decision

1. Add `radial_droop_deg` to `VerticalParameters`. Zero is horizontal; positive
   values lower the radial tips; the accepted range is `0 <= droop < 90`.
2. Keep `radial_length_m` as the **physical conductor length**, not its
   horizontal projection. For a radial at angle `delta`:
   - horizontal span = `L cos(delta)`;
   - tip height = `base_height_m - L sin(delta)`;
   - the wire keeps its exact 3D length.
3. Reject a profile whose radial tips fall below `z = 0`, and reject a tip at
   `z = 0` when `base_height_m > 0`; this keeps a sloped radial from emitting a
   ground-contact endpoint through the NEC clearance gap. Horizontal radials at
   `base_height_m = 0` remain allowed and the existing clearance raises the
   model. A non-vertical wire near the ground also triggers the documented
   clearance, so a sloped radial tip between 0 and 1 cm is not missed.
4. Reconstruct the droop in `from_custom_parameters()` from the physical wire
   length and vertical drop. All radials must share one length and droop within
   the existing tolerance; independent per-radial angles remain unsupported.
5. Expose one editor field with EN/ES label and help, enabled only when
   `radial_count > 0`, and preserve it in estimate-context restoration.
6. Persist it in schema 61 with a no-value-rewrite migration: schema 60
   vertical payloads load at `0°`, so their canonical wires are unchanged.
7. Add design-summary and construction-sheet rows for droop and tip height, and
   update the scene/plan callout so the radial length is not shown as a shorter
   horizontal projection without qualification.
8. Add the family-optimizer variable with a hard tip-clearance constraint, or
   classify it explicitly as installation context. It must not be an uncovered
   geometric field.
9. Do **not** add the field to `PhasedVerticalParameters` in this slice. That
   family has its own feed/phase model; decide separately.

## Consequences

Positive:

- One uniform droop covers the common radial-skirt case without custom wires.
- `droop = 0` is bit-identical to the current geometry.
- Physical length, horizontal footprint, and tip height are explicit and
  testable.
- Old projects load unchanged at schema 61.

Costs:

- Schema 61 and a projection-aware construction presentation.
- A new optimizer variable and tip-clearance validation.
- The user must raise the base height enough to allow a meaningful droop.

## Out of scope

- Independent angle or length per radial.
- Arbitrary radial layouts (use custom wires).
- Buried or soil-contact radials.
- The native NEC `GN` radial screen.
- Performance claims or an “optimal” droop preset without a traceable source.
- The phased vertical field.

## Acceptance

- `droop = 0` reproduces the current canonical wires exactly.
- Positive droop produces connected radials with exact 3D lengths and tips at
  the declared height.
- A tip at or below ground is rejected when the base is elevated, with a clear
  message; horizontal radials at base zero and near-ground sloped tips still
  receive the documented NEC clearance.
- `to_custom_parameters()`/`from_custom_parameters()` round-trip droop and
  physical length.
- Schema 60 projects load at 0°; schema 61 round-trips.
- EN/ES help, editor enablement, estimate context, presets, scene, wire
  schedule, design summary, and construction sheet agree.
- The optimizer either varies the field with a hard constraint or records it as
  context; field coverage, determinism, and Apply Best pass.
- A real nec2c sloped-radial case completes with positive input resistance.
- No new numerical reference or performance claim is added.
