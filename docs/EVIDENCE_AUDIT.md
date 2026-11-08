# Evidence audit

**Date:** 2026-11-05; updated 2026-11-08
**Scope:** catalog templates classified as experimental in
`src/antennadesk/domain/design/evidence.py`.

This audit follows Phase 5 of [`PENDING_WORK_PLAN.md`](PENDING_WORK_PLAN.md).
It does not promote a template merely because its geometry looks reasonable.
Level B requires a published design rule or starting point with a traceable
source and a stated tolerance; level A requires a numerical comparison with an
independent source. A missing reference keeps the template at level C with a
visible limitation.

## Promoted so far

| Template | Previous | Current | Published reference | Tolerance |
|---|---|---|---|---|
| `delta_loop` | C | B | ON4UN, *Low-Band DXing*, Ch. 10: a resonant delta loop is approximately 1.05–1.06 λ | 1 % on resonant circumference |
| `vertical` | C | B | ARRL practical length rules: `234/f` for a quarter-wave vertical and `585/f` for a 5/8-wave vertical | 0.5 % on radiator length |
| `loaded_vertical` | C | B | K7MEM, “Short Loaded Vertical”, citing ARRL Antenna Book, 17th ed., pp. 16-5 to 16-11: a 102 in whip at 14.1 MHz needs a 4.511 µH base loading coil | 5 % on the 102 in whip length and 4.511 µH coil inductance; published example only |
| `inverted_v` | C | B | ARRL, “Wire Antennas for the Beginner”: a 120° inverted-V total length is `465.6/f` feet | 1 % on total length at 120° |
| `j_pole` | C | B | M0UKD, “Slim Jim and J Pole calculator”: 0.75 λ overall, with a 0.5 λ radiator and a 0.25 λ stub; ARRL QST, Feb 2003, conventional 2 m J-pole | 1 % on the half-wave and quarter-wave sections; 10 % on the overall height against the ARRL 2 m construction |
| `slim_jim` | C | B | F. Judd, G2BCX, “Slim Jim - 2 metre aerial”, *Practical Wireless*, 1978: about 60 in overall at 145 MHz; M0UKD calculator section fractions | 1 % on the sections; 5 % on the overall length at 2 m |
| `endfed` | C | B | ARRL End-Fed Half-Wave Antenna Kit: 66 ft on 40 m, 33 ft on 20 m, 16 ft on 10 m, 49:1 transformer, about 2500 Ω; PA9X: counterpoise 0.05 λ of the longest wavelength | 5 % on the half-wave wire length; 0.05 λ counterpoise; 49:1 ratio |
| `trap_dipole` | C | B | RSARS, “W3DZZ Multi-band Antenna 80-40-20-15-10m”: 33 ft inner and 22 ft outer sections, 7.1 MHz traps, 5.024 µH and 100 pF | 1 % on the 33/22 ft sections; 2 % on trap resonance |
| `sloper` | C | B | Chameleon Antenna CHA LEFS Feather manual: 66.5 ft EFHW radiator, 49:1 transformer, far end about 25 ft, feed transformer about 3 ft | 5 % on the radiator length and deployment heights |
| `doublet` | C | B | VU3DXR, “94-Foot Multi Band Doublet Antenna”: 94 ft total, 41 ft of 450 Ω ladder line, 1:1 current balun, tuner | 5 % on the radiator and feed-line lengths; 450 Ω line |
| `zepp` | C | B | ARRL Antenna Book, 24th ed., Ch. 20: a true Zepp is an end-fed half-wave radiator matched by a quarter-wave open-wire line; W8JI, “End-fed vertical J-pole and horizontal Zepp”: a 1/4 λ stub feeding a 1/2 λ element with a 1:1 current balun at the tuner | 5 % on the half-wave and quarter-wave starting lengths; spacing and radius set the stub impedance |

The corresponding tests are:

- `tests/unit/domain/design/test_formulas.py::test_delta_loop_circumference_matches_the_published_range`
- `tests/unit/domain/design/test_estimators.py::test_estimator_lengths_match_the_published_arrl_formulas`
- `tests/ui/test_vertical_dialog.py::test_loaded_vertical_dialog_loads_the_published_mobile_example`
- `tests/unit/domain/design/test_estimators.py::test_inverted_v_total_length_matches_the_published_120_degree_rule`
- `tests/unit/domain/design/test_estimators.py::test_j_pole_matches_the_published_three_quarter_wave_rule`
- `tests/unit/domain/design/test_estimators.py::test_j_pole_overall_height_matches_the_arrl_two_metre_construction`
- `tests/unit/domain/design/test_estimators.py::test_slim_jim_matches_the_published_two_metre_length`
- `tests/unit/domain/design/test_estimators.py::test_endfed_length_matches_the_arrl_efhw_kit`
- `tests/unit/domain/test_trap_dipole.py::test_w3dzz_parameters_match_the_published_sections`
- `tests/unit/domain/test_endfed.py::test_sloper_reference_matches_the_chameleon_lefs_geometry`
- `tests/unit/domain/test_doublet.py::test_doublet_reference_matches_the_published_94_foot_design`
- `tests/ui/test_doublet_dialog.py::test_doublet_dialog_accepts_the_published_94_foot_design`
- `tests/unit/domain/test_zepp.py::test_zepp_uses_a_half_wave_radiator_and_quarter_wave_stub`
- `tests/unit/domain/test_zepp.py::test_zepp_has_an_open_second_stub_conductor`

The first three rows were added on 2026-11-04; the J Pole, Slim Jim, end-fed,
trap-dipole, sloper, doublet, and Zepp rows were added on 2026-11-05. The loaded
vertical row was added on 2026-11-06 for the published mobile-whip example
preset. These promotions validate a **starting dimension**, not gain, feedpoint
impedance, or pattern accuracy. The limitations remain explicit in the evidence
registry.

## Remaining level C templates

| Template | Why it remains experimental | Possible next evidence |
|---|---|---|
| `magnetic_loop` | Small-loop geometry with an ideal series tuning capacitor and optional ESR; the coupling loop and detailed capacitor loss are not modeled. | A published magnetic-loop design with dimensions, capacitor ESR, measured impedance, and efficiency. |
| `inverted_l` | Bent end-fed geometry; no independent numeric reference for this configuration. | A published inverted-L design with dimensions and measured impedance. |
| `fan_dipole` | Mutual coupling and the V angle are installation-specific; the elements are not independent dipoles. | A published coupled-fan measurement, not a scalar angle correction. |
| `random_wire` | Performance depends on the tuner and the installation; the length is deliberately non-resonant. | No universal numeric reference; keep experimental. |
| `ringo` | The simplified radiator and matching ring are an application preset, not a published commercial model. | Manufacturer data or an independent measurement. |
| `custom` | User-defined geometry has no fixed reference. | Imports and diagnostics only; no accuracy claim. |
| `biquad` | Quarter-wave loop side and eighth-wave reflector spacing are starting heuristics; the wire reflector and shared-rail current distribution are not independently validated. | A published biquad design with dimensions, feedpoint impedance, gain, and reflector construction. |
| `double_biquad` | Four-loop extension of the same heuristic; the extra loop pair changes the current distribution and feed impedance. | A published double-biquad design or measurement with dimensions and feedpoint impedance. |
| `beverage` | One-wavelength length and 500 Ω termination are heuristics; the termination is a wire stub with a series resistor, not a complete ground system, and receiving gain is not independently validated. | A published Beverage design or measurement with length, height, termination, ground, and received-signal data. |
| `loaded_dipole` | The coil is an ideal series R-L load; core loss, self-capacitance, link contact resistance, and the portable installation are not modeled. | A published loaded/linked dipole design with coil Q, dimensions, and measured impedance. |
| `phased_vertical` | The ideal linear phase and amplitude progression, combining network, per-element matching, and radial screen efficiency are not independently validated; impedance and SWR refer only to the primary feed. | A published phased-array design or measurement with element spacing, phase, amplitude, feed network, and measured pattern or impedance. |

## Follow-up review of the remaining level C templates (2026-11-06)

The remaining level C templates were reviewed for a possible promotion.
`loaded_vertical` was promoted through the published 102 in mobile example.
The other four keep their level because the available sources either describe a
different geometry or depend on installation details that the current model
cannot represent. This is a deliberate decision, not a missing citation.

| Template | Sources considered | Why it remains C |
|---|---|---|
| `ringo` | Cushcraft AR-2 Ringo: 1.2 m height and 12.7 cm ring diameter, 135–160 MHz. Cushcraft AR-6 Ringo: 3.1 m height and 33 cm ring diameter, 50–54 MHz. | A preset with the AR-6 starting dimensions is available (52 MHz, 3.05 m radiator, 0.33 m ring, 0.05 m ring height assumption). It remains C because the simplified matching ring and the 0.725λ estimator are not the commercial antenna's electrical model. |
| `fan_dipole` | No source found that provides a universal coupled-fan correction. Mutual coupling depends on element spacing, angle, height, and ground. | A scalar length or angle correction would hide the interaction and would not be a traceable reference for the generated geometry. |
| `random_wire` | No universal reference; performance depends on the tuner, counterpoise, and installation. | The template is intentionally non-resonant and tuner-assisted. No general numeric claim is possible. |
| `custom` | User-defined geometry has no fixed reference. | Imports and diagnostics are structural; any accuracy claim would depend on the imported model. |

The detailed sources are:

- K7MEM, “Short Loaded Vertical”, <https://k7mem.com/Ant_Loaded_Vertical.html>
- W8JI, “Mobile and loaded antenna”,
  <https://www.w8ji.com/mobile_and_loaded_antenna.htm>
- Universal Radio, Cushcraft AR2 Ringo specifications,
  <https://www.universal-radio.com/catalog/hamants/0633.html>
- Universal Radio, Cushcraft AR6 Ringo specifications,
  <https://www.universal-radio.com/catalog/hamants/0634.html> (10.1 ft height,
  13 in ring diameter, 50–54 MHz).

The next evidence step for `ringo` would require a model that reproduces the
commercial matching ring; the AR-6 preset is a geometry starting point only.
The loaded-vertical example now covers only the published 102 in whip. A
capacitive top hat is modeled as horizontal wires, and coil Q is exposed as an
editor convenience, but vehicle ground and mast effects remain outside the
model. The four previously reviewed C templates keep their visible experimental
warning. The inverted-L and magnetic-loop families also start at C until a
published reference supplies a traceable numeric metric or measured impedance.

## Rules for the next audit

1. Prefer a named source that specifies the geometry and the measured metric.
2. Record the metric, value, and tolerance; do not apply a universal tolerance.
3. A length rule promotes a starting dimension only. Do not claim gain or
   impedance accuracy from it.
4. If a source only describes construction, keep the template at C or B with a
   clearly limited claim.
5. Never generate a reference value with the engine under test.

## Current summary

- **A, reference-backed:** 5 templates.
- **B, published/heuristic:** 18 templates.
- **C, experimental:** 11 templates, all with a documented limitation.

The `half_square` and `bobtail_curtain` templates entered the catalog at level B
on 2026-11-07 from Cebik's published 7.15 MHz dimensions. They are new
templates, not promotions from level C; the free-space starting geometry is
published, while pattern, ground, and matching remain unvalidated.

The machine-readable registry and the generated table in
[`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) remain the source of truth.
