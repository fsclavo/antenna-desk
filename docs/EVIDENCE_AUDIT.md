# Evidence audit

**Date:** 2026-11-04
**Scope:** catalog templates classified as experimental in
`src/antennadesk/domain/design/evidence.py`.

This audit follows Phase 5 of [`PENDING_WORK_PLAN.md`](PENDING_WORK_PLAN.md).
It does not promote a template merely because its geometry looks reasonable.
Level B requires a published design rule or starting point with a traceable
source and a stated tolerance; level A requires a numerical comparison with an
independent source. A missing reference keeps the template at level C with a
visible limitation.

## Promoted in this pass

| Template | Previous | Current | Published reference | Tolerance |
|---|---|---|---|---|
| `delta_loop` | C | B | ON4UN, *Low-Band DXing*, Ch. 10: a resonant delta loop is approximately 1.05–1.06 λ | 1 % on resonant circumference |
| `vertical` | C | B | ARRL practical length rules: `234/f` for a quarter-wave vertical and `585/f` for a 5/8-wave vertical | 0.5 % on radiator length |
| `inverted_v` | C | B | ARRL, “Wire Antennas for the Beginner”: a 120° inverted-V total length is `465.6/f` feet | 1 % on total length at 120° |

The corresponding tests are:

- `tests/unit/domain/design/test_formulas.py::test_delta_loop_circumference_matches_the_published_range`
- `tests/unit/domain/design/test_estimators.py::test_estimator_lengths_match_the_published_arrl_formulas`
- `tests/unit/domain/design/test_estimators.py::test_inverted_v_total_length_matches_the_published_120_degree_rule`

These promotions validate a **starting dimension**, not gain, feedpoint
impedance, or pattern accuracy. The limitations remain explicit in the evidence
registry.

## Remaining level C templates

| Template | Why it remains experimental | Possible next evidence |
|---|---|---|
| `loaded_vertical` | The loading coil is an ideal series model; coil Q and ground are not independently validated. | A published mobile-whip design with measured impedance and coil details. |
| `fan_dipole` | Mutual coupling and the V angle are installation-specific; the elements are not independent dipoles. | A published coupled-fan measurement, not a scalar angle correction. |
| `trap_dipole` | Traps are ideal parallel LC circuits; no independent impedance or resonance reference. | A published trap design with measured trap and antenna impedance. |
| `endfed` | The transformer is an ideal ratio and the counterpoise is simplified geometry. | A published end-fed half-wave measurement with transformer and counterpoise specified. |
| `sloper` | The slope and feed arrangement are installation-specific. | A documented reference installation with geometry and measured pattern. |
| `random_wire` | Performance depends on the tuner and the installation; the length is deliberately non-resonant. | No universal numeric reference; keep experimental. |
| `zepp` | The current preset omits the second matching conductor and the choke. | A refined model plus a published Zepp or end-fed Zepp measurement. |
| `j_pole` | Published construction data exist, but this simplified feed and stub model has no independent numeric check. | A reference design with measured feedpoint impedance at a specified frequency. |
| `slim_jim` | Folded construction and feed placement are not independently validated. | A published Slim Jim measurement with the fold spacing and feed point. |
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
- **B, published/heuristic:** 8 templates.
- **C, experimental:** 12 templates, all with a documented limitation.

The machine-readable registry and the generated table in
[`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) remain the source of truth.
