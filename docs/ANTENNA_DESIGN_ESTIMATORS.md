# Antenna dimension estimators

This document defines the frequency-first dimension estimators. They produce
**starting dimensions**, not verified construction values. Final dimensions
depend on height, ground, conductor diameter, insulation, nearby objects, and
the matching network.

## Workflow

```text
DesignIntent
  frequency, family, subtype, orientation/polarization, environment, constraints
        ↓
DimensionEstimate
  parameters, method, confidence, assumptions, warnings, tolerance, sources
        ↓
Apply to a design
        ↓
Optional refinement with the existing optimizer or synthesis
```

The estimator layer is pure domain code. The UI calls it through
`EstimateAntennaDimensions`; no estimator imports Qt, the solver, or the project
repository.

## Confidence levels

- **physical**: directly derived from a wavelength fraction.
- **empirical**: a documented practical factor is applied.
- **reference_scaled**: a published design is scaled by frequency.
- **heuristic**: an application starting point with no universal formula.

Every estimate carries its confidence, source identifiers, assumptions,
warnings, and a dimension tolerance.

## Formulas and sources

### Common factors

- Wavelength: `λ = c / f`.
- Half-wave practical factor: `0.5λ × 0.95`. The 0.95 end-effect factor is
  documented in the ARRL Antenna Book discussion used by this project.
- Quarter-wave practical factor: `0.25λ × 0.95`.
- Half-wave vertical: `0.5λ × 0.95`, using the same end-effect factor as a
  dipole. The feed impedance is high, so matching is required.
- Five-eighth-wave vertical: `0.625λ × 0.95`, matching the ARRL 585/f
  practical formula.
- Resonant full-wave loop: circumference `1.0λ` for an ideal thin circular
  loop, with the polygon correction described below.
- Folded-dipole starting spacing: `0.02λ`.
- Radial starting length: `0.25λ`.

### Families

| Family | Starting estimate | Confidence | Notes |
|---|---|---|---|
| Wire dipole | `0.5λ × 0.95` total length | empirical | Height and ground affect resonance |
| Folded dipole | same element length; `0.02λ` spacing; 4:1 ideal feed transformer | empirical | Spacing controls step-up impedance; the 4:1 default is editable to 6:1 or 1:1 |
| Loop / quad / delta | circumference `λ × (1.02895 + 0.05028/N + 0.09665/N²)` | empirical | `N` sides; quad=4, delta=3; calibrated polygon preset; the delta case falls in ON4UN's published 1.05–1.06λ range; vertical and horizontal loops share the same circumference rule |
| Vertical 1/4 | `0.25λ × 0.95`; radial `0.25λ` | empirical | ARRL 234/f length rule; radial count/length are starting values |
| Vertical 1/2 | `0.5λ × 0.95`; radial `0.25λ` | empirical | High feed impedance; matching required |
| Vertical 5/8 | `0.625λ × 0.95`; radial `0.25λ` | empirical | ARRL 585/f length rule; high feed impedance; matching required |
| Inverted-V | half-wave dipole total, split in two legs | empirical | Included angle affects feed impedance; the 120° case matches the ARRL 465.6/f rule within 1% |
| Fan dipole | one half-wave element per band | empirical | Elements interact; the V angle shifts resonance, especially on the highest band |
| End-fed / EFHW | published EFHW wire: 66 ft on 40 m, 33 ft on 20 m, 16 ft on 10 m; `0.05λ` counterpoise; 49:1 transformer | heuristic | ARRL kit and PA9X rule; the editor exposes explicit 40/20/10 m preset buttons; transformer and counterpoise remain starting points |
| OCFD | half-wave total, feed at 1/3, 4:1 ideal transformer | heuristic | Existing synthesis can refine length/feed; actual balun ratio depends on height and feed offset |
| J Pole / Slim Jim | J Pole: 0.75λ overall, 0.5λ radiator, 0.25λ stub; Slim Jim: 0.5λ radiator above a 0.25λ folded stub and gap | empirical | M0UKD published rule and G2BCX 2 m length; feed offset and stub still need tuning |
| Zepp | 0.5λ radiator above a 0.25λ two-wire stub; spacing and radius set the stub impedance | empirical | Published 3/4-wave topology; the real second conductor is modeled, but the 1:1 choke and common-mode current are not |
| Ringo | 0.725-wave vertical with a small horizontal matching ring, calibrated for the simplified AntennaDesk geometry | heuristic | Not a universal commercial Ringo formula |
| Yagi | DL6WU 2–32 element trimming reference scaled by frequency | reference scaled | No unique Yagi design; optimize for the target; horizontal or vertical polarization |
| Moxon | Cebik 20 m wire reference scaled by frequency | reference scaled | Gap and tips are sensitive; horizontal or vertical polarization |
| Biquad / double biquad | loop side `0.25λ × 0.95`; reflector `0.5 × side` | heuristic | No independent numerical reference; the wire reflector and shared-rail current distribution are experimental |
| Beverage | length `1.0λ`; height and termination from the editor | heuristic | Receiving antenna; the termination and low gain are not independently validated |
| T2FD | span `300/F(MHz)` ft, spacing `10/F(MHz)` ft | heuristic | Broadband starting geometry; highest design frequency is required; not a resonance calculation |

Ground-mounted radials are placed 1 cm above the ground plane in the NEC deck.
The estimator and project keep the requested base height; the clearance is a
solver constraint, not a design dimension. NEC-2 rejects horizontal radials
lying exactly on a ground plane.

### Folded dipole feed transformer

An equal-conductor folded dipole is an approximately 4:1 impedance
transformation. New designs start with an ideal 4:1 feed transformer, stored in
`FoldedDipoleParameters.transformer_ratio` and applied by
`SimulationSpec.feed_transformer_ratio`. The ratio does not change the NEC
geometry. It is editable because 6:1 is a common alternative for a 300 Ω feed,
and 1:1 shows the raw antenna impedance.

A 4:1 transformer on a ~267 Ω resonant folded dipole leaves about 67 Ω, so the
displayed SWR is about 1.3, not 1.0. Use the project matching network for an
exact 50 Ω match. The transformer is ideal: balun loss, common-mode current, and
balance are not modeled. The estimator warning and the construction sheet state
the modeled ratio.

### J Pole and Slim Jim starting point

M0UKD's published calculator defines the J pole as 0.75 λ overall, split into a
0.5 λ radiator and a 0.25 λ matching stub. The Slim Jim keeps the same
quarter-wave stub, adds a small gap, and folds the half-wave radiator alongside
it. The estimator applies the project's 0.95 end-effect factor to both
sections. F. Judd, G2BCX, “Slim Jim - 2 metre aerial”, *Practical Wireless*,
1978, gives about 60 in overall for 2 m.

The 50 Ω feed position is a tuning starting point, not a validated impedance.
Ground, mast, and feed-line coupling are not modeled.


## Ground and fan constraints

The vertical, inverted-V, fan-dipole, and end-fed estimators keep the starting
geometry above the ground plane:

- A ground-mounted vertical is modeled 1 cm above the ground in the NEC deck.
- An inverted-V estimate widens the included angle, and raises the apex if
  needed, when the requested apex would put the ends below ground. The estimate
  carries `estimator.warning.inverted_v_angle_increased`.
- OCFD and horizontal Yagi/Moxon estimates raise a zero height to 0.01 m.
  Vertical Yagi/Moxon estimates require a height above half the longest
  element or rectangle width; the estimator rejects a lower height with a
  clear error instead of emitting invalid geometry.
- Fan-dipole elements use progressively narrower included angles so their wires
  do not overlap. The apex is raised if a longer element needs it, and the
  estimate carries `estimator.warning.fan_angle_increased` when adjusted. The
  design frequency is the lowest selected fan band. Element lengths are straight
  half-wave starting points; the V angle and coupling shift the final resonance,
  especially on the highest band. Use the Bands tab or the element optimizer to
  tune the final lengths.
- An end-fed end height outside the wire's vertical reach is clamped to the
  reachable range and the estimate carries
  `estimator.warning.endfed_end_height_clamped`.

## End-fed starting point

The ARRL End-Fed Half-Wave Antenna Kit publishes 66 ft for 40 m, 33 ft for
20 m, and 16 ft for 10 m, with a 49:1 transformer and a counterpoise
connection. PA9X documents the `0.05λ` counterpoise rule of thumb. The
estimator matches those wire lengths within 5%.

The transformer is applied as an ideal feed-point impedance transformation for
the reported impedance and SWR; it is not a physical unun model. The
counterpoise is geometry, not an ideal ground. Height, ground, feed-line
routing, and the common-mode choke are not modeled, so verify the final
installation with simulation or measurement.

The EFHW model uses a **fixed feed section** at the start of the same physical
wire (0.5 m by default, three segments) so the NEC delta-gap source does not
depend on the radiator segmentation. When no real counterpoise is enabled, a
short **installation return** (0.10 m by default) is modeled as a proxy for the
unavoidable coax/mast/earth path; it is not a physical radial. These are
modeling boundary conditions, not extra construction dimensions. The proxy
terminates at the ground plane; for a ground-level feed it is a 0.10 m wire on
the ground plane. The proxy is excluded from the drawn geometry, wire schedule,
and bill of materials. The EFHW editor can run a segmentation convergence check
over 10, 21, and 51 radiator segments. For the shortened presets the verdict
uses **R and X only** (absolute R spread up to 1 Ω and X spread up to 10 Ω)
because the absolute SWR depends on the unmodeled transformer/core/installation
details; SWR is shown as informational. The 80-10 preset is impedance-converged
with the current model; the 40-20-10 preset remains R/X-sensitive. Use the model
for trends and verify SWR with a VNA.

The shortened loaded EFHW presets (80-10 m and 40-20-10 m) have no
frequency-first estimator. A loading coil changes the electrical length
nonlinearly: the 80-10 m reference uses 20.35 m + 110 µH + 2.39 m, and the
40-20-10 m reference uses 10.01 m + 23 µH + 1.85 m. The loading coil is modeled
at a fixed node: the radiator is partitioned at the published coil offset, and
the coil section keeps three segments so segmentation changes do not move the
coil. The 100 pF capacitor is an ideal primary shunt; the 0.198 µH leakage is
an editable starting estimate from Squash Practice's measured 49:1
transformer, not this exact build. Core loss, capacitor ESR, winding capacitance,
the choke, and ground are not modeled. An optional inverted-L bend is
available: the vertical section is measured from the feed, and the horizontal
run is the remaining wire length. The G0KYA starting installation is about 8 m
vertical and 15 m horizontal, but the bend is modeled as a sharp 90° corner and
has not been independently validated. The default installation is horizontal
at 10 m; change the feed and end heights for a sloper, or enable the bend for
an inverted-L installation. Start from the published preset and edit the coil
and wire values; scaling those dimensions to another frequency is a heuristic,
not a published rule.

## Loop polygon correction

A closed thin-wire polygon resonates at a slightly longer conductor than the
ideal `1.0λ` circular loop. AntennaDesk applies

```text
C = λ × (1.02895 + 0.05028 / N + 0.09665 / N²)
```

where `N` is the number of sides. The coefficients are an application preset
calibrated with NEC-2 using the AntennaDesk loop model in free space for
`N = 3..32`; the residual in that calibration set is below `0.001λ`. This is
not a universal loop formula. Height above ground, ground model, wire diameter,
insulation, and nearby objects shift resonance, so the result remains a
starting point.

The loop estimator is orientation-agnostic. Applying a frequency estimate keeps
the loop editor's current `vertical` or `horizontal` orientation and only
changes the starting circumference, side count, and height intent.

At resonance a full-wave loop normally presents roughly `100-150 Ω` at the
feed point. Changing only its circumference cannot bring that to `50 Ω`; use a
`2:1` balun or the Matching Network dialog for a `50 Ω` system.

## Families without an estimator

The inverted-L, magnetic-loop, half-square, and bobtail-curtain templates have
no frequency-first estimator. They are generated from explicit geometry, and
the UI disables **Estimate Dimensions...** for them. The magnetic loop also
requires a user-supplied tuning capacitance; its default is a starting point,
not a calculated resonance value.

## Beverage starting dimensions

The Beverage editor's **Load one-wavelength starting length** action sets the
horizontal wire to `λ = c / f` at the current frequency. The height, azimuth,
radius, and termination resistance are preserved from the current editor
values; the default termination is 500 Ω.

Confidence is **heuristic**. A Beverage is a receiving antenna; its gain is low
and its pattern, termination efficiency, ground, and feed line are not
independently validated. The starting action is a convenience, not a design
claim.

## Biquad starting dimensions

The biquad editor's **Load quarter-wave starting dimensions** action uses:

- loop side = `0.25λ × 0.95` (the same practical quarter-wave factor as the
  other families);
- reflector spacing = half the loop side, i.e. `0.125λ × 0.95`;
- base height from the current editor value.

Confidence is **heuristic**. There is no independent numerical reference for
this generated geometry, so no gain, feedpoint-impedance, or bandwidth
tolerance is claimed. The biquad is classified experimental in
`evidence.py`; the starting action is a convenience, not a validated design.

## Half-square and bobtail-curtain starting dimensions

The **Load Cebik 7.15 MHz reference** button in the shared array editor scales
the published free-space dimensions by frequency:

- Half square: `62.4 ft` horizontal by `39 ft` vertical at `7.15 MHz`.
- Bobtail curtain: `125 ft` horizontal by `38 ft` vertical at `7.15 MHz`.

The half square is fed at a top corner and the bobtail at the top junction of
the center vertical. Cebik's Table 1 reports about `4.6 dBi` and `65 Ω` for the
half square and about `6.3 dBi` and `40 Ω` at the center/top junction for the
bobtail. Those values are not AntennaDesk validation targets: the model uses
the published starting geometry only, and ground, support height, feed line,
and matching remain installation-specific. The generic **Optimize...** action
can sweep the overall horizontal span, but it does not optimize the vertical
height or the feed offset.

## Radial-system presets

The vertical and loaded-vertical editors offer UI-only radial starting points.
They are not persisted; only the numeric base height, radial count, radial
length, and radial angle are saved with the design. Selecting a preset and then
editing a numeric radial field switches the selector to **Custom / measured**.

| Preset | Base/radial plane | Radial count | Radial length | Status |
|---|---|---|---|---|
| Ground radials | 0.25 m | 16 | `0.25λ` | Empirical quarter-wave starting length |
| Elevated radials | 2.0 m | 4 | `0.25λ` | Application starting point; height is installation-specific |
| Ground screen | 0.25 m | 32 | `0.10λ` | Dense radial approximation, not a bonded mesh |

The quarter-wave radial is the ARRL practical starting rule already used by the
vertical estimator. The elevated-plane height and the compact screen length are
application starting points, not published universal rules. The screen is a
dense radial field; it does not model a bonded wire mesh, a buried conductor,
or a solid ground plane. Verify radial count, length, height, and soil with a
sensitivity sweep and a feedpoint measurement. Confidence: heuristic. Tolerance:
not applicable to these presets.

## Loaded vertical preset

The loaded vertical / mobile whip catalog preset is not a frequency-first
estimator. It supplies a 2.0 m radiator, a 0.25 m base height, four 1.0 m
radials, and a 10 µH series coil at 1.0 m as application starting points. The
coil is an ideal series load with zero capacitance; its resistance is a
user-supplied loss estimate. Tune the height, coil position, and inductance with
the solver. The radial plane is a simplified counterpoise, not a vehicle body,
and no independent numerical reference is claimed for a mobile installation.

## Trap dipole starting dimensions

The trap dipole template is not a frequency-first estimator and is not eligible
for **Estimate Dimensions...**. The **Set starting dimensions from bands**
button inside its editor is an application helper:

- center section = half-wave factor at the high band;
- total length = half-wave factor at the low band;
- each outer section = `(total - center) / 2`;
- trap frequency = high band frequency;
- trap capacitance = `1 / ((2 * pi * f_trap)^2 * L)` for the entered
  inductance.

The helper ignores the loading effect of the traps on the low band, so the
calculated total is usually too long. Treat it as a starting point and tune the
length, trap position, inductance, and trap frequency with the solver. There is
no independent numerical reference for this trap-dipole configuration.

## Sloper, random wire, and doublet presets

These catalog presets are not frequency-first estimators:

- **Sloper** uses the end-fed half-wave factor for its wire length, a 10 m feed
  height, a 49:1 transformer, and a 0.05λ counterpoise. The end height is
  selected so the slope fits inside the wire. Tune the length, slope, and
  matching with the solver.
- **Random wire** uses a 17 m non-resonant wire, a 9:1 transformer, and a 0.05λ
  counterpoise. The length is an application starting point, not a resonance
  calculation.
- **Doublet** starts with a half-wave dipole and a 450 Ω, 10 m open-wire line.
  The feed line is project-level post-processing; the tuner is not modeled as a
  matching network. Tune the dipole length and line for the bands you use.

No independent numerical reference is claimed for these presets.

## Zepp preset

The Zepp preset follows the classic 3/4-wave end-fed topology: a 0.5 λ
radiator connects to the top of one conductor of a 0.25 λ parallel-wire stub.
The second conductor is open at the antenna end; a short base connector joins
both conductors, and the feed point is its midpoint. The stub is real geometry,
so its current and radiation are part of the result.

The parallel-wire characteristic impedance is estimated with

```text
Z0 = 276 log10(D / r)
```

where `D` is the center-to-center spacing and `r` is the conductor radius. The
default 0.05 m spacing with a 1 mm radius is about 469 Ω. The formula ignores
insulation, nearby conductors, and the finite stub length, so it is a geometric
starting value.

The 1:1 common-mode choke at the transmitter end is a construction requirement,
not a solver element. NEC-2 has no ferrite or common-mode choke model. The coax,
common-mode current, and installation effects are not modeled. Use odd
harmonics of the design frequency for analysis; even harmonics have severe
current imbalance in the stub. Tune the radiator and stub for the installed
height, ground, and hardware.

## G5RV preset

The G5RV preset is not a frequency-first estimator. It uses the published
102 ft dipole with a 29 ft 300 Ω or 34 ft 450 Ω matching section. The line is
modeled as a lossless geometry `TL` two-port. The published dimensions come from
Carr, *Practical Antenna Handbook* (via the Wikipedia G5RV article). The line
velocity factor is installation-specific; the default `1.0` treats the published
length as the electrical length. No independent numerical reference is claimed
for the complete lossless model or for a specific installation.

## T2FD preset

The T2FD uses a **reference-backed broadband starting estimate**, not a
resonance estimate. **Estimate Dimensions...** requires both the lowest and
highest design frequencies; it preserves the current termination resistance and
transformer ratio. The editor's starting-dimension helper uses the same
"wide-long" construction rule documented by L. B. Cebik, W4RNL:

- span (each parallel conductor): `300 / F(MHz)` feet;
- conductor spacing: `10 / F(MHz)` feet.

For the default 3.5 MHz lower band edge, that is a 26.13 m span and 0.87 m
spacing. The 800 Ω non-inductive termination and 16:1 feed transformer follow
the commercial B&W AC3-30 3-30 MHz design described in the Wikipedia T2FD
article (90 ft span, 18 in spacing, 800 Ω resistor, 16:1 balun). Other published
T2FDs use 390-480 Ω terminations with a 4:1 balun to 75 Ω; both values remain
editable.

The model places the resistor at the midpoint of the non-driven conductor and
the feed at the midpoint of the driven conductor. The resistor is a series
`LD 0` load. The transformer is an ideal post-processing two-port: it divides the
antenna impedance by the selected ratio for the transmitter-side SWR and
realized-gain calculations, but it is not part of the NEC geometry.

Assumptions and limitations:

- The resistor is ideal and has no temperature rise or power rating.
- The transformer and balun are ideal; balun loss, leakage, and common-mode
  current are not modeled.
- The model supports horizontal and vertical flat installations. The
  "tilted" installation is not modeled; the name is retained for the family.
- The antenna is non-resonant, so no resonance tolerance is claimed. The span
  and spacing are construction starting points, not verified cut lengths.
- A significant part of the applied power is dissipated in the termination,
  especially near the lower band edge. Realized gain and efficiency show this
  loss.
- Above roughly 1.25 wavelengths the main lobe moves away from broadside; the
  pattern view shows the resulting high-angle lobes.
- There is no independent numerical reference for the complete ideal-resistor,
  ideal-transformer model or for a specific installation.

## Yagi scope

The frequency-only estimator supports **2 to 32 elements** using the first
elements of the published DL6WU 32-element reference (Cebik, derived from the
RSGB VHF/UHF DX Book). Shorter Yagis use the DL6WU trimming principle: keep the
reflector, driven element, and the first directors. The driven element is
always index 1. The estimate itself is a straight driven element; applying it
in the UI preserves the current folded-driven option and spacing.

The DL6WU reference dimensions assume 4 mm elements at 432 MHz. Element
diameter correction and boom-mounting correction are not applied; this is a
starting design for NEC refinement. The existing Yagi editor and optimizer
remain the path for other published designs or diameter corrections.

The estimator carries the requested `polarization` into the generated
parameters. Both polarizations keep the boom horizontal. Vertical geometry
uses `height_m` as the boom centerline and fails when the longest element would
reach the ground, so the user must raise the boom before applying the estimate.
The Moxon estimator applies the same rule with `height_m - width_m / 2`.

## Source policy

Each estimator declares source identifiers. Add a source only when the formula
or published design is traceable. If no source exists, the estimator is
`heuristic` and must say so.

Reference sources currently used:

- ARRL Antenna Book: dipole end-effect, resonant loop, and vertical length
  factors (quarter-wave, half-wave, five-eighth-wave).
- ARRL, “Wire Antennas for the Beginner”: 120° inverted-V total length
  `465.6/f` feet.
- ON4UN, *Low-Band DXing*, Ch. 10: resonant delta-loop circumference of
  approximately 1.05–1.06 λ.
- NBS TN-688: five-element Yagi preset in the editor.
- DL6WU/Cebik: 2–32 element trimming Yagi starting design.
- L. B. Cebik, W4RNL, “The Moxon Rectangle: A Review”, Table 1: 20 m wire Moxon.
- Carr, *Practical Antenna Handbook* (via the Wikipedia G5RV article): 102 ft
  G5RV dipole and 29 ft 300 Ω / 34 ft 450 Ω matching sections.
- L. B. Cebik, W4RNL, "Modeling the T2FD": wide-long span and spacing rule for
  the T2FD. The Wikipedia T2FD article and the B&W AC3-30 product review
  document the 800 Ω termination and 16:1 commercial transformer.
- Application preset: Ringo proportions, the loop polygon correction, the
  end-fed transformer/counterpoise starting point, the loaded-vertical mobile
  preset, the trap-dipole starting dimensions, and the sloper, random-wire, and
  doublet presets. They are not universal formulas.

## Tests

- Formula and unit tests for every estimator.
- A parameterized NEC smoke test that estimates every supported family and
  confirms the resulting model solves and returns finite impedance.
- NEC-2 resonance checks for the loop polygon preset and the Ringo near-match
  estimate.
- Registry coverage for every current `ANTENNA_TYPE_*`.
- Explicit unsupported result for custom geometry and non-reference Yagi
  element counts.
- Reference-scaling tests for Yagi and Moxon.
- UI tests for estimate, invalidation, and apply.
- Snapshot tests for estimator outputs.

## Definition of Done for a new estimator

1. Add the intent fields it needs.
2. Register the estimator by antenna type.
3. Document the formula, source, assumptions, tolerance, and limitations.
4. Return a valid `AntennaDesignParameters` and `DimensionEstimate`.
5. Add domain, application, UI, and registry tests.
6. Make the current-template **Estimate Dimensions** dialog recognize the new
   template without adding a free family selector.
7. Update the user guide and changelog.

## Current limitations

- Height and ground are not solved analytically; use simulation refinement.
- Custom geometry has no frequency-only estimator.
- Yagi supports the DL6WU 2–32 element trimming reference; element-diameter
  and boom-mounting corrections are not applied.
- Moxon and Ringo are scaled presets, not universal synthesis.
- End-fed matching, counterpoise, and feed-line effects are installation
  specific.
- Loaded-vertical coil values are starting points; a mobile vehicle body is not
  modeled.
- OCFD dimensions and the 4:1 transformer are starting points. The actual
  feed-point impedance depends on height, ground, and feed offset; the balun is
  an ideal impedance transformation with no loss or common-mode model.
- Trap-dipole dimensions are starting points; trap loading, component losses,
  and installation effects are not solved analytically.
- T2FD span, spacing, termination, and transformer are starting points; the
  resistor and transformer are ideal, and the tilted installation is not
  modeled. The estimator is a broadband sizing rule, not a resonance claim.
- Sloper, random-wire, and doublet presets are application starting points; the
  doublet tuner is not modeled as a matching network.
- The G5RV uses a lossless geometry line and a user-supplied velocity factor;
  the transmitter coax and tuner are separate.
- Estimator provenance is shown in the dialog and persisted as optional design
  metadata. Editing the design clears it.
