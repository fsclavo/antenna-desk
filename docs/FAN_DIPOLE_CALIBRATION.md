# Fan dipole V-angle and coupling calibration

**Status:** investigation complete
**Date:** 2026-11-03
**Scope:** decide whether the fan estimator should apply an automatic V-angle
length correction

## Question

The fan estimator uses straight half-wave lengths, but each element is built as
a V with a different included angle and is coupled to the other elements. A 5 m
element at 28.48 MHz should have a reasonable SWR when isolated, but a 20/10 m
fan can show a much higher SWR. Is a simple length correction justified?

## Standalone V element

The following NEC-2 runs use a single V element at 10 m above finite ground
(εr = 13, σ = 0.005 S/m). The initial length is the straight half-wave length
from the estimator. The table reports the frequency of minimum SWR and the
ratio to the target frequency.

| Included angle | 14.1 MHz resonance | Ratio | 28.4 MHz resonance | Ratio |
|---:|---:|---:|---:|---:|
| 60° | 15.087 MHz | 1.070 | 30.388 MHz | 1.070 |
| 80° | 14.875 MHz | 1.055 | 29.820 MHz | 1.050 |
| 100° | 14.734 MHz | 1.045 | 29.536 MHz | 1.040 |
| 110° | 14.664 MHz | 1.040 | 29.394 MHz | 1.035 |
| 120° | 14.593 MHz | 1.035 | 29.252 MHz | 1.030 |
| 140° | 14.523 MHz | 1.030 | 29.110 MHz | 1.025 |
| 160° | 14.523 MHz | 1.030 | 28.968 MHz | 1.020 |
| 180° | 14.523 MHz | 1.030 | 28.968 MHz | 1.020 |

A smooth angle-dependent correction is possible for an isolated element, but
even at 180° the straight half-wave formula is about 2–3% high at this height
and ground model. The correction would be an application calibration, not a
physical law.

## Coupled 20/10 m fan

For a 20/10 m fan with a 10.1 m element at 120° and a 5.0 m element at 100°,
the 10 m element alone is about 47 − j50 Ω at 28.48 MHz, but the complete fan
is about 1152 − j232 Ω. The input impedance is not the parallel combination of
two independent dipoles because the elements are mutually coupled.

Optimizing both lengths over a bounded grid found a best SWR of about 3.25:1;
optimizing angles as well did not produce a robust low-SWR solution. The
interaction dominates the result, and it changes with height, ground, angle,
and the other element's length.

## Decision

Do **not** add a universal automatic V-angle or coupling correction to
`estimate_fan_dipole()`.

Reasons:

- the isolated-element correction is installation-dependent;
- the coupled-fan impedance is not a simple parallel combination;
- a correction that improves one 20/10 geometry can worsen another;
- silently changing lengths would make the estimator look more precise than
  the model supports.

Keep the estimator as a documented starting point, keep the V-angle/coupling
warning, and use the Bands tab plus the element optimizer to tune the final
lengths. The optimizer should continue to make clear that unchecked elements
remain in the antenna.

## Follow-up

- Reworking the fan coupling would require a different model (for example
  explicit per-element feeds, traps, or a measured/optimized preset), not a
  scalar length factor.
- If a future calibration is added, it must be tied to a documented geometry,
  height, and ground model and must not be presented as universal.
