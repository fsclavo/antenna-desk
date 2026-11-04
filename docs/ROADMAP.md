# AntennaDesk roadmap and backlog

**Updated:** 2026-11-03
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
- Guided dipole, folded dipole, trap dipole, T2FD, loop (generic, delta, quad),
  vertical (1/4λ, 1/2λ, and 5/8λ with radials, plus a loading-coil option and a
  mobile-whip preset), inverted-V, fan dipole, end-fed, sloper, random wire,
  doublet, OCFD, J Pole, Slim Jim, Ringo, Yagi, Moxon, and custom-wire designs.
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
- Per-band multiband analysis for G5RV, OCFD, end-fed presets, fan dipole, trap
  dipole, T2FD, and doublet, with a Bands results tab and band-aware reports.
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
- Published `v0.1.0` with unsigned, SHA-256-verified artifacts (completed).
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
  selected band, with progress, cancellation, partial results, and one pattern
  snapshot per band by default.
- **Analyze Bands...** UI integrated with the central **Band analysis** group
  and global **Simulation pattern** settings, plus a band selection dialog and
  a **Bands** results tab showing best SWR, gain, takeoff angle, efficiency,
  and status. The top action bar stays Apply/Estimate/Optimize.
- Band/batch metadata on simulation runs, schema version 4 migration (extended
  by version 5 with OCFD/custom transformer fields), and band-aware CSV, HTML,
  PDF, and comparison summaries.
- Deferred: a segmented frequency plan in one NEC deck, only if measurements
  show that per-band runs are too slow or too large.
- Deferred: per-band pattern PNG export.

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
| P1 | Independent references for remaining experimental templates | A/B | partial |
| P1 | Optional ideal transformer/4:1 balun for OCFD | B | done |
| P1 | Multiband batch engine and per-family band defaults (M6) | B | done |
| P1 | Band selection UI and band summary results (M6) | B | done |
| P2 | Persist band-analysis batches and band-aware reports (M6) | B | done |
| P2 | Cross-band comparison table | B | done |
| P3 | Per-band pattern PNG export | B | pending |
| P2 | GPG/Authenticode code signing for release artifacts | n/a | deferred |
| P2 | Relative permeability export to NEC | B | pending |
| P2 | Custom/imported geometry optimization and space constraints | n/a | pending |
| P2 | Live VNA/hardware control | n/a | deferred |
| P2 | Additional full-wave engines | n/a | deferred |
| P2 | Physical antenna validation | A | blocked: no measurements |
| P3 | Segmented frequency plan in one NEC deck | B | deferred |

## Next

Modeling track:

1. Relative-permeability export and a pattern-metric selector for realized
   gain/directivity.
2. ZS6BKW and Zepp presets using geometry transmission lines.

Release track:

1. `v0.1.0` is published with checksum-verified unsigned artifacts.
2. Add GPG/Authenticode signing in a later release if required.

Validation track:

1. Independent references for remaining experimental templates.
2. Physical measurements when the project owner has data.

## Definition of done for a generator

- Domain generator is independent of Qt and the solver.
- Geometry invariants and feed connectivity are tested.
- Scaling with frequency is tested.
- Presets identify their source or heuristic.
- Experimental generators show a visible limitation/warning.
- A reference test is added when a traceable numeric oracle exists.
- Documentation and changelog are updated.
