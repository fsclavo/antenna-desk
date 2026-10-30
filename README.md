# AntennaDesk

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** active antenna catalog development. Center-fed dipoles, folded
dipoles, regular-polygon loops, custom wires, Yagis, and inverted-Vs are
supported, with schema v3 persistence and migration. VNA CSV import and
measurement comparison are deferred.

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
`spikes/phase0/build/`. If it is not found, use **File → Locate NEC2C...** to
select the executable.

On first launch, a 40 m dipole is loaded so you can press **Simulate**
immediately. Use **File → New Antenna...** to open the antenna catalog, search
by type, and choose a wire dipole, folded dipole, loop, Yagi, inverted-V, or
custom-wire design. The panel also converts an existing design between the
basic template types.

## Documentation

- [Development blueprint](docs/antennadesk-development-blueprint.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Solver adapter](docs/SOLVER_ADAPTER.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [User guide](docs/USER_GUIDE.md)
- [Confirmed project decisions](docs/PROJECT_DECISIONS.md)
- [ADR-0001 — MVP engine](docs/ADR/0001-solver-selection.md)
- [ADR-0002 — Report and export formats](docs/ADR/0002-report-formats.md)
- [ADR-0003 — Project schema v2 and dipole orientation](docs/ADR/0003-project-schema-v2.md)
- [ADR-0004 — Simulation run persistence](docs/ADR/0004-simulation-run-persistence.md)
- [ADR-0005 — Folded dipole and loop templates](docs/ADR/0005-new-wire-geometries.md)
- [ADR-0006 — Series and parallel RLC loads](docs/ADR/0006-series-loads.md)
- [ADR-0007 — Custom wire designs](docs/ADR/0007-custom-wire-designs.md)
- [NEC engine evaluation](docs/spikes/phase0-solver-evaluation.md)
- [Phase 0 reproducible spike](spikes/phase0/README.md)
- [Agent instructions](AGENTS.md)
- [Changelog](CHANGELOG.md)

## What exists today

- Guided antenna wizard and a main window with a design panel, construction
  dimensions in Plan view, installation/height details in Elevation view, an
  isometric 3D view, and results tabs.
- Asynchronous simulation with cancellation, timeouts, and diagnostics.
- Impedance, SWR, frequency-sweep, and far-field pattern charts, including
  selectable azimuth/elevation cuts, polar lobe diagrams, and an isometric 3D
  radiation-pattern wireframe. Sweeps use 100 points by default, and pattern
  resolution can be set to 10°, 5°, 2°, or 1°.
- Save/open of versioned `.antennadesk` projects with multiple design
  variants; schema v3 adds persisted simulation runs and migrates older files.
- A/B variant comparison with metrics, SWR charts, and pattern overlays.
- Currents tab and resonance markers on impedance/SWR sweeps.
- Bounded antenna-dimension optimization for a target reactance, minimum SWR,
  maximum SWR bandwidth, maximum power gain, maximum efficiency, or a weighted
  SWR/gain balance: wire-dipole and folded-dipole element length, or loop
  circumference, with an evaluation log and sensitivity table.
- Custom straight-wire antennas with a coordinate editor, template-to-custom
  conversion, a parametric Yagi generator with an editable element table and
  NBS starting preset, an inverted-V generator, experimental ground radial
  generator, practical NEC-2
  deck import, and basic MMANA-GAL `.maa` geometry import, plus series/parallel
  RLC loads, load markers, and report rows.
- Optional transmitter-side feed line with characteristic impedance, length,
  velocity factor, matched loss, and transformed impedance/SWR.
- Printable/HTML construction sheet with type-aware dimensions, feed position,
  loads, and simulated result.
- CSV/PNG export for sweep results, far-field patterns, and geometry, plus
  self-contained HTML/PDF reports.
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

- Horizontal and vertical center-fed dipoles, folded dipoles, and
  regular-polygon loops are implemented. Folded and loop templates currently
  have theoretical sanity tests but no published independent impedance
  reference; VNA CSV import and measurement records are not implemented yet.
- Series and parallel RLC loads are supported on one wire segment; general
  matching networks and radial ground screens are not implemented. The feed
  line is a uniform line model evaluated at the transmitter; it does not change
  the antenna pattern or power gain.
- Simulation runs are stored in the project, including raw solver text; the
  native project size limit is 10 MB. Use Compact Simulation History to keep
  only the latest run per variant. High-resolution patterns and long sweeps
  multiply runtime and stored points.
- Optimization adjusts one primary dimension per design. It supports one
  reactance, SWR, bandwidth, gain, or efficiency objective, or a weighted
  SWR/gain score; it does not expose a Pareto front or optimize several
  dimensions at once.
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.
- Simulation reports and construction sheets have native PDF export; HTML
  versions remain available.
- The segmentation policy is a documented heuristic; explicit counts are used
  for reference cases. The UI derives per-wire counts and aligns the feed wire
  to a segment center.
- Known diagnostic codes are localized in the UI; the raw solver detail
  remains available in English in the tooltip and raw-output tab.
- PySide6 is pinned below 6.10 because 6.12 triggered a shutdown refcount
  crash with pyqtgraph in this environment.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
