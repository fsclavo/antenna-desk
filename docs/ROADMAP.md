# AntennaDesk roadmap and backlog

**Updated:** 2026-11-11
**Status:** active product roadmap after catalog, measurement, optimization,
packaging, and the 2026-11-11 product-experience review.
**Scope:** product direction, milestones, and the ordered antenna expansion
backlog. The active execution queue is
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
- VNA CSV import, measurement conditions/reference plane, measured/simulated
  comparison, resonance differences, and project measurement records.
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
  release workflow.

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
- Published `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.3.1`, `v0.4.0`, and `v0.4.1`
  with unsigned, SHA-256-verified artifacts (completed).
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
| 4 | Magnetic loop | New family | L | High | B/C; A only with an exact published design | **Implemented on 2026-11-07:** first-class tuned small loop with a top gap, ideal series capacitor and ESR, conductor-loss simulation, efficiency reporting, SWR-bandwidth reporting, and a dedicated editor. A coupling loop and detailed capacitor loss model remain limitations. |
| 5 | Yagi folded driven element | Modification of `yagi` | M | Medium | B/A | **Implemented on 2026-11-07:** optional two-conductor folded driven element with end connectors and adjustable spacing. The published NBS preset can be loaded with the folded element; feed impedance remains a tuning result, not a reference value. |
| 6 | Gamma / beta / hairpin match | Modification of `yagi` | M | Medium | B/A | **Partially implemented on 2026-11-07:** beta/hairpin geometry with a split driven element, shorted stub, and adjustable length/spacing. Gamma is deliberately deferred because NEC-2 close-spaced gamma assemblies are unreliable; use the matching-network dialog for an equivalent. |
| 7 | Balun/unun with losses | Cross-cutting model | M | High | B/C | **Implemented on 2026-11-07:** project-level matched insertion loss with a power-law frequency fit. It reduces realized gain and is reported per frequency; it does not alter geometry, impedance, or SWR. Apply it to EFHW, OCFD, G5RV, T2FD, or any other design. |
| 8 | Capacity hat / top-loaded vertical | Modification of `vertical` | M | High | B/A | **Implemented:** the vertical template already has a capacitive top hat and loading coil. Reports, construction sheet, and scene summary now expose the hat geometry, with a dedicated scene contract case. The hat remains an application starting point, not an independently validated loading design. |
| 9 | Explicit EFHW presets for the existing EndFed + OCFD/G5RV variants | Presets/UX, not a new family | S | Medium–high | A/B | **Implemented on 2026-11-07:** the EndFed editor is labeled EFHW, exposes 40/20/10 m preset buttons using the published 66/33/16 ft lengths and 49:1 transformer, and keeps the existing harmonic band plan. OCFD/G5RV variants remain presets. |
| 10 | Half-square / bobtail curtain | New family | M | Medium | B/A | **Implemented on 2026-11-07:** one self-contained vertical-array family with half-square and bobtail-curtain variants, top-junction feed with adjustable offset, schema-16 persistence, catalog routes, editor, geometry dimensions, reports, and construction sheet. The Cebik 7.15 MHz dimensions are the published starting point; pattern, ground, and matching remain unvalidated and there is no frequency-first estimator. |
| 11 | Biquad / double biquad | New family | M | Medium | B/C | **Implemented on 2026-11-07:** two- or four-loop stack with shared rails, optional wire reflector, quarter-wave starting dimensions, inline editor, schema 19, scene contract, reports, and family optimizer. The biquad starting dimensions are published (B); the double biquad remains C because the published side-by-side topology differs from the vertical stack. |
| 12 | Beverage | New family | M | Medium | B/C | **Implemented on 2026-11-07:** long receiving wire with optional resistive termination, one-wavelength starting length, inline editor, schema 20, scene contract, reports, construction notes, and family optimizer. The one-wavelength length and 500 Ω termination are published (B); gain, pattern, and termination efficiency remain unvalidated. |
| 13 | Loaded / linked dipole | New family or `dipole` variant | M | Medium | B/C | **Implemented on 2026-11-07:** center-fed loaded dipole with symmetric series R-L coils or open links, schema 21, inline editor, scene contract, reports, construction notes, and family optimizer. B3 reviewed the published 3.91 MHz BVARC example; the template remains C because the source ground model is unspecified. Coil core loss, self-capacitance, and link contact resistance remain limitations. |
| 14 | Wire sag / tapered elements / boom correction | Geometry model | M | Medium | B/C | **Partially implemented 2026-11-07:** optional sampled parabolic sag on horizontal wire dipoles (schema 22) and optional tapered Yagi tips (schema 23), with scene/report/conductor-length support. Boom-mounting correction remains pending because no universal published model is available. |
| 15 | Phased verticals / arrays | Architectural | XL | High | B/A | **Implemented on 2026-11-08:** multi-source excitation, ideal linear phase and amplitude progression, 2–4 verticals with radial screens, schema 25, inline editor, scene/source markers, reports, construction notes, and family optimizer. The combining network is ideal and the family remains experimental pending a traceable array reference or measurement. |
| 16 | Quad beam / hexbeam | New family | L | Medium–high | B/A | **Implemented on 2026-11-08:** quad beam with 2–3 square loops and a separate single-band hexbeam with published G3TXQ dimensions, schema 26 and 30, editors, scene contracts, reports, construction notes, and family optimizers. The hexbeam reconstructs the bent wire path and is classified published/heuristic; frame and multi-band nesting are not modeled. |
| 17 | Log-periodic | New family | L | Medium | A/B | Many elements and a feed network; high test burden. |
| 18 | Discone | New family | L | Medium | B/C | **Implemented on 2026-11-08:** radial-wire cone and top disc with an apex feed gap, schema 27, inline editor, scene contract, reports, construction notes, and family optimizer. The wire approximation and missing coax/mast model keep it experimental. |
| 19 | Trapped / multiband Yagi | New family | L | High | B/C | **Implemented on 2026-11-08:** two-band Yagi with one ideal parallel LC trap pair per element, schema 28, inline editor, scene contract, reports, construction notes, and family optimizer. Trap loss, boom mounting, feed line, and matching remain unvalidated. |
| 20 | Shortened loaded EFHW | EndFed variant | M | Medium | B/C | **Implemented on 2026-11-09, matching model extended 2026-11-10, inverted-L option 2026-11-11:** 80-10 m (20.35 m + 110 µH + 2.39 m) and 40-20-10 m (10.01 m + 23 µH + 1.85 m) presets with a 49:1 transformer, editable series coil, schema 33 for the matching values, schema 34 for the project design target, and schema 35 for the optional inverted-L bend, catalog entries, band plans, reports, construction notes, and optimizer variables. The optional primary 100 pF shunt and 0.198 µH leakage estimate are modeled; the bend uses a sharp 90° corner with an 8 m vertical starting section and no independent validation. The common-mode choke, ground, core loss, capacitor ESR, and winding capacitance are not modeled. Edited or scaled geometry is experimental. |

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
execution queue. UX1–UX6 are complete; the 0.5 **Decide** release is closed and
the 0.6 **Build** release is in progress. UX7–UX20 stay here until the next
product slice is selected and they are ready to execute.

Rules for this track:

- Every item must remove a decision or a manual step. A calculator alone is not
  enough.
- No new electromagnetic model without a traceable source or measurement. Items
  that cannot be validated are labeled experimental and show their limits.
- Progressive disclosure: Guided, Standard, and Advanced modes; no new dialog
  for every option.
- Local-first: no accounts, servers, or telemetry.
- Pause new antenna families. The existing catalog covers the common cases;
  log-periodic remains blocked by C3.
- Each release leaves the full gate green and is usable on its own.

| Release | ID | Item | Outcome | Size | Evidence | Status |
|---|---|---|---|---|---|---|
| 0.5 Decide | UX1 | Guided mode and next-step coach | State-driven next action and progressive disclosure | S–M | n/a | done 2026-11-11 |
| 0.5 Decide | UX2 | Installation profile | Reusable site envelope and constraints | S–M | n/a | done 2026-11-11 |
| 0.5 Decide | UX3 | Antenna suitability profiles and guided advisor | Constraint-filtered shortlist with operating intent and trade-offs | M | B/C | done 2026-11-11 |
| 0.5 Decide | UX4 | Comparison 2.0 | 2–4 designs under a common basis, recomputed | M–L | B | done 2026-11-11 |
| 0.5 Decide | UX5 | Contextual explanations and confidence card | Metric meaning, evidence, assumptions, and limits | M | A/B/C | done 2026-11-11 |
| 0.6 Build | UX6 | Feed-chain topology and loss budget | Tuner/balun position and per-stage loss | M–L | B/C | done 2026-11-11 |
| 0.6 Build | UX7 | Construction package 2.0 | As-built, hardware BOM, coil/trap sheet, checklist | M | B/C | proposed |
| 0.6 Build | UX8 | Integrated coil/trap/loading calculators | Prefilled calculators that apply to the design | M | B | proposed |
| 0.6 Build | UX9 | Construction pre-flight checks | Detect geometry, feed, segmentation, and support issues | S–M | n/a | proposed |
| 0.7 Measure | UX10 | Measurement sessions and timeline | Multi-session records and before/after comparison | M | A/B | proposed |
| 0.7 Measure | UX11 | Sensitivity-based tuning assistant | Bounded adjustment from solver sensitivity | M–L | B/C | proposed |
| 0.7 Measure | UX12 | Measurement uncertainty card | Calibration, reference-plane, and environment limits | S–M | B/C | proposed |
| 0.8 Explore | UX13 | Parameter sweeps (what-if) | 1D/2D sweeps with overlays and a budget | M | B | proposed |
| 0.8 Explore | UX14 | Tolerance and robustness analysis | Corner cases and Monte Carlo with critical dimensions | M–L | B/C | proposed |
| 0.8 Explore | UX15 | Project journal | Timeline, as-built, photos, notes, and version comparison | M | n/a | proposed |
| 0.8 Explore | UX16 | Guided experiments | Three tutorials built on the sweep engine | M–L | B | proposed |
| 0.9 Sustain | UX17 | Curated reference design library | 10–20 sourced designs; published versus simulated | M + content | A/B | proposed |
| 0.9 Sustain | UX18 | Minimal materials reference | Static, sourced wire/coax/ferrite/insulator table | S–M | B | proposed |
| 0.9 Sustain | UX19 | Portable project bundle | Export/import project plus assets; no server | S–M | n/a | proposed |
| 0.9 Sustain | UX20 | Editable BOM costs | Manual cost column and totals | S | n/a | proposed |

Release sequence: **0.5 Decide** is the first slice because it has the highest
user value and the lowest modeling risk. **0.6 Build** converts a simulation into
a build package. **0.7 Measure** closes the loop with VNA data. **0.8 Explore**
adds advanced learning and robustness. **0.9 Sustain** adds content and
packaging. The names and numbers are working labels, not release commitments.

Deliberate exclusions for this track: server-based community projects, terrain
and obstacle modeling, common-mode choke and real balun models before G27 has
measurements or traceable data, a price catalog, live VNA control, additional
full-wave engines, and new antenna families. These remain deferred, blocked, or
out of scope; they are not silently implied by the items above.

## Next

The active execution queue is
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Evidence status is in
[`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md). The archived 2026-11-04 phase plan is
kept at
[`archive/PENDING_WORK_PLAN_2026-11-04.md`](archive/PENDING_WORK_PLAN_2026-11-04.md).

Product track:

1. UX1–UX6 are complete. The 0.5 **Decide** release is closed and the 0.6
   **Build** release is in progress. UX7–UX9 are the next Build candidates;
   UX10–UX20 remain product scope in the backlog above.

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
4. `v0.4.2` is prepared with the Windows hidden-console solver fix and automatic
   wheel/sdist checksums.
5. Add GPG/Authenticode signing in a later release if required.

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
