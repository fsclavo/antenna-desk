# C3 log-periodic spike — Cebik 10 m reference

**Date:** 2026-11-16
**Engine:** nec2c 1.3.3
**Status:** passed for the straight-element family; the 7 MHz wire design is a
separate swept-element variant.

## Question

Can the existing `AntennaModel` + `Wire` + `FeedPoint` + `TransmissionLine`
architecture model an LPDA with a transposed phase line, without a separate
model or solver, and reproduce a published reference?

A first attempt with independent ideal voltage sources of alternating polarity
had produced a negative primary-feed resistance. The spike had to replace that
approximation with a real transmission-line two-port.

## Reference

L. B. Cebik, W4RNL, "A 10-Meter LPDA", Phase 3:

- LPCAD 28-30 MHz geometry;
- four elements: 215.074, 192.584, 172.445, 154.412 in;
- cumulative positions: 0, 35.592, 67.462, 96.000 in;
- 1.0 in diameter, 75 Ω phase line, VF = 1.0;
- source at the shortest (front) element;
- three transmission-line sections with reversed polarity;
- published NEC-4 values at 29 MHz: **7.36 dBi**, **22.01 dB** front-to-back;
- published element-center currents: 0.53/10.6°, 0.89/−79.1°, 0.94/−168.1°,
  0.55/109.6°.

The 200 Ω variant publishes **7.04 dBi** and **24.56 dB** at the same
frequency. The 0.5 in and #12 rows in the same table use different optimization
geometry (27.5-29.5 and 27-29 MHz), so they are not the exact 28-30 MHz LPCAD
case.

## Method

1. Build the geometry with `LogPeriodicParameters.to_antenna()`; each element is
   a straight wire and each adjacent pair is a `TransmissionLine` with
   `phase_reversal=True`.
2. Emit the normal NEC deck. The adapter writes the reversed lines as negative
   characteristic impedance (`TL ... -75.0 ...`).
3. Run nec2c at 29 MHz with 43/41/39/37 segments, then with 21/21/21/21,
   31/29/27/25, and 51/49/47/45 segments.
4. Compute the forward gain at φ = 0°, the rear gain at φ = 180°, and the
   element-center current phases.
5. Repeat with `phase_reversal=False` as a negative control.
6. Repeat the 200 Ω line.

## Results

| Case | 75 Ω published | nec2c | 200 Ω published | nec2c |
|---|---:|---:|---:|---:|
| Gain at 29 MHz | 7.36 dBi | **7.37 dBi** | 7.04 dBi | **7.05 dBi** |
| Front-to-back | 22.01 dB | **22.01 dB** | 24.56 dB | **24.56 dB** |
| Input impedance | — | **52.38 − j1.39 Ω** | — | **112.92 − j46.73 Ω** |

Element-center current phases for the 75 Ω line:

| Element | Published | nec2c |
|---|---:|---:|
| 1 (rear) | 10.6° | 12.1° |
| 2 | −79.1° | −77.6° |
| 3 | −168.1° | −166.5° |
| 4 (front) | 109.6° | 111.2° |

All phases are within 1.6°. The relative magnitudes normalized to the strongest
element are 0.56/0.94/1.00/0.58 against the published 0.56/0.95/1.00/0.59.

Segmentation stability:

| Segments | R (Ω) | X (Ω) | Gain (dBi) | F/B (dB) |
|---|---:|---:|---:|---:|
| 43/41/39/37 | 52.38 | −1.39 | 7.37 | 22.01 |
| 21/21/21/21 | 52.45 | −1.63 | 7.36 | 22.10 |
| 31/29/27/25 | 52.40 | −1.49 | 7.36 | 22.08 |
| 51/49/47/45 | 52.37 | −1.35 | 7.37 | 21.98 |

The resistance varies by less than 0.15%, the reactance by 0.28 Ω, the gain by
0.01 dB, and the front-to-back ratio by 0.12 dB.

Negative control without phase reversal: 4.97 dBi gain and 2.78 dB
front-to-back. The reversal is not cosmetic.

## ARRL/Cebik 7 MHz wire design

The ARRL Antenna Book 7 MHz wire LPDA (Table 2) publishes τ = 0.845,
σ = 0.06, lengths 71.304/60.252/50.913/43.022 ft, spacings
8.557/7.230/6.110 ft, a 334.2 Ω phase line, a 6-inch rear jumper, a 4:1 balun,
and 5.9 dBi/208 Ω. Its construction section sweeps the wire elements forward
60° to the feed line, forming a V-shaped array. A straight-element NEC model
gives 3.56 dBi, 160.5 Ω, and 3.3 dB front-to-back, so the table is not a
straight-element performance reference.

The table still supplies a published τ/σ geometry check: the generated lengths
and spacings can be compared with the published dimensions independently of the
V construction. The V variant needs an explicit sweep-angle parameter and its
own evidence before it can claim the published performance.

## Conclusion

The spike passes. The existing architecture models the transposed feed with one
generic `TransmissionLine.phase_reversal` flag, and the 1.0 in/75 Ω Cebik
reference matches the published NEC-4 gain, front-to-back ratio, current phases,
and segmentation behavior. The family is validated at evidence level **B**, not
A, because the reference is a published model rather than a measurement.
