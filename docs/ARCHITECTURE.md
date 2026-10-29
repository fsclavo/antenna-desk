# Architecture

AntennaDesk follows a ports-and-adapters architecture. The domain is
independent of the GUI, the solver, and the persistence format. The
application layer coordinates use cases through ports; adapters implement those
ports.

## Current layers

```text
presentation
  ui/app.py, main_window.py, wizard, widgets, workers, i18n
        │
application
  ports: ProjectRepository, AntennaSolver, CancelToken
  use cases: CreateDipoleProject, SaveProject, OpenProject,
             EditDipoleLength, UpdateDipoleDesign, AddDesignVariant,
             RenameDesignVariant, DeleteDesignVariant, RunSimulation,
             OptimizeDipoleLength
        │
domain
  common: units, identifiers, time, validation
  antennas: Point3D, Wire, ConductorMaterial, FeedPoint, AntennaModel,
            DipoleParameters
  environment: GroundModel, Environment
  projects: DesignVariant, Project
  simulation: FrequencyPlan, FarFieldRequest, SegmentationPolicy,
              SimulationSpec, SolverMetadata, SolverCapabilities,
              SimulationResult, FrequencyResult
        │
adapters
  persistence: JsonProjectRepository, Pydantic schema, migrations, atomic writes
  simulation/nec2: input writer, parser, process runner, normalization
  simulation: discretization, SWR normalization, fingerprint
  optimization: bounded length search, evaluation log, sensitivity
  reporting: CSV, self-contained HTML, construction sheet, SVG charts
```

## Dependency rules

- `domain/` imports only the Python standard library.
- `application/` imports the domain and defines ports; it does not import
  PySide6, Pydantic, or concrete adapters.
- `persistence/` imports the domain and Pydantic; it is the only place where
  the project schema is serialized.
- `simulation/nec2/` implements the `AntennaSolver` port. It imports the
  domain and application ports, but the domain and application do not import
  it.
- The GUI depends on application use cases and ports, never on solver or
  persistence details.
- UI widgets never perform electromagnetic calculations. Simulation runs in a
  `QThread` worker and returns a normalized `SimulationResult`.

## Phase 1 flow

```text
CreateDipoleProjectCommand
        │
        ▼
DipoleParameters ──► AntennaModel
        │
        ▼
DesignVariant ──► Project
        │
        ▼
SaveProject ──► ProjectRepository ──► JsonProjectRepository
```

Opening a project reverses the flow: the repository validates and migrates the
document, maps it to domain objects, and the application re-validates the
project before returning it.

## Phase 2 flow

```text
RunSimulationCommand
        │
        ▼
AntennaSolver.validate() ──► diagnostics
        │
        ▼
Nec2cSolver.run()
  ├─ write NEC-2 input from AntennaModel + SimulationSpec
  ├─ run nec2c in a short temporary directory
  ├─ capture exit code, stdout, stderr, and raw output
  ├─ parse impedance, currents, power budget, and far-field data
  └─ normalize to SimulationResult (SWR, fingerprint, status)
```

The `AntennaSolver` port returns a normalized `SimulationResult` that also
contains the raw input and output text. Expected runtime failures
(cancellation, timeout, non-zero exit, parse error, missing executable) are
represented as a result with status `error` or `cancelled` and structured
diagnostics, rather than escaping into the UI.

## Phase 3 flow

```text
MainWindow
  ├─ DipoleWizard / DipoleForm ──► DipoleParameters
  ├─ UpdateDipoleDesign / CreateDipoleProject ──► immutable Project
  ├─ GeometryView (canonical AntennaModel snapshot)
  ├─ SimulationWorker (QThread) ──► RunSimulation ──► AntennaSolver
  ├─ ResultsView (impedance, SWR, pattern, currents, diagnostics, raw data)
  ├─ ComparisonDialog (A/B metrics, SWR, pattern)
  └─ Export CSV / HTML report
```

Simulation results are immutable snapshots with a model/spec fingerprint.
Completed and partial runs are stored in the project as `SimulationRun`
objects. The window caches the latest run per design; opening a project reloads
them, and comparison/report/construction actions work across sessions. Editing
a design clears its current result view, but earlier run snapshots remain in
the project.

## Phase 4 flow

```text
Selected DesignVariant ──► RunSimulation ──► SimulationResult
        │                                      │
        ├─ Add/Rename/Delete variant            ├─ ComparisonDialog (A/B)
        ├─ ResultsView (impedance/SWR/pattern/currents)
        └─ CSV / HTML report ──► reproducible artifact
```

Reports are generated from the immutable result and the project snapshot. The
HTML report includes the fingerprint, solver version, specification,
diagnostics, impedance table, resonance points, and SVG charts.

## Phase 5 flow

```text
AntennaDesignParameters + base SimulationSpec
        │
        ▼
OptimizeAntennaDimension
  ├─ single-frequency, no-pattern evaluation spec at the design frequency
  ├─ bounded reactance search (endpoints, coarse scan, interpolation)
  ├─ evaluation log
  └─ ±10/25 mm sensitivity probes
        │
        ▼
OptimizationDialog ── Apply best dimension ──► design update ──► full simulation
        │
        └─ ConstructionDialog / construction sheet (dimensions + last result)
```

Optimization runs in a worker thread. The final full-sweep/pattern simulation is
performed after applying the dimension so the normal result/report path remains
the single source of truth.

## Phase 6 — new geometry (in progress)

Phase 6 starts with a vertical center-fed dipole in the existing
`wire_dipole` model. `DipoleParameters.orientation` selects horizontal or
vertical geometry; the vertical template uses `height_m` as the base height.

The second slice adds two multi-wire templates:

- `FoldedDipoleParameters`: two parallel elements, two end connectors, and a
  center feed on the driven element.
- `LoopParameters`: a vertical regular polygon with 3–128 sides and a feed at
  the midpoint of the first side.

`AntennaDesignParameters` is the union of the three parameter types.
`DesignVariant` stores the union and validates that `antenna_type` matches the
parameters. The canonical model remains the shared `AntennaModel`, so the
solver adapter does not need geometry-specific branches. Schema version 3 is
kept: the new payloads are additive, and old `wire_dipole` documents are
unchanged. Series RLC loads are optional antenna payloads and are emitted as
`LD 0` cards by the solver adapter.

The form exposes an antenna-type selector with conditional spacing/sides
fields. Multi-wire designs switch the geometry view to Plan, where construction
dimensions live; Elevation shows installation data (height above ground, feed
height, and ground line, plus a folded-conductor section). Reports,
construction sheets, and comparison use type-aware dimensions.


The UI is bilingual through `ui/i18n.py` and supports metric or imperial
presentation units. Project files and the domain remain in canonical units.

## Immutability and snapshots

Domain objects are frozen dataclasses. Editing a design returns a new
`Project`; the previous object remains unchanged. Simulation results are
immutable and carry a fingerprint of the model and specification. This is the
foundation for the rule that editing a design must not modify previous
simulation results.

## Persistence boundary

The domain uses dataclasses. Pydantic v2 models live only in
`persistence/schema.py` and validate the external JSON representation. This
keeps schema concerns out of the domain while still rejecting malformed or
untrusted files.

Project files use the `antennadesk-project` format with a schema version.
Saves are atomic: write a temporary file in the target directory, flush and
`fsync`, then replace the destination with `os.replace`. Schema version 2 added
dipole orientation, version 3 adds persisted simulation runs, and older
documents are migrated explicitly.

Simulation runs are persisted in schema version 3. Raw solver text is stored
with the normalized result. The UI warns at 8 MB, blocks files above the 10 MB
limit, and offers simulation-history compaction.

## Not implemented yet

- Measurement import adapters.
- Multi-objective optimization, bandwidth/gain objectives, and space
  constraints beyond the min/max length bounds.
- Measurement records and VNA CSV import.
