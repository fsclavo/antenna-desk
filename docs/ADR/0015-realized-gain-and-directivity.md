# ADR-0015 — Realized gain and directivity

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none

## Context

NEC-2 reports far-field power gain relative to the power accepted by the
antenna. That value includes conductor and ground losses but does not include
the transmitter-to-antenna link: feed-line loss, matching-network loss, the
ideal feed transformer, or mismatch at the reference plane. It is also not
directivity. Reporting a single `gain_total_db` as if it were realized gain
overstates station performance.

The project needs explicit, testable conventions for three quantities:

1. **Power gain (NEC)**: radiated power density relative to the accepted input
   power, including structure losses.
2. **Directivity**: power gain divided by radiation efficiency.
3. **Realized gain**: power gain multiplied by the transducer gain of the
   transmitter-to-antenna cascade.

## Decision

1. Keep the parsed NEC far-field values as power gain. Do not relabel them as
   realized gain or directivity.
2. Derive directivity per frequency as
   `D_dB = G_NEC_dB - 10 log10(eta_structure)`, where `eta_structure` is the
   NEC power-budget efficiency. If the power budget is missing or non-positive,
   directivity is unknown.
3. Model the feed line, matching network, and ideal transformer as a two-port
   cascade from the transmitter to the antenna:
   - feed line first, then matching network;
   - the ideal transformer is an impedance scaling applied to the antenna load;
   - each block exposes an ABCD matrix.
4. Compute the link transducer gain relative to the available power of a source
   at `SimulationSpec.reference_impedance_ohm`. The result includes transmitter
   mismatch, line loss, network loss, and residual load mismatch.
5. Report realized gain per frequency as
   `G_realized_dB = G_NEC_dB + G_T_dB`.
6. Report informational loss components evaluated at a representative
   frequency:
   - mismatch loss at the transmitter reference plane;
   - matched feed-line loss;
   - matching-network loss.
   The exact realized gain uses the full cascade; the components need not add
   exactly because they are evaluated at their nominal reference planes.
7. Keep the pattern charts as NEC power gain until a dedicated pattern-metric
   selector is added. Label them explicitly as power gain.
8. Persist the new per-frequency values as optional fields. Older runs load
   with `None`; no migration is required.

## Consequences

Positive:

- Reports and the results summary distinguish power gain, directivity, and
  realized gain.
- Feed-line and network losses become visible instead of being hidden in a
  single SWR number.
- The two-port math is unit-tested independently of the solver.

Limitations:

- Directivity depends on NEC's reported efficiency; conductor and ground
  losses must be enabled for a meaningful value.
- The matching-network loss is evaluated with the feed-line characteristic
  impedance as its source; it is an engineering estimate, not a full
  transmitter/receiver model.
- The tuner is not modeled as a matching network.
- The pattern charts still show power gain, not realized gain.
- The feed-line loss component uses the matched-line loss; the realized gain
  uses the exact cascade.

## Follow-ups

- Add a pattern-metric selector for power gain, directivity, and realized gain.
- Add a transmitter/tuner network model.
- Compare the link-budget math against measured station data when available.
