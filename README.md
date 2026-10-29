# AntennaDesk

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** Phase 4 complete (variant comparison and reports). Phase 5
(optimization and construction) is next.

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
immediately. Use **File → New Dipole...** for the guided wizard.

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
- [NEC engine evaluation](docs/spikes/phase0-solver-evaluation.md)
- [Phase 0 reproducible spike](spikes/phase0/README.md)
- [Agent instructions](AGENTS.md)
- [Changelog](CHANGELOG.md)

## What exists today

- Guided dipole wizard and a main window with a design panel, dimensioned
  construction-sketch geometry (elevation and plan views), and results tabs.
- Asynchronous simulation with cancellation, timeouts, and diagnostics.
- Impedance, SWR, frequency-sweep, and far-field pattern charts.
- Save/open of versioned `.antennadesk` projects with multiple design
  variants.
- A/B variant comparison with metrics, SWR charts, and pattern overlays.
- Currents tab and resonance markers on impedance/SWR sweeps.
- CSV export and self-contained HTML reports (use the browser print dialog for
  PDF).
- English and Spanish UI, plus metric and imperial presentation units.
- Immutable domain model for units, geometry, conductors, feed points, ground
  models, environments, and horizontal half-wave dipoles.
- Versioned JSON persistence with atomic saves and a migration framework.
- A `nec2c` solver adapter with input generation, output parsing, SWR
  normalization, currents, power budget, and far-field patterns.
- Numerical validation against the NEC-2 User's Guide examples.
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

- Only horizontal center-fed dipoles are implemented in the wizard and design
  panel.
- No loads, networks, transmission lines, or radial ground screens.
- Simulation results are session-only. Reopening a project clears them;
  comparison and reports require results simulated in the current session.
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.
- Native PDF export is deferred; HTML reports can be saved as PDF from a
  browser.
- The segmentation policy is a documented heuristic; explicit counts are used
  for reference cases.
- Domain and solver diagnostic messages are currently reported in English;
  their codes are stable and can be translated in a later phase.
- PySide6 is pinned below 6.10 because 6.12 triggered a shutdown refcount
  crash with pyqtgraph in this environment.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
