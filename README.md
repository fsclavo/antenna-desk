# AntennaDesk

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** Phase 2 complete (solver adapter and numerical references). Phase 3
(guided MVP and GUI) is next. The GUI is not implemented yet.

## Documentation

- [Development blueprint](docs/antennadesk-development-blueprint.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Solver adapter](docs/SOLVER_ADAPTER.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [Confirmed project decisions](docs/PROJECT_DECISIONS.md)
- [ADR-0001 — MVP engine](docs/ADR/0001-solver-selection.md)
- [NEC engine evaluation](docs/spikes/phase0-solver-evaluation.md)
- [Phase 0 reproducible spike](spikes/phase0/README.md)
- [Agent instructions](AGENTS.md)
- [Changelog](CHANGELOG.md)

## What exists today

- Immutable domain model for units, geometry, conductors, feed points, ground
  models, environments, and horizontal half-wave dipoles.
- Validated project and design-variant model.
- Versioned `.antennadesk` JSON format with atomic saves and a migration
  framework.
- Use cases to create, save, open, and edit a dipole length.
- A [40 m dipole example](examples/dipole_40m.antennadesk).
- A `nec2c` solver adapter with input generation, process execution,
  cancellation, timeouts, output parsing, SWR normalization, currents,
  power budget, and far-field patterns.
- Numerical validation against the NEC-2 User's Guide examples.
- Unit, integration, and acceptance tests.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

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

## Phase 0 engine spike

The MVP uses **nec2c 1.3.3** as an external process, pinned by commit and
shipped with a maintained Windows portability patch. The validation reproduces
the examples printed in the NEC-2 User's Guide and runs on Linux and Windows
(CI: 19/19 checks).

```bash
bash spikes/phase0/scripts/build_nec2c.sh
python3 spikes/phase0/scripts/run_reference.py --nec2c spikes/phase0/build/nec2c
```

## Known limitations

- The GUI is not implemented.
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.
- No loads, networks, transmission lines, or radial ground screens.
- Simulation results are not persisted in the project file yet.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
