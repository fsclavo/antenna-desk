# AntennaDesk roadmap and backlog

**Updated:** 2026-11-05
**Status:** active roadmap after catalog, measurement, optimization, and
packaging work.

## Product direction

AntennaDesk is a design and experimentation tool for radio amateurs, not a
catalog of reference-approved antennas. The solver must remain trustworthy, but
users must be able to create, modify, and simulate geometries that have never
been built and therefore have no external reference.

Validation therefore applies at two different levels:

1. **Solver validation:** the NEC adapter and normalization must match
   independent references. This remains strict.
2. **Template/generator validation:** a template is not blocked because no
   independent result exists. It must be labeled with its evidence level and
   must not claim more accuracy than it has.

## Evidence levels

| Level | Meaning | Required evidence |
|---|---|---|
| A. Reference-backed | Compared with an independent source | Traceable source, metric, tolerance |
| B. Published or heuristic | Based on a published design rule or starting point | Source or documented heuristic |
| C. Experimental | Arbitrary geometry or unverified generator | Structural tests and visible warning |

A 10% tolerance is acceptable for many dimension/heuristic comparisons. It is
not a universal rule for gain, nulls, or impedance; each metric keeps its own
tolerance.

## Current state

Completed:

- Solver adapter, normalized results, persistence, imports, and reports.
- Guided dipole, folded dipole, trap dipole, T2FD, loop (generic, delta, quad,
  and horizontal/sky), vertical (1/4λ, 1/2λ, and 5/8λ with radials, plus a
  loading-coil option, radial-system presets, and a mobile-whip preset),
  inverted-V, inverted-L, fan
  dipole, end-fed, sloper, random wire, doublet, OCFD, J Pole, Slim Jim, Ringo,
  Yagi, Moxon, and custom-wire designs.
- Series/parallel RLC loads and traps; L/Pi/T matching networks with component
  Q/loss; uniform feed-line post-processing.
- Frequency-first dimension estimation for the families with a documented
  estimator, with source identifiers, confidence, assumptions, warnings, and a
  loop polygon correction calibrated with NEC-2. The trap dipole and T2FD use
  starting-dimension helpers in their editors instead.
- Single-dimension and multi-element optimization, target impedance, gain,
  front-to-back, efficiency, weighted multi-objective search, Pareto ranks, and
  integer variables.
- Yagi element-count optimization: trailing directors are added from the
  DL6WU reference or removed, with the driven element preserved.
- End-fed counterpoise geometry and an ideal feed transformer ratio, with
  estimator starting values.
- VNA CSV import, measurement conditions/reference plane, measured/simulated
  comparison, resonance differences, and project measurement records.
- Construction sheets, CSV/HTML/PDF reports, PNG/SVG/DXF exports, and
  project-level Undo/Redo with chart cursors.
- Wheel/sdist packaging, packaging CI, application icon, and Linux desktop
  entry.
- Native Linux AppImage, Debian package, and Windows bundle recipes with
  bundled `nec2c`, checksums, and a tag-triggered release workflow.
- Reference anchors for NEC examples, selected ARRL dipole/folded/loop
  properties, the published Cebik 20 m wire Moxon, and the NBS Yagi preset.
- Directivity and realized gain separated from NEC power gain, with a two-port
  feed-line/matching-network cascade and reported mismatch, line, and network
  losses.
- Transmission lines as geometry: NEC `TL` two-ports between wire points,
  persisted in the model, drawn as dashed construction lines, and editable from
  the design panel.
- G5RV catalog preset with the published 102 ft dipole and a 300 Ω / 450 Ω
  geometry matching line.
- ZS6BKW catalog preset with the Cebik/W4RNL reference dimensions and the
  common 450 Ω commercial variant, using a lossless geometry matching line.
- Zepp catalog preset with a real two-wire quarter-wave matching stub, an
  explicit 1:1 choke requirement, and an odd-harmonic analysis plan; labeled
  with published starting dimensions.
- Per-band multiband analysis for G5RV, OCFD, end-fed presets, fan dipole, trap
  dipole, T2FD, and doublet, with a Bands results tab and band-aware reports.
  The Pattern frequency selector lists all analyzed bands, and each band uses
  the global pattern-frequency policy.
- Global **Simulation sweep** in Advanced simulation: Auto (template) or a
  custom Start/Stop/Points override for every antenna family.
- Optional ideal OCFD feed transformer (4:1 default for new designs), preserved
  through custom-wire conversion and usable by the synthesis dialog.
- Fan dipole Simulate now covers every distinct element band automatically and
  surfaces the V-angle/coupling tuning warning. Its element optimizer has a
  synchronized band selector, per-element band labels, mismatch warning,
  lowest-element-band default, and target-frequency segmentation.
- T2FD catalog preset with a broadband series termination, an ideal feed
  transformer, and Cebik wide-long starting dimensions.
- `v0.1.0` published with wheel/sdist, AppImage, Debian package, Windows zip,
  and SHA-256 checksums. Signing is optional and deferred.
- `v0.2.0` adds inverted-L and horizontal/sky-loop generators, schema 10,
  the soil presets, asynchronous project saves, and the band-analysis UI.

Deferred:

- Live VNA/hardware control.
- Additional full-wave engines.
- Physical antenna validation until measurements are available.

## Milestones

### M1 — Parametric Yagi generator (completed)

- Element table: position along boom, total length, radius.
- Add/remove elements and arbitrary driven-element index.
- NBS 0.8λ five-element starting preset.
- Generate a first-class editable Yagi design.
- Structural tests plus a reference-backed NEC check for the NBS preset.
- UI: Yagi entry in the **New Antenna** catalog with an inline element editor.

### M2 — Inverted-V generator (completed)

- Apex height, included angle, leg length, azimuth, wire radius, ground.
- Free-space and ground simulations.
- Structural and scaling tests; reference only when a primary numeric source is
  available.

### M3 — Catalog expansion (completed)

- Delta loop and quad presets.
- Moxon rectangle.
- Off-center-fed dipole and fan dipole.
- Vertical with radial ground-screen options.
- End-fed wire, J Pole, Slim Jim, and Ringo.
- Each entry records its evidence level and limitations.

### M4 — Advanced design and measurement (completed)

- Multi-element optimization and constrained geometry, including Yagi,
  fan-dipole, Moxon, vertical, inverted-V, Ringo, and loop variables.
- Weighted multi-objective search with Pareto ranks and candidate selection.
- Integer variables for radial count, loop side count, and Ringo ring sides.
- Yagi element count as a discrete search variable, with reference-based
  director addition and driven-element preservation.
- VNA CSV import and measured/simulated SWR, R, X, and |Z| comparison.
- Measurement conditions and reference-plane metadata.
- Bounded impedance synthesis for OCFD, J Pole, and Slim Jim.

### M5 — Release hardening (completed)

- Linux AppImage, Debian `.deb`, and Windows onedir bundle recipes (completed).
- Bundle `nec2c` next to the frozen executable (completed).
- Install the icon and desktop entry in the AppImage; embed the Windows icon
  (completed).
- Tag-triggered release workflow with wheel/sdist, AppImage, Debian package,
  Windows zip, and checksums (completed).
- Optional GPG detached signatures and Windows Authenticode signing hooks
  (completed, deferred for the initial release).
- Published `v0.1.0` and `v0.2.0` with unsigned, SHA-256-verified artifacts
  (completed).
- Keep the wheel/sdist smoke test as the fallback distribution path
  (completed).

### M6 — Multiband analysis (core implemented)

Goal: let naturally multiband antennas be analyzed over a user-selected band
set without pretending that every family is broadband. The detailed plan is in
[`docs/MULTIBAND_ANALYSIS_PLAN.md`](MULTIBAND_ANALYSIS_PLAN.md).

Scope:

- Band catalog and validated band selections, reusing
  `domain/simulation/bands.py`.
- Per-family defaults for G5RV, OCFD, end-fed/random wire/sloper, fan dipole,
  trap dipole, T2FD, and doublet, with evidence and limitation notes. The
  doublet default is inferred from a high-impedance/open-wire project feed line.
- A batch analysis service that runs the existing single-band solver once per
  selected band, with progress, cancellation, partial results, and the global
  pattern-frequency policy applied inside each band.
- **Analyze Bands...** UI integrated with the central **Band analysis** group
  and global **Simulation pattern** settings, plus a band selection dialog and
  a **Bands** results tab showing best SWR, gain, takeoff angle, efficiency,
  and status. The top action bar stays Apply/Estimate/Optimize.
- Band/batch metadata on simulation runs, schema version 4 migration (extended
  by version 5 with OCFD/custom transformer fields, version 6 with persisted
  analysis band plans, version 7 with Yagi/Moxon polarization, version 8 with
  vertical top-hat fields, version 9 with the inverted-L design type, and
  version 10 with loop orientation), and band-aware CSV, HTML, PDF, and
  comparison summaries.
- Deferred: a segmented frequency plan in one NEC deck, only if measurements
  show that per-band runs are too slow or too large.

Acceptance criteria:

- Selecting 40/20/10 m for an OCFD runs three band analyses and presents three
  inspectable results.
- G5RV keeps its continuous "All HF" option and also supports a band list.
- The centralized action bar and global **Simulation pattern** group remain
  intact; band selection does not add per-form controls.
- Single-band Simulate remains unchanged.
- Save/open, reports, and undo/redo preserve the band analysis.
- No default claims resonance without documented evidence.

## Backlog

| Priority | Item | Evidence | Status |
|---|---|---|---|
| P1 | Independent references for remaining experimental templates | A/B | partial: `delta_loop`, `vertical`, `loaded_vertical` (published preset), `inverted_v`, `j_pole`, `slim_jim`, `endfed`, `trap_dipole`, `sloper`, `doublet`, and `zepp` promoted to B. The inverted-L was added as C on 2026-11-06. The other four C templates were reviewed the same day; the Ringo now has a Cushcraft AR-6 starting-dimensions preset, but promotion needs a matching-ring model; see [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| P1 | Fan dipole V-angle calibration and angle optimization | B | investigated; angle optimizer deferred |
| P1 | Optional ideal transformer/4:1 balun for OCFD | B | done |
| P1 | Multiband batch engine and per-family band defaults (M6) | B | done |
| P1 | Band selection UI and band summary results (M6) | B | done |
| P2 | Persist band-analysis batches and band-aware reports (M6) | B | done |
| P2 | Cross-band comparison table | B | done |
| P2 | GPG/Authenticode code signing for release artifacts | n/a | deferred |
| P2 | Evaluate PySide6 6.11.3 against the deliberate pin | n/a | done 2026-11-05: 6.11.3 evaluated with shutdown stress (ADR-0025); 6.12 remains excluded |
| P2 | Relative permeability export to NEC | B | not supported by NEC-2; warning implemented |
| P2 | Pattern metric selector for power/directivity/realized gain | B | done |
| P2 | ZS6BKW and Zepp multiband presets | B | done |
| P2 | Custom/imported geometry optimization and space constraints | n/a | pending |
| P2 | Live VNA/hardware control | n/a | deferred |
| P2 | Additional full-wave engines | n/a | deferred |
| P2 | Physical antenna validation | A | blocked: no measurements |
| P3 | Segmented frequency plan in one NEC deck | B | deferred; benchmark keeps per-band |

### Antenna backlog

Ordered expansion backlog proposed on 2026-11-06. Effort assumes one
experienced developer; validation is the realistic ceiling for the current
canonical wire model, not a promise. `A` requires an exact published geometry
with an independent numeric metric; `B` requires a published rule or starting
point; `C` is structural/experimental only.

| Order | Candidate | Type | Effort | Value | Validation | Notes |
|---:|---|---|---|---|---|---|
| 1 | Inverted L | New family | M | High | C (B/A possible) | **Implemented on 2026-11-06:** first-class family with an editor, catalog route, persistence, geometry, reports, and tests. It remains experimental and has no estimator until a published reference is added. |
| 2 | Horizontal loop / sky loop | Modification of `loop` | S–M | High | B/A | **Implemented on 2026-11-06:** the loop editor now selects vertical or horizontal orientation, with schema 10 persistence, plan/elevation scene handling, and dimension/report tests. |
| 3 | Elevated radials / ground screen | Modification of `vertical` | S–M | High | B/A | **Implemented on 2026-11-06:** the vertical editor has no-radial, ground-radial, elevated-radial, and dense ground-screen starting presets over the existing radial fields. The screen is a dense radial approximation, not a bonded mesh. |
| 4 | Magnetic loop | New family | L | High | B/C; A only with an exact published design | Needs gap, tuning capacitor, ESR/loss, efficiency, bandwidth, and matching. Not a variant of the full-wave loop. |
| 5 | Yagi folded driven element | Modification of `yagi` | M | Medium | B/A | Two wires plus connectors; changes feed impedance and matching. |
| 6 | Gamma / beta / hairpin match | Modification of `yagi` | M | Medium | B/A | Geometry and feed hardware; may coexist with the matching-network dialog. |
| 7 | Balun/unun with losses | Cross-cutting model | M | High | B/C | Frequency-dependent loss model; improves EFHW, OCFD, G5RV, and T2FD. |
| 8 | Capacity hat / top-loaded vertical | Modification of `vertical` | M | High | B/A | Short verticals on low bands; needs hat geometry and possibly loading. |
| 9 | Explicit EFHW presets for the existing EndFed + OCFD/G5RV variants | Presets/UX, not a new family | S | Medium–high | A/B | `EndFedParameters` with `EndFedPreset.STANDARD` already models an EFHW using a half-wave wire and 49:1 transformer. The work is naming clarity plus published 40/20/10 m presets and an optional band plan; OCFD/G5RV variants remain presets. Quick win; can be advanced ahead of the sequence if needed. |
| 10 | Half-square / bobtail curtain | New family | M | Medium | B/A | Multi-wire geometry and feed; published designs exist. |
| 11 | Biquad / double biquad | New family | M | Medium | B/A | Two loops and reflector; needs a scene contract and tests. |
| 12 | Beverage | New family | M | Medium | B/A | Receiving antenna; termination, ground, and long-wire geometry. |
| 13 | Loaded / linked dipole | New family or `dipole` variant | M | Medium | B/C | Portable/SOTA use; existing load model helps, but coil Q and links need care. |
| 14 | Wire sag / tapered elements / boom correction | Geometry model | M | Medium | B/C | Realism for Yagi and wire antennas; touches geometry and solver inputs. |
| 15 | Phased verticals / arrays | Architectural | XL | High | B/A | Requires multiple sources, phase, and feed networks; not a simple family. |
| 16 | Quad beam / hexbeam | New family | L | Medium–high | B/A | Multi-element loop geometry; feed and scene complexity. |
| 17 | Log-periodic | New family | L | Medium | A/B | Many elements and a feed network; high test burden. |
| 18 | Discone | New family | L | Medium | B/C | Many wires and broadband behavior; niche VHF/UHF value. |
| 19 | Trapped / multiband Yagi | New family | L | High | B/C | Traps and multiple elements; difficult independent validation. |

Items 1–7 are the immediate recommended sequence. Items 8–14 are the next
medium-sized candidates; items 15–19 are large or architectural and should not
start until the single-feed families and the shared geometry/load model are
stable.

EFHW is deliberately **not** listed as a new family: the standard `EndFed`
template already models it. Item 9 covers explicit EFHW presets, labels, and
band planning for that existing family.

## Next

Detailed pending-work plan:
[`docs/PENDING_WORK_PLAN.md`](PENDING_WORK_PLAN.md).

Modeling track:

1. Completed on 2026-11-05: refined Zepp matching-section geometry with a real
   second conductor and an explicit 1:1 choke requirement. The choke remains a
   construction note because NEC-2 cannot model it.

Release track:

1. `v0.2.0` is published with checksum-verified unsigned artifacts.
2. Add GPG/Authenticode signing in a later release if required.

Validation track:

1. Independent references for remaining experimental templates. The reference
   passes promoted `delta_loop`, `vertical`, `inverted_v`, `j_pole`,
   `slim_jim`, `endfed`, `trap_dipole`, `sloper`, `doublet`, and `zepp` to
   level B; the remaining level C templates and their next evidence needs are
   listed in [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md).
2. Physical measurements when the project owner has data.

## Definition of done for a generator

- Domain generator is independent of Qt and the solver.
- Geometry invariants and feed connectivity are tested.
- Scaling with frequency is tested.
- Presets identify their source or heuristic.
- Experimental generators show a visible limitation/warning.
- A reference test is added when a traceable numeric oracle exists.
- Documentation and changelog are updated.
