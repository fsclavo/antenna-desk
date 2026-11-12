# AntennaDesk

[![Tests](https://img.shields.io/github/actions/workflow/status/fsclavo/antenna-desk/ci.yml?branch=main&label=tests)](https://github.com/fsclavo/antenna-desk/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/fsclavo/antenna-desk?label=release&sort=semver)](https://github.com/fsclavo/antenna-desk/releases/latest)

**Developed by Fernando Sclavo (LU2EFI).**

Desktop application for designing, simulating, and building antennas for
amateur radio. Local-first, Linux and Windows, powered by a NEC-2
electromagnetic engine.

**Status:** pre-alpha. The antenna catalog, estimators, simulation,
measurements, optimization, matching, and reporting flows are implemented.
Native AppImage, Debian, and Windows packages include `nec2c`. Version `0.5.0`
is published; signing is optional and deferred for later releases. Center-fed
dipoles, folded dipoles, trap dipoles, T2FDs, vertical and horizontal loops,
magnetic loops, custom wires, Yagis, Moxon, fan dipoles, inverted-Vs,
inverted-Ls, OCFDs,
end-fed wires, slopers, random wires, doublets, J Poles, Slim Jims, Ringos,
half squares, bobtail curtains, biquads, double biquads, Beverage receiving
wires, loaded/linked dipoles, verticals, and loaded verticals are supported.
Yagi and Moxon arrays support horizontal or vertical polarization with a
horizontal boom, plus optional folded driven elements and beta/hairpin
matching stubs. Projects use versioned JSON persistence, lossless gzip
compression, and explicit migrations. VNA CSV import
and measured/simulated comparison are available.

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

AntennaDesk opens on the **Start an antenna project** page. Choose
**New Antenna...** to open the antenna catalog, search by family, and create the
first design, or **Open Project...** to load an existing `.antennadesk` file.
After a project exists, the template is shown read-only in the design panel;
use **Change...** next to it or **Design → Change Template...** to replace the
current design with another catalog template.

## Installation and release

Native packages:

- Linux AppImage: `AntennaDesk-<version>-x86_64.AppImage`, built with
  `packaging/build_appimage.sh`.
- Debian/Ubuntu: `antennadesk_<version>_amd64.deb`, built with
  `packaging/build_deb.sh`.
- Windows installer:
  `AntennaDesk-<version>-windows-x86_64-setup.exe`, built with
  `packaging/build_windows.ps1` and NSIS.
- Windows portable: `AntennaDesk-<version>-windows-x86_64.zip`, built by the
  same script.

The Windows installer creates Start Menu and Desktop shortcuts and registers an
uninstaller in Add/Remove Programs. The portable zip remains available for
users who do not want a system installation.

All native packages include `nec2c`. Install from a wheel when you manage the
solver yourself:

```bash
python -m pip install dist/antennadesk-*.whl
```

See [Release checklist](docs/RELEASE.md) for build, smoke-test, checksum, and
optional signing steps.

## Documentation

Start with the [documentation index](docs/README.md). It lists the source of
truth for each topic, every ADR, and the archived plans.

- [User guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Solver adapter](docs/SOLVER_ADAPTER.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [Evidence audit](docs/EVIDENCE_AUDIT.md)
- [Roadmap and antenna backlog](docs/ROADMAP.md)
- [Active execution backlog](docs/AUTONOMOUS_BACKLOG.md)
- [Release checklist](docs/RELEASE.md)
- [Confirmed project decisions](docs/PROJECT_DECISIONS.md)
- [Changelog](CHANGELOG.md)

## What exists today

- Frequency-first dimension estimates for the families with a documented
  estimator, with assumptions, confidence, and optional numerical refinement.
- Project-level Undo/Redo and hover cursors on the result charts.
- Antenna catalog with direct per-template editors and a main window with a
  design panel, a shape-aware construction sketch with a collision-aware
  dimension layout, front/plan orthographic views, detail insets, an isometric
  3D view, and results tabs.
- Asynchronous simulation with cancellation, timeouts, and diagnostics.
- Multiband analysis with family defaults, per-band solver runs, a **Bands**
  results tab, and band-aware CSV/HTML/PDF summaries.
- Optional ideal OCFD feed transformer, defaulting to 4:1 for new designs, with
  raw-impedance and transformed SWR/realized-gain views.
- Impedance, SWR, frequency-sweep, and far-field pattern charts, including
  selectable azimuth/elevation cuts, polar lobe diagrams, and an isometric 3D
  radiation-pattern wireframe colored by gain with a dBi legend and a takeoff
  angle at the maximum-gain marker. Sweeps use 100
  points by default, and pattern resolution defaults to 5° and can be set to
  10°, 5°, 2°, or 1°.
- Save/open of versioned `.antennadesk` projects with multiple design
  variants; schema version 24 adds the optional multi-source antenna model,
  schema 23 adds optional tapered Yagi tips, schema 22 adds
  optional wire sag on horizontal dipoles, schema 21 adds loaded/linked
  dipoles, schema 20 adds Beverage receiving wires, schema 19 adds biquad and
  double-biquad designs, schema 18 adds persisted optimization summaries,
  schema 17 adds typed G5RV, ZS6BKW, and Zepp designs, schema 16 adds
  half-square and bobtail-curtain designs, schema 15 adds frequency-dependent
  balun/unun loss and repairs undersized Yagi matching hardware, and older files
  migrate explicitly.
- A/B variant comparison with metrics, SWR charts, and pattern overlays.
- VNA CSV import with measured impedance/SWR records and a measured/simulated
  SWR, R, X, or |Z| comparison tab, including resonance differences.
- Currents tab and resonance markers on impedance/SWR sweeps.
- Family-driven antenna optimization with one explicit descriptor per typed
  family, no generic fallback, and a joint deterministic differential-evolution
  plus local-search engine. Every geometry, feed, and family-load variable is
  searched together; topology remains a user choice. Supported families include
  dipoles, loops, verticals, inverted-V/L, J Pole, Ringo, SCV, biquad, Beverage,
  loaded/linked dipole, OCFD, EndFed, fan/trap/T2FD, Yagi, and Moxon, with
  target impedance, minimum SWR, maximum gain, maximum front-to-back, maximum
  efficiency, maximum bandwidth, and weighted multi-objective scores.
- Balanced, thorough, and fast optimizer budgets with automatic extension,
  evaluation counting, deterministic seeds, ranked result tables, sensitivity
  reports, and Apply Best routed through an exhaustive editor adapter.
- **CSV export** of the ranked optimizer evaluation log, including metrics,
  errors, Pareto flags, and design variables.
- Optional **maximum turning radius** for every family and **maximum boom
  length** for Yagi/Moxon arrays. Candidates outside the mechanical limits are
  rejected and reported, and the limits are saved with the optimization
  summary.
- Band-aware and robust optimization modes, a descriptive Pareto front,
  deterministic post-run recommendations, and a compact run summary persisted
  with the design so the result can be audited without storing every
  evaluation.
- Optional **tapered Yagi element tips**: a shared tip length and smaller tip
  radius add two outer segments to every element. The model does not include a
  boom-mounting correction; use published or measured element lengths.
- Optional **wire sag** on horizontal wire dipoles: the straight span is
  replaced by a sampled parabolic path with the feed at the center segment, a
  sag dimension in the scene, and a conductor-length report. Other families
  remain straight until their sag model is added.
- First-class **Loaded / linked dipole** with symmetric series loading coils
  or open links that leave only the center section active. It includes a
  portable starting geometry, inline editing, reports, and a family optimizer;
  coil Q is derived from an explicit series resistance.
- First-class **Beverage** receiving wire with a one-wavelength starting
  length, optional resistive termination to ground, inline editor, reports, and
  a family optimizer. It is an experimental low-gain receiving model, not a
  validated pattern or gain reference.
- First-class **Biquad** and **Double biquad** presets with two or four stacked
  square loops, an optional wire reflector, quarter-wave starting dimensions,
  inline editing, reports, and a family optimizer. The geometry is an
  experimental starting point, not a validated gain or impedance claim.
- First-class typed **G5RV**, **ZS6BKW**, and **Zepp** presets with their own
  editors, matching-line geometry, reports, and family optimizers. The doublet
  remains a dipole plus a project-level feed line.
- Explicit optimizer unavailability for magnetic loops, random wires, arbitrary
  custom geometry, and imports.
- Custom straight-wire antennas with a coordinate editor, template-to-custom
  conversion, a parametric Yagi generator with an editable element table and
  NBS starting preset, Moxon, fan dipole, end-fed with optional counterpoise
  and transformer, J Pole, Slim Jim, Ringo, inverted-V, inverted-L,
  off-center-fed dipole, and vertical generators, experimental ground radial
  generator, practical NEC-2 deck import, and basic MMANA-GAL `.maa` geometry
  import, plus series/parallel RLC loads, load markers, and report rows.
- Optional transmitter-side feed line with characteristic impedance, length,
  velocity factor, matched loss, and transformed impedance/SWR.
- Optional L/Pi/T matching networks at the feedpoint, with automatic L design
  from a load R/X, optional component Q/loss, evaluation before the feed line,
  and a parallel-trap helper in the load editor.
- Vertical radial-system presets for ground radials, elevated radials, and a
  dense ground-screen approximation, with editable numeric fields.
- Top-loaded vertical geometry with a capacitive hat and loading coil, including
  report and scene dimensions.
- Half-square and bobtail-curtain self-contained vertical arrays with
  top-junction feeds, adjustable feed offset, geometry dimensions, reports, and
  construction sheets.
- Explicit EFHW labeling and published 40/20/10 m preset buttons for the
  end-fed template.
- Project-level balun/unun insertion-loss model with a frequency-dependent
  power-law fit and per-frequency reporting.
- Magnetic-loop generator with a top gap, ideal series tuning capacitor and
  ESR, conductor-loss simulation, and efficiency/SWR-bandwidth reporting.
- Printable/HTML construction sheet with type-aware dimensions, feed position,
  loads, and simulated result.
- CSV, PNG, SVG, PDF, and layered DXF export for results, patterns, and
  geometry, plus self-contained HTML/PDF reports.
- English and Spanish UI, plus metric and imperial presentation units.
- Immutable domain model for units, geometry, conductors, feed points, ground
  models, environments, wire dipoles, folded dipoles, and regular-polygon
  loops.
- Versioned JSON persistence with atomic saves, lossless gzip compression, and
  a migration framework.
- A `nec2c` solver adapter with input generation, output parsing, SWR
  normalization, currents, power budget, and far-field patterns.
- Numerical validation against NEC-2 User's Guide examples and selected ARRL
  Antenna Book properties.
- Unit, integration, UI, and acceptance tests.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest -m "fast and not slow"   # quick unit-test lane, about 8 s
uv run pytest                          # full suite
uv run --group cross-engine pytest tests/integration/simulation/test_necpp_cross_engine.py -q  # optional PyNEC check (Linux)
uv run pytest benchmarks --benchmark-only -p no:pytest-qt   # report-only performance benchmarks
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run mypy --config-file mypy_ui.ini
```

`mypy_ui.ini` is a permissive ratchet for the Qt layer: files without existing
errors are checked in CI, and the remaining UI files are removed from the
exclusion list as they are fixed. The UI tests run offscreen through
`pytest-qt`; no display is required.

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
- Optimization covers every first-class typed family through explicit
  descriptors and a joint hybrid search over geometry, feed, and family-load
  variables, including typed G5RV, ZS6BKW, Zepp, biquad, Beverage, and
  loaded/linked dipole presets. Magnetic loops, random wires, and
  custom/imported geometry are explicitly unavailable; the
  doublet is a dipole plus a project-level feed line. Band-aware and robust
  modes evaluate several operating points, the Pareto front is descriptive, and
  run summaries persist with the design. Synthesis remains a bounded starting
  point, not a global inverse solver.
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
- Simulation runs are stored in the project, including raw solver text. Project
  files are losslessly gzip-compressed JSON; the 64 MB limit applies to the
  compressed file, with a warning above 32 MB. Use
  **Tools → Compact Simulation History** to keep only the latest run per
  variant. High-resolution patterns and long sweeps multiply runtime and stored
  points.
- The segmentation policy is a documented heuristic; explicit counts are used
  for reference cases. The UI derives per-wire counts and aligns the feed wire
  to a segment center.
- Known diagnostic codes are localized in the UI; the raw solver detail remains
  available in English in the tooltip and raw-output tab.
- PySide6 is pinned below 6.12 because 6.12 triggered a shutdown refcount crash
  with pyqtgraph in this environment. 6.11.3 was evaluated in ADR-0025.

## Author

AntennaDesk is developed by Fernando Sclavo (LU2EFI), an amateur radio
operator. See [AUTHORS.md](AUTHORS.md) for attribution.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
