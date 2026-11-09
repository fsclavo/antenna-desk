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
| `biquad` | C | B | Martybugs, “Biquad Antenna Construction” (after Trevor Marshall), 2.44 GHz: quarter-wave sides (about 31 mm), 15 mm reflector spacing, and a 123 mm square solid reflector; measured 11–12 dBi | 2 % on loop side; 10 % on reflector spacing |
| `beverage` | C | B | W. Silver, N0AX, and F. Donovan, W3LPL, “The Beverage Antenna, 100 Years Later”, *QST*, November 2021, pp. 55–57: one-wavelength starting length, 500 Ω termination, 6–10 ft typical height | 1 % on the one-wavelength starting length; 500 Ω nominal termination |

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
- `tests/unit/domain/test_biquad.py::test_biquad_starting_side_is_a_quarter_wave_and_spacing_is_half_the_side`
- `tests/unit/domain/test_beverage.py::test_beverage_starting_length_is_one_wavelength`

The first three rows were added on 2026-11-04; the J Pole, Slim Jim, end-fed,
trap-dipole, sloper, doublet, and Zepp rows were added on 2026-11-05. The loaded
vertical row was added on 2026-11-06 for the published mobile-whip example
preset. The biquad and Beverage rows were added on 2026-11-08 for starting
dimensions only. These promotions validate a **starting dimension**, not gain,
feedpoint impedance, or pattern accuracy. The limitations remain explicit in
the evidence registry.

## Remaining level C templates

| Template | Why it remains experimental | Possible next evidence |
|---|---|---|
| `magnetic_loop` | Small-loop geometry with an ideal series tuning capacitor and optional ESR; the coupling loop and detailed capacitor loss are not modeled. | A published magnetic-loop design with dimensions, capacitor ESR, measured impedance, and efficiency. |
| `inverted_l` | Bent end-fed geometry; no independent numeric reference for this configuration. | A published inverted-L design with dimensions and measured impedance. |
| `fan_dipole` | Mutual coupling and the V angle are installation-specific; the elements are not independent dipoles. | A published coupled-fan measurement, not a scalar angle correction. |
| `random_wire` | Performance depends on the tuner and the installation; the length is deliberately non-resonant. | No universal numeric reference; keep experimental. |
| `ringo` | The simplified radiator and matching ring are an application preset, not a published commercial model. | Manufacturer data or an independent measurement. |
| `custom` | User-defined geometry has no fixed reference. | Imports and diagnostics only; no accuracy claim. |
| `double_biquad` | The published double biquad is a side-by-side pair on a solid reflector; the template is a four-loop vertical stack with a wire reflector, so the topology and feed impedance differ. | A published side-by-side double-biquad measurement that matches the current vertical-stack topology, or a topology change with its own reference. |
| `loaded_dipole` | The published 3.91 MHz BVARC example gives dimensions and EZNEC feed resistance, but the source does not state its ground model and the template's generic defaults use a different coil position. | A measured loaded/linked dipole with coil Q, ground, and feedpoint impedance for the template's geometry. |
| `phased_vertical` | The ideal linear phase and amplitude progression, combining network, per-element matching, and radial screen efficiency are not independently validated; impedance and SWR refer only to the primary feed. | A published phased-array design or measurement with element spacing, phase, amplitude, feed network, and measured pattern or impedance. |
| `quad_beam` | Quarter-wave loop sides and fifth-wave spacing are starting heuristics; boom, spreaders, mast, feed line, and matching network are not modeled, and gain and front-to-back ratio are not independently validated. | A published quad-beam design or measurement with loop dimensions, spacing, feed, and measured gain, front-to-back ratio, or impedance. |
| `discone` | The cone and disc are radial wire approximations, not solid surfaces; the coax, mast, and feed transition are not modeled, and impedance, bandwidth, and pattern are not independently validated. | A published discone design or measurement with cone/disc dimensions, feed transition, and measured impedance or pattern. |
| `trap_yagi` | The traps are ideal parallel LC loads with no core or dielectric loss; boom mounting, trap hardware, feed line, and matching network are not modeled, and gain and impedance are not independently validated. | A published trapped-Yagi design or measurement with trap values, dimensions, boom mounting, and measured impedance or gain on both bands. |

### Inverted-L evidence review (2026-11-08, B1)

No source was found that matches the current template closely enough to promote
it. The template is a straight vertical section plus a horizontal top, fed at
the base, with no radial screen.

Sources considered:

- Cebik/W4RNL, “Modeling 160-Meter Vertical Arrays, Part 4”: the 40 m inverted-L
  cases use 32-radial ground systems, and the no-radial comparison is a MININEC
  perfect-ground result that the article itself calls unrealistic. The current
  template cannot represent those radials.
- K9LA, “Another Simple 160-Meter Antenna”: 60 ft vertical with a slanted top
  down to 15 ft plus a single 129 ft radial; the template has a horizontal top
  and no radial.
- K2AV “Design Inverted L”: uses a folded counterpoise and a specific matching
  system; neither is represented by the template.
- Construction articles with measured SWR: dimensions vary by installation and
  do not provide an exact geometry plus a numeric impedance/gain result for the
  template.

The template therefore remains **level C**. Promotion would require either a
measured, no-radial simple inverted-L with exact dimensions and a numeric
metric, or extending the template to model a documented radial screen. That
extension is a separate feature, not an evidence promotion.

### Ringo evidence review (2026-11-08, B2)

The Cushcraft AR-6 manual (7/93) was reviewed. It confirms the 50–54 MHz
coverage, 3.1 m height, 33 cm ring diameter, 3.75 dB gain, and 16° radiation
angle. It also gives a tuning chart for the radiator length and tuning-rod
position, and specifies a 75 Ω coaxial tuning stub.

The current Ringo template still models a simplified closed ring connected to
the radiator base. It does not model the split tuning ring, the adjustable
tuning rod, or the 75 Ω coaxial stub, and the manual does not publish a
feedpoint resistance/reactance table that could be compared directly. The
manufacturer data therefore improves the documented starting geometry but does
not validate the electrical model. The template remains **level C** until the
matching hardware is modeled or a measured impedance is available.

### B3 evidence review: biquad, double biquad, Beverage, loaded dipole (2026-11-08)

Four level C templates were reviewed. Two starting-dimension promotions and two
keeps:

- **biquad → B (starting dimensions only).** The Martybugs construction article
  gives quarter-wave sides (about 31 mm at 2.44 GHz), 15 mm reflector spacing,
  and a measured 11–12 dBi with a 123 mm solid reflector. The template's
  quarter-wave side and half-side spacing match the published starting
  dimensions within the stated tolerance. The template's wire-rectangle
  reflector and shared rails do not reproduce the measured gain or feed
  impedance; those remain experimental.
- **Beverage → B (starting dimensions only).** The QST article gives a 1 λ
  starting length, 500 Ω termination, and 6–10 ft typical height; the template
  defaults to exactly 1 λ and 500 Ω. Gain and pattern are not promoted because
  the termination is a wire stub and the article's gain figure depends on a
  ground model the template does not reproduce.
- **double_biquad remains C.** The published double biquad is a side-by-side
  pair on a 110 × 220 mm solid reflector; the template is a four-loop vertical
  stack on a wire reflector. The topology, current distribution, and feed
  impedance differ, so the published dimensions and gain are not a direct
  reference.
- **loaded_dipole remains C.** The BVARC/W5RH 3.91 MHz design gives 62 ft total,
  coils about 50% out each side, and 38.6 µH each. The article's EZNEC feed
  resistance is 8/21/25 Ω at 25/35/50 ft, but it does not state the EZNEC
  ground model. A NEC2 comparison over free, perfect, and average finite ground
  did not match all three values unambiguously (perfect ground gave about
  7.7/13.2/22.0 Ω and average ground about 14.6/18.4/24.5 Ω), so no numeric
  tolerance was claimed. The template's generic defaults also use a different
  coil position.

The biquad and Beverage entries validate only the published starting
dimensions. Their gain, feedpoint impedance, pattern, ground, and construction
details remain explicit limitations.

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
- **B, published/heuristic:** 21 templates.
- **C, experimental:** 12 templates, all with a documented limitation.

The `half_square` and `bobtail_curtain` templates entered the catalog at level B
on 2026-11-07 from Cebik's published 7.15 MHz dimensions. They are new
templates, not promotions from level C; the free-space starting geometry is
published, while pattern, ground, and matching remain unvalidated.

The machine-readable registry and the generated table in
[`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) remain the source of truth.
