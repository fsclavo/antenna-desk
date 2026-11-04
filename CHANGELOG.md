# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Yagi and Moxon designs now support selectable **horizontal or vertical
  polarization** while keeping the boom horizontal. Vertical Yagi elements
  rotate around the boom; the Moxon rectangle lies in a vertical plane. Height
  remains the boom centerline and the geometry is rejected when the elements or
  rectangle would reach the ground. Existing designs and projects default to
  horizontal. Project schema version 7 migrates them explicitly.
- The 3D pattern high-resolution paint mesh now uses a 40% coarser angular
  step for large patterns, reducing vertex and segment counts by about half.
  Stored far-field data, cuts, and exports are unchanged.
- Added a reproducible multiband benchmark. The measured 3/5/8-band batches
  keep the per-band solver architecture; see `docs/MULTIBAND_PERFORMANCE.md`.
- OCFD and End-fed generators now label the frequency as the fundamental/design
  frequency and let the user choose the harmonic analysis band plan at
  creation. The plan is persisted with the design, restored on reopen, and does
  not change geometry. Random-wire uses the same selector for its tuner-assisted
  80–10 m analysis plan.
- **Zepp** catalog preset: end-fed half-wave radiator with a quarter-wave
  lossless matching section. It is labeled experimental, includes starting
  dimensions from frequency, uses 40/20/10 m as a harmonic starting plan, and
  explicitly omits the second matching conductor, 1:1 choke, and common-mode
  current.
- T2FD now has a frequency-first **Estimate Dimensions...** path using the
  Cebik wide-long broadband starting rule. It requires the lowest and highest
  design frequencies and preserves the current termination and transformer.
- ZS6BKW has a template-specific optimizer for dipole wire length and matching
  line length, while keeping the line impedance and velocity factor fixed.
- **ZS6BKW** catalog preset with a 28.4 m / 400 Ω / 13.6 m Cebik/W4RNL
  reference variant and a 27.5 m / 450 Ω / 12.2 m commercial variant, modeled
  with a lossless geometry transmission line. The default band analysis uses
  the 40/20/17/12/10 m no-ATU set and a 61-point 7.0–29.7 MHz sweep.
- **Simulation sweep** in **Advanced simulation** provides Auto (template) and
  Custom Start/Stop/Points modes for every antenna family, including generated
  templates that previously used a fixed sweep with no UI control.
- During a band analysis, the **Pattern** frequency selector now lists pattern
  frequencies from every analyzed band and switches the active band when one is
  selected. The **Bands** tab remains synchronized.
- Band analysis now applies the global **Pattern frequencies** policy inside
  each band instead of forcing one snapshot per band.
- The main window now starts on a **Start an antenna project** page instead of
  creating a demo 40 m dipole. **New Antenna...** creates the first project and
  **Open Project...** loads an existing file; project and design controls appear
  only after a project is open.
- **Estimate Dimensions...** now refines only the template already loaded in the
  editor. The dialog preselects the current family, preloads its frequency and
  template-specific fields, and refuses to replace the template. Templates
  without an estimator show the action disabled with an explanation.
- OCFD designs support an optional ideal feed transformer, defaulting to the
  common 4:1 balun for new designs while old projects remain untransformed.
  The ratio is editable, applies to impedance/SWR/realized gain, and preserves
  pattern geometry. Custom designs also carry an optional transformer ratio.
- Pattern charts, polar plots, the 3D lobe, and cursor readouts can now switch
  between power gain, directivity, and realized gain.
- Pattern PNG export on a band analysis now writes one image per band into a
  selected folder while preserving the current pattern selection.
- Multiband analysis for G5RV, OCFD, end-fed/random-wire/sloper, fan dipole,
  trap dipole, T2FD, and doublet designs. **Analyze Bands...** runs the existing solver
  once per selected band, stores band/batch metadata on simulation runs, and
  adds a **Bands** results tab with best SWR, gain, takeoff angle, efficiency,
  and status. Band summaries are included in CSV, HTML, and PDF exports.
- The 3D radiation-pattern wireframe is colored by gain (green, yellow, red)
  with a min/max dBi legend, while keeping the lobe interior transparent.
- The 3D lobe maximum-gain marker now reports the takeoff angle above the
  ground plane (or elevation for free-space models) alongside the gain.
- End-fed designs support a user-selectable counterpoise (drop plus horizontal
  wire) and an ideal feed transformer ratio. The one-time estimator starts with
  a 49:1 transformer and a 0.05λ counterpoise as application starting points.
- Frequency-first vertical estimation supports the half-wave form
  (`0.5λ × 0.95`) in addition to quarter-wave and five-eighth-wave, with a
  matching warning for the high half-wave feed impedance.
- Vertical templates support an optional series loading coil at a selected
  height above the base. A loaded vertical / mobile whip catalog preset starts
  with a 2.0 m radiator, four short radials, and an editable 10 µH coil as
  application starting points.
- Trap-dipole templates support two parallel LC traps, automatic trap
  capacitance from the target frequency and inductance, and a starting-dimension
  helper for the low and high bands.
- T2FD (terminated folded dipole) templates support a broadband 800 Ω series
  termination, an ideal feed transformer, horizontal or vertical geometry, and
  a Cebik wide-long starting-dimension helper (`300/F` span, `10/F` spacing).
- Catalog presets for a sloper, a random wire, and a doublet. Sloper and random
  wire use the end-fed template with preset metadata; the doublet creates a
  center-fed dipole and configures a project-level open-wire feed line.
- Directivity and realized gain are now separated from NEC power gain. The
  results summary and reports show power gain, directivity, realized gain, and
  the mismatch, feed-line, and matching-network loss components. The feed
  line, matching network, and ideal transformer are evaluated as a two-port
  cascade; the pattern charts remain NEC power gain.
- Transmission lines can be modeled as geometry: a lossless two-port between
  two wire offsets, persisted with the design, emitted as NEC `TL` cards,
  drawn as dashed construction lines, and edited from the design panel. This is
  separate from the transmitter feed-line post-processing model.
- G5RV catalog preset with the published 102 ft dipole and a 300 Ω / 8.84 m or
  450 Ω / 10.36 m lossless geometry matching line, plus a 41-point wideband
  custom sweep.
- Simulations choose the finest pattern resolution that fits the project size
  budget. Custom designs expose an Auto (max) setting, an estimated-size
  indicator, and a pattern-disabled fallback; generated templates coarsen the
  selected resolution automatically and report an informational diagnostic.
  Oversized solver output now reports a specific `solver.output_too_large`
  diagnostic.
- Sweeps longer than five points now compute the far-field pattern at
  amateur-band snapshots while keeping every impedance/SWR point. Custom designs
  can choose Auto (bands), 5, 9, 13, 17, or 21 pattern frequencies. The pattern tab
  lists the snapshots, so a 200-point G5RV sweep can show nine bands at 5°
  instead of a 30° pattern at every point. The project-size budget accounts for
  the sweep and pattern snapshot counts separately.
- Added `docs/QA_STRATEGY.md` and the Phase 0 test tooling: the suite now
  auto-detects `spikes/phase0/build/nec2c` so solver tests do not skip silently
  on a developer machine, registers `science`, `solver`, `slow`, `golden`, and
  `ui` markers, and the CI caches the uv environment. The UI teardown now
  dispatches deferred deletes, which cuts the full suite from 142 s to 56 s.
- Added a coverage job with per-package thresholds, a permissive mypy pass over
  58 of the 75 UI modules (`mypy_ui.ini`), English/Spanish translation parity
  tests, and Hypothesis property tests for units and the three importers. The
  3,654-line main-window test module is split into eight feature modules, and
  the two-port math is cross-checked against scikit-rf. Every catalog template
  now has a machine-readable evidence entry, rendered into the validation plan.
  The solver is also cross-checked against nec2++ for three canonical
  geometries, physical invariants cover power balance, pattern-integral
  directivity, and rotation invariance, and weekly mutation testing runs
  `mutmut` on the design formulas and intent. A curated MMANA corpus with a
  checksum manifest now covers structural regression and a NEC2C smoke run,
  and analytical closed forms cover the short-dipole and small-loop limits.
  The 1,442-line nec2c adapter test module is split into four modules.
- Added `docs/EXPERIMENTAL_VALIDATION_PROTOCOL.md`, the level 3 measurement
  protocol for a half-wave dipole with an IEEE 149-2021 / GUM uncertainty
  budget. No measurement is recorded yet.

### Changed

- Audited the experimental templates in
  [`docs/EVIDENCE_AUDIT.md`](docs/EVIDENCE_AUDIT.md). The delta loop, vertical,
  and inverted-V generators moved from evidence level C to B after checking
  their published length rules, with explicit tolerances and regression tests.
  The remaining experimental templates and their next evidence needs are
  documented.
- CI now pins every action by commit SHA, runs `uv lock --check` and
  `pip-audit --skip-editable`, and Dependabot tracks GitHub Actions and Python
  dependencies.
- Renumbered the duplicate ADR 0014: undo/redo is now ADR 0024. Added tests for
  unique, contiguous ADR numbering and matching headings.
- **New Variant...** is now **New Design in Project...**, and the design
  selector, menus, comparison dialog, and history labels use “design” instead of
  “variant”.
- The basic wire/folded/loop template field is read-only and has a **Change...**
  button. **Change Template...** preselects the current catalog entry and still
  requires confirmation before replacing the design.
- Specialized antenna generators now choose the template first and ask for the
  project name afterwards, with a suggested band/template name.
- **Simulation pattern** and **Band analysis** now live in a collapsible
  **Advanced simulation** section below the design form. The design form starts
  directly under the Apply/Estimate/Optimize action bar.
- **Apply design** remains an explicit save without simulation, while
  **Simulate** saves the current form values and runs the solver.
- Fan dipole **Simulate** now analyzes every distinct element band
  automatically and opens the Bands tab, so a 10 m element is no longer hidden
  by a 40 m-only sweep. The estimator warning and user guide now call out the
  V-angle/coupling shift on the highest band.
- The fan-element optimizer now has a synchronized Band selector and a Band
  column, preselects the band active in the Bands tab, warns when the target
  frequency and selected elements disagree, and recomputes segmentation for the
  target frequency. Its default frequency is the lowest element band rather than
  a stale design frequency, and it explains that unchecked elements still
  affect the antenna.
- Project schema version 6 adds optional per-design analysis band plans on top
  of the version 5 transformer fields. Older projects migrate without changing
  their geometry or results.
- Project schema version 5 adds optional OCFD/custom feed-transformer ratios
  on top of the version 4 band/batch run metadata. Older projects migrate
  without changing their geometry or results.
- Project schema version 4 adds optional `band_id` and `batch_id` metadata to
  simulation runs. Version 3 projects migrate without changing their data.
- The design panel now has one action bar (**Apply design**, **Estimate
  Dimensions...**, **Optimize...**) and a compact global **Simulation pattern**
  group. The duplicate per-form pattern controls and bottom Apply/Optimize
  buttons were removed.
- Pattern resolution and pattern-frequency controls are now global to every
  antenna family. Generated dipoles, Yagis, loops, verticals, and future
  templates use the same Auto (max)/Auto (bands) policy as the G5RV and get 1°
  or 2° band snapshots when they fit the compressed budget.
- The 3D pattern view draws a coarser display mesh while rotating or zooming
  and returns to the full-resolution wireframe when the movement stops. This
  keeps 1° and 2° patterns responsive without removing stored data.
- Project files are now compact JSON compressed losslessly with gzip. Existing
  plain-JSON projects still load. The 32 MB hard limit and 20 MB warning apply
  to the compressed file, so a 200-point G5RV with 13 band snapshots at 2° is
  about 8 MB, and nine band snapshots at 1° is about 20 MB.
- The project storage budget is now 24 MB compressed, with a save warning above 20 MB and
  a 32 MB hard limit. This lets pattern-rich runs keep more band snapshots and
  a finer angular step: a 200-point G5RV with 13, 17, or 21 snapshots uses
  5°, and with five snapshots it can use 2°.

### Fixed

- Five-eighth-wave vertical estimates now apply the same end-effect factor as
  the quarter- and half-wave estimates, matching the ARRL 585/f practical
  formula. The estimated radiator is about 5% shorter than before, and the
  estimate is labeled empirical instead of physical.
- A NEC deck line containing only separators (for example `,`) no longer raises
  an `IndexError`; it is ignored like a blank line. Imported files are untrusted
  data, so the parser now reports malformed cards as `ValueError`.
- `normalize_azimuth_degrees` now returns `0.0` for tiny negative angles. The
  modulo result (`360.0 - 1e-15`) rounded to exactly `360.0`, which violated
  the documented `[0, 360)` range.
- Added segmentation diagnostics `segmentation.segment_too_short` and
  `segmentation.radius_ratio_low`, with the computed Δ/λ and Δ/a in the
  message, following the NEC-2 User's Guide modeling guidelines. The solver
  integration suite now includes a segmentation-convergence study of the
  30.48 m dipole in free space and over finite ground.
- Frequency-first estimator geometries stay above ground: inverted-V estimates
  widen the included angle (and raise the apex if needed), fan-dipole estimates
  use distinct progressively narrower element angles, and end-fed estimates
  clamp an unreachable end height. Fan dipoles now reject two elements with the
  same included angle because their wires would overlap.
- Ground-mounted vertical radials are raised 1 cm in the NEC deck. A freshly
  estimated vertical with finite ground previously failed with `nec2c exited
  with code 255` because the radials lay exactly on the ground plane. Wires
  below ground now produce a clear `geometry.below_ground` diagnostic instead.
- NEC `LD` and `TL` cards now use local segment numbers within each wire tag;
  loads on wires after the first were previously mapped to global segment
  numbers.

## [0.1.0] - 2026-11-02

### Added

- Project-level Undo/Redo for applied design, variant, template, load, feed-line,
  matching-network, measurement, and estimator changes, with protected
  simulation-run history.
- Hover cursors on impedance, SWR, pattern, currents, and measurement charts
  with nearest-point readouts and theme-aware overlays.
- Menu ergonomics: standard File/Edit order, Change Template in the Design
  menu, grouped Import/Export entries, and Language/Units under Tools.
- The design panel now leads with **Estimate Dimensions...** as the primary
  frequency-first action; Change Template remains in the Design menu and keeps
  its Ctrl+Shift+T shortcut.
- Single-sourced package version from `antennadesk.__version__`, About-dialog
  version display, and a Hatchling wheel/sdist build with a package smoke-test
  workflow.
- Native release packages: Linux AppImage, Debian `.deb`, and Windows onedir
  zip recipes with bundled `nec2c`, application icons, SHA-256 checksums, and
  optional GPG or Authenticode signing hooks.
- Tag-triggered release workflow that builds the wheel/sdist, AppImage, Debian
  package, and Windows zip and attaches them to the GitHub release.
- Shared PyInstaller bundle builder and a packaging cleanup script so local
  validation can run in temporary directories without orphan build artifacts.
- Optional release signing: detached GPG signatures for every artifact,
  embedded AppImage signatures, and Windows Authenticode for both executables.
- `antennadesk --version` for packaged-application smoke tests.
- Frequency-first dimension estimation for dipoles, folded dipoles, loops,
  verticals (1/4λ, 1/2λ, and 5/8λ), inverted-V, fan dipoles, end-fed, OCFD,
  J Pole, Slim Jim, Ringo, Yagi (2–32 elements from the DL6WU trimming
  reference), and Moxon (Cebik reference scaled by frequency).
- `Design → Design from Frequency...` dialog with assumptions, warnings,
  confidence, sources, dimension table, apply-to-current-design flow, and an
  optional one-step handoff to the matching optimizer or synthesis dialog.
- Applied estimates persist their method, confidence, assumptions, warnings,
  tolerance, and source identifiers as optional design provenance; editing the
  design clears it.
- Estimator provenance is shown in HTML reports and PDF construction/simulation
  sheets alongside the design dimensions.
- Yagi frequency changes rescale the current element table by wavelength, and a
  warning flags element dimensions that do not match the current frequency.
- Traceable estimator contract with source identifiers and explicit unsupported
  cases for custom geometry and Yagi element counts outside 2–32.
- Phase 1 domain model for units, geometry, conductors, feed points, ground
  models, environments, and horizontal half-wave dipoles.
- Immutable project and design-variant model with validation.
- Versioned JSON project format with atomic saves and a migration framework.
- Create, save, open, and edit-length use cases.
- A 40 m dipole example project.
- Unit, integration, and acceptance tests for Phase 1.
- Architecture, domain-model, and validation-plan documentation.
- CI for lint, formatting, type checking, and tests on Linux and Windows.
- Phase 2 simulation model: frequency plans, far-field requests, segmentation
  policy, solver metadata/capabilities, and normalized results.
- `nec2c` solver adapter with input generation, process execution,
  cancellation, timeouts, output parsing, SWR normalization, currents, power
  budget, and far-field patterns.
- Conductor conductivity (`LD 5`) support, toggleable for perfect-conductor
  reference cases.
- Reference validation against the NEC-2 User's Guide examples.
- A reproducible reference-simulation script for the production adapter.
- Phase 3 guided GUI: main window, dipole wizard, design panel, 2D geometry
  view, asynchronous simulation with cancellation, results charts, and
  diagnostics.
- English/Spanish UI and metric/imperial presentation units.
- PySide6 and PyQtGraph dependencies, with PySide6 pinned below 6.10 to avoid a
  shutdown crash observed with 6.12.
- Offscreen UI tests with `pytest-qt`.
- Dimensioned construction-sketch geometry view with total and per-leg
  dimensions, height dimension, feed/center/end markers, ground hatching,
  scale bar, and azimuth compass.
- Elevation and plan view modes, plus optional vertical exaggeration for
  low-height layouts.
- Phase 4 design-variant management: add, rename, delete, and switch variants.
- A/B comparison dialog with metrics, SWR overlay, and gain-pattern overlay.
- Currents tab and resonance markers on impedance/SWR sweeps.
- CSV export and self-contained HTML reports with inline SVG charts.
- Phase 5 bounded dipole length optimization with min/max limits, target
  reactance, evaluation log, and ±10/25 mm sensitivity probes.
- Optimization dialog with worker thread, cancellation, and apply-best-length
  flow.
- Printable/HTML construction sheet with leg lengths, feed position, simulated
  result, resonance, and construction notes.
- Phase 6 first slice: vertical center-fed dipole template and orientation
  selector in the form and wizard.
- Project schema version 2 with dipole orientation and an explicit v1 to v2
  migration.
- Vertical geometry sketch, orientation-aware construction sheet, and NEC-2
  Example 3 reference validation.
- Persisted simulation runs in project schema version 3, including normalized
  results, diagnostics, and raw solver text; v2 projects migrate to an empty
  run list.
- Simulation save/reopen flow: the latest run per variant is restored for
  comparison, reports, and construction sheets across sessions.
- Solver integration jobs on Linux and Windows.
- Phase 6 second slice: parametric folded-dipole and regular-polygon loop
  templates, antenna-type union, and type/geometry consistency validation.
- Antenna-type selector with conditional spacing/sides fields; design
  conversion updates the derived geometry and switches multi-wire designs to
  Plan view.
- Generic New Antenna wizard with type selection, type-aware geometry and
  review pages, and the current design type as the initial choice.
- Additive schema v3 payloads for folded dipole and loop parameters, with
  round-trip and mismatch tests; existing wire-dipole documents are unchanged.
- Multi-wire geometry rendering, type-aware construction sheets and HTML
  reports, and mixed-geometry comparison.
- Geometry-view roles clarified: Plan carries construction dimensions (including
  feed legs and folded/loop measurements); Elevation shows installation height,
  feed height, and ground for all geometries. Folded plans show two elements
  with exaggerated spacing, and elevation adds a two-conductor section; loop
  plans show a circle with diameter, circumference, and side count fitted to
  the view, and loop elevation shows a vertical edge-on line with bottom height
  and diameter.
- Folded dipole and loop solver integration tests run against `nec2c`; these
  currently provide topology and sanity coverage, not independent impedance
  references.
- UI diagnostics for known stable codes are localized; the raw English
  solver message remains in the tooltip.
- Native PDF construction sheet with type-aware dimensions, simulation rows,
  notes, and footer.
- Native PDF simulation report with design/configuration tables, impedance
  table, resonance, SVG-derived charts, diagnostics, and footer.
- Compact simulation history action that keeps only the latest run per design,
  reducing project size.
- Save-time warning when a project exceeds 8 MB and a clear block above the
  10 MB native-file limit.
- Independent ARRL Antenna Book reference checks for free-space dipole gain
  and the folded-dipole gain/pattern/resistance relationship.
- Far-field pattern CSV export with frequency, angles, gains, polarization,
  and E-field components, plus PNG export of the current pattern view and
  geometry view.
- Custom straight-wire antennas with a coordinate editor, persistence, and
  simulation flow; optimization is disabled for custom designs.
- Practical NEC-2 deck import (GW, EX, FR, GE/GN, LD 0/1) into custom designs,
  with warnings for unsupported cards.
- Basic MMANA-GAL `.maa` geometry/source import into custom designs; ground and
  loads are explicitly reported as not imported.
- NEC import accepts comma-separated cards; custom wire editing reports short,
  overlapping, and crossing wires.
- Maximum-gain and maximum-efficiency optimization objectives, a weighted
  balanced SWR + gain objective, an experimental ground-radial wire generator
  in the custom editor, an ARRL free-space quad-loop resistance reference, load
  markers in Plan/3D geometry views, and conversion from a template to custom
  wires.
- Configurable pattern resolution (10°, 5°, 2°, or 1°) with point-count
  estimates, and a 100-point default for the frequency sweep.
- Series and parallel RLC loads on wires: validation, load editor,
  design/persistence support, NEC `LD 0`/`LD 1` export, and
  report/construction-sheet rows.
- Isometric 3D geometry view with ground grid, feed marker, axes, and scale.
- Polar pattern diagram in the Pattern tab with selectable azimuth/elevation
  cuts, alongside the existing line chart. The UI requests a full phi sweep.
- Projected 3D radiation-pattern wireframe in a separate Pattern sub-tab.
- Azimuth polar plots show the antenna direction and default to the
  highest-gain elevation cut; above-ground elevation cuts use open arcs to
  avoid a misleading closed lobe.
- Per-wire segmentation overrides and a feed-aligned count heuristic; the UI
  derives counts from the selected model, gives short folded connectors at
  least three segments, and persists the overrides additively in schema v3.
- Palette-aware diagram theme: the geometry sketch and pyqtgraph charts follow
  the GUI light/dark palette, including backgrounds, axes, labels, grids, and
  series colors, with runtime updates when the palette changes.
- Renderer-neutral geometry scene and orthographic view policy: the sketch now
  projects the canonical wire model instead of synthesizing circles or lines
  per antenna type, with true front/plan views, shape-aware auto-selection,
  collision-aware dimension placement, detail insets, and a scriptable scene
  that can later feed SVG, PDF, or DXF export.
- Semantic construction dimensions for loops, folded dipoles, J Pole/Slim Jim,
  Ringo, Yagi, Moxon, end-fed, inverted-V, fan dipole, vertical, OCFD, and
  generic custom wires, including a gap detail inset for Slim Jim, a spacing
  detail inset for closely spaced folded dipoles, Moxon tip/gap dimensions,
  and a top inset for Ringo/radial verticals.
- Legacy custom generator designs keep their semantic Yagi/Vertical/summary
  labels instead of falling back to a generic wire count.
- The geometry header reports when low-priority dimensions had to be hidden
  for space at small window sizes.
- Vector geometry export to SVG and PDF from the same scene used by the
  on-screen sketch.
- `docs/GEOMETRY_PRESENTATION.md`: normative presentation contract, required
  tests, anti-patterns, and Definition of Done for new antenna families.
- Contract tests covering wire preservation, default views, dimension validity,
  layout collisions, presentation-type registration, and catalog routing for
  both New Antenna and Change Template.
- Angular construction dimensions for inverted-V and fan-dipole included
  angles, with collision-aware arc and label placement.
- Layered DXF export of the current geometry scene, including wires, feed/load
  markers, linear dimensions, angular dimensions, and a title, using `ezdxf`
  (MIT, GPL-3.0-compatible).
- Deterministic scene snapshots for every antenna family and 2D view, with an
  explicit update command for intentional shape changes.
- Performance-safe simulation defaults: 0.05λ segmentation target and 31-point
  sweeps for generated templates, fixing 60-second timeouts on large radial
  vertical models while keeping reference cases explicitly fine-segmented.
- Interactive isometric geometry rotation with mouse drag and double-click
  reset.

### Changed

- Release signing is optional and deferred for the initial release. Unsigned
  native packages are published with SHA-256 checksums; GPG and Authenticode
  hooks remain available for later releases.
- Refreshed the roadmap, README, architecture, domain-model, validation-plan,
  and user-guide status to reflect the completed catalog, estimators,
  measurements, optimization, matching, and packaging work.
- Removed redundant New Antenna, Open Project, and Save toolbar buttons; the
  actions remain available in the File menu and by keyboard shortcut.
- Added an optional uniform feed line with characteristic impedance, length,
  velocity factor, matched loss, transmitter-side impedance/SWR, project/run
  persistence, diagnostics, and dialog integration.
- Added a parametric Yagi generator with an editable element table, driven
  element selection, and an NBS TN-688 5-element starting preset.
- Added an experimental inverted-V generator with apex height, leg length,
  included angle, azimuth, geometry preview, and editable custom-wire output.
- Consolidated antenna creation into a searchable **New Antenna** catalog with
  an Antenna Type selector and family grouping; removed per-type New menu
  entries.
- Separated antenna Family from Template in the design panel, including
  generated custom designs.
- Reorganized the menu bar into File, Design, Simulation, Tools, Language,
  Units, and Help, with Import/Export, Variants, and Custom Wires submenus.
- Added an experimental vertical generator with an optional radial plane and
  catalog entry.
- Added generator editing for inverted-V designs, automatic elevation view for
  vertical-plane multi-wire geometry, and 100-point sweep controls for custom
  and generated designs.
- Added Change Template to replace the current design from the antenna catalog.
- Generalized Edit Generator to Yagi and vertical designs by reconstructing
  their parameters from custom geometry.
- Inverted-V now defaults to finite ground, and the 3D pattern view draws the
  ground plane for grounded models.
- Localized ground and material selector labels in the generator and custom
  antenna dialogs.
- Added drag rotation, wheel zoom, and double-click reset to the 3D radiation
  pattern view.
- Clip below-ground pattern points from the 3D view for grounded models.
- Fix the 3D projection so positive height is drawn above the ground plane in
  both pattern and geometry views.
- Increase the default radiation-pattern resolution from 10° to 5°, doubling
  the angular points per axis.
- Raise the vertical generator's default base/radial-plane height to 0.25 m to
  avoid numerical instability over finite ground.
- Added an experimental off-center-fed dipole generator with feed-offset,
  catalog, editing, and persistence integration.
- Promoted OCFD to a first-class template with an inline design-panel editor and
  native project persistence.
- Promoted Yagi, inverted-V, and vertical generators to first-class templates
  with inline editors, native persistence, and reporting support.
- Added inline editing, schema round trips, and reporting coverage for all
  first-class generators.
- Added delta-loop and quad-loop catalog presets that initialize the loop editor
  with three or four sides.
- Added an experimental first-class Moxon rectangle generator with inline
  editing, catalog, persistence, and reporting support.
- Added an experimental first-class fan dipole generator with editable pairs,
  catalog, persistence, and reporting support.
- Added an experimental first-class end-fed wire generator with optional sloping
  geometry, catalog, persistence, and reporting support.
- Added experimental first-class J Pole and Slim Jim generators with inline
  editors, catalog, persistence, and reporting support.
- Added an experimental first-class Ringo vertical with a base matching ring,
  catalog, persistence, and reporting support.
- Raised J Pole and Ringo default base/ring heights to 0.25 m so their ground
  connectors do not lie in the finite-ground plane.
- Added dedicated J Pole and Slim Jim plan/elevation views with radiator, stub,
  spacing, and template-specific labels.
- Fixed Slim Jim geometry headers when the antenna model name is the generic
  variant name.
- Corrected Slim Jim topology: a folded rectangle with horizontal top and
  bottom connectors and a gap in one vertical leg between the radiator and
  matching stub.
- Placed the impedance and SWR charts side by side and reduced the default
  geometry pane height to give results more room.
- Change Template is always reachable from the Design menu and with
  Ctrl+Shift+T.
- Added VNA CSV import for R/X, S11 real/imaginary, and magnitude/phase data,
  persisted measurements, measurement conditions/reference plane, and a
  measured/simulated SWR tab.
- Persist generator metadata (`generator_id`, `generator_name`) in custom
  designs and show it in the custom design panel.
- Fixed NEC `EX` source segment numbering for feeds on tags other than the
  first wire.
- Length optimization is generalized to the primary dimension: wire/folded
  element length or loop circumference. `EditDipoleLength` remains limited to
  wire dipoles.
- Optimization objective selector: target reactance, minimum SWR, maximum SWR
  bandwidth, maximum power gain, maximum efficiency, or balanced SWR + gain,
  with objective-specific limits, weights, and grid resolution.
- Added bounded two-variable impedance synthesis for OCFD, J Pole, and Slim Jim
  designs. It searches length/feed ratio or radiator/feed-offset (stub for Slim
  Jim) over user bounds, evaluates at the target frequency, and applies the best
  dimensions for a full validation sweep.
- Added a target-impedance objective to dimension optimization. It accepts a
  selectable complex target `R + jX` and ranks candidates by impedance error;
  OCFD and end-fed wire designs can now be length-optimized against that
  target.
- Optimization and synthesis result tables are ranked from best to worst by the
  active objective, with a visible rank column, the original evaluation number,
  and failed evaluations last. Synthesis rows also show the complex impedance
  error against the target.
- Measurement comparison now plots measured and simulated SWR, resistance,
  reactance, or impedance magnitude, and reports measured/simulated series
  resonances with their frequency difference.
- Measurements can now be edited (metadata and conditions) and deleted from
  the Measurements tab, with project persistence and confirmation before
  deletion.
- Added a reference-backed Moxon validation test using the published 20 m wire
  dimensions and free-space gain, impedance, and front-to-back values from
  L. B. Cebik, W4RNL.
- Added a published/heuristic OCFD sanity test for the 0.2 L feedpoint
  resistance range and the documented trend toward lower R as the feed moves
  toward the centre.
- Fixed the frequency-first J Pole estimate: the non-folded J Pole now uses the
  total 3/4-wave height and a 40% stub feed point; Slim Jim keeps its half-wave
  radiator estimate.
- Added parameterized domain and NEC smoke tests for every frequency-first
  estimator, including folded dipole, end-fed, OCFD, Ringo, J Pole/Slim Jim,
  Yagi, Moxon, loops, verticals, inverted-V, and fan dipoles.
- Recalibrated the Ringo estimator for the simplified Ringo geometry, improving
  the 146 MHz estimate from a very high SWR to approximately 1.3.
- Added a **Load 20 m wire reference preset** button to the Moxon editor and
  marked that preset as reference-backed in the catalog.
- Added a bounded multi-variable coordinate-search optimizer in the domain.
- Added the first multi-element Yagi workflow: select element lengths and boom
  gaps, set a target R/X, constrain the search around the current dimensions,
  enforce a minimum gap and keep the first element fixed, review a ranked
  evaluation table, and apply the best geometry for a full simulation. Radii
  remain fixed in this slice.
- Yagi optimization now supports target impedance, maximum power gain, and
  maximum front-to-back ratio objectives. Gain and F/B evaluations use the
  far-field pattern; the ranked table reports the selected objective.
- Added bounded fan-dipole element-length optimization against a target
  impedance, with selectable elements, search bounds, ranked evaluations, and
  apply-and-simulate flow.
- Added bounded Moxon optimization of width, spacing, reflector tip, and driven
  tip for target impedance, maximum gain, or maximum front-to-back ratio.
- Unified the Yagi, fan-dipole, and Moxon element optimizers on a shared
  bounded evaluation engine while keeping their template-specific dialogs.
- The shared engine now drives a generic multi-element dialog used by Yagi,
  fan-dipole, and Moxon optimization, with template-specific variables and
  builders.
- Added a weighted multi-objective mode for multi-element optimization,
  combining gain, front-to-back, SWR penalty, and efficiency with transparent
  user weights.
- Multi-objective results now include a Pareto rank column, with successive
  non-dominated fronts computed from the selected metrics.
- Optimization result rows can be selected to apply a specific candidate or
  Pareto compromise instead of only the best weighted score.
- Multi-element optimization supports integer variables; vertical radial count,
  loop side count, and Ringo ring sides are searched discretely.
- Yagi optimization can include element count as a discrete variable. Added
  directors follow the DL6WU reference scaled to frequency, the driven element
  is preserved, and gaps keep a fixed 0.1 m minimum.
- Loop optimization now preserves the selected loop shape and side count, and
  documents that full-wave loops normally need a balun or matching network for
  a 50 Ω system.
- The loop estimator applies a NEC-2-calibrated polygon correction, so quad,
  delta, and generic loops start near resonance instead of several percent
  short. The loop optimizer starts its target resistance at 100 Ω for a 2:1
  balun.
- Target-impedance searches report SWR relative to the target resistance;
  folded dipoles, loops, OCFDs, and 5/8-wave verticals now show their matching
  limitation explicitly.
- Removed the obsolete template-specific optimization dialogs and workers; the
  generic dialog is now the only multi-element optimization UI.
- Replaced the separate optimization menu actions with one **Optimize...**
  action that dispatches from the current template, plus an Optimize button in
  the design panel. Frequency-first estimation is now **Estimate Dimensions...**.
- Added the AntennaDesk application icon and a Linux desktop-entry file for
  release packaging.
- Added a lossless L matching network evaluated before the feed line, with
  project/run persistence and impedance/SWR diagnostics.
- The matching-network dialog can auto-design an L section from a load R/X at
  the design frequency, or report that a single L section cannot match it.
- Matching-network support now includes manual Pi and T topologies with
  project/run persistence and input-impedance evaluation.
- Matching networks can include component loss through a Q factor; loss is
  reflected in input impedance/SWR, not in reported antenna gain.
- Added a parallel-trap helper to the load editor that computes capacitance from
  inductance and resonant frequency.

- Documentation and README are now in English.

### Fixed

- Geometry view now resets zoom, pan, and vertical exaggeration when the model
  changes, so switching antennas always fits the new drawing.
- Change Template now handles the Delta loop and Quad loop catalog entries and
  opens the loop wizard with 3 or 4 sides instead of silently keeping the
  previous design.
- Quad and delta loops are drawn as their real polygons; vertical loops use a
  front view and their plan view is correctly shown edge-on.
- End-fed sloping wires, Yagi/Moxon elements, Ringo rings, J Pole stubs, and
  loads are no longer collapsed or hidden by type-specific shortcuts.
- Slim Jim feed offset is measured from the stub base, and loop top height is
  exact for odd side counts and rotated azimuths.
- End-fed wire length now means the physical conductor length, not just its
  horizontal run; steep slopes are rejected when they exceed the wire length.
- Dimension labels are measured, prioritized, and placed with collision
  avoidance; units and translations are rebuilt on change.
- The geometry compass labels the X/Y axes, matching the documented +X toward
  +Y azimuth convention.

## [0.1.0.dev0] - 2026-10-29

### Added

- Phase 0 solver spike selecting `nec2c 1.3.3` as the external NEC-2 engine.
- Reproducible reference cases from the NEC-2 User's Guide.
- Linux and Windows build scripts, including a Windows portability patch.
- GitHub Actions workflow for the solver spike.
- Project documentation: blueprint, ADR-0001, project decisions, and solver
  evaluation.

[Unreleased]: https://github.com/fsclavo/antenna-desk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.1.0
[0.1.0.dev0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.1.0.dev0
