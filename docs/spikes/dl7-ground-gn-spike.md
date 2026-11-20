# DL7 spike — NEC-2 ground screen and cliff

**Date:** 2026-11-20.
**Status:** exploratory spike; implementation decision pending. The numeric
examples below are decision context, not a validated reference: the decks were
temporary and the pinned source cache is git-ignored, so a clean checkout cannot
reproduce them without adding a committed case.
**Question:** can NEC-2's native `GN` radial screen and second-medium/cliff
fields provide a trustworthy site model for AntennaDesk?

## Sources

- NEC-2 manual, Ground Parameters (`GN`) and Radiation Pattern (`RP`) cards:
  <https://www.nec2.org/part_3/cards/gn.html>,
  <https://www.nec2.org/part_3/cards/rp.html>.
- Pinned `nec2c` source in `spikes/phase0/.cache/`.
- Real `nec2c` runs; decks are temporary and not part of the project.

## What the engine supports

`GN IPERF NRADL EPSE SIG F3 F4 F5 F6`

- `IPERF=0`: finite ground, reflection-coefficient approximation.
- `NRADL>0`: radial wire ground screen centred at the origin in the XY plane;
  `F3` is screen radius, `F4` is screen wire radius.
- With `NRADL=0`, `F3/F4` are a second medium and `F5/F6` are the edge distance
  and height for a cliff.
- The second medium changes only far-field patterns, **not** antenna impedance
  or currents.
- `RP` mode 4 selects the radial screen, 3 the circular cliff, 2 the linear
  cliff, and 5/6 combine a screen with a cliff.

The current adapter always emits `RP 0`, so DL7 would need a pattern-mode
plumbing change even if the ground fields were added.

## Test cases

Vertical monopole: 10 m, radius 2 mm, 7.1 MHz, finite ground
`εr=13`, `σ=0.005 S/m`, 21 segments. Pattern: theta 0–90°, 5° step.

| Case | R (Ω) | X (Ω) | Notes |
|---|---:|---:|---|
| Flat finite ground | 266.76 | -767.01 | no screen |
| Native `GN` screen, 16 radials, 5 m, 1 mm | 33.62 | -17.47 | `RP 4` |
| Dense-wire screen, 16 × 5 m radials at z=0.01 m | 1022.60 | -422.81 | ordinary wires, `RP 0` |
| Circular cliff, medium 2 water, edge 0 m | 266.76 | -767.01 | impedance unchanged, as documented |

Pattern comparison, flat vs circular cliff at edge 0 m:

| Theta | Flat total (dB) | Cliff total (dB) | Delta |
|---:|---:|---:|---:|
| 5° | -29.48 | -28.30 | +1.18 |
| 10° | -23.46 | -22.28 | +1.18 |
| 30° | -14.05 | -12.79 | +1.26 |
| 60° | -9.51 | -7.75 | +1.76 |
| 85° | -15.77 | — | cliff case was sampled to 80° in this run |

A 50 m edge distance produced only small changes at 80–85°; the effect grows as
the antenna approaches the edge. This is consistent with the manual: the second
medium is a far-field model.

## Findings

1. **Native `GN` screen and dense radials disagree by a large factor** for input
   impedance in this case (33.6 − j17.5 Ω vs 1022.6 − j422.8 Ω). The native
   result is numerically plausible, but the dense-wire result is also affected
   by wires only 1 cm above finite ground and by thin-wire near-ground limits.
   Neither is a validated reference.
2. **The native screen is a reflection-coefficient approximation**, not a
   physical radial mesh. It can change SWR substantially and must not be
   presented as an accurate radial-system model without a measurement or a
   traceable published case.
3. **The cliff/second-medium path is far-field only** and leaves impedance
   unchanged. That is a clean, bounded behavior: a site-profile feature can
   honestly say "pattern changes, SWR does not".
4. **`RP` mode plumbing is required.** The adapter currently emits `RP 0`; a
   native screen/cliff implementation must add a structured pattern-mode field
   and parser expectations.
5. **Full terrain is still out of scope.** This spike only covers a radial
   screen and a single straight/circular edge; it does not cover faceted terrain,
   diffraction, buildings, vegetation, or multiple reflections.

## Recommendation

- Do **not** implement a broad DL7 terrain feature yet.
- If a bounded site slice is wanted, implement the **cliff/second-medium
  far-field profile** first, labelled B/C, with the explicit statement that SWR
  and currents are unchanged. It is the safest part of `GN`.
- Treat the native radial screen as an **experimental pattern approximation**
  only, or block it until a measurement/published reference is available for
  input impedance. Keep the dense-wire radial screen as the current model and
  keep its warning.
- Full terrain (DL8) remains blocked until a validated terrain model or a second
  engine is selected.
