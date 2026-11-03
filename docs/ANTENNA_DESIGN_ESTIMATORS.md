# Antenna dimension estimators

This document defines the frequency-first dimension estimators. They produce
**starting dimensions**, not verified construction values. Final dimensions
depend on height, ground, conductor diameter, insulation, nearby objects, and
the matching network.

## Workflow

```text
DesignIntent
  frequency, family, subtype, environment, constraints
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
- Five-eighth-wave vertical: `0.625λ`.
- Resonant full-wave loop: circumference `1.0λ` for an ideal thin circular
  loop, with the polygon correction described below.
- Folded-dipole starting spacing: `0.02λ`.
- Radial starting length: `0.25λ`.

### Families

| Family | Starting estimate | Confidence | Notes |
|---|---|---|---|
| Wire dipole | `0.5λ × 0.95` total length | empirical | Height and ground affect resonance |
| Folded dipole | same element length; `0.02λ` spacing | empirical | Spacing controls step-up impedance |
| Loop / quad / delta | circumference `λ × (1.02895 + 0.05028/N + 0.09665/N²)` | empirical | `N` sides; quad=4, delta=3; calibrated polygon preset |
| Vertical 1/4 | `0.25λ × 0.95`; radial `0.25λ` | empirical | Radial count/length are starting values |
| Vertical 1/2 | `0.5λ × 0.95`; radial `0.25λ` | empirical | High feed impedance; matching required |
| Vertical 5/8 | `0.625λ` | physical | High feed impedance; matching required |
| Inverted-V | half-wave dipole total, split in two legs | empirical | Included angle affects feed impedance |
| Fan dipole | one half-wave element per band | empirical | Elements interact |
| End-fed | half-wave wire; `0.05λ` counterpoise; 49:1 transformer | heuristic | Transformer and counterpoise are application starting points |
| OCFD | half-wave total, feed at 1/3 | heuristic | Existing synthesis can refine length/feed |
| J Pole / Slim Jim | J Pole: total 3/4-wave height, quarter-wave stub, feed at 40% of stub; Slim Jim: half-wave radiator above the folded stub | empirical | Feed offset and stub need tuning |
| Ringo | 0.725-wave vertical with a small horizontal matching ring, calibrated for the simplified AntennaDesk geometry | heuristic | Not a universal commercial Ringo formula |
| Yagi | DL6WU 2–32 element trimming reference scaled by frequency | reference scaled | No unique Yagi design; optimize for the target |
| Moxon | Cebik 20 m wire reference scaled by frequency | reference scaled | Gap and tips are sensitive |

Ground-mounted radials are placed 1 cm above the ground plane in the NEC deck.
The estimator and project keep the requested base height; the clearance is a
solver constraint, not a design dimension. NEC-2 rejects horizontal radials
lying exactly on a ground plane.


## Ground and fan constraints

The vertical, inverted-V, fan-dipole, and end-fed estimators keep the starting
geometry above the ground plane:

- A ground-mounted vertical is modeled 1 cm above the ground in the NEC deck.
- An inverted-V estimate widens the included angle, and raises the apex if
  needed, when the requested apex would put the ends below ground. The estimate
  carries `estimator.warning.inverted_v_angle_increased`.
- Fan-dipole elements use progressively narrower included angles so their wires
  do not overlap. The apex is raised if a longer element needs it, and the
  estimate carries `estimator.warning.fan_angle_increased` when adjusted.
- An end-fed end height outside the wire's vertical reach is clamped to the
  reachable range and the estimate carries
  `estimator.warning.endfed_end_height_clamped`.

## End-fed starting point

The end-fed estimate includes a 49:1 ideal transformer and a `0.05λ`
counterpoise as application starting points. The transformer is applied as a
feed-point impedance transformation for the reported impedance and SWR; it is
not a physical unun model. The counterpoise is geometry, not an ideal ground.
Both values vary with the installation, feed height, ground, and routing, so
verify them with simulation or measurement.

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

At resonance a full-wave loop normally presents roughly `100-150 Ω` at the
feed point. Changing only its circumference cannot bring that to `50 Ω`; use a
`2:1` balun or the Matching Network dialog for a `50 Ω` system.

## Loaded vertical preset

The loaded vertical / mobile whip catalog preset is not a frequency-first
estimator. It supplies a 2.0 m radiator, a 0.25 m base height, four 1.0 m
radials, and a 10 µH series coil at 1.0 m as application starting points. The
coil is an ideal series load with zero capacitance; its resistance is a
user-supplied loss estimate. Tune the height, coil position, and inductance with
the solver. The radial plane is a simplified counterpoise, not a vehicle body,
and no independent numerical reference is claimed for a mobile installation.

## Trap dipole starting dimensions

The trap dipole template is not a frequency-first estimator and is not listed
in the Design from Frequency dialog. The **Set starting dimensions from bands**
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

## G5RV preset

The G5RV preset is not a frequency-first estimator. It uses the published
102 ft dipole with a 29 ft 300 Ω or 34 ft 450 Ω matching section. The line is
modeled as a lossless geometry `TL` two-port. The published dimensions come from
Carr, *Practical Antenna Handbook* (via the Wikipedia G5RV article). The line
velocity factor is installation-specific; the default `1.0` treats the published
length as the electrical length. No independent numerical reference is claimed
for the complete lossless model or for a specific installation.

## T2FD preset

The T2FD is not a frequency-first resonance estimator. It is a
**reference-backed starting geometry** for a non-resonant, terminated folded
dipole. The editor's starting-dimension helper uses the "wide-long" construction
rule documented by L. B. Cebik, W4RNL:

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
always index 1.

The DL6WU reference dimensions assume 4 mm elements at 432 MHz. Element
diameter correction and boom-mounting correction are not applied; this is a
starting design for NEC refinement. The existing Yagi editor and optimizer
remain the path for other published designs or diameter corrections.

## Source policy

Each estimator declares source identifiers. Add a source only when the formula
or published design is traceable. If no source exists, the estimator is
`heuristic` and must say so.

Reference sources currently used:

- ARRL Antenna Book: dipole end-effect, resonant loop, and vertical length
  factors (quarter-wave, half-wave, five-eighth-wave).
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
6. Add the family to the Design from Frequency dialog.
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
- Trap-dipole dimensions are starting points; trap loading, component losses,
  and installation effects are not solved analytically.
- T2FD span, spacing, termination, and transformer are starting points; the
  resistor and transformer are ideal, and the tilted installation is not
  modeled.
- Sloper, random-wire, and doublet presets are application starting points; the
  doublet tuner is not modeled as a matching network.
- The G5RV uses a lossless geometry line and a user-supplied velocity factor;
  the transmitter coax and tuner are separate.
- Estimator provenance is shown in the dialog and persisted as optional design
  metadata. Editing the design clears it.
