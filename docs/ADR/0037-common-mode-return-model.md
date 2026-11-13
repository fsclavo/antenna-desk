# ADR-0037 — Bounded feedpoint common-mode choke for end-fed antennas

- **Status:** Accepted
- **Date:** 2026-11-13
- **Deciders:** Fernando Sclavo, development
- **Related:** ADR-0028 (matching-network precedence), EF8/EF8a in
  [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md)

## Context

An end-fed antenna needs a return path. EF8a lets the user choose the
installation proxy, a physical counterpoise, or a coax-shield wire
approximation. The shield is a real conductor, but a useful common-mode model
must also account for the choke that separates the shield from the shack.

A complete model would need:

- the coax shield as a transmission line with transfer impedance;
- the choke's measured complex impedance versus frequency;
- the shack-end ground and the real cable route;
- the resulting common-mode current distribution.

NEC-2 has no coax-shield transfer-impedance element and no distributed ferrite
model. AntennaDesk does not have a traceable universal `Zcm(f)` dataset for a
specific choke, and inventing one would violate the project's reference-value
policy. Sources such as AA5TB, KW4TI, K9YC, and G3TXQ describe the problem and
measurement methods, but they do not provide a single universal choke model
that can be applied to every user's hardware.

## Decision

Implement a **bounded feedpoint choke model**:

1. The user supplies the measured series equivalent `R` and `X` of their choke
   and the frequency at which it was measured, plus a source description.
2. The choke is placed at the **feedpoint**, in series with the start of the
   coax-shield return wire. The model is a NEC series load.
3. `R` is held constant. A positive `X` is realized as a series inductance and
   a negative `X` as a series capacitance, evaluated at the measurement
   frequency. The reactance therefore changes with frequency across a sweep;
   this is an extrapolation from one measured point, not a measured curve.
4. The choke is off by default, requires the `coax_shield` return path, and is
   rejected when the user supplies no non-zero impedance or no source.
5. The editor warns when the measurement frequency differs from the design
   frequency by more than 1 %, and when the choke is predominantly reactive
   (`|X| > R`), because a reactive choke can increase common-mode current by
   cancelling the shield reactance.
6. Reports show the choke R/X and measurement frequency. The model is
   identified as a feedpoint model, not a shack-end choke.

The model is intentionally **not** a universal choke preset. A future preset
requires a traceable measured `Zcm(f)` table for a precisely defined winding.

## Consequences

- A user with a VNA measurement can explore how a real choke impedance changes
  the shield current, feedpoint impedance, and pattern in NEC.
- The model does not claim to predict the common-mode current on an installed
  feedline, the shield's transfer impedance, or the effect of a shack-end choke.
- The choke's resistive part is a NEC load loss and is not added to the
  post-processing balun/unun loss. This avoids double counting.
- The model remains a bounded approximation; validation against a measured
  common-mode current is still required before treating absolute values as
  predictive.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Built-in universal `Zcm(f)` table | No traceable dataset covers arbitrary chokes; a preset would be mistaken for the user's hardware |
| Ideal lossless choke | Hides the reactive-cancellation problem and provides no measurable effect |
| Treat choke `R` as differential balun loss | Wrong power path; the choke is a common-mode element |
| Model the shack end now | Requires a coax-shield transmission-line model, shack ground, and cable route that are not available |
| Ignore common mode entirely | EF8a's shield wire is already a model; ignoring the choke leaves a misleading open shield |

## Validation plan

1. Measure a specific choke's series `R` and `X` with a VNA at the design
   frequency using a two-port S21 method.
2. Enter those values and the source in the end-fed editor.
3. Compare the modeled feedpoint impedance and shield current against a
   measurement or a validated common-mode simulation.
4. Record the choke construction, core, turns, cable, measurement fixture, and
   uncertainty. Do not generalize the result to other chokes.
