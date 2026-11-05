# Evidence audit

**Date:** 2026-11-05
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
| `inverted_v` | C | B | ARRL, “Wire Antennas for the Beginner”: a 120° inverted-V total length is `465.6/f` feet | 1 % on total length at 120° |
| `j_pole` | C | B | M0UKD, “Slim Jim and J Pole calculator”: 0.75 λ overall, with a 0.5 λ radiator and a 0.25 λ stub; ARRL QST, Feb 2003, conventional 2 m J-pole | 1 % on the half-wave and quarter-wave sections; 10 % on the overall height against the ARRL 2 m construction |
| `slim_jim` | C | B | F. Judd, G2BCX, “Slim Jim - 2 metre aerial”, *Practical Wireless*, 1978: about 60 in overall at 145 MHz; M0UKD calculator section fractions | 1 % on the sections; 5 % on the overall length at 2 m |
| `endfed` | C | B | ARRL End-Fed Half-Wave Antenna Kit: 66 ft on 40 m, 33 ft on 20 m, 16 ft on 10 m, 49:1 transformer, about 2500 Ω; PA9X: counterpoise 0.05 λ of the longest wavelength | 5 % on the half-wave wire length; 0.05 λ counterpoise; 49:1 ratio |

The corresponding tests are:

- `tests/unit/domain/design/test_formulas.py::test_delta_loop_circumference_matches_the_published_range`
- `tests/unit/domain/design/test_estimators.py::test_estimator_lengths_match_the_published_arrl_formulas`
- `tests/unit/domain/design/test_estimators.py::test_inverted_v_total_length_matches_the_published_120_degree_rule`
- `tests/unit/domain/design/test_estimators.py::test_j_pole_matches_the_published_three_quarter_wave_rule`
- `tests/unit/domain/design/test_estimators.py::test_j_pole_overall_height_matches_the_arrl_two_metre_construction`
- `tests/unit/domain/design/test_estimators.py::test_slim_jim_matches_the_published_two_metre_length`
- `tests/unit/domain/design/test_estimators.py::test_endfed_length_matches_the_arrl_efhw_kit`

The first three rows were added on 2026-11-04; the J Pole, Slim Jim, and
end-fed rows were added on 2026-11-05. These promotions validate a **starting
dimension**, not gain, feedpoint impedance, or pattern accuracy. The
limitations remain explicit in the evidence registry.

## Remaining level C templates

| Template | Why it remains experimental | Possible next evidence |
|---|---|---|
| `loaded_vertical` | The loading coil is an ideal series model; coil Q and ground are not independently validated. | A published mobile-whip design with measured impedance and coil details. |
| `fan_dipole` | Mutual coupling and the V angle are installation-specific; the elements are not independent dipoles. | A published coupled-fan measurement, not a scalar angle correction. |
| `trap_dipole` | Traps are ideal parallel LC circuits; no independent impedance or resonance reference. | A published trap design with measured trap and antenna impedance. |
| `sloper` | The slope and feed arrangement are installation-specific. | A documented reference installation with geometry and measured pattern. |
| `random_wire` | Performance depends on the tuner and the installation; the length is deliberately non-resonant. | No universal numeric reference; keep experimental. |
| `zepp` | The current preset omits the second matching conductor and the choke. | A refined model plus a published Zepp or end-fed Zepp measurement. |
| `ringo` | The simplified radiator and matching ring are an application preset, not a published commercial model. | Manufacturer data or an independent measurement. |
| `doublet` | Feed-line length, impedance, and tuner settings dominate the result. | A documented doublet installation with feed-line and tuner details. |
| `custom` | User-defined geometry has no fixed reference. | Imports and diagnostics only; no accuracy claim. |

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
- **B, published/heuristic:** 11 templates.
- **C, experimental:** 9 templates, all with a documented limitation.

The machine-readable registry and the generated table in
[`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) remain the source of truth.
