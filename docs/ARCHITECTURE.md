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

## Phase 6 — new geometry (completed; physical validation deferred)

Phase 6 starts with a vertical center-fed dipole in the existing
`wire_dipole` model. `DipoleParameters.orientation` selects horizontal or
vertical geometry; the vertical template uses `height_m` as the base height.
Yagi and Moxon use a separate `polarization` field: the boom always stays
horizontal, and vertical polarization is a real rotation of the canonical
wires around the boom.

The second slice adds two multi-wire templates:

- `FoldedDipoleParameters`: two parallel elements, two end connectors, and a
  center feed on the driven element.
- `LoopParameters`: a vertical regular polygon with 3–128 sides and a feed at
  the midpoint of the first side.

`AntennaDesignParameters` is the union of the supported parameter types.
`DesignVariant` stores the union and validates that `antenna_type` matches the
parameters. The canonical model remains the shared `AntennaModel`, so the
solver adapter does not need geometry-specific branches. Schema version 8 is
current: parameter payloads are additive, and old `wire_dipole` documents are
unchanged. A design may also store an optional analysis band plan; it is
intent metadata and never changes the canonical geometry. Series RLC loads are
optional antenna payloads and are emitted as `LD 0` cards by the solver
adapter.

The form exposes an antenna-type selector with conditional spacing/sides
fields. The geometry view is renderer-neutral: `ui/geometry/builder.py`
projects the canonical wires with an orthographic basis, attaches semantic
dimensions and detail insets, and `ui/geometry/layout.py` places the dimensions
in screen space using font metrics and collision avoidance. The default view is
derived from the geometry (front for vertical planes, plan for horizontal
arrays, front plus a top inset for non-planar models), and changing the model
resets zoom, pan, and vertical exaggeration. Reports, construction sheets, and
comparison use type-aware dimensions.

The main window uses a `QUndoStack` with immutable project snapshots for
Undo/Redo. Simulation runs are kept outside the undoable editable snapshot and
merged back on restore, so undoing a design edit does not delete completed
solver history. `ResultsView` shares a reusable `ChartCursor` across the
impedance, SWR, pattern, currents, and measurement charts.

The frequency-first estimator layer is domain code: `DesignIntent` and
`DimensionEstimate` are Qt-free, and `EstimateAntennaDimensions` is an
application use case. The UI displays the estimate and applies the resulting
`AntennaDesignParameters`; numerical refinement remains in the existing
optimization and synthesis use cases.

The geometry presentation layer has no Qt dependency in `scene.py`,
`views.py`, or `builder.py`; only the layout and widget use Qt. The same scene
can therefore be tested headlessly and reused for future SVG/PDF/DXF export.


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
dipole orientation, version 3 added persisted simulation runs, version 4 adds
optional band/batch metadata, version 5 adds optional OCFD/custom feed
transformer ratios, version 6 adds optional per-design analysis band plans,
version 7 adds Yagi/Moxon polarization, version 8 adds vertical top-hat fields,
and older documents are migrated explicitly.

Simulation runs are persisted in schema version 8. Raw solver text is stored
with the normalized result. Project files are compact JSON compressed with
gzip; plain JSON files from older versions still load. The UI warns at 20 MB
compressed, blocks files above the 32 MB compressed limit, and offers
simulation-history compaction.

Multiband analysis is an application-level batch over the existing single-band
solver boundary. `AnalyzeBands` runs one `SimulationSpec` per selected band,
keeps completed results when another band fails or is cancelled, and groups
them in an immutable `BandAnalysisResult`. The adapter still receives one
contiguous `FrequencyPlan` at a time, so no NEC deck or parser change is
required. OCFD and custom designs can carry an optional ideal feed-transformer
ratio in the same `SimulationSpec` cascade used by end-fed and T2FD designs. Each band run carries a stable `band_id` and shared `batch_id`; the
project reconstructs the latest batch from those runs. Pattern resolution is
global and snapshots are one per band by default. The architecture leaves a
future segmented `FrequencyPlan` or multi-`FR` deck as an optimization, not a
prerequisite for the user workflow.

## Current limitations

- `nec2c` is bundled in the native AppImage, Debian package, and Windows zip,
  but remains an external runtime dependency for wheel installs. Native release
  artifacts are unsigned by default.
- Measurement import is CSV-based. There is no live VNA or instrument-control
  adapter.
- Series and parallel RLC loads are supported on one wire segment. L/Pi/T
  matching networks are post-processed at the feedpoint. General
  transmission-line geometry is modeled as NEC `TL` two-ports between wire
  points; physical parallel-line coupling is not modeled.
- Far-field results are NEC power gains. Directivity and realized gain are
  derived per frequency; the pattern charts still show power gain. See
  [ADR-0015](ADR/0015-realized-gain-and-directivity.md).
- The UI estimates the persisted project size before a run and may coarsen the
  far-field pattern to the finest step that fits. For sweeps longer than five
  points, the pattern is computed at amateur-band snapshots (or a user-selected
  count) while the impedance/current sweep keeps every point. The policy is
  applied centrally in the main window, so every current and future antenna
  family inherits it; family builders only provide the frequency plan and
  segmentation. Oversized sweeps keep the frequency plan and disable the
  pattern rather than failing. See
  [ADR-0017](ADR/0017-simulation-storage-budget.md) and
  [ADR-0019](ADR/0019-pattern-snapshots.md).
- The end-fed feed transformer is an ideal impedance ratio; it is not a
  physical unun model. The counterpoise is ordinary wire geometry.
- Relative permeability is not emitted to NEC.
- Custom and imported designs are excluded from the guided optimizer. Space
  constraints are limited to variable bounds and the Yagi minimum-gap rule.
- One full-wave engine (NEC-2) is supported; additional engines are deferred.
