# AntennaDesk

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** Phase 6 in progress. Horizontal and vertical center-fed dipoles,
folded dipoles, and regular-polygon loops are supported, with schema v3
persistence and migration. VNA CSV import and measurement comparison are next.

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
immediately. Use **File → New Antenna...** for the guided wizard. The wizard
starts with the antenna type currently selected in the design panel and offers
wire dipole, folded dipole, and loop. The panel also converts an existing design
between those types.

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
- [ADR-0006 — Series RLC loads](docs/ADR/0006-series-loads.md)
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
  radiation-pattern wireframe.
- Save/open of versioned `.antennadesk` projects with multiple design
  variants; schema v3 adds persisted simulation runs and migrates older files.
- A/B variant comparison with metrics, SWR charts, and pattern overlays.
- Currents tab and resonance markers on impedance/SWR sweeps.
- Bounded antenna-dimension optimization for a target reactance, minimum SWR,
  or maximum SWR bandwidth: wire-dipole and folded-dipole element length, or
  loop circumference, with an evaluation log and sensitivity table.
- Series and parallel RLC loads on wires, with a load editor, NEC `LD 0`/`LD 1`
  export, and report rows.
- Printable/HTML construction sheet with type-aware dimensions, feed position,
  loads, and simulated result.
- CSV export and self-contained HTML reports (use the browser print dialog for
  PDF).
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
  networks, transmission lines, and radial ground screens are not implemented.
- Simulation runs are stored in the project, including raw solver text; the
  native project size limit is 10 MB. Use Compact Simulation History to keep
  only the latest run per variant.
- Optimization is limited to one primary dimension per design against a single
  reactance, SWR, or bandwidth objective. It does not optimize gain, efficiency,
  or multi-objective trade-offs yet.
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
