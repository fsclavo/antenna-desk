# ADR-0055 — Flower Pot half-wave family and electrical-length representation

- **Status:** accepted and implemented 2026-11-26 for the FP1 scope; the
  required physical-versus-electrical spike is complete and selected Option A
- **Date:** 2026-11-26
- **Related:** FP1, [`AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) §FP1,
  [`GEOMETRY_PRESENTATION.md`](../GEOMETRY_PRESENTATION.md),
  [ADR-0010](0010-first-class-generator-templates.md),
  [ADR-0013](0013-frequency-first-dimension-estimation.md),
  [ADR-0026](0026-family-optimizer-architecture.md),
  [ADR-0037](0037-common-mode-return-model.md),
  [ADR-0043](0043-design-versus-analysis-frequency.md)

## Context

The VK2ZOI "Flower Pot" is a **coaxially fed vertical half-wave dipole**:

- the coax center conductor forms the top radiator;
- the outside of the coax shield forms the bottom radiator;
- the feed is the junction between them;
- a resonant choke wound in the coax below the bottom radiator isolates the
  feedline from the radiating shield;
- the assembly sits inside PVC conduit, which loads the antenna electrically.

It is **not an end-fed antenna**. Some sources call it an "end-fed resonant
feedline dipole" because the coax reaches the antenna from the bottom, but the
radiating structure is a center-fed dipole. It is also not a vertical with
radials: the lower conductor is a radiating arm, not a ground plane.

The published half-wave dimensions are physical cut lengths. For 2 m:

```text
top 457 mm + bottom 447 mm = 904 mm at about 146 MHz
```

A free-space half-wave at 146 MHz is about 1027 mm. A bare-wire NEC model with
the physical 904 mm dimensions resonates well above the 2 m band because the
coax dielectric, the conduit, and the end effect load the antenna electrically.
The published construction survey reports an overall empirical factor of about
`0.88` to `0.885` for the 2 m and 6 m builds. That factor is a construction
correction, not the coax velocity factor.

The current canonical model supports straight wires, one primary feed, optional
sources, lumped RLC loads, two-port transmission lines, and a ground model. It
does **not** support:

- a coax cable as an inner conductor plus an outer shield with different
  interior and exterior currents;
- a dielectric coating or a dielectric radome;
- a common-mode choke as a solver element;
- a floating sleeve or a cylindrical conductor;
- a shorted one-port coax stub;
- a transmission line whose shield is also a radiating wire.

The family optimizer and estimator contracts are well suited to a two-section
vertical dipole. The missing capability is the representation of the coax
construction, not the dipole itself.

Only the half-wave version maps cleanly to the current straight-wire model.
The other published variants need new primitives:

| Variant | Missing primitive |
|---|---|
| Dual-band half-wave with a foil sleeve | Sleeve/cylinder conductor and its phasing coupling |
| Single 5/8 | Shorted one-port coax stub in parallel at the feed |
| Double 5/8 | Coax/TL radiator with a 75 Ω quarter-wave transformer |
| Experimental dual-band high-gain | Sleeve, half-wave phasing line, and two driven sections |

## Decision

1. **Scope the first family to the half-wave Flower Pot**, with the published
   2 m and 6 m starting dimensions. Do not add the 5/8, double 5/8, dual-band
   sleeve, or high-gain variants in this ADR. Each needs its own spike and ADR.
2. **Model the radiator as two collinear wires** with different radii and
   materials: the top coax inner conductor and the bottom coax shield. The feed
   is at their junction. The lower wire ends at the choke. The feedline below
   the choke is the project `FeedLine`, not part of the antenna geometry.
3. **Use an ideal choke in the MVP.** The lower radiator ends at the choke and
   no feedline common-mode path is modeled. The UI, reports, and evidence must
   state that the real choke impedance, its self-resonance, the common-mode
   current, and the coax dielectric loss are not modeled. Do not synthesize a
   choke R+jX from the published turns/former table.
4. **Do not use display-only geometry.** The canonical `to_antenna()` model is
   the model that is solved. If the solved model differs from the physical cut
   lengths, the difference must be explicit in the family parameters and in the
   construction report. A hidden simulation-only scale factor outside the
   canonical model is not acceptable.
5. **Use the selected Option A: an explicit NEC electrical equivalent plus a
   physical cut list.** The spike compared A–D and selected a feed-centered
   electrical scale of **1.087**, separate from the 0.88 construction factor.
   The model scale is explicit in the family parameters and construction
   report; no hidden simulation-only scale is allowed. See
   [`fp1-flower-pot-length-representation.md`](../spikes/fp1-flower-pot-length-representation.md).
6. **Expose both length systems explicitly.** The family parameters carry the
   physical top and bottom cut lengths, their radii, the installation base
   height, the conduit/coax construction context, the **0.88 construction
   shortening factor**, and the **1.087 electrical model scale** selected by
   the spike. The construction sheet must show the physical cut list. The wire
   schedule must show the canonical wires and label the scaled lengths as
   electrical equivalents. Neither table may be the only source of a build
   value, and the two factors must never be presented as interchangeable.
7. **Keep the lower tip above ground.** The base height is an installation
   parameter; the family must not place the lower radiator endpoint at `z = 0`
   or let the NEC ground clearance silently move it. A positive base height is
   required, and validation uses the **scaled electrical lower tip**, which
   extends about 38.9 mm (2 m) or 108.3 mm (6 m) below the physical lower cut
   when the feed is kept at the physical junction height. A clear validation
   message must state that margin.
8. **Classify the feed as a balanced antenna with an integrated choke.** The
   app must not require a separate current balun or classify the family as an
   unbalanced vertical. The feed-connection detail should say: coax center to
   the top radiator, shield to the bottom radiator, resonant choke at the base
   of the lower radiator, no separate balun. Add the family to the feed-balance
   and feed-connection coverage.
9. **Evidence level B for the published starting dimensions, C for the coax and
   choke equivalent.** The published source gives construction dimensions and
   VSWR plots, not a numerical R+jX table or a calibrated gain measurement. The
   catalog must not claim 50 Ω, a specific gain, or a validated choke. Scaled
   frequencies outside the published 2 m/6 m rows are heuristic.
10. **Persist with the next schema bump after the completed spike** (schema 71
    is current at this commit) and an additive/no-op migration for existing
    files. The family payload is optional; old projects load unchanged.
11. **Add the estimator and optimizer coverage required by ADR-0013 and
    ADR-0026**, or record an explicit unavailable reason. The initial optimizer
    may vary the top and bottom physical lengths; the shortening factor and
    choke are construction context, not free variables, unless a later ADR
    justifies otherwise.
12. **Keep the deferred variants out of the catalog** until their primitives and
    validation exist. A catalog entry that only draws a plain vertical dipole
    is not a Flower Pot model.

## Physical-versus-electrical spike

The spike was a standalone NEC-2 investigation using the bundled `nec2c`; it
did not need application code. It compared:

| Option | Canonical geometry | Solver model | Construction values | Risk |
|---|---|---|---|---|
| **A. Electrical equivalent + cut list** | Scaled by `1 / factor` | Correct resonance for the modelled band | Physical cut list separate | Medium: two lengths to explain and test |
| **B. Physical geometry + insulation/velocity** | Physical | `IS`-style dielectric coating or a documented per-wire electrical-length scale | Physical and canonical are the same | High: new domain/solver capability and calibration |
| **C. Physical geometry + lumped equivalent** | Physical | Series load that restores resonance | Physical | Medium: non-physical equivalent, frequency-specific |
| **D. Bare physical wire** | Physical | No correction | Physical | Low, but **rejected**: it resonates in the wrong place and would mislead the builder |

The spike recorded, for 2 m and 6 m:

- the bare-wire resonance and input impedance for the physical lengths;
- the resonance and impedance for each corrected option;
- sensitivity to top and bottom radii, base height, ground model, and
  segmentation;
- whether `nec2c` supports the `IS` insulated-wire card and whether a calibrated
  coating reproduces the published band behaviour;
- whether the chosen option preserves the published top/bottom split and the
  physical feed height;
- the difference between the canonical wire length and the physical cut length
  that the construction sheet must disclose.

The comparison target was the published VSWR behaviour and the published
dimensions, not an invented R+jX value. The spike did not treat a VSWR plot as
a precision impedance reference.

### Spike result (2026-11-26)

The full run is recorded in
[`fp1-flower-pot-length-representation.md`](../spikes/fp1-flower-pot-length-representation.md).
With the bundled `nec2c`, 0.5/1.5 mm assumed radii, free space, and 21/41
segments:

| Case | 2 m resonance | 6 m resonance |
| --- | ---: | ---: |
| D: bare physical wire | 158.505 MHz | 57.357 MHz |
| A: scale `1 / 0.88` | 139.653 MHz | 50.515 MHz |
| A: scale **1.087** | 145.935 MHz | 52.795 MHz |

The naive `1 / 0.88` scale double-counts the wire end effect. A single **1.087**
scale places both rows within 0.2 % of the published band centers. Radius
sensitivity moves the 2 m resonance by about 1.9 MHz over 0.25–3.0 mm radii, so
1.087 is a NEC model calibration, not a velocity factor.

`nec2c` rejects the NEC-4 `IS` card and the 4nec2 `LD 7` card; its loading code
accepts only types 0–5. Option B is unavailable for the MVP and would not model
the coax/PVC construction even if present. Option C needs 101.8 nH (2 m) or
339.2 nH (6 m) at the feed, which is not constant per unit length and has no
physical choke/coax justification. Option D is rejected because it resonates
far outside both published bands.

### Selection rule (applied)

1. **B is unavailable.** `nec2c` has no stable insulated-wire/coating model for
   this construction.
2. **A is selected** with an explicit canonical electrical model and a separate
   physical cut list.
3. **C is rejected** as a non-physical, band-specific equivalent.
4. **D is rejected** because it misleads the builder.

## Geometry presentation

The construction view is elevation. The scene must:

- draw both canonical wires and the feed at their junction;
- show the physical cut lengths separately from the scaled electrical model
  lengths; label the latter as the solver equivalent;
- dimension the top and bottom sections, the total radiator, the base height,
  and the electrical lower-tip extension;
- show the choke as a labeled, not-to-scale detail inset, not as a synthetic
  canonical wire; the feed gap remains an as-built construction dimension;
- state the PVC conduit and common-mode choke as construction notes, not as
  wires;
- avoid a plan view that collapses the vertical wires to a point;
- keep every displayed dimension anchored to the canonical model or to a
  declared construction parameter.

The scene contract test must preserve both wires and the feed, assert the
construction view, assert no zero-length dimension, and assert that the choke
and conduit overlays are not counted as canonical wires. The wire schedule must
list both conductors with their radii, materials, and scaled electrical
lengths and state that they are the electrical model; the family-specific cut
list must list the physical top and bottom lengths. The coax, conduit, and
choke remain explicit construction notes, and no numeric choke table is embedded
until measured data exists.

## Estimator

The frequency-first estimator covers the published 2 m and 6 m starting points:

- physical total length approximately `0.44 λ`;
- top/bottom split approximately `50.5 / 49.5` of the physical total;
- default construction shortening factor `0.88` for grey PVC conduit,
  editable; this is not the electrical model scale;
- published rows: 457/447 mm at 146 MHz and 1273/1245 mm at 52.7 MHz;
- electrical model scale `1.087` for `to_antenna()`, separate from the
  construction factor and labelled as a NEC calibration;
- no numeric choke table is embedded: the choke is a construction item with a
  warning that it must be resonated and measured before it can be modeled;
- confidence B for the published rows, heuristic outside them;
- a tolerance of 5% on the physical top and bottom lengths; no impedance or
  gain tolerance is claimed;
- warnings for conduit material, coax type, feedline/choke not modeled, and
  installation height.

The estimator must not claim a 50 Ω feedpoint or a gain value. The 0.88
construction factor and the 1.087 electrical model scale are shown as two
different quantities.

## Optimizer

The initial descriptor may vary the top and bottom physical lengths with:

- a target-impedance or minimum-SWR objective at the design frequency;
- hard constraints for positive lengths, a positive base height, and the
  top/bottom construction envelope;
- a deterministic seed and the normal budget profiles;
- an Apply Best path through the family editor and a full simulation.

The **1.087 electrical model scale**, the **0.88 construction factor**, choke,
conduit, and feedline are context, not optimizer variables, unless a later ADR
defines a traceable model for them. Constraints must include the scaled
electrical lower-tip clearance as well as the physical cut geometry. The
optimizer must not tune the model into a geometry that cannot be built.

## Consequences

Positive:

- Adds a popular VHF/portable family that fits the existing Vertical catalog.
- Reuses the straight-wire solver, estimator, optimizer, scene, and reporting
  contracts; no new runtime dependency.
- Makes the coax construction and its limits explicit instead of hiding them
  behind a plain dipole.
- Gives the project a documented path to the 5/8 and dual-band variants without
  pretending they are already modeled.

Costs:

- A new family payload, schema bump, catalog entry, form/dialog, i18n/help,
  geometry, reports, estimator, optimizer, and tests.
- An explicit physical-versus-electrical length contract.
- A new feed-connection/balance branch for an integrated choke.
- A construction-only cut list and BOM rows for coax, conduit, choke former,
  end cap, and tape.

## Out of scope

- Single 5/8, double 5/8, dual-band sleeve, and high-gain variants.
- A choke R+jX synthesis from turns/former data; common-mode current; coax
  shield radiation; dielectric loss; a dielectric conduit body.
- A 70 cm single-band half-wave design outside the published choke table.
- A 50 Ω, gain, bandwidth, or efficiency claim.
- A new solver engine or an external circuit simulator.
- Any change to the existing feed-line post-processing model or the project
  container format beyond the additive family payload.

## Acceptance

- The spike compared options A–D at 2 m and 6 m and recorded the selected
  Option A representation in this ADR; no numerical reference is invented.
- The family parameters, `to_antenna()`, scene, wire schedule, cut list, and
  construction sheet keep the 0.88 construction factor and the 1.087
  electrical model scale distinct and agree on which lengths are canonical
  and which are physical.
- The scaled electrical lower-tip extension is visible and validated against
  the base height.
- The construction view preserves both wires and the feed; the choke inset and
  conduit note are not canonical wires; dimensions are non-zero and anchored.
- The estimator reproduces the published 2 m and 6 m starting dimensions within
  the documented 5% physical-length tolerance and reports the
  choke/conduit/feedline limitations.
- The feed connection says "integrated choke, no separate current balun" and
  does not require the project current-balun record.
- The family optimizer covers the top/bottom lengths, passes field-coverage,
  budget, constraint, determinism, Apply Best, and solver QA, and does not claim
  a validated 50 Ω match.
- Old projects load unchanged at the new schema; the new payload round-trips.
- EN/ES help is complete and in the manifest; the catalog routes work in both
  New Antenna and Change Template.
- A real `nec2c` case completes at 2 m and 6 m with a finite impedance and a
  resonance consistent with the selected representation. No gain or impedance
  claim is added.

## Risks

| Risk | Mitigation |
|---|---|
| The equivalent dipole does not reproduce the coax/choke behaviour | Spike first; label the limitation; compare with a measured build when available |
| The scaled electrical lower tip goes below ground | Validate the scaled tip, show the extension, and require positive clearance |
| The user cuts the electrical length instead of the physical length | Show both; make the cut list authoritative; explicit copy in the form and construction sheet; never collapse 0.88 and 1.087 |
| The published VSWR plot is treated as a numerical reference | Use it only as a qualitative band/behaviour check; do not invent R+jX |
| The choke table is mistaken for an impedance model | State that it is a self-resonance construction guide; keep the choke ideal in the MVP |
| The family is confused with an end-fed or a vertical with radials | Catalog description, help, and feed-connection detail state the topology explicitly |
| Scope creep into the 5/8 and dual-band variants | Keep them out of the catalog until their ADRs and primitives exist |
| VHF segmentation or thin-wire quality | Use the existing model-quality policy; add a real 2 m/6 m solver regression |

## References

- [`fp1-flower-pot-length-representation.md`](../spikes/fp1-flower-pot-length-representation.md),
  FP1 NEC-2 length-representation spike, 2026-11-26.
- J. Bishop, VK2ZOI, "Half-Wave Flower Pot Antenna",
  <https://vk2zoi.com/articles/half-wave-flower-pot/>.
- J. Bishop, VK2ZOI, "Flower Pots",
  <https://vk2zoi.com/flower-pots/>.
- VK4PK, "My 6 Meter Flowerpot Antenna", BARC, 2021, construction survey,
  <https://barc.org.au/assets/projects/flowerpot_antenna/VK4PK_My_6m_Flowerpot_Antenna-v1.0.pdf>.
- J. Bishop, VK2ZOI, "Dual Band Half-Wave Flower Pot Antenna",
  <https://vk2zoi.com/articles/dual-band-half-wave-flower-pot/>.
- J. Bishop, VK2ZOI, "Single 5/8 Flower Pot Antenna",
  <https://vk2zoi.com/articles/single-five-eighth-flower-pot/>.
- J. Bishop, VK2ZOI, "Double 5/8 Flower Pot Antenna",
  <https://vk2zoi.com/articles/double-five-eighth-flower-pot/>.
- J. Bishop, VK2ZOI, "Experimental Dual Band High Gain Flower Pot Antenna",
  <https://vk2zoi.com/articles/dual-band-high-gain-flower-pot/>.
