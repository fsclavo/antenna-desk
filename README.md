# AntennaDesk

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** pre-alpha. The antenna catalog, estimators, simulation,
measurements, optimization, matching, and reporting flows are implemented.
Native AppImage, Debian, and Windows packages include `nec2c`. Version `0.1.0`
is published; signing is optional and deferred for later releases. Center-fed
dipoles, folded dipoles, trap dipoles, loops, custom wires, Yagis, Moxon, fan
dipoles, inverted-Vs, OCFDs, end-fed wires, slopers, random wires, doublets,
J Poles, Slim Jims, Ringos, verticals, and loaded verticals are supported, with
schema v3 persistence and migration. VNA CSV import and measured/simulated
comparison are available.

## Launch the GUI

The GUI uses `nec2c` for simulation. Build it once:

```bash
bash spikes/phase0/scripts/build_nec2c.sh
```

On Windows, build it with the MSYS2/UCRT64 script:

```bash
bash spikes/phase0/scripts/build_nec2c_windows.sh
```

Install the Python environment and launch the application:

```bash
uv sync
uv run python -m antennadesk
```

The application looks for `nec2c` in `NEC2C`, on `PATH`, and in
`spikes/phase0/build/`. If it is not found, use **Tools → Locate NEC2C...** to
select the executable.

On first launch, a 40 m dipole is loaded so you can press **Simulate**
immediately. Use **File → New Antenna...** to open the antenna catalog, search
by type, and choose a wire dipole, folded dipole, loop, Yagi, inverted-V, or
custom-wire design. The panel also converts an existing design between the
basic template types.

## Installation and release

Native packages:

- Linux AppImage: `AntennaDesk-<version>-x86_64.AppImage`, built with
  `packaging/build_appimage.sh`.
- Debian/Ubuntu: `antennadesk_<version>_amd64.deb`, built with
  `packaging/build_deb.sh`.
- Windows: `AntennaDesk-<version>-windows-x86_64.zip`, built with
  `packaging/build_windows.ps1`.

All native packages include `nec2c`. Install from a wheel when you manage the
solver yourself:

```bash
python -m pip install dist/antennadesk-*.whl
```

See [Release checklist](docs/RELEASE.md) for build, smoke-test, checksum, and
optional signing steps.

## Documentation

- [Development blueprint](docs/antennadesk-development-blueprint.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Solver adapter](docs/SOLVER_ADAPTER.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [User guide](docs/USER_GUIDE.md)
- [Release checklist](docs/RELEASE.md)
- [Confirmed project decisions](docs/PROJECT_DECISIONS.md)
- [ADR-0001 — MVP engine](docs/ADR/0001-solver-selection.md)
- [ADR-0002 — Report and export formats](docs/ADR/0002-report-formats.md)
- [ADR-0003 — Project schema v2 and dipole orientation](docs/ADR/0003-project-schema-v2.md)
- [ADR-0004 — Simulation run persistence](docs/ADR/0004-simulation-run-persistence.md)
- [ADR-0005 — Folded dipole and loop templates](docs/ADR/0005-new-wire-geometries.md)
- [ADR-0006 — Series and parallel RLC loads](docs/ADR/0006-series-loads.md)
- [ADR-0007 — Custom wire designs](docs/ADR/0007-custom-wire-designs.md)
- [ADR-0008 — Feed-line post-processing](docs/ADR/0008-feed-line-post-processing.md)
- [ADR-0009 — Catalog and experimental templates](docs/ADR/0009-catalog-and-experimental-templates.md)
- [ADR-0010 — First-class generator templates](docs/ADR/0010-first-class-generator-templates.md)
- [ADR-0011 — Bounded impedance synthesis](docs/ADR/0011-bounded-impedance-synthesis.md)
- [ADR-0012 — Geometry presentation and dimension layout](docs/ADR/0012-geometry-presentation.md)
- [ADR-0013 — Frequency-first dimension estimation](docs/ADR/0013-frequency-first-dimension-estimation.md)
- [ADR-0014 — Undo/Redo and chart cursors](docs/ADR/0014-undo-redo-and-chart-cursors.md)
- [ADR-0015 — Realized gain and directivity](docs/ADR/0015-realized-gain-and-directivity.md)
- [ADR-0016 — Transmission line as geometry](docs/ADR/0016-transmission-line-as-geometry.md)
- [ADR-0017 — Simulation storage budget](docs/ADR/0017-simulation-storage-budget.md)
- [Antenna dimension estimators](docs/ANTENNA_DESIGN_ESTIMATORS.md)
- [Geometry presentation contract](docs/GEOMETRY_PRESENTATION.md)
- [NEC engine evaluation](docs/spikes/phase0-solver-evaluation.md)
- [Phase 0 reproducible spike](spikes/phase0/README.md)
- [Agent instructions](AGENTS.md)
- [Changelog](CHANGELOG.md)

## What exists today

- Frequency-first dimension estimates for the families with a documented
  estimator, with assumptions, confidence, and optional numerical refinement.
- Project-level Undo/Redo and hover cursors on the result charts.
- Guided antenna wizard and a main window with a design panel, a shape-aware
  construction sketch with a collision-aware dimension layout, front/plan
  orthographic views, detail insets, an isometric 3D view, and results tabs.
- Asynchronous simulation with cancellation, timeouts, and diagnostics.
- Impedance, SWR, frequency-sweep, and far-field pattern charts, including
  selectable azimuth/elevation cuts, polar lobe diagrams, and an isometric 3D
  radiation-pattern wireframe colored by gain with a dBi legend and a takeoff
  angle at the maximum-gain marker. Sweeps use 100
  points by default, and pattern resolution defaults to 5° and can be set to
  10°, 5°, 2°, or 1°.
- Save/open of versioned `.antennadesk` projects with multiple design
  variants; schema v3 adds persisted simulation runs and migrates older files.
- A/B variant comparison with metrics, SWR charts, and pattern overlays.
- VNA CSV import with measured impedance/SWR records and a measured/simulated
  SWR, R, X, or |Z| comparison tab, including resonance differences.
- Currents tab and resonance markers on impedance/SWR sweeps.
- Bounded antenna-dimension optimization for a selectable target impedance
  `R + jX`, target reactance, minimum SWR, maximum SWR bandwidth, maximum power
  gain, maximum efficiency, or a weighted SWR/gain balance: wire-dipole,
  folded-dipole, OCFD, end-fed wire, or loop dimensions, with an evaluation
  log, ranked result table, and sensitivity table.
- Bounded two-variable impedance synthesis for OCFD, J Pole, and Slim Jim
  designs, with a target frequency/R/X, evaluation log, and apply-and-simulate
  flow.
- Bounded multi-element optimization for target impedance, maximum gain,
  maximum front-to-back ratio, or a weighted gain/F-B/SWR/efficiency score,
  with template-specific variables, integer variables (including Yagi element
  count), Pareto ranks, candidate selection, and apply-and-simulate flow.
- Bounded fan-dipole element-length optimization against a target impedance.
- Bounded Moxon optimization of width, spacing, and tip dimensions for target
  impedance, gain, or front-to-back ratio.
- Custom straight-wire antennas with a coordinate editor, template-to-custom
  conversion, a parametric Yagi generator with an editable element table and
  NBS starting preset, Moxon, fan dipole, end-fed with optional counterpoise
  and transformer, J Pole, Slim Jim, Ringo, inverted-V, off-center-fed dipole,
  and vertical generators, experimental ground radial generator, practical
  NEC-2 deck import, and basic MMANA-GAL `.maa` geometry import, plus
  series/parallel RLC loads, load markers, and report rows.
- Optional transmitter-side feed line with characteristic impedance, length,
  velocity factor, matched loss, and transformed impedance/SWR.
- Optional L/Pi/T matching networks at the feedpoint, with automatic L design
  from a load R/X, optional component Q/loss, evaluation before the feed line,
  and a parallel-trap helper in the load editor.
- Printable/HTML construction sheet with type-aware dimensions, feed position,
  loads, and simulated result.
- CSV, PNG, SVG, PDF, and layered DXF export for results, patterns, and
  geometry, plus self-contained HTML/PDF reports.
- English and Spanish UI, plus metric and imperial presentation units.
- Immutable domain model for units, geometry, conductors, feed points, ground
  models, environments, wire dipoles, folded dipoles, and regular-polygon
  loops.
- Versioned JSON persistence with atomic saves and a migration framework.
- A `nec2c` solver adapter with input generation, output parsing, SWR
  normalization, currents, power budget, and far-field patterns.
- Numerical validation against NEC-2 User's Guide examples and selected ARRL
  Antenna Book properties.
- Unit, integration, UI, and acceptance tests.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

The UI tests run offscreen through `pytest-qt`; no display is required.

To run the real solver integration tests, build `nec2c` and point `NEC2C` at
the executable:

```bash
bash spikes/phase0/scripts/build_nec2c.sh
NEC2C=spikes/phase0/build/nec2c uv run pytest tests/integration/simulation
```

To run the reference dipole through the production adapter:

```bash
uv run python scripts/run_reference_simulation.py \
  --nec2c spikes/phase0/build/nec2c
```

## Known limitations

- All catalog families are implemented, but some remain experimental or
  heuristic. Folded dipoles still lack an independent impedance reference;
  loops have the ARRL quad-loop resistance check. VNA CSV import and
  measurement comparison are implemented; live instrument control is not.
- Series and parallel RLC loads are supported on one wire segment. L/Pi/T
  matching networks are post-processed at the feedpoint, and the vertical
  generator supports a radial screen. General transmission-line geometry and
  arbitrary radial screens are not modeled. The feed line is a uniform
  post-processing model; it does not change the antenna pattern or power gain.
- Optimization covers primary-dimension, multi-element, integer, and Pareto
  searches for generated templates. Custom/imported designs are excluded, and
  there are no boom-length or turning-radius constraints. Synthesis is a
  bounded starting point, not a global inverse solver.
- Far-field values are NEC power gains. Realized gain and directivity are not
  separated. Relative permeability is not emitted to NEC. Conductor
  conductivity is emitted when `SimulationSpec.include_conductor_losses` is
  true.
- The end-fed feed transformer is an ideal impedance ratio, not a physical
  unun model. Its counterpoise is geometry, not an ideal ground plane.
- Native packages include `nec2c`. The initial release is unsigned; verify the
  published SHA-256 checksums. Optional GPG and Windows Authenticode signing
  hooks are available for later releases. The wheel/sdist remains available for
  users who manage the solver themselves.
- Simulation runs are stored in the project, including raw solver text; the
  native project size limit is 10 MB. Use **Tools → Compact Simulation History**
  to keep only the latest run per variant. High-resolution patterns and long
  sweeps multiply runtime and stored points.
- The segmentation policy is a documented heuristic; explicit counts are used
  for reference cases. The UI derives per-wire counts and aligns the feed wire
  to a segment center.
- Known diagnostic codes are localized in the UI; the raw solver detail remains
  available in English in the tooltip and raw-output tab.
- PySide6 is pinned below 6.10 because 6.12 triggered a shutdown refcount crash
  with pyqtgraph in this environment.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
