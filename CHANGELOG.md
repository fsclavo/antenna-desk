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

### Changed

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
