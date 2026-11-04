# ADR-0023 — Yagi and Moxon horizontal/vertical polarization

- **Status:** Accepted
- **Date:** 2026-11-04
- **Deciders:** Fernando Sclavo, development
- **Phase:** Generated arrays

## Context

The Yagi and Moxon templates were hard-coded as horizontal arrays. Both are
also used with vertical polarization: the boom stays horizontal and the
radiating elements rotate around it. Adding a UI label without changing the
canonical wires would produce a horizontal simulation while claiming vertical
polarization, which is worse than not supporting the mode.

The orientation must be persisted so reopening a project reconstructs the same
geometry. Existing projects have no polarization field and must remain
horizontal.

## Decision

- Add `Polarization` (`horizontal` or `vertical`) to `YagiParameters` and
  `MoxonParameters`, defaulting to horizontal.
- Keep the boom horizontal in both modes:
  - Yagi elements rotate from the horizontal plane to vertical planes.
  - The complete Moxon rectangle rotates into a vertical plane; its bent tips
    still run along the boom.
- Keep `height_m` as the boom/element centerline height.
- Validate that the lowest Yagi tip and the lowest Moxon edge stay above
  ground.
- Bump the native project schema to **version 7** and migrate version 6
  documents by adding `parameters.polarization = "horizontal"` to Yagi and
  Moxon designs only.
- Reuse the existing canonical wire model, solver adapter, estimator registry,
  scene builder, and simulation path. Polarization changes the generated
  coordinates, not the solver contract.
- Do not support vertical booms, tilted polarization, or dual/circular
  polarization in this change.

## Consequences

### Positive

- The UI, reports, geometry views, and solver agree on one real geometry.
- Existing horizontal designs and projects open unchanged.
- Vertical Yagi/Moxon patterns come from the same solver and normalization
  path as every other family.
- In free space, the vertical design is a 90-degree rotation of the horizontal
  design and must match its impedance and total gain.

### Negative

- The height semantics are now different for horizontal and vertical modes:
  the same numeric height means the element plane or the boom centerline.
- Vertical arrays need explicit ground clearance and can be invalid at a
  height that is legal for a horizontal array.
- The schema and report summaries gain another field.

### Neutral

- The plan view of a vertical array is edge-on; the geometry header says so
  and elevation is selected by default.
- Frequency-first estimation keeps the selected polarization and applies the
  same ground-clearance validation.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Add a label without changing the wires | Simulation would contradict the UI |
| Support vertical booms too | Out of scope and changes the mechanical/electrical model |
| Infer polarization from wire coordinates only | Ambiguous, fragile, and hides design intent |
| Use the existing dipole `orientation` field | Different semantics: the Yagi/Moxon boom stays horizontal |
| Support arbitrary polarization angles | Requires a more general rotation and UI; defer |

## Follow-up

1. Keep the free-space rotation equivalence test in the NEC integration suite.
2. Revisit arbitrary polarization angles only if a user need is demonstrated.
3. Do not add dual or circular polarization without a two-port model.
