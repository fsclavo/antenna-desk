# Experimental validation protocol

**Status:** protocol defined; no measurement recorded yet
**Date:** 2026-11-04
**Scope:** level 3 validation for one reference antenna, following
`VALIDATION_PLAN.md`.

This document defines how to compare a real antenna with a simulation. It is
not a substitute for the software tests (level 1) or the numerical references
(level 2). One measurement validates one installation, not the whole model.

## 1. Why one reference case

Level 2 already checks the solver against published values and physical
invariants. Level 3 answers a different question: does the canonical model,
with the real ground, height, feed line, and construction tolerances, predict
what the antenna actually does?

A single well-documented case is enough to expose a systematic error. A set of
casual measurements is not: without an uncertainty budget, a 2 dB difference
cannot be attributed to the model, the range, or the antenna.

## 2. Reference antenna

Use a half-wave dipole:

- design frequency 14.1 MHz, total length near `0.475 λ` (about 10.1 m);
- thin copper wire, 1–2 mm, with the same radius recorded in the project;
- center feed with a 1:1 current balun or a common-mode choke;
- horizontal, broadside to the range, at a measured height above ground;
- both legs straight and in the same horizontal plane.

The simulated counterpart uses the measured height, wire radius, balun
treatment (ideal or absent), and the ground model described in section 4. The
simulation and the measurement must describe the same antenna, not an idealized
one.

A second case, a vertical with four radials, is optional and only after the
dipole case is closed.

## 3. Equipment

Minimum viable set:

- vector network analyzer, 1–30 MHz, with a calibration kit (SOLT or ECal);
- short, low-loss coax between the VNA and the antenna, with the loss measured
  or taken from the datasheet;
- adapters and a torque wrench for the connectors;
- clamp-on ferrites at both cable ends;
- a calibrated reference antenna for the gain comparison (a second dipole with
  a known gain, or a commercial reference with its calibration certificate);
- a signal source and a receiver or spectrum analyzer for the gain and pattern
  runs, unless the VNA supports a remote source;
- a non-conductive mast, a measuring tape, a compass, and a level;
- a turntable or rotator for pattern cuts, or a fixed source and a rotator on
  the antenna under test.

The reference antenna's gain uncertainty and the VNA specifications are inputs
to the budget. Without them, the result is a comparison, not a validation.

## 4. Site and installation record

Record, before the first measurement:

- date, time, operator, and location (coordinates or a description);
- ground type and estimated conductivity/permittivity, or the model used in the
  simulation and why;
- antenna height above ground, measured at the feed and at both ends;
- orientation (azimuth), polarization, and distance to the nearest conductor,
  building, fence, tree, or vehicle;
- balun/choke type, feed-line type and length, and connector types;
- weather: temperature, humidity, wind, and precipitation;
- VNA model, serial number, calibration date, IF bandwidth, and number of
  points;
- reference antenna model, serial number, calibration date, and gain with its
  uncertainty.

Store this in the measurement's `notes`, `calibration`, `reference_plane`, and
`feed_line` fields until the schema is extended (section 8).

## 5. Impedance and SWR

1. Calibrate the VNA at the antenna reference plane, after the feed line, with
   the same adapters used for the measurement. Verify the calibration with a
   known load and a short.
2. Measure `S11` from 13.9 to 14.3 MHz with at least 401 points and a narrow IF
   bandwidth. Record the raw Touchstone file.
3. Convert to impedance at the reference plane and find the series resonance
   (minimum `|S11|`).
4. Repeat the sweep three times, reconnecting the cable each time, to estimate
   connector repeatability.
5. Compare resistance, reactance, and SWR at the measured resonance with the
   simulation at the same frequency. Do not compare at different frequencies.

## 6. Gain

Use the gain comparison method:

1. Place the reference antenna at the same height, orientation, and
   polarization as the antenna under test.
2. Measure the received power with the reference and with the antenna under
   test at the same source power and distance.
3. Correct both readings for feed-line loss and mismatch at the receiver.
4. `G_aut = G_ref + P_aut - P_ref` in dB.
5. Repeat with the antennas interchanged if the range allows it, to expose a
   range asymmetry.

The three-antenna method is an alternative when no calibrated reference is
available. It needs three antennas and more measurement time, and it still
requires a range evaluation.

## 7. Pattern

1. Measure azimuth cuts at the design frequency in 5° steps, with the antenna
   under test rotating and the source fixed.
2. Measure elevation cuts at the same frequency, or at least the take-off angle
   and the first null.
3. Normalize each cut to its maximum and compare with the simulated cut at the
   same plane.
4. Record the range background with the antenna removed or terminated, to
   estimate multipath and ambient noise.

## 8. Uncertainty budget

Follow JCGM 100:2008 (GUM) and the uncertainty guidance in IEEE Std 149-2021.
The values below are **planning estimates** to size the budget before measuring;
replace each one with the instrument datasheet, the calibration certificate, or
the range evaluation.

| Source | Type | Planning estimate (k=1) | How to obtain it |
|---|---|---:|---|
| VNA magnitude/phase accuracy | B | 0.05 dB / 0.5° | Datasheet at the measurement frequency |
| Calibration kit | B | 0.02 dB / 0.2° | Kit certificate |
| Connector repeatability | A | 0.05 dB / 0.5° | Three reconnects |
| Feed-line loss | B | 0.1 dB | Measured or datasheet |
| Reference antenna gain | B | 0.3 dB | Calibration certificate |
| Mismatch (source and receiver) | B | 0.2 dB | Measured `S11` and `S22` |
| Range multipath / reflections | B | 0.5 dB | Background run and range evaluation |
| Height and positioning | B | 0.2 dB | Tape and level, repeated |
| Polarization alignment | B | 0.3 dB | Rotate for maximum, record the peak |
| Receiver linearity | B | 0.1 dB | Attenuator step test |
| Environmental drift | A | 0.2 dB | Repeat the reference at the end |

Combine in quadrature (`u_c = sqrt(sum(u_i^2))`) and report the expanded
uncertainty with `k = 2` (about 95 %). For impedance, propagate the `S11`
uncertainty to `R` and `X` analytically or with a Monte Carlo run of the
conversion.

Do not reuse these numbers as results. They are a template, not evidence.

## 9. Acceptance

The simulation is consistent with the measurement when the difference lies
inside the combined expanded uncertainty (`k = 2`). Report:

- measured and simulated `R`, `X`, SWR, resonance frequency, gain, and pattern
  cut;
- the difference and the combined uncertainty for each;
- the raw Touchstone and pattern files;
- the installation record and the uncertainty budget.

If the difference is outside the band, investigate in this order: reference
plane and cable loss, balun/common-mode current, ground and height, nearby
objects, then the model. A model change requires a new numerical reference or a
documented physical reason, not a tolerance widened to fit one measurement.

## 10. Data model

The current `Measurement` record stores the name, source, calibration text,
reference plane, feed line, notes, reference impedance, and the frequency/
impedance points. That is enough for the impedance comparison.

The following fields are proposed for a future schema version, once a real
measurement exists:

- instrument model, serial, and calibration date;
- reference antenna model, serial, gain, and gain uncertainty;
- cable loss and connector type;
- measurement height, distance, and polarization;
- expanded uncertainty for `R`, `X`, SWR, gain, and pattern, with coverage
  factor and confidence level;
- a link to the raw Touchstone and pattern files.

Until then, record the budget in `notes` and keep the raw files with the
project.

## 11. Current limitation

There is no VNA and no suitable site available at the moment. This protocol
defines the procedure, the metadata, and the uncertainty budget so the
measurement can be executed without redesigning it later. Level 3 remains
open until one case is recorded and compared.

## References

- IEEE Std 149-2021, *IEEE Recommended Practice for Antenna Measurements*.
- JCGM 100:2008, *Evaluation of measurement data — Guide to the expression of
  uncertainty in measurement* (GUM).
- ARRL Antenna Book, 24th edition, for practical dipole construction and
  feed-line guidance.
