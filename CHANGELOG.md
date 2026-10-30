# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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

### Changed

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
- Placed the impedance and SWR charts side by side and reduced the default
  geometry pane height to give results more room.
- Moved Change Template to a fixed button above the design panel so it is always
  reachable.
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

- Documentation and README are now in English.

## [0.1.0.dev0] - 2026-10-29

### Added

- Phase 0 solver spike selecting `nec2c 1.3.3` as the external NEC-2 engine.
- Reproducible reference cases from the NEC-2 User's Guide.
- Linux and Windows build scripts, including a Windows portability patch.
- GitHub Actions workflow for the solver spike.
- Project documentation: blueprint, ADR-0001, project decisions, and solver
  evaluation.

[Unreleased]: https://github.com/fsclavo/antenna-desk/compare/v0.1.0.dev0...HEAD
[0.1.0.dev0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.1.0.dev0
