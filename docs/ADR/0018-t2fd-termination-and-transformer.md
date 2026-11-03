# ADR-0018 — T2FD termination and transformer model

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none

## Context

The T2FD (terminated folded dipole) is a broadband HF antenna built from two
parallel conductors joined at both ends. One conductor is fed at its midpoint;
the other carries a non-inductive terminating resistor at its midpoint. The
resistor limits the feedpoint impedance excursions and converts a significant
part of the applied power into heat. Commercial designs add a transformer
between the antenna and the coax (for example, 800 Ω to 50 Ω with 16:1).

The project needs a reproducible model that keeps the resistor in the
electromagnetic solution, keeps the transformer out of the NEC geometry, and
does not claim more precision than the published construction rules provide.

## Decision

1. Implement the T2FD as a **first-class** `T2FDParameters` type, not as a
   `CustomAntennaParameters` preset. The family keeps its own editor, catalog
   entry, persistence payload, report rows, and geometry presentation.
2. Build the canonical model from four wires: two parallel conductors and two
   end connectors. The feed is at the midpoint of the driven conductor. The
   termination is a `SeriesLoad` at the midpoint of the other conductor.
3. Treat the terminating resistor as a series `LD 0` load. This is the NEC
   representation of a resistor inserted in the conductor.
4. Keep the transformer out of the NEC geometry. Store its ratio in
   `T2FDParameters` and pass it to `SimulationSpec.feed_transformer_ratio`.
   The existing two-port link budget then applies an ideal impedance
   transformation to the transmitter-side SWR, mismatch loss, and realized
   gain.
5. Support horizontal and vertical flat installations. Do not synthesize a
   tilted geometry from the family name. The tilt is an installation detail and
   remains a documented limitation.
6. Use odd segment counts on both parallel conductors so the feed and the
   termination fall at the center of a segment. Keep both counts equal so the
   folded geometry remains balanced.
7. Use Cebik's wide-long starting rule: `300/F(MHz)` feet of span and
   `10/F(MHz)` feet of spacing at the lowest design frequency. Default to the
   commercial 800 Ω termination and 16:1 transformer for 50 Ω coax. Both values
   remain editable because other published T2FDs use 390-480 Ω and a 4:1
   transformer to 75 Ω.
8. Document that the resistor and transformer are ideal, that balun losses are
   not modeled, and that the antenna is non-resonant.

## Consequences

Positive:

- The resistor participates in the NEC solution, so its loss and its effect on
  the input impedance are visible in efficiency, gain, and SWR.
- The transformer is evaluated by the same link-budget code as feed lines and
  matching networks.
- The model uses the canonical four-wire geometry and does not special-case
  the sketch.
- The starting dimensions are traceable to a published construction rule.

Limitations:

- The resistor has no power rating or temperature model.
- The transformer and balun are ideal; common-mode current and balun loss are
  not modeled.
- A tilted installation is not modeled.
- No resonance tolerance is claimed; the span and spacing are starting points.
- The pattern becomes high-angle above roughly 1.25 wavelengths, which is a
  property of the antenna rather than a solver defect.

## Follow-ups

- Add an optional tilt angle if a traceable geometry and reference become
  available.
- Add a resistor power-dissipation report row from the load current.
- Compare the model against measured impedance and efficiency data when
  measurements are available.
