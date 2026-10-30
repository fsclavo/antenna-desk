# ADR-0008 — Feed line as post-processing

- **Status:** Accepted
- **Date:** 2026-10-30
- **Supersedes:** none

## Context

AntennaDesk needs a transmission-line model between the transmitter and the
antenna feed. NEC-2 can model a line with a `TL` card, but that requires an
auxiliary segment and changes the source/segment layout. An ideal or uniform
lossy line does not change the antenna current distribution or its radiation
pattern; it only transforms the impedance presented to the transmitter.

## Decision

1. Add an immutable `FeedLine` value object with characteristic impedance,
   length, velocity factor, and matched loss per 100 m.
2. Store it in `SimulationSpec` and as a project-level setting, not in the
   antenna geometry. The project keeps the current line configuration; each
   simulation run keeps the exact line used. Schema v3 remains additive.
3. After NEC normalization, transform each antenna-terminal impedance with the
   standard complex transmission-line equation. Compute SWR from the transformed
   impedance and the configured reference impedance.
4. Add an informational diagnostic when a line is applied. Document that
   impedance/SWR are transmitter-side while pattern and power gain remain
   antenna-side.
5. Expose the setting through **File → Feed Line...** and apply it to template,
   custom, and optimization simulations.

## Consequences

Positive:

- No dummy wire, tag, or segmentation changes are required.
- The full simulation and optimization paths share the same line behavior.
- The model is testable independently with closed-form quarter-wave cases.

Limitations:

- The result does not report antenna-terminal impedance separately.
- Insertion loss is not added to pattern gain or realized gain.
- The model is a uniform line; non-uniform lines and general matching networks
  are out of scope.
