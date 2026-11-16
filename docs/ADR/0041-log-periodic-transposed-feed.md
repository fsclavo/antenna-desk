# ADR-0041 — Log-periodic family with a transposed phase line

- **Status:** Accepted
- **Date:** 2026-11-16
- **Deciders:** Fernando Sclavo, development
- **Related:** C3 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md),
  [ADR-0001](0001-solver-selection.md), and
  [`../spikes/c3-log-periodic-spike.md`](../spikes/c3-log-periodic-spike.md)

## Context

The log-periodic dipole array (LPDA) is a beam whose elements are all driven
through a two-wire phase line. The line connects the center of each element to
the next with a crossover between every pair; the rear element terminates the
line and the front element is the feed point. A first attempt used independent
ideal voltage sources with alternating polarity. NEC2C reported a negative
primary-feed resistance, so that approximation is unusable.

The project already has a canonical `AntennaModel` with `Wire`, `FeedPoint`,
`Load`, `TransmissionLine`, and `Source` primitives. A new solver or a parallel
model type for one antenna family would violate the architecture boundary.

## Decision

1. **The LPDA is a normal family.** `LogPeriodicParameters.to_antenna()` returns
   an ordinary `AntennaModel` with one straight wire per element and one
   `TransmissionLine` between each adjacent pair of element centers. No new
   solver, adapter, scene type, or serialization path is introduced.

2. **Phase reversal is a generic line property.** `TransmissionLine` gains a
   `phase_reversal: bool = False` field. The NEC adapter maps it to the
   standard negative characteristic impedance in the `TL` card. The domain does
   not mention NEC, and other families can use the same capability for a
   twisted or crossed line.

3. **The reference is a published model, not a measurement.** The primary
   validation case is L. B. Cebik, W4RNL, "A 10-Meter LPDA", Phase 3: four
   elements, 1.0 in diameter, 28-30 MHz, 75 Ω and 200 Ω phase lines. The
   published NEC-4 values at 29 MHz are 7.36 dBi and 22.01 dB front-to-back for
   the 75 Ω line, and 7.04 dBi and 24.56 dB for the 200 Ω line. The family
   evidence level is **B** until a measured LPDA with complete geometry and
   feed data is available.

4. **The ARRL/Cebik 7 MHz wire design is out of scope for this family.** Its
   elements are swept forward 60° to the feed line, forming a V-shaped wire
   array. Modeling it as a straight-element LPDA does not reproduce its
   published 5.9 dBi/208 Ω table values. A future variant may add an explicit
   element sweep angle with its own evidence.

5. **The model is the published free-space reference.** It is lossless by
   default, has no balun or feed-line loss, and does not include a rear stub,
   boom, mast, or construction tolerances. The feed transformer ratio is applied
   in post-processing through the existing `SimulationSpec` field. The rear
   element is continuously shorted at its center, matching the published
   truncated-line termination.

6. **The family has no full optimizer descriptor.** The descriptor registry
   returns an explicit unavailable reason. A single published 10 m design does
   not provide an independent tolerance for an automated τ, σ, or element-count
   search. The generic one-dimensional length scaling remains available because
   it scales the whole electrical design (element sequence and band ratio).

## Consequences

- The LPDA reuses the existing wire solver, segmentation policy, feed model,
  scene renderer, reports, and project format.
- The phase-reversal flag is persisted in schema 52. Older projects migrate
  with `phase_reversal: false`, preserving their previous behavior.
- The scene draws the phase line as a dashed transmission-line overlay. The
  elements remain the canonical wires, and the scene contract counts only wire
  polylines.
- The family is labeled B with a visible limitation: the performance comparison
  is against a published NEC-4 model, not a measurement.
- A future swept-element V-LPDA variant needs a new geometry parameter and its
  own reference; it must not reuse this family's B claim.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Model the phase line as physical crossed wires | Requires a dense wire model and accurate crossover junctions; the NEC TL facility is the standard published approach and is already in the architecture |
| Use independent ideal sources with alternating polarity | Produced negative primary-feed resistance in NEC2C |
| Add a separate LPDA solver/model type | Duplicates the canonical model and violates the family boundary |
| Treat the 7 MHz V-wire table as a straight-element reference | The physical elements are swept forward 60°; the straight model does not reproduce its performance |
| Add a τ/σ optimizer without a measured reference | Invents a tolerance the published model does not provide |
| Use a measured A-level reference now | No measured LPDA with complete geometry, feed, and performance data was found |

## Validation plan

1. Unit-test the exact Cebik geometry, τ/σ ratios, element schedule, feed at the
   front element, and the three reversed transmission lines.
2. Unit-test the negative `TL` characteristic impedance for phase reversal and
   the schema round-trip/migration.
3. Run NEC2C at 29 MHz and reproduce the published 75 Ω and 200 Ω gain and
   front-to-back ratios, the element-center current phases, and segmentation
   stability.
4. Run the no-reversal control and confirm the pattern collapses.
5. Add the catalog, Change Template, scene contract, default-view, dimension,
   wire-schedule, report, help, and EN/ES tests.
6. Run the full gate.

The reproducible spike record is in
[`../spikes/c3-log-periodic-spike.md`](../spikes/c3-log-periodic-spike.md).
