# AntennaDesk roadmap and backlog

**Updated:** 2026-11-24
**Status:** active product roadmap after catalog, measurement, optimization,
packaging, the 2026-11-11 product-experience review, and the 2026-11-19
trust/station review.
**Scope:** product direction, milestones, the ordered antenna expansion
backlog, and the 1.0 trust/1.1 station/1.2 site tracks. The active execution
queue is
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md); evidence status is in
[`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md).

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

**Latest published release:** `0.10.1` (2026-11-24). The 1.0 Confidence wave is
complete; 1.1 Station is done as narrowed (DL1/DL2 done, DL5 narrowed), and
1.2 has partial DL3/DL6 work and a bounded DL7 implementation. DL4 is canceled.
See [`STATUS.md`](STATUS.md)
and the [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md).

Completed:

- Solver adapter, normalized results, persistence, imports, and reports.
- Guided dipole, folded dipole, trap dipole, T2FD, loop (generic, delta, quad,
  horizontal/sky, and magnetic), vertical (1/4λ, 1/2λ, and 5/8λ with radials,
  plus a loading-coil option, radial-system presets, and a mobile-whip preset),
  inverted-V, inverted-L, fan
  dipole, end-fed, sloper, random wire, doublet, OCFD, J Pole, Slim Jim, Ringo,
  Yagi, Moxon, and custom-wire designs.
- Series/parallel RLC loads and traps; L/Pi/T matching networks with component
  Q/loss; uniform feed-line post-processing.
- Frequency-first dimension estimation for the families with a documented
  estimator, with source identifiers, confidence, assumptions, warnings, and a
  loop polygon correction calibrated with NEC-2. The trap dipole and T2FD use
  starting-dimension helpers in their editors instead.
- Family-specific optimization descriptors with a joint deterministic hybrid
  engine, target impedance, gain, front-to-back, efficiency, bandwidth, and
  weighted multi-objective scores, all typed geometry/feed/load variables,
  explicit unavailable reasons, and no generic fallback.
- Yagi element optimization: every element length, every inter-element gap,
  height, folded spacing when enabled, and beta/hairpin dimensions when
  selected are searched together; the element count and polarization stay
  fixed.
- End-fed counterpoise geometry and an ideal feed transformer ratio, with
  estimator starting values.
- VNA CSV and one-port Touchstone import, simulated Touchstone export,
  measurement conditions/reference plane, measured/simulated comparison,
  resonance differences, and project measurement records.
- Construction sheets, CSV/HTML/PDF reports, PNG/SVG/DXF exports, and
  project-level Undo/Redo with chart cursors.
- Construction view and wire schedule: family-aware front/top/auxiliary views,
  dimension-anchor checks, an embedded multi-view sheet with a dimensioned
  construction view, a complementary orthographic view, and an isometric view;
  title block and BOM, wire and BOM CSV exports, evidence/limitation rows, and
  localized HTML/PDF reports with vector construction figures and report charts,
  plus localized diagnostic messages and evidence text.
- Basic dipole, folded dipole, and loop templates open their full variable
  editor directly; the old multi-page wizard is gone.
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
- Global **Simulation sweep** in the Simulation tab: Auto (template) or a
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
- `v0.3.0` adds the construction-view and reporting overhaul, localized
  sheets/reports with vector PDF figures and multi-view grids, direct basic
  antenna editors, the expanded family catalog through schema 31, and shortened
  loaded EFHW presets.
- `v0.3.1` fixes cross-platform construction-label overlap and large-font form
  widths on Windows.
- `v0.4.0` adds the matching-network precedence/design target, Feed & matching
  visibility, impedance-point network creation, and the optional shortened-EFHW
  inverted-L bend (schema 34–35). It is published with unsigned,
  checksum-verified artifacts; the Windows bundle was built and smoke-tested in
  CI.
- `v0.4.1` adds the Windows NSIS installer and updates the author credit. It is
  published with unsigned, checksum-verified artifacts and keeps the portable
  Windows zip and all previous Linux and Python artifacts.
- `v0.4.2` hides `nec2c` console windows during Windows simulations and
  optimizations, and generates wheel/sdist checksums automatically in the
  release workflow. It is published with unsigned, checksum-verified artifacts.
- `v0.5.0` adds folded-dipole, full-wave loop, and Yagi folded-driven feed
  transformer defaults; the project current-balun record; side-by-side
  azimuth/elevation pattern cuts; metric-aware pattern views; and the
  accumulated project, measurement, construction, and workflow work through
  schema 44. It is published with unsigned, checksum-verified artifacts.
- `v0.6.0` adds the source-backed materials reference, the 16-cable coax catalog
  with feed-line presets, portable project bundles, editable BOM costs (schema
  45), and the Moxon/Yagi catalog starting frequencies. It is published with
  unsigned, checksum-verified artifacts.

Deferred:

- Live VNA/hardware control.
- Additional full-wave engines. A future review of **momwire** as an optional
  high-fidelity engine is deferred; start it only with the owner's explicit
  approval. The review must cover release maturity, Linux/Windows packaging,
  independent validation, and parity with the reference cases before any
  integration work.
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

- Family optimizer redesign completed 2026-11-07 (see ADR-0026): explicit
  descriptor per typed family, joint differential-evolution plus local search,
  all geometry/feed/family-load variables, Fast/Balanced/Thorough budgets with
  automatic extension, deterministic seeds, hard/soft constraints, sensitivity,
  and an exhaustive Apply Best adapter. Phase C adds band-aware and robust
  modes, a descriptive Pareto front, deterministic recommendations, and
  schema-18 persisted run summaries.
- Supported typed families: dipoles, loop, vertical/inverted-V/inverted-L,
  J Pole/Slim Jim, Ringo, SCV, biquad, Beverage, loaded/linked dipole,
  phased vertical array, quad beam, discone, trapped Yagi, hexbeam, OCFD,
  EndFed, typed G5RV/ZS6BKW/Zepp,
  fan/trap/T2FD, Yagi, and Moxon. The doublet radiator uses the dipole
  descriptor and its feed line remains in the matching stage.
- Explicitly unavailable optimizers: magnetic loop, random wire, and arbitrary
  custom/imported geometry.
- Yagi element lengths and boom gaps are bounded variables; the element count,
  polarization, folded/match topology, and driven index remain user choices.
- VNA CSV and one-port Touchstone import, simulated Touchstone export, and
  measured/simulated SWR, R, X, and |Z| comparison.
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
- Published `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.3.1`, `v0.4.0`, `v0.4.1`,
  `v0.4.2`, `v0.5.0`, `v0.6.0`, `v0.7.0`, `v0.7.1`, `v0.8.0`, `v0.8.1`,
  `v0.8.2`, and `v0.9.0` with unsigned, SHA-256-verified artifacts
  (completed).
- Keep the wheel/sdist smoke test as the fallback distribution path
  (completed).

### M6 — Multiband analysis (core implemented)

Goal: let naturally multiband antennas be analyzed over a user-selected band
set without pretending that every family is broadband. The detailed plan is in
[`docs/archive/plans/MULTIBAND_ANALYSIS_PLAN.md`](archive/plans/MULTIBAND_ANALYSIS_PLAN.md).

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
  version 10 with loop orientation, version 11 with the magnetic-loop design
  type, version 12 with the folded Yagi driven element, version 13 with the
  beta/hairpin Yagi match, version 14 with the balun/unun loss model, and
  version 15 with the Yagi matching-hardware repair), and band-aware CSV, HTML,
  PDF, and comparison summaries.
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

## Product backlog

This table keeps product priority and evidence. Execution status, blockers, and
acceptance criteria live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). The 2026-11-11
product-experience review shifts the emphasis from catalog breadth to the
decide-build-measure workflow; the new track is below.

| Priority | Item | Evidence | Status |
|---|---|---|---|
| P0 | 1.0 trust, 1.1 station, and 1.2 site track (TS1–TS7, DL1–DL9; DL8 post-1.2) | B/C | wave 0 done 2026-11-19; 1.1 done as narrowed (DL1/DL2 done, DL5 narrowed); 1.2 partial (DL3/DL6, DL7 implemented bounded; DL4 canceled); see [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md#product-trust-and-station-wave) |
| P1 | Independent references for remaining experimental templates | A/B | partial: `delta_loop`, `vertical`, `loaded_vertical` (published preset), `inverted_v`, `j_pole`, `slim_jim`, `endfed`, `trap_dipole`, `sloper`, `doublet`, `zepp`, `biquad`, and `beverage` promoted to B for starting dimensions. Inverted L, Ringo, double biquad, and loaded dipole remain C; see [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| P1 | Fan dipole V-angle calibration and angle optimization | B | investigated; lengths and angles are now searched jointly by the family optimizer, but the calibration warning remains |
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
| P2 | Convert G5RV, ZS6BKW, Zepp, and doublet to typed families and add optimizers | B | done 2026-11-07: G5RV/ZS6BKW/Zepp typed with schema 17; doublet was already a typed dipole plus feed line |
| P2 | Band-aware, robust, Pareto, persisted summaries, and recommendations | B | done 2026-11-07 (Phase C, schema 18) |
| P2 | Custom/imported geometry optimization and space constraints | n/a | space constraints done 2026-11-07 (turning radius for all families, boom length for Yagi/Moxon); custom/imported geometry optimization remains deliberately unavailable |
| P2 | Live VNA/hardware control | n/a | deferred |
| P2 | Additional full-wave engines | n/a | deferred |
| P2 | Physical antenna validation | A | blocked: no measurements |
| P3 | Segmented frequency plan in one NEC deck | B | deferred; benchmark keeps per-band |
| P3 | Full terrain model (DL8) | B/C | blocked on DL7 and a validated terrain ADR |

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
| 3 | Elevated radials / ground screen | Modification of `vertical` | S–M | High | B/A | **Implemented on 2026-11-06; uniform droop added 2026-11-24:** the vertical editor has no-radial, ground-radial, elevated-radial, and dense ground-screen starting presets over the existing radial fields, plus one uniform downward droop with physical radial length. The screen remains a dense radial approximation, not a bonded mesh; no performance claim. See ADR-0052. |
| 4 | Magnetic loop | New family | L | High | B/C; A only with an exact published design | **Implemented on 2026-11-07:** first-class tuned small loop with a top gap, ideal series capacitor and ESR, conductor-loss simulation, efficiency reporting, SWR-bandwidth reporting, and a dedicated editor. A coupling loop and detailed capacitor loss model remain limitations. |
| 5 | Yagi folded driven element | Modification of `yagi` | M | Medium | B/A | **Implemented on 2026-11-07:** optional two-conductor folded driven element with end connectors and adjustable spacing. The published NBS preset can be loaded with the folded element; feed impedance remains a tuning result, not a reference value. |
| 6 | Gamma / beta / hairpin match | Modification of `yagi` | M | Medium | B/A | **Partially implemented on 2026-11-07:** beta/hairpin geometry with a split driven element, shorted stub, and adjustable length/spacing. Gamma is deliberately deferred because NEC-2 close-spaced gamma assemblies are unreliable; use the matching-network dialog for an equivalent. |
| 7 | Balun/unun with losses | Cross-cutting model | M | High | B/C | **Implemented on 2026-11-07:** project-level matched insertion loss with a power-law frequency fit. It reduces realized gain and is reported per frequency; it does not alter geometry, impedance, or SWR. Apply it to EFHW, OCFD, G5RV, T2FD, or any other design. |
| 8 | Capacity hat / top-loaded vertical | Modification of `vertical` | M | High | B/A | **Implemented:** the vertical template already has a capacitive top hat and loading coil. Reports, construction sheet, and scene summary now expose the hat geometry, with a dedicated scene contract case. The hat remains an application starting point, not an independently validated loading design. |
| 9 | Explicit EFHW presets for the existing EndFed + OCFD/G5RV variants | Presets/UX, not a new family | S | Medium–high | A/B | **Implemented on 2026-11-07:** the EndFed editor is labeled EFHW, exposes 40/20/10 m preset buttons using the published 66/33/16 ft lengths and 49:1 transformer, and keeps the existing harmonic band plan. OCFD/G5RV variants remain presets. |
| 10 | Half-square / bobtail curtain | New family | M | Medium | B/A | **Implemented on 2026-11-07:** one self-contained vertical-array family with half-square and bobtail-curtain variants, top-junction feed with adjustable offset, schema-16 persistence, catalog routes, editor, geometry dimensions, reports, and construction sheet. The Cebik 7.15 MHz dimensions are the published starting point; pattern, ground, and matching remain unvalidated and there is no frequency-first estimator. |
| 11 | Biquad / double biquad | New family | M | Medium | B/C | **Implemented on 2026-11-07:** two- or four-loop stack with shared rails, optional wire reflector, quarter-wave starting dimensions, inline editor, schema 19, scene contract, reports, and family optimizer. The biquad starting dimensions are published (B); the double biquad remains C because the published side-by-side topology differs from the vertical stack. |
| 12 | Beverage | New family | M | Medium | B/C | **Implemented on 2026-11-07:** long receiving wire with optional resistive termination, one-wavelength starting length, inline editor, schema 20, scene contract, reports, construction notes, and family optimizer. **Updated 2026-11-19:** ground-referenced feed/termination stubs, ideal feed transformer (default 9:1), optimizer ratio variable, and schema 56. The one-wavelength length and 500 Ω termination are published (B); the 9:1 ratio is a practical matching assumption; gain, pattern, and termination efficiency remain unvalidated. |
| 13 | Loaded / linked dipole | New family or `dipole` variant | M | Medium | B/C | **Implemented on 2026-11-07:** center-fed loaded dipole with symmetric series R-L coils or open links, schema 21, inline editor, scene contract, reports, construction notes, and family optimizer. B3 reviewed the published 3.91 MHz BVARC example; the template remains C because the source ground model is unspecified. Coil core loss, self-capacitance, and link contact resistance remain limitations. |
| 14 | Wire sag / tapered elements / boom correction | Geometry model | M | Medium | B/C | **Partially implemented 2026-11-07:** optional sampled parabolic sag on horizontal wire dipoles (schema 22) and optional tapered Yagi tips (schema 23), with scene/report/conductor-length support. Boom-mounting correction remains pending because no universal published model is available. |
| 15 | Phased verticals / arrays | Architectural | XL | High | B/A | **Implemented on 2026-11-08:** multi-source excitation, ideal linear phase and amplitude progression, 2–4 verticals with radial screens, schema 25, inline editor, scene/source markers, reports, construction notes, and family optimizer. The combining network is ideal and the family remains experimental pending a traceable array reference or measurement. |
| 16 | Quad beam / hexbeam | New family | L | Medium–high | B/A | **Implemented on 2026-11-08:** quad beam with 2–3 square loops and a separate single-band hexbeam with published G3TXQ dimensions, schema 26 and 30, editors, scene contracts, reports, construction notes, and family optimizers. The hexbeam reconstructs the bent wire path and is classified published/heuristic; frame and multi-band nesting are not modeled. |
| 17 | Log-periodic | New family | L | Medium | B | **Implemented on 2026-11-16:** straight-element log-periodic dipole array with a transposed phase line, schema 52, catalog route, inline editor, element table, scene contract, reports, construction notes, and NEC2C reference tests. The Cebik 10 m 1.0 in, 75 Ω design reproduces the published NEC-4 gain and front-to-back ratio; the ARRL/Cebik 7 MHz swept-element wire variant remains future work. Evidence is B: published-model comparison, not a measurement. |
| 18 | Discone | New family | L | Medium | B/C | **Implemented on 2026-11-08:** radial-wire cone and top disc with an apex feed gap, schema 27, inline editor, scene contract, reports, construction notes, and family optimizer. The wire approximation and missing coax/mast model keep it experimental. |
| 19 | Trapped / multiband Yagi | New family | L | High | B/C | **Implemented on 2026-11-08:** two-band Yagi with one ideal parallel LC trap pair per element, schema 28, inline editor, scene contract, reports, construction notes, and family optimizer. Trap loss, boom mounting, feed line, and matching remain unvalidated. |
| 20 | Shortened loaded EFHW | EndFed variant | M | Medium | B/C | **Implemented on 2026-11-09, matching model extended 2026-11-10, inverted-L option 2026-11-11:** 80-10 m (20.35 m + 110 µH + 2.39 m) and 40-20-10 m (10.01 m + 23 µH + 1.85 m) presets with a 49:1 transformer, editable series coil, schema 33 for the matching values, schema 34 for the project design target, and schema 35 for the optional inverted-L bend, catalog entries, band plans, reports, construction notes, and optimizer variables. The optional primary 100 pF shunt and 0.198 µH leakage estimate are modeled; an optional measured 49:1 loss table from Squash Practice/AF7NX is available, and the bend uses a sharp 90° corner with an 8 m vertical starting section and no independent validation. An optional feedpoint common-mode choke accepts measured series R/X on the coax shield (ADR-0037), and an optional design-specific L-network can replace the fixed internal match (ADR-0038); shack-end choke placement, shield transfer impedance, ground, capacitor ESR, and winding capacitance are not modeled. Edited or scaled geometry is experimental. |

### HexBeam follow-ups (C6/C7 implemented 2026-11-18)

These extend an existing family; they are not new antenna families. The
single-band HexBeam in item 16 was corrected on 2026-11-18, and the multi-band
version is implemented.

- **HexBeam geometry correctness (M) — implemented 2026-11-18.** The
  single-band G3TXQ broadband wire path now follows the six-spreader frame:
  M-shaped driver across the front, U-shaped reflector around the rear three
  sides, and 24 in tip spacers near the lateral vertices, on the hexagon sides.
  Every wire point stays at or inside the 130 in turning radius; the overall
  span is the 6.60 m frame diameter, not a tip-derived 9.03 m. The drawn tip gap
  is the published 0.61 m, the reflector midpoint is at the rear, and the model
  has ten canonical wires. Semantic geometry, scene, adaptive-unit, optimizer,
  report, and persistence tests cover the corrected path. No schema or solver
  change. See [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md) and
  [`spikes/c6-hexbeam-geometry.md`](spikes/c6-hexbeam-geometry.md).
- **Multi-band HexBeam, 1-5 bands (L) — implemented 2026-11-18.**
  One shared six-spreader frame carries nested driver/reflector pairs from the
  published G3TXQ 20/17/15/12/10 m table, with the 20 m row reconciled to
  218/412. The editor selects the band set and shows a read-only per-band
  table; the scene draws every band with the primary band emphasized, and
  reports include per-band rows. Each analysis excites one selected band while
  the other bands remain passive; a real NEC2C run completed for 20, 15, and
  10 m. Coax jumpers, inter-band coupling, the balun, spreader sag, and frame
  hardware remain unmodeled. Full multi-band optimization and automatic
  frequency scaling are explicitly unavailable.
  6 m can be added later as an optional sixth band. The published dimensions are
  starting values (B); multi-band gain, SWR, and front-to-back ratio are not
  validated.

Optional HexBeam follow-ups are queued in the execution backlog: **C7h** 6 m
band and **C7i** feed-harness/inter-band coupling (blocked on a traceable model
or measurement). **C7d** selected-band optimization is implemented: the active
band's driver and reflector halves, tip gap, and height are optimized while the
shared frame and the other bands stay fixed; full-stack optimization remains
unavailable. **C7e** active-band dimensions/highlight is implemented: the scene
dimensions and feed marker follow a transient band selector while the other
bands remain visible. **C7f** editable band rows/custom sets are implemented:
published checkboxes seed the table, rows can be added or removed, custom
labels and frequencies are marked as custom, and replacing them with a
published preset requires confirmation.
**C7g** band-aware starting-set scaling is implemented: the primary-frequency
field can uniformly scale the selected published stack within its primary band,
with a reference-scaled warning. A general multiband frequency-first estimator
is not recommended; the published rows are band-specific.

Items 1–7 were the immediate recommended sequence; items 8–14 are the next
medium-sized candidates, with 8–13 done and 14 partially done. Items 15–19 are
large or architectural and should not start until the single-feed families and
the shared geometry/load model are stable. Item 20 is an implemented EndFed
variant and does not change that rule.

EFHW is deliberately **not** listed as a new family: the standard `EndFed`
template already models it. Item 9 covers explicit EFHW presets, labels, and
band planning for that existing family.

### Product experience backlog (proposed 2026-11-11)

The 2026-11-11 review of the desired-backlog proposal keeps the product focus on
the decision-to-measurement workflow instead of adding more antenna families.
The catalog is broad enough; the next value is helping the operator choose,
understand, build, and improve a design. This is product scope, not a second
execution queue. UX1–UX17 are complete. The 0.5 **Decide**, 0.6 **Build**, 0.7
**Measure**, and 0.8 **Explore** releases are closed, and the 0.9 **Sustain**
slice is complete. UX18–UX31 are implemented. UX32–UX38 were completed on
2026-11-17. The UX queue is closed. The adaptive length display-units track
(U1–U6) is complete, including the manual desktop light/dark and font-scaling
QA on 2026-11-24; the release plan decides whether it lands in 0.10.0 or a later
release.

Rules for this track:

- Every item must remove a decision or a manual step. A calculator alone is not
  enough.
- No new electromagnetic model without a traceable source or measurement. Items
  that cannot be validated are labeled experimental and show their limits.
- Progressive disclosure: Guided, Standard, and Advanced modes; no new dialog
  for every option.
- Local-first: no accounts, servers, or telemetry.
- Pause new antenna families. The existing catalog covers the common cases;
  the log-periodic straight-element family is implemented, and its optional
  7 MHz swept-element variant is the only remaining C3 follow-up.
- Each release leaves the full gate green and is usable on its own.

| Release | ID | Item | Outcome | Size | Evidence | Status |
|---|---|---|---|---|---|---|
| 0.5 Decide | UX1 | Guided mode and next-step coach | State-driven next action and progressive disclosure | S–M | n/a | done 2026-11-11 |
| 0.5 Decide | UX2 | Installation profile | Reusable site envelope and constraints | S–M | n/a | done 2026-11-11 |
| 0.5 Decide | UX3 | Antenna suitability profiles and guided advisor | Constraint-filtered shortlist with operating intent and trade-offs | M | B/C | done 2026-11-11 |
| 0.5 Decide | UX4 | Comparison 2.0 | 2–4 designs under a common basis, recomputed | M–L | B | done 2026-11-11 |
| 0.5 Decide | UX5 | Contextual explanations and confidence card | Metric meaning, evidence, assumptions, and limits | M | A/B/C | done 2026-11-11 |
| 0.6 Build | UX6 | Feed-chain topology and loss budget | Tuner/balun position and per-stage loss | M–L | B/C | done 2026-11-11 |
| 0.6 Build | UX7 | Construction package 2.0 | As-built, hardware BOM, coil/trap sheet, checklist | M | B/C | done 2026-11-11 |
| 0.6 Build | UX8 | Integrated coil/trap/loading calculators | Prefilled calculators that apply to the design | M | B | done 2026-11-11 |
| 0.6 Build | UX9 | Construction pre-flight checks | Detect geometry, feed, segmentation, and support issues | S–M | n/a | done 2026-11-12 |
| 0.7 Measure | UX10 | Measurement sessions and timeline | Multi-session records and before/after comparison | M | A/B | done 2026-11-12 |
| 0.7 Measure | UX11 | Sensitivity-based tuning assistant | Bounded adjustment from solver sensitivity | M–L | B/C | done 2026-11-12 |
| 0.7 Measure | UX12 | Measurement uncertainty card | Calibration, reference-plane, and environment limits | S–M | B/C | done 2026-11-12 |
| 0.8 Explore | UX13 | Parameter sweeps (what-if) | 1D/2D sweeps with overlays and a budget | M | B | done 2026-11-12 |
| 0.8 Explore | UX14 | Tolerance and robustness analysis | Corner cases and Monte Carlo with critical dimensions | M–L | B/C | done 2026-11-12 |
| 0.8 Explore | UX15 | Project journal | Timeline, as-built, photos, notes, and version comparison | M | n/a | done 2026-11-12 |
| 0.8 Explore | UX16 | Guided experiments | Three tutorials built on the sweep engine | M–L | B | done 2026-11-12 |
| 0.9 Sustain | UX17 | Curated reference design library | 10–20 sourced designs; published versus simulated | M + content | A/B | done 2026-11-12 |
| 0.9 Sustain | UX18 | Minimal materials reference | Source-backed four-tab table with coax feed-line apply | S–M | B | done 2026-11-12 |
| 0.9 Sustain | UX19 | Portable project bundle | ZIP project + assets with safe import | S–M | n/a | done 2026-11-12 |
| 0.9 Sustain | UX20 | Editable BOM costs | Manual cost column and totals | S | n/a | done 2026-11-12 |
| 0.9 Sustain | UX21 | Side-by-side azimuth/elevation pattern cuts | Four-pane Cuts view with independent cuts | M | n/a | done 2026-11-12 |
| 0.9 Sustain | UX22 | Pattern metric visibility | Metric-aware titles and a three-metric summary | S–M | n/a | done 2026-11-12 |
| 0.9 Sustain | UX23 | Common coax catalog and feed-line presets | 16 source-backed cables with a shared feed-line selector | M | B | done 2026-11-12 |
| post-0.9 | UX24 | Retune catalog starting frequencies | Common operating-band defaults with coherent starting geometry | S–M | B | done 2026-11-12 |
| post-0.9 | UX25 | Stainless steel 304 conductor | Source-backed 304 preset and shared material selector | S–M | B | done 2026-11-13 |
| post-0.9 | UX26 | Geometry and pattern in exported reports | Canonical geometry and pattern cuts in HTML/PDF | M–L | B | done 2026-11-13 |
| post-0.9 | UX27 | Spanish ROE terminology | Use ROE consistently in the UI and reports | S–M | n/a | done 2026-11-13 |
| post-0.9 | UX28 | Vertical radiator length terminology | Separate physical radiator length from installation height | S–M | n/a | done 2026-11-13 |
| post-0.9 | UX29 | Constructive feed connection | Read-only feedpoint assembly and schematic | M–L | B | done 2026-11-13 |
| post-0.9 | UX30 | Per-template material defaults | Template-appropriate material preselection | S–M | B | done 2026-11-17 |
| post-0.9 | UX31 | Coax-as-coax feed schematic | Coax cross-section and per-interface drawings | S–M | B | done 2026-11-17 |
| post-0.9 | UX32 | Quad beam frequency-first starting dimensions | Frequency-seeded geometry and explicit reload | S | B | done 2026-11-17 |
| post-0.9 | UX33 | Generalize frequency-first generator seeding | Same starting behavior for four more generators | S–M | B | done 2026-11-17 |
| post-0.9 | UX34 | Design-frequency vs analysis-frequency semantics | [ADR-0043](ADR/0043-design-versus-analysis-frequency.md) and resize policy | S | n/a | done 2026-11-17 |
| post-0.9 | UX35 | Pristine-geometry frequency recalculation | Recalculate untouched geometry; never silently resize tuned designs | M | B | done 2026-11-17 |
| post-0.9 | UX36 | Quad beam frequency-first estimator | Enable **Estimate Dimensions...** for quad beam | M | B | done 2026-11-17 |
| post-0.9 | UX37 | Explicit scale-to-frequency action | Approximate scaling for tuned, allowlisted designs | M–L | B/C | done 2026-11-17 |
| post-0.9 | UX38 | Select the Design tab after creation | Keep the new design visible after New Antenna | S | n/a | done 2026-11-17 |

UX24 was added from direct user feedback after the 0.9 slice closed and was
implemented the same day. It is part of the 0.6.0 release.

### Adaptive length display units (implemented 2026-11-18)

The metric display currently uses meters for every length and millimeters for
wire diameters; imperial uses feet and inches. That is readable for HF but poor
for VHF/UHF construction: a 435 MHz Moxon gap shows `0.007 m`, and its 24.8 cm
width rounds to `0.25 m`. The same problem exists in imperial with `0.023 ft`.

The accepted policy is presentation-only and follows the magnitude, never the
band:

- Metric auto: mm below 1 cm, cm from 1 cm to below 1 m, m at 1 m and above.
- Imperial auto: in below 1 ft, ft at 1 ft and above.
- Scalar fields and dimension labels choose by value; editable and report
  tables choose one unit per table and show it in the header.
- A field or table unit is frozen while editing; it re-evaluates on model,
  preset, optimizer, undo/redo, or preference reload.
- The Units preference keeps an escape hatch: metric auto (default), metric
  fixed in meters, imperial auto (default), and imperial fixed in feet.
- Human-readable construction sheets and reports follow the policy. CSV stays
  canonical meters/mm; DXF stays canonical meters with `$INSUNITS=6` and meter
  dimension text.

Canonical storage, the domain, the solver, and the project schema are
unchanged. The normative rules and examples are in
[`DISPLAY_UNITS_SPEC.md`](DISPLAY_UNITS_SPEC.md); the decision is
[ADR-0044](ADR/0044-adaptive-length-display-units.md).

| Order | Slice | Outcome | Size | Depends on | Status |
|---:|---|---|---|---|---|
| U0 | Spec and ADR | Closed policy, examples, test matrix, and execution slices | S | none | done 2026-11-17 |
| U1 | Shared formatter and Units preference | Pure `DisplayUnits`, automatic/fixed metric and imperial, QSettings, help | S–M | U0 | done 2026-11-17 |
| U2 | Geometry scenes | Dimension labels, summaries, scale bar, insets, layout | M | U1 | done 2026-11-17 |
| U3 | Family forms and editable tables | Per-field ranges/steps, table headers, Moxon/hexbeam range fixes, adaptive Yagi table | M–L | U1 | done 2026-11-18 |
| U4 | Optimization, synthesis, and auxiliary dialogs | Same policy across every length surface | M | U1, U3 | done 2026-11-18 |
| U5 | Construction sheet and human-readable reports | Design summary, wire schedule, BOM, title block, CSV/DXF exception | M–L | U1, U2, U3 | done 2026-11-18 |
| U6 | Documentation, help audit, and visual QA | User guide, changelog, EN/ES help, light/dark/scaling QA | S–M | U2–U5 | done 2026-11-24 |

U1–U6 are complete: the formatter/preference, geometry scenes, every family
editor and editable table, the optimization/synthesis/auxiliary dialogs, the
construction/report surfaces, documentation, EN/ES help, and the manual
light/dark/font-scaling QA are all closed. The release plan decides whether the
track lands in 0.10.0 or a later release; do not add a global current-units
singleton, a `UnitSystem.CM` value, frequency-based selection, or per-cell table
units.

Release sequence: **0.5 Decide** is the first slice because it has the highest
user value and the lowest modeling risk. **0.6 Build** converts a simulation into
a build package. **0.7 Measure** closes the loop with VNA data. **0.8 Explore**
adds advanced learning and robustness. **0.9 Sustain** adds content and
packaging. The names and numbers are working labels, not release commitments.

Deliberate exclusions for the UX track: server-based community projects, terrain
and obstacle modeling beyond the bounded DL7 native ground screen/cliff and the
ADR-gated DL8 full-terrain item, common-mode choke and real balun models before
G27 has measurements or traceable data, a price catalog, live VNA control,
additional full-wave engines, and new antenna families. These remain deferred,
blocked, or out of scope; they are not silently implied by the items above. DL8
is blocked on a validated terrain ADR; additional full-wave engines remain
deferred until that ADR selects one.

### Product trust and station track (proposed 2026-11-19)

The 2026-11-19 review shifts the next product slice from catalog breadth to
trust, station completeness, and site awareness. The catalog is broad enough;
the next value is answering the questions an operator asks before building:
does the model converge, does it cover the band, will the ATU match it, where
does it fall on the Smith chart, and what does the site do to the pattern.

This is product scope. Execution, acceptance criteria, dependencies, and risk
live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md#product-trust-and-station-wave).
The UX track rules apply unchanged. This track adds: table-stakes items land
before delight items; no new antenna families; terrain starts with the bounded
cliff/second-medium work; near-field/RF exposure (DL4) is canceled. Antenna content work (C7h 6 m HexBeam, the LPDA 7 MHz swept variant,
and new catalog presets) waits until this track closes.

| Release | ID | Item | Outcome | Size | Evidence | Status |
|---|---|---|---|---|---|---|
| 1.0 Confidence | TS1 | Convergence study | 3–5 density ladder with a self-consistency verdict | M | n/a | done 2026-11-19 |
| 1.0 Confidence | TS2 | Decision metrics and band overlay | 2:1 bandwidth, HPBW, F/B, takeoff, band edges | M | B | done 2026-11-19 |
| 1.0 Confidence | DL9 | Circular-polarization metrics | Axial ratio, sense, CP gain, cross-pol | S–M | B | done 2026-11-19 with TS2 |
| 1.0 Confidence | TS3 | NEC-2 deck export | Portable, auditable deck and copy action | S | n/a | done 2026-11-19 |
| 1.0 Confidence | TS4 | Autosave and crash recovery | Atomic recovery file and restore prompt | S–M | n/a | done 2026-11-19 |
| 1.0 Confidence | TS5 | VNA import 2.0 | `.s2p`, presets, mapping, locale-aware parsing | M | n/a | done 2026-11-19 |
| 1.0 Confidence | TS6 | Recent projects and start examples | Faster launch-to-design path | S | n/a | done 2026-11-19 |
| 1.0 Confidence | TS7 | Documentation truth pass | Docs match behavior; status review | S | n/a | done 2026-11-19 |
| 1.1 Station | DL1 | Smith chart and matching workbench | Interactive locus, reference planes, measured overlay, editable feed-line preview, automatic L/Pi/T preview, export | M–L | n/a | done 2026-11-19; manual component entry remains |
| 1.1 Station | DL2 | Tuner matchability and realizable components | Bounded L/Pi/T check, E12/E24, Q loss, limiting part, best effort/bypass, band-center rows, port ratings | M–L | B/C | done 2026-11-20; per-component branch ratings optional |
| 1.1 Station | DL5 | Support structures | Yagi mast and guy wires done; boom, tower, attachments, and hardware deferred pending ADR/spike | M–L | B/C | narrowed 2026-11-24 |
| 1.2 Site and exploration | DL3 | Live tuning preview | Managed length/non-length dimensions and optional coarse pattern preview implemented; Apply closes; optional non-modal remains | M–L | n/a | implemented 2026-11-24 |
| 1.2 Site and exploration | DL4 | Near-field and RF exposure | Canceled 2026-11-24; not relevant to the amateur design workflow | — | — | canceled |
| 1.2 Site and exploration | DL6 | Stacked Yagi arrays | First slice done 2026-11-25: form, schema 66, catalog, per-port sources, scene/reports, splitter + phase-line specification, co-simulated TL network with the reference line, a matched line loss plus a per-port mismatch correction, one shared mast, a Wilkinson N-port divider mode with a reconstructed pattern and per-level L/Pi/T matching networks, and bounded spacing/phase optimization; component tolerances and folded driven elements remain | L | C | partial 2026-11-25 |
| 1.2 Site and exploration | DL7 | Native ground screen and cliff | Bounded cliff/second-medium far-field profile implemented; native screen still unvalidated for SWR | M–L | B/C | implemented 2026-11-24 |
| post-1.2 | DL8 | Full terrain model | Validated terrain model or second engine | XL | B/C | blocked on DL7/ADR |

Release sequence for this track: **1.0 Confidence** closed truth,
interoperability, convergence, metrics, and recovery on 2026-11-19. **1.1
Station** adds Smith, tuner/components, and support structures; DL1 and DL2 are
done, and DL5 is narrowed. **1.2 Site and exploration** adds live preview,
stacking, and bounded cliff ground; DL4 is canceled. **DL8** remains post-1.2 until a validated terrain
ADR exists. The names and numbers are working labels; the backlog is the
executable order.

## Next

The active execution queue is
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Evidence status is in
[`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md). The archived 2026-11-04 phase plan is
kept at
[`archive/PENDING_WORK_PLAN_2026-11-04.md`](archive/PENDING_WORK_PLAN_2026-11-04.md).

Product track:

1. UX1–UX17 are complete. The 0.5 **Decide**, 0.6 **Build**, 0.7 **Measure**,
   and 0.8 **Explore** releases are closed. UX18–UX38 are implemented; the 0.9
   **Sustain** slice is complete. The UX queue is closed. The adaptive length
   display-units track is complete through U6, including manual visual QA;
   release preparation is next.
2. The 2026-11-19 **product trust and station** track has completed wave 0:
   1.0 Confidence (TS1–TS7, DL9) is done. Wave 1 Station (DL1, DL2, DL5) is
   active: DL1 (Smith chart, reference planes, measured overlay, editable
   feed-line preview, automatic L/Pi/T preview, and export) is done. DL2's
   first slice (bounded tuner check, E12/E24, Q loss, limiting part, L/Pi/T
   best effort, bypass, band-center rows, and port ratings) is done; only
   per-component branch ratings remain optional. DL5 is narrowed. Wave 2 is in
   progress: DL3 is partial, DL6 has its first slice implemented (per-level
   matching remain), and DL7 is implemented as a bounded
   cliff slice; DL4 is canceled by product decision. DL8 stays
   post-1.2 until a validated terrain ADR exists. Execution and acceptance criteria are in
   [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md#product-trust-and-station-wave).

Modeling track:

1. Completed on 2026-11-05: refined Zepp matching-section geometry with a real
   second conductor and an explicit 1:1 choke requirement. The choke remains a
   construction note because NEC-2 cannot model it.

Release track:

1. `v0.3.1` is published with checksum-verified unsigned artifacts.
2. `v0.4.0` is published with checksum-verified unsigned artifacts. The Windows
   bundle was built and smoke-tested in CI; Linux assets were built and
   smoke-tested locally because the release runner's package mirror DNS failed.
3. `v0.4.1` is published with the NSIS Windows installer and CI-built Linux
   packages. All release jobs completed successfully.
4. `v0.4.2` is published with the Windows hidden-console solver fix and
   automatic wheel/sdist checksums.
5. `v0.5.0` is published with the feed-transformer defaults, current-balun
   record (schema 44), side-by-side pattern cuts, and the accumulated project,
   measurement, construction, and workflow work. All release jobs completed
   successfully in CI, including the Windows bundle and installer QA.
6. `v0.6.0` is published with the materials reference, coax catalog and
   feed-line presets, portable project bundles, BOM costs (schema 45), and
   catalog starting frequencies. All release jobs completed successfully in CI,
   including the Windows bundle and installer QA.
7. Add GPG/Authenticode signing in a later release if required.
8. `v0.7.0`, `v0.7.1`, `v0.8.0`, `v0.8.1`, `v0.8.2`, and `v0.9.0` are published;
   see [`CHANGELOG.md`](../CHANGELOG.md) and the archived release QA records in
   [`archive/releases/`](archive/releases/).
9. The 2026-11-19 trust/station track completed 1.0 Confidence. 1.1 Station is
   done as narrowed (DL1/DL2 done, DL5 narrowed); 1.2 has partial DL3/DL6 work
   and a bounded DL7 implementation, with DL4 canceled. There are no committed
   dates, and each release is gated by the acceptance criteria in the backlog.

Validation track:

1. Independent references for remaining experimental templates. The reference
   passes promoted `delta_loop`, `vertical`, `inverted_v`, `j_pole`,
   `slim_jim`, `endfed`, `trap_dipole`, `sloper`, `doublet`, `zepp`, `biquad`,
   and `beverage` to level B for starting dimensions; the remaining level C
   templates and their next evidence needs are listed in
   [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md).
2. Physical measurements when the project owner has data.

## Definition of done for a generator

- Domain generator is independent of Qt and the solver.
- Geometry invariants and feed connectivity are tested.
- Scaling with frequency is tested.
- Presets identify their source or heuristic.
- Experimental generators show a visible limitation/warning.
- A reference test is added when a traceable numeric oracle exists.
- Documentation and changelog are updated.
