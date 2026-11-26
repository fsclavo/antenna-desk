# FP1 Flower Pot physical-versus-electrical length spike

**Date:** 2026-11-26

**Status:** spike complete; **Option A selected** with an explicit NEC
electrical-length scale and a separate physical cut list.

**Related:** FP1, [ADR-0055](../ADR/0055-flower-pot-half-wave-family.md),
[`AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) §FP1

## Question

The Flower Pot is built from physical coax cut lengths that are much shorter
than a free-space half-wave. The published 2 m row is 457 mm top + 447 mm
bottom at 146 MHz; the 6 m row is 1273 mm top + 1245 mm bottom at 52.7 MHz.
A bare-wire NEC model of those physical lengths does not resonate in the
published band because the coax dielectric, the PVC conduit, the feed
construction, and the wire end effect all load the antenna.

The spike must select one canonical representation that:

- puts the modelled resonance in the published band;
- keeps the physical cut list authoritative for construction;
- keeps any difference between physical and solved lengths explicit;
- does not require a new solver or an invented dielectric/velocity value.

## External anchors

Only the published physical rows and band centers are used as external anchors:

| Band | Top cut | Bottom cut | Physical total | Target |
| --- | ---: | ---: | ---: | ---: |
| 2 m | 457 mm | 447 mm | 904 mm | 146 MHz |
| 6 m | 1273 mm | 1245 mm | 2518 mm | 52.7 MHz |

These are the VK2ZOI/VK4PK construction values already recorded in ADR-0055.
No VSWR plot point is treated as an R+jX reference.

## Model assumptions

The comparison uses the bundled `spikes/phase0/build/nec2c` with:

- two collinear vertical wires sharing the feed point;
- top radius 0.5 mm (inner conductor assumption);
- bottom radius 1.5 mm (shield outer-radius assumption);
- 21 segments for the 2 m rows and 41 for the 6 m rows unless noted;
- free space, no conductor losses, no choke, no feedline, no conduit body;
- feed at the junction; electrical lengths are scaled about the feed so the
  physical feed height is preserved.

The radii are modelling assumptions, not published conductor measurements.
The sensitivity table below shows why the selected scale is a model
calibration, not a precision velocity factor.

## Results

### Bare physical wire (Option D)

| Band | Resonance | R at resonance | X at published target |
| --- | ---: | ---: | ---: |
| 2 m | 158.505 MHz | 81.54 Ω | −93.40 Ω at 146 MHz |
| 6 m | 57.357 MHz | 80.34 Ω | −112.33 Ω at 52.7 MHz |

The bare physical wire resonates far above both published bands. Option D is
rejected: it would mislead the builder and cannot be the solved model.

### Electrical scale 1/0.88 (naive Option A)

Scaling the physical lengths by `1 / 0.88` gives 1027.3 mm (2 m) and
2861.4 mm (6 m):

| Band | Resonance | R at resonance | X at published target |
| --- | ---: | ---: | ---: |
| 2 m | 139.653 MHz | 80.90 Ω | +54.34 Ω at 146 MHz |
| 6 m | 50.515 MHz | 79.85 Ω | +60.47 Ω at 52.7 MHz |

This overshoots in the opposite direction. The published 0.88 construction
factor is relative to a free-space half-wave; it already contains the wire end
effect. Applying it directly as a NEC length scale double-counts that effect.

### Explicit NEC scale 1.087 (selected Option A)

A single scale of **1.087** is derived from the two bare-wire resonance ratios:

- 2 m: `158.505 / 146 = 1.08565`;
- 6 m: `57.357 / 52.7 = 1.08837`;
- mean: **1.087**, with the two rows within 0.2 % of their band centers.

| Band | Electrical top | Electrical bottom | Electrical total | Resonance | X at target |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 m | 496.8 mm | 485.9 mm | 982.6 mm | 145.935 MHz | +0.53 Ω |
| 6 m | 1383.6 mm | 1353.3 mm | 2736.9 mm | 52.795 MHz | −2.49 Ω |

The model input resistance at the target is about **81 Ω** (2 m) and
**80 Ω** (6 m). This is a NEC model result, not a measured or 50 Ω claim.

### Option B: insulated-wire or coating model

The bundled `nec2c` does **not** support the NEC-4 `IS` card or the 4nec2
`LD 7` extension:

- an `IS` card is rejected with `FAULTY DATA CARD LABEL AFTER GEOMETRY
  SECTION`;
- an `LD 7` card is rejected with `IMPROPER LOAD TYPE CHOSEN`;
- the bundled source accepts only loading types 0–5.

Even if `LD 7` were available, it models a thin dielectric coating, not a coax
inner conductor plus shield inside a PVC conduit. There is no calibrated
coating/velocity value for this construction. Option B is unavailable for the
MVP and is not physically adequate without a new solver capability and data.

### Option C: lumped equivalent

The series reactance needed at the feed for the bare physical lengths is:

| Band | Bare X at target | Series inductance |
| --- | ---: | ---: |
| 2 m | −93.40 Ω | 101.8 nH |
| 6 m | −112.33 Ω | 339.2 nH |

That is 112.6 nH/m at 2 m and 134.7 nH/m at 6 m. The equivalent is not constant
per unit length, is frequency-specific, and has no physical choke/coax
justification. Option C is rejected.

## Sensitivity

### Segmentation

| Band | Segments | Resonance | R at resonance |
| --- | ---: | ---: | ---: |
| 2 m | 11 / 21 / 41 | 146.002 / 145.935 / 145.890 MHz | 78.37 / 81.12 / 86.01 Ω |
| 6 m | 21 / 41 / 81 | 52.804 / 52.795 / 52.789 MHz | 77.66 / 80.01 / 83.81 Ω |

Resonance is stable within 0.11 MHz (2 m) and 0.015 MHz (6 m); resistance
varies with segmentation. The model scale is not a resistance calibration.

### Radii

With scale 1.087 and the same segmentation:

| Band | Top/bottom radius | Resonance | X at target |
| --- | --- | ---: | ---: |
| 2 m | 0.25 / 0.75 mm | 146.759 MHz | −6.70 Ω |
| 2 m | 0.50 / 1.50 mm | 145.935 MHz | +0.53 Ω |
| 2 m | 1.00 / 3.00 mm | 144.829 MHz | +8.86 Ω |
| 6 m | 0.25 / 0.75 mm | 52.999 MHz | −8.45 Ω |
| 6 m | 0.50 / 1.50 mm | 52.795 MHz | −2.49 Ω |
| 6 m | 1.00 / 3.00 mm | 52.531 MHz | +4.17 Ω |

The 2 m resonance moves by about 1.9 MHz over this radius range. The family
must expose both radii and label the electrical scale as a model calibration,
not a velocity factor.

### Ground and base height

With scale 1.087, feed at the physical junction height:

| Band | Ground | Base 1 m | Base 3 m |
| --- | --- | ---: | ---: |
| 2 m | free | 145.935 MHz | 145.935 MHz |
| 2 m | perfect | 145.772 MHz | 145.898 MHz |
| 2 m | finite εr=13, σ=0.005 | 145.845 MHz | 145.915 MHz |
| 6 m | free | 52.795 MHz | 52.795 MHz |
| 6 m | perfect | 53.101 MHz | 52.790 MHz |
| 6 m | finite εr=13, σ=0.005 | 52.968 MHz | 52.794 MHz |

At the published-band scale the ground shift is small at these heights; the
model is not a substitute for an in-situ measurement or a choke model.

## Selected representation

**Option A: explicit NEC electrical equivalent plus a physical cut list.**

- The family stores the physical top and bottom cut lengths and the published
  construction shortening factor (`0.88`).
- It also stores an explicit **electrical model scale** (`1.087` default) used
  only by `to_antenna()`. The scale is a NEC calibration from the published
  rows, not a measured velocity factor.
- The canonical wires are scaled about the feed by 1.087; the physical feed
  height and the top/bottom split are preserved.
- The construction sheet and wire schedule show both the physical cut list and
  the electrical model lengths. The model top extends above the physical top by
  about 39.8 mm (2 m) or 110.8 mm (6 m). The model lower tip extends below the
  physical lower cut by about 38.9 mm (2 m) or 108.3 mm (6 m) when the feed is
  kept at the physical height.
- Base-height validation uses the model lower tip, not only the physical cut.
  The family must require enough clearance for that extension.
- No hidden simulation-only scale is allowed. The construction sheet is
  authoritative for cutting; the wire schedule labels the canonical wires as
  electrical equivalents.

The 0.88 construction factor and the 1.087 electrical scale are different
quantities:

- `0.88` compares the physical cut to a free-space half-wave and is a
  construction/estimator factor;
- `1.087` compares the NEC electrical model to the physical cut and is a solver
  calibration.

The family must not collapse them into one field.

## Consequences for implementation

- `FlowerPotParameters` carries physical top/bottom lengths, top/bottom radii,
  the 0.88 construction factor, the 1.087 electrical model scale, base height,
  material/ground, and construction context.
- `to_antenna()` applies only the 1.087 scale, about the feed.
- The estimator uses the 0.88 construction factor and the published 2 m/6 m
  rows; it does not present the 1.087 scale as a physical cut.
- The optimizer varies physical lengths; the electrical scale, construction
  factor, radii, choke, conduit, and feedline are context, not free variables.
- The scene and construction sheet show physical and electrical lengths,
  the feed junction, and the lower-tip extension.
- Evidence remains B for the published physical rows and C for the electrical
  equivalent; no 50 Ω, gain, choke, or conduit claim is added.

## Limitations

- These are NEC-2 model outputs with assumed radii and segmentation, not
  measurements.
- The coax shield, dielectric, conduit body, choke, and feedline are not
  canonical geometry; the ideal-choke limitation remains.
- The published VSWR behaviour is used only as a qualitative band target.
- A measured build is still required before claiming a validated match or
  pattern.
