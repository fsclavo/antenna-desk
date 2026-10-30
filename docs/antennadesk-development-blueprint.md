# AntennaDesk — Development Blueprint
## Antenna design, simulation, and construction application for amateur radio

**Version:** 1.0 · **Status:** initial blueprint for OpenCode · **Working name:** AntennaDesk  
**Target platforms:** Linux and Windows · **Initial UI language:** Spanish, prepared for English  
**Type:** desktop application, local-first, with an external electromagnetic engine

---

## 1. Executive summary

AntennaDesk aims to make antenna design accessible without sacrificing
technical rigor. The user should be able to start from an intent — for example,
“a dipole for 40 meters, with a maximum height of 8 m and 18 m of available
space” — generate a model, simulate it, explore the results, and produce a
buildable design sheet.

The competitive advantage will not be reimplementing all electromagnetic
physics, but offering a guided workflow, parametric models, clear diagnostics,
optimization with practical constraints, and traceability between design,
simulation, and measurement.

### Principles

1. **Own domain model:** geometry and design intent do not depend on the GUI or
   NEC.
2. **Separation by domain:** domain, use cases, solver, persistence,
   visualization, and interchange are independent modules.
3. **Existing engine first:** evaluate NEC-2/nec2c and related options; do not
   write a custom solver in the MVP.
4. **Guided design first:** the user should not need to know NEC cards or
   segmentation to create a dipole.
5. **Visible rigor and limitations:** every simulation stores conditions,
   engine version, warnings, and provenance.
6. **Buildability:** allow physical constraints and explain the trade-offs.
7. **Local-first:** no accounts, cloud, or mandatory telemetry.
8. **Incremental:** each phase must leave a functional, tested, documented
   application.

### MVP non-goals

- Replace general electromagnetic tools for every geometry and frequency.
- Create a custom electromagnetic engine.
- Accurately simulate buildings, trees, masts, feed lines, and any real
  environment without modeling them.
- Include direct control of a NanoVNA or other instruments.
- Optimize exclusively for SWR.
- Include complex dielectric antennas, massive arrays, or advanced full-wave
  3D analysis.
- Create accounts, cloud synchronization, or multi-user collaboration.

---

## 2. Users and scope

### Users

- Amateur radio operators who build dipoles, verticals, loops, and wire
  antennas.
- Builders who want to compare variants before cutting material.
- Clubs that teach antennas and applied electromagnetics.
- Advanced users who need a geometry editor, without it being the mandatory
  entry point.

### MVP

- Guided design wizard for a half-wave dipole.
- Parametric model of straight conductors.
- Target frequency, length, height, orientation, and diameter.
- Basic ground model compatible with the selected solver.
- Simulation through a NEC-2 engine integrated through an adapter.
- Input impedance, SWR with respect to an explicit reference impedance,
  frequency sweep, current, and far-field pattern when the engine supports it.
- Basic geometry view.
- Save/open a versioned native project.
- Export NEC input file, CSV results, and report.
- Diagnostics before and after simulation.
- Automated tests and CI on Linux/Windows.

### Functional evolution

| Stage | Functionality |
|---|---|
| 0.1 | Guided dipole, NEC engine, results, and native project |
| 0.2 | Variant comparison, export, and reports |
| 0.3 | Length optimization and physical constraints |
| 0.4 | Folded dipole, simple vertical, loop, and supported loads |
| 0.5 | NEC model import and VNA CSV measurements |
| 0.6+ | Yagi, advanced editor, multi-objective optimization, and new engines |

Do not present an antenna type as reference-backed until reference tests and
an explanation of its limitations exist. Experimental generators and arbitrary
geometries are allowed when they are visibly labeled, structurally tested, and
do not claim validated accuracy.

---

## 3. Architecture

Apply a modular architecture inspired by **Hexagonal Architecture / Ports and
Adapters**. Do not use microservices: this is a local desktop application.

```text
┌────────────────────────────────────────────────────────┐
│ Presentation: PySide6                                  │
│ Wizard · geometry editor · charts · diagnostics        │
└─────────────────────────┬──────────────────────────────┘
                          │ commands / queries
┌─────────────────────────▼──────────────────────────────┐
│ Application: use cases                                 │
│ CreateProject · EditAntenna · RunSimulation · Optimize │
│ CompareVariants · ImportMeasurement · ExportReport     │
└───────────────┬─────────────────────────┬───────────────┘
                │                         │
┌───────────────▼────────────┐  ┌─────────▼──────────────┐
│ Domain                     │  │ Ports / interfaces     │
│ Project, Antenna, Geometry │  │ Solver, Repository,    │
│ Feed, Ground, Results      │  │ Importer, Exporter     │
└────────────────────────────┘  └─────────┬──────────────┘
                                          │
                              ┌───────────▼──────────────┐
                              │ Adapters                 │
                              │ NEC-2 · JSON · CSV · PDF │
                              └──────────────────────────┘
```

### Dependency rules

- `domain/` does not import PySide6, SciPy, or concrete solver libraries.
- The GUI does not perform electromagnetic calculations or know NEC syntax.
- The application depends on interfaces, not concrete implementations.
- The adapter translates the canonical model to NEC and normalizes its output.
- Raw solver data is preserved for diagnostics; the application consumes
  normalized results.
- Simulation never runs on the Qt main thread.
- A simulation represents an immutable snapshot of the model, not a reference
  to an object that changes later.
- Persistence is versioned and migrated explicitly.
- Do not introduce abstractions without a real change boundary.

### Suggested structure

```text
antennadesk/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── AGENTS.md
├── CHANGELOG.md
├── src/antennadesk/
│   ├── __main__.py
│   ├── bootstrap.py
│   ├── config/
│   ├── domain/
│   │   ├── common/          # units, IDs, validation
│   │   ├── projects/        # project, variants, revisions
│   │   ├── antennas/        # geometry, conductors, sources, loads
│   │   ├── environment/     # ground and environmental conditions
│   │   ├── simulation/      # specification, results, diagnostics
│   │   ├── optimization/    # objectives and constraints
│   │   └── measurements/    # measurement records and context
│   ├── application/
│   │   ├── ports/           # solver, repository, import/export interfaces
│   │   ├── use_cases/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── dto/
│   ├── geometry/            # transformations and geometric validation
│   ├── simulation/
│   │   ├── solver_registry.py
│   │   ├── discretization.py
│   │   ├── normalization.py
│   │   └── nec2/            # adapter, input writer, parser, capabilities
│   ├── optimization/
│   ├── persistence/         # JSON, schema, migrations
│   ├── interchange/         # NEC, CSV, VNA data
│   ├── reporting/           # report model, HTML/PDF
│   ├── ui/
│   │   ├── viewmodels/
│   │   ├── wizard/
│   │   ├── geometry_view/
│   │   ├── results_view/
│   │   └── widgets/
│   └── resources/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── acceptance/
│   ├── reference_cases/
│   ├── fixtures/
│   └── ui/
├── examples/
├── docs/
│   ├── DEVELOPMENT_BLUEPRINT.md
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_MODEL.md
│   ├── SOLVER_ADAPTER.md
│   ├── VALIDATION_PLAN.md
│   ├── USER_GUIDE.md
│   └── ADR/
├── scripts/
└── packaging/
```

Do not create all empty files at the beginning. Add modules when implementing
real functionality.

---

## 4. Domains and responsibilities

### 4.1 Projects

Entities: `Project`, `DesignVariant`, `ProjectMetadata`, `ProjectRevision`.

Responsibilities:

- Create, rename, save, and duplicate projects.
- Keep comparable variants.
- Store exact snapshots of models and simulations.
- Record schema and application versions.

Critical rule: editing a design does not modify the results of previous
simulations.

### 4.2 Antenna model

Entities/objects: `AntennaModel`, `Wire`, `Point3D`, `ConductorMaterial`,
`FeedPoint`, `LumpedLoad`, `GroundModel`, `Environment`, `FrequencyPlan`,
`AntennaTemplate`, `DesignConstraint`.

Canonical units:

- Length: meters.
- Frequency: Hz.
- Impedance: ohms.
- Conductivity: S/m when applicable.
- Single angular convention, converted at system boundaries.
- The UI always shows the unit and converts explicitly.

Design parameters (for example, total length) must be separated from derived
geometry (coordinates), from solver numerical discretization, and from
results.

### 4.3 Geometry

Functions:

- Transform, rotate, and translate geometries.
- Compute lengths and bounds.
- Detect non-finite coordinates, zero-length conductors, duplicates,
  junctions, and problematic crossings.
- Generate a preview.
- Propose discretization, without confusing numerical segments with physical
  conductors.

### 4.4 Simulation

`SimulationSpec` contains frequency or sweep, ground, calculation
configuration, discretization, and solver/version.

Normalized `SimulationResult` contains:

- Status: completed, cancelled, partial, or error.
- Computed frequencies.
- Complex feed-point impedance.
- SWR with an explicit reference impedance.
- Currents per element/segment when available.
- Pattern, polarization, and far-field results according to engine
  capabilities.
- Clearly documented gain/directivity conventions.
- Warnings, solver version, model fingerprint, and duration.
- References to raw input/output.

Do not use a single ambiguous `gain` field: distinguish gain, realized gain,
and directivity when applicable.

### 4.5 Solver adapter

Conceptual interface:

```python
class AntennaSolver(Protocol):
    def capabilities(self) -> SolverCapabilities: ...
    def validate(self, model, spec) -> list[Diagnostic]: ...
    def run(self, model, spec, progress_callback=None, cancel_token=None) -> RawSolverResult: ...
    def version(self) -> SolverVersion: ...
```

The adapter must:

1. Validate capabilities and inputs.
2. Translate geometry and conditions to the engine format.
3. Generate a reproducible input.
4. Execute the process in a controlled way.
5. Capture stdout, stderr, and exit code.
6. Parse output with explicit rules.
7. Normalize units, signs, and conventions.
8. Preserve raw files.
9. Emit diagnostics with context.
10. Cancel without leaving orphan processes.

### 4.6 Optimization

First function: adjust the length of a dipole within physical limits to
approach a resonance or target reactance.

Requirements:

- Explicit interval and limits.
- Record of evaluations and objective function.
- Time/iteration limits.
- Explanation of the modified parameters.
- Re-simulate and validate the final solution.
- Do not use minimum SWR as a universal objective: SWR does not prove
  efficiency or a useful pattern.

Later: bandwidth, gain in a target direction, space constraints, construction
cost/complexity, and multi-objective optimization.

### 4.7 Measurements

Record instrument, date, original file/hash, frequency range, data type,
reported calibration state, reference plane, coax/accessories,
antenna/variant, height, orientation, environment, and notes.

The MVP imports documented CSV. Do not assume all VNA CSV files have the same
format, or that a measurement at one reference plane is directly comparable
with the impedance of an ideal source at another plane.

### 4.8 Reporting

The report includes:

- Project/variant and dimensions.
- Frequency and environment conditions.
- Engine, version, and configuration.
- Results and charts with units.
- Warnings and limitations.
- Optimization parameters.
- Associated measurement data.
- Date and simulation fingerprint.

Use a common report model. HTML can be the base; PDF is added when output is
reproducible.

---

## 5. Domain model and invariants

```text
Project
 ├── DesignVariant
 │    └── AntennaModel
 │         ├── Geometry / Wires
 │         ├── FeedPoint
 │         ├── ConductorMaterial
 │         ├── Loads
 │         └── Environment / GroundModel
 ├── SimulationRun
 │    ├── SimulationSpec
 │    ├── SolverMetadata
 │    ├── SimulationResult
 │    └── Diagnostics
 ├── MeasurementRecord
 └── ReportReference
```

Invariants:

- All numeric magnitudes are finite.
- No conductor has zero length.
- The source references a valid location compatible with the solver.
- Frequencies are positive and sweeps are valid and bounded in size.
- The saved file is validated when opened.
- Results are linked to an immutable snapshot.
- Conversion to the solver produces diagnostics for non-representable
  elements.
- Approximations and simplifications are never hidden.

Templates (dipole, vertical, loop) generate the same canonical `AntennaModel`;
they must not create independent simulation paths.

---

## 6. Electromagnetic engine and numerical risks

### Initial decision

Evaluate NEC-2/nec2c and options such as NEC2++/PyNEC. Perform a technical
spike before committing architecture:

- License and redistribution obligations.
- Integration as a library or external process.
- Operation on Linux and Windows.
- Native dependencies and packaging.
- Availability of impedance, current, pattern, and sweeps.
- Maintenance quality and output formats.
- Geometry, ground, and load limitations.
- Executable reference case.

Do not assume that a GPL library can be distributed without consequences for
the final product license. Document the decision in an ADR. Xnec2c can serve
as a technical and UX reference, although not necessarily as an embedded
dependency.

### Discretization

Discretization is an important source of errors. The user defines physical
conductors; the adapter creates numerical segments for the engine.

There must be:

- Documented segmentation policy.
- Diagnostics for segments that are too short/long according to engine
  recommendations.
- Validation of sources, junctions, and crossings.
- Segment visualization in advanced mode.
- Persistence of numerical configuration.
- Warnings if the geometry falls outside known recommendations.

Do not turn a segmentation rule into universal truth: base it on the solver
documentation and validate it with concrete cases.

### Physical limitations

The application must explain that:

- Low SWR does not prove high efficiency.
- Real ground may differ from the model.
- Physical feeding can introduce common mode.
- Unmodeled buildings, trees, masts, and cables can alter results.
- Real diameters, materials, and dimensions have tolerances.
- Gain, realized gain, and directivity are not interchangeable.
- Simulation is a prediction conditioned by the model, not a guarantee of
  real-world performance.

---

## 7. UX: guided design and advanced mode

### Main window

- Top bar: project, variant, save, undo/redo, and simulate.
- Design panel: antenna parameters and constraints.
- Center: 2D/3D geometry.
- Summary panel: warnings and status.
- Results in tabs: impedance/SWR, pattern (line and polar lobes), currents,
  diagnostics, and raw data.

Avoid overloading the MVP. Show advanced features progressively.

### Dipole wizard

1. Choose a band or enter a frequency.
2. Specify orientation and available space.
3. Enter height.
4. Choose conductor/diameter.
5. Review ground conditions and assumptions.
6. Generate the initial model.
7. Simulate.
8. Interpret resonance, impedance, SWR, and pattern.
9. Adjust length with a guided control.
10. Export the construction sheet.

The initial length must be presented as an approximation, not as a universal
final length.

### UX principles

- Show intent first, then numerical details.
- Visible units, tooltips, and brief explanations.
- Actionable errors.
- Clearly separate analytical estimates, simulations, and measurements.
- Warn before simulating if the model is questionable.
- Keyboard accessibility.
- Initial language Spanish, prepared for English.

---

## 8. Technology stack

| Area | Proposed choice | Use |
|---|---|---|
| Language | Python 3.11+ | Logic, integration, and scientific ecosystem |
| GUI | PySide6 / Qt Widgets | Cross-platform desktop |
| Environment/dependencies | `uv` + `uv.lock` | Reproducibility |
| Typing | type hints + mypy | Contracts and maintenance |
| Lint/format | Ruff | Quality and style |
| Tests | pytest | Unit, integration, acceptance |
| Computation | NumPy, SciPy | Optimization and auxiliary calculations |
| Interactive charts | PyQtGraph | Sweeps and curves |
| Reports | Optional Matplotlib + HTML/PDF | Static charts and reports |
| Solver | NEC-2 through an adapter | Electromagnetic simulation |
| Native project | Versioned JSON | Portability and transparency |
| Measurements | Documented CSV | Initial import |
| Linux | AppImage after validation | Distribution |
| Windows | PyInstaller initially | Executable |
| CI | GitHub Actions | Tests and builds |

### Decisions not to anticipate

- Do not use scikit-rf as the domain model: it can help manage network data
  in a future phase, but it does not represent antenna geometry.
- Do not add PyVista/VTK until a lightweight 3D view is proven insufficient.
- Do not introduce a database in the MVP if JSON satisfies the use case.
- Do not use `pickle` for project files.
- Do not run the solver from widgets.
- Do not add cloud services or telemetry by default.
- Do not add dependencies without justifying cost, license, and benefit.

---

## 9. Persistence and interoperability

### Native format

Use JSON with `schema_version`, validation, and migrations. Atomic save through
a temporary file and replacement after confirming success. Do not execute file
content or accept arbitrary deserialization.

Illustrative example:

```json
{
  "format": "antennadesk-project",
  "schema_version": 1,
  "project": {"id": "uuid", "name": "40 m dipole", "units": "metric"},
  "designs": [{
    "id": "uuid",
    "name": "Initial",
    "antenna_type": "wire_dipole",
    "parameters": {
      "target_frequency_hz": 7100000,
      "total_length_m": 20.0,
      "height_m": 8.0
    }
  }],
  "simulation_runs": []
}
```

### NEC

- Export reproducible NEC input.
- Import only a documented subset at the beginning.
- Warn about ignored/unsupported elements.
- Do not silently discard unknown cards.
- Do not promise perfect round-trip until tests exist.

### CSV and VNA

Document columns, units, separators, decimals, phase convention, and missing
data. Implement adapters per file format; do not treat all CSV files as equal.
Initially, import files; direct instrument control is outside the MVP.

---

## 10. Scientific validation and testing

### Three levels that must not be confused

1. **Software test:** the implementation does what is intended.
2. **Numerical validation:** it matches independent references within
   documented tolerances.
3. **Experimental validation:** it is compared with real measurements,
   considering uncertainty and environment.

### Initial reference cases

- Straight dipole in free space.
- Dipole with frequency sweep.
- Horizontal dipole over ground at different heights.
- Vertical with ground/radial model supported by the engine.
- Loop and loads when implemented.
- Invalid models to test diagnostics.

References must come from a traceable technical source, an independent tool,
or a cross-checked calculation. Do not create expected values using the same
implementation under test.

### Tests

**Unit:** units, geometry, validations, SWR from complex impedance,
serialization, migrations, and normalization.

**Integration:** solver adapter, real output parsing, errors, cancellation,
CSV import, reports, and project reopening.

**Acceptance:** create a dipole without coordinates; simulate; modify length
without altering previous results; save/reopen; export a report; receive an
actionable error for an invalid model.

**Numerical regression:** versioned fixtures, explicit tolerances, version/
configuration metadata, and manual review of result changes. Do not update
snapshots automatically without analysis.

---

## 11. Execution, robustness, and security

- Run simulations outside the main thread using `QProcess`, `QThreadPool`, or
  an option validated in the spike.
- Keep the UI responsive.
- Show progress only if the engine provides real data.
- Allow cancellation and cleanup of temporary processes.
- Limit concurrency, duration, and optimization iterations.
- Log each simulation.
- Cache only with a key that includes model, configuration, and solver
  version.
- Treat imported files as untrusted data.
- Avoid shell commands built by concatenating user input.
- Validate paths and file sizes.
- Do not execute embedded scripts.
- Do not download/execute engines automatically without an explicit,
  verifiable mechanism.
- Solver failures must not close the application.

---

## 12. Reporting and documentation

HTML reports as the base and PDF when the format is stable. Include geometry,
dimensions, conditions, engine/version, results with units, warnings,
optimization parameters, and related measurement data.

Initial documentation:

- First project: HF dipole.
- How to interpret impedance and SWR.
- What a simulation can and cannot say.
- How to compare variants.
- How to import VNA measurements.
- Diagnosis of common errors.

Maintain a glossary: resonance, reactance, SWR, impedance, gain, directivity,
polarization, ground, segment, source, and load.

---

## 13. OpenCode and development discipline

Create and maintain:

- `AGENTS.md`
- `docs/DEVELOPMENT_BLUEPRINT.md`
- `docs/ARCHITECTURE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/SOLVER_ADAPTER.md`
- `docs/VALIDATION_PLAN.md`
- `docs/ADR/`

### Suggested `AGENTS.md` content

```markdown
# Project instructions

- Read docs/DEVELOPMENT_BLUEPRINT.md before implementing features.
- Preserve boundaries between domain, application, solver adapters, persistence and UI.
- Domain code must not import PySide6 or concrete solver libraries.
- Never put electromagnetic calculations in widgets/view models.
- Do not invent numerical reference values.
- New domain rules require unit tests.
- Solver behavior changes require integration/regression tests.
- Keep units and result conventions explicit.
- Do not silently discard unsupported imported model elements.
- Never use pickle for project files.
- Keep the UI responsive during simulations.
- Explain why a new dependency is needed.
- Update docs when behavior or project schema changes.
- Run relevant tests, lint and type checks before declaring a task complete.
- Report assumptions, tests run and remaining limitations.
- Implement one coherent milestone at a time; do not scaffold the whole roadmap.
```

### Recommended workflow

For each task, OpenCode must:

1. Read the blueprint and existing code.
2. Identify affected domains and dependencies.
3. Propose a short plan and the files to modify.
4. Implement the minimum scope.
5. Add tests.
6. Run relevant tests, lint, and type checking.
7. Review architectural boundaries.
8. Update documentation.
9. Report changes, decisions, tests, and limitations.

Do not ask it to implement the entire product at once.

---

## 14. CI/CD and distribution

### CI

On every PR:

- Install dependencies from `uv.lock`.
- Ruff.
- mypy on defined modules.
- pytest.
- Domain tests without solver dependency.
- Solver integration where available.
- Package build.
- Validation of examples and reference projects.

### Linux and Windows

Linux: first test reproducible execution; package an AppImage only after
verifying native libraries, license, and dependencies; test on representative
distributions.

Windows: PyInstaller as the first option, after validating solver integration;
test on a clean installation without Python; document dependencies and usual
security notices without recommending disabling protections.

Engine distribution may be the main packaging risk. Resolve it in Phase 0, not
at the end.

---

## 15. Main risks

| Risk | Mitigation |
|---|---|
| Solver license incompatible | Early spike and ADR before integration |
| Wrong or misinterpreted results | Independent reference cases and physical validation |
| Inadequate geometry/discretization | Diagnostics and prior validation |
| Excessive scope | MVP limited to dipole and straight conductors |
| UX that hides physical assumptions | Show conditions, warnings, and glossary |
| Unmaintained external dependency | Custom adapter and evaluated alternative |
| Linux/Windows differences | CI and clean-package testing |
| Incorrect VNA comparison | Store calibration, reference plane, and accessories |
| Hard-to-build optimization | Physical constraints and explicit objectives |
| Loss of old projects | Versioned schema and tested migrations |

---

## 16. Roadmap with exit criteria

### Phase 0 — Technical spike (P0)

- Compare NEC-2/nec2c, NEC2++/PyNEC, and relevant options.
- Review license, redistribution, Python/process integration, and portability.
- Run a simple case on Linux and Windows.
- Inspect input/output and result availability.
- Create an ADR with the decision and risks.

**Exit:** engine selected with evidence and a reproducible case. Do not start
the GUI before resolving the distribution risk.

### Phase 1 — Domain and persistence (P0)

- Structure, tooling, and `AGENTS.md`.
- Minimum units, geometry, conductor, source, and environment.
- Validations.
- Versioned JSON and atomic save.
- Domain and migration tests.

**Exit:** create, validate, save, and reopen a dipole without GUI or solver.

### Phase 2 — Adapter and references (P0)

- Input generation.
- Execution, error capture, and cancellation.
- Parsing and normalization.
- Reference cases with tolerances.
- Logs and warnings.

**Exit:** reference dipole simulated reproducibly and compared with an
independent source.

### Phase 3 — Guided MVP (P0)

- Main window and wizard.
- Frequency, length, height, and diameter parameters.
- Automatically generated geometry.
- Asynchronous simulation.
- Impedance, SWR, sweep, and basic pattern.
- Save/open projects.

**Exit:** a user simulates a dipole without editing coordinates or NEC files.

### Phase 4 — Comparison and reports (P1)

- Improved geometry view.
- A/B comparison.
- Currents if the engine supports them.
- CSV and HTML/PDF reports.
- Resonance markers.

**Exit:** comparable variants and a reproducible report.

### Phase 5 — Optimization and construction (P1)

- Length adjustment with limits.
- Iteration and objective logging.
- Space constraints.
- Construction sheet and sensitivity analysis.

**Exit:** the user adjusts a dipole to a target and understands the changes.

### Phase 6 — New antennas and measurements (P1/P2)

- Add vertical, loop, or folded dipole according to demand.
- VNA CSV import through adapters.
- Measurement condition records.
- Simulation/measurement comparison.
- Physical antenna validation.

**Exit:** each new geometry has reference tests and documented limitations.

### Phase 7 — Advanced editor (P2)

- Free conductor editor.
- NEC subset import.
- Advanced sources/loads.
- Multi-objective optimization.
- Other engines only when a need is demonstrated.

**Exit:** advanced users can extend designs without harming the guided flow.

---

## 17. Recommended first milestone

Do not start with an attractive interface. First create a vertical slice:

1. Build a dipole model from parameters.
2. Validate it and generate diagnostics.
3. Convert it to NEC input.
4. Run the engine and capture output.
5. Normalize impedance and pattern.
6. Compare with an independent reference.
7. Save the model, configuration, and result.
8. Reopen the project and generate a minimal report.

After validating this path, implement the wizard and the GUI.

---

## 18. Definition of Done

A feature is complete when:

- It meets acceptance criteria.
- It has tests appropriate to the risk.
- It respects domain boundaries.
- It uses explicit units and conventions.
- It exposes errors and limitations.
- It updates documentation.
- It does not block the UI during long operations.
- It passes relevant tests/lint/type checks.
- It does not introduce dependencies without justification.
- It maintains project compatibility or includes a migration.
- It states remaining limitations.

A simulation feature is not complete because the engine returns a number: it
needs validation, interpretation, and warnings.

---

## 19. Health metrics

- Reference cases passing.
- Numerical regressions investigated and resolved.
- Test coverage of the domain and adapters.
- Main flows with acceptance tests.
- UI responsiveness during simulation.
- Example projects that open in every release.
- Clean Linux/Windows builds.
- Import formats with fixtures and tests.

Code coverage is an auxiliary signal, not proof of electromagnetic validity.

---

## 20. Initial ADRs

Create short decisions with context, alternatives, decision, and consequences:

1. Engine and license.
2. Architecture and domain boundaries.
3. Units and angular conventions.
4. Project format and migrations.
5. Simulation execution/cancellation.
6. 3D visualization strategy.
7. Import/export formats.
8. Product license.
9. Linux/Windows packaging.

---

## 21. Initial instruction for OpenCode

Use this document as a guide, not as an order to implement everything at once.

**First task:** perform only Phase 0. Compare NEC engine options in terms of
license, integration, portability, available results, maintenance, and
distribution. Create a comparison table, a reproducible spike, and a
recommended ADR. Do not implement the GUI or the complete model yet.

After that decision is approved, move to Phase 1. If a specific task
contradicts the blueprint, explain the conflict before changing the
architecture.

---

## 22. Initial technical references

- Qt for Python / PySide6: https://doc.qt.io/qtforpython-6/
- PyNEC: https://pypi.org/project/PyNEC/
- Xnec2c, manual: https://www.xnec2c.org/
- Xnec2c, repository: https://github.com/KJ7LNW/xnec2c

These are starting points, not definitive approval. Confirm version,
maintenance, compatibility, license, and redistribution conditions when
choosing the engine.
