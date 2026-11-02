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
- Five-eighth-wave vertical: `0.625λ`.
- Resonant full-wave loop: circumference `1.0λ`.
- Folded-dipole starting spacing: `0.02λ`.
- Radial starting length: `0.25λ`.

### Families

| Family | Starting estimate | Confidence | Notes |
|---|---|---|---|
| Wire dipole | `0.5λ × 0.95` total length | empirical | Height and ground affect resonance |
| Folded dipole | same element length; `0.02λ` spacing | empirical | Spacing controls step-up impedance |
| Loop / quad / delta | circumference `1.0λ` | empirical | Quad=4 sides, delta=3 |
| Vertical 1/4 | `0.25λ × 0.95`; radial `0.25λ` | empirical | Radial count/length are starting values |
| Vertical 5/8 | `0.625λ` | physical | High feed impedance; matching required |
| Inverted-V | half-wave dipole total, split in two legs | empirical | Included angle affects feed impedance |
| Fan dipole | one half-wave element per band | empirical | Elements interact |
| End-fed | half-wave wire | heuristic | Matching transformer and counterpoise not modeled |
| OCFD | half-wave total, feed at 1/3 | heuristic | Existing synthesis can refine length/feed |
| J Pole / Slim Jim | J Pole: total 3/4-wave height, quarter-wave stub, feed at 40% of stub; Slim Jim: half-wave radiator above the folded stub | empirical | Feed offset and stub need tuning |
| Ringo | 0.725-wave vertical with a small horizontal matching ring, calibrated for the simplified AntennaDesk geometry | heuristic | Not a universal commercial Ringo formula |
| Yagi | DL6WU 2–32 element trimming reference scaled by frequency | reference scaled | No unique Yagi design; optimize for the target |
| Moxon | Cebik 20 m wire reference scaled by frequency | reference scaled | Gap and tips are sensitive |

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

- ARRL Antenna Book: dipole end-effect, resonant loop, quarter-wave vertical.
- NBS TN-688: five-element Yagi preset in the editor.
- DL6WU/Cebik: 2–32 element trimming Yagi starting design.
- L. B. Cebik, W4RNL, “The Moxon Rectangle: A Review”, Table 1: 20 m wire Moxon.
- Application preset: Ringo proportions; explicitly heuristic.

## Tests

- Formula and unit tests for every estimator.
- A parameterized NEC smoke test that estimates every supported family and
  confirms the resulting model solves and returns finite impedance.
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
- Estimator provenance is shown in the dialog and persisted as optional design
  metadata. Editing the design clears it.
