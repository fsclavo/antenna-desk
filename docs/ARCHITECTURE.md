# Architecture

AntennaDesk follows a ports-and-adapters architecture. The domain is
independent of the GUI, the solver, and the persistence format. The
application layer coordinates use cases through ports; adapters implement those
ports.

## Current layers

```text
presentation
  ui/app.py, main_window.py, catalog.py, exporters.py, import_actions.py,
  project_io.py, recovery_actions.py, recent_actions.py,
  element_optimization_actions.py, optimization_actions.py, dialogs, widgets,
  workers, i18n
  presentation/units.py: Qt-free length formatting shared with reporting
        │
application
  ports: ProjectRepository, AntennaSolver, CancelToken
  use cases: CreateDipoleProject, SaveProject, OpenProject,
             EditDipoleLength, UpdateDipoleDesign, AddDesignVariant,
             RenameDesignVariant, DeleteDesignVariant, RunSimulation,
             OptimizeDipoleLength
  simulation services: segment layout, model-quality resolution,
             segmentation diagnostics, typed-family specs, far-field
             pattern presets, and pattern-budget planning
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
  persistence: ProjectContainerRepository, Pydantic schema, atomic ZIP writes
  simulation/nec2: input writer, parser, process runner, normalization
  simulation: SWR normalization, fingerprint, assumptions, preflight
  optimization: family descriptors and hybrid deterministic engine
  reporting: CSV, self-contained HTML, construction sheet, SVG charts
```

The application block lists the original dipole-core use cases. Current use
cases also include band analysis, family optimization, convergence studies,
parameter sweeps, robustness, impedance synthesis, measurement tuning, and
project bundles. The domain is no longer dipole-only.

## Dependency rules

- `domain/` imports only the Python standard library.
- `application/` imports the domain and defines ports; it does not import
  PySide6, Pydantic, or concrete adapters.
- `presentation/` is Qt-free display policy shared by the UI and human-readable
  reports. It imports only the domain.
- `persistence/` imports the domain and Pydantic; it is the only place where
  the project schema is serialized.
- `simulation/nec2/` implements the `AntennaSolver` port. It imports the
  domain and application-layer ports and simulation services, but the domain
  and application do not import it.
- The GUI depends on application use cases and ports. `ui/app.py` is the
  composition root and builds the concrete repository, solver, NEC exporter,
  and pre-flight runner; `main_window.py` no longer imports solver or
  persistence details. New adapter imports must stay in the composition root.
- UI widgets never perform electromagnetic calculations. Simulation runs in a
  `QThread` worker and returns a normalized `SimulationResult`.

### Qt worker lifecycle

Background UI work goes through one controller,
`ui/workers/task_runner.TaskRunner` (see
[ADR-0053](ADR/0053-qt-worker-task-lifecycle.md)). The controller:

- owns one `QThread` and one worker at a time;
- queues every worker-to-controller signal to the GUI thread and carries a
  generation so a late result from an abandoned task is ignored;
- emits `succeeded`, `failed`, `cancelled`, and `finished` only after the
  thread has stopped, so a handler may start the next task;
- cancels cooperatively and closes with a bounded wait; if the worker does not
  stop in time, the thread is detached, keeps its worker alive, and deletes
  both when it finishes;
- provides `run_worker_blocking()` for the modal project-I/O and end-fed paths,
  built on the same controller instead of a second thread lifecycle.

`QThread(` and `moveToThread(` are forbidden outside `task_runner.py`; an
architecture test enforces the boundary.

## Project creation and persistence flow

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
SaveProject ──► ProjectRepository ──► ProjectContainerRepository
```

Opening a project reverses the flow: the repository validates and migrates the
document, maps it to domain objects, and the application re-validates the
project before returning it.

## Simulation flow

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

## Pre-flight flow

```text
MainWindow
  ├─ base/family SimulationSpec + project feed chain
  ├─ domain/design/preflight.py
  │    ├─ AntennaModel.validate()
  │    ├─ shared wire crossing/overlap checks
  │    ├─ installation envelope and construction record
  │    └─ PreflightFinding / PreflightReport
  └─ simulation/preflight.py
       ├─ validate_segmentation()
       ├─ validate_nec2_assumptions()
       └─ stored result status and model fingerprint
```

`PreflightReport` is computed on demand and is not persisted. The UI dialog,
construction sheet, native PDF, and ZIP package all render the same report.
Errors make `ready` false; warnings and information remain review items. The
solver adapter calls the same `validate_nec2_assumptions()` helper, so
pre-flight and a real run cannot disagree about below-ground geometry,
ground clearance, permeability, or the far-field ground request.

## Main-window flow

```text
MainWindow
  ├─ BasicAntennaDialog / DipoleForm ──► DipoleParameters
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

## Comparison and report flow

```text
Selected DesignVariant ──► RunSimulation ──► SimulationResult
        │                                      │
        ├─ Add/Rename/Delete variant            ├─ ComparisonDialog (A/B)
        ├─ ResultsView (impedance/SWR/pattern/currents)
        └─ CSV / HTML report ──► reproducible artifact
```

Reports are generated from the immutable result and the project snapshot. The
HTML and native PDF reports include the fingerprint, solver version,
specification, diagnostics, impedance table, resonance points, SVG charts, a
canonical geometry figure, azimuth/elevation pattern cuts, and one static 3D
total-gain wireframe in the primary far-field section. The geometry figure is
rendered offscreen from the design snapshot with a fixed size and light theme;
report rendering does not read live widgets. The 3D wireframe is built by the
Qt-free `reporting/pattern_lobe.py` with a fixed projection and palette, is
decimated to at most 19×37 displayed vertices, and keeps the stored pattern and
2D cuts at full resolution. The `UiPreferences` report options can omit the
primary figure (enabled by default) and optionally add one figure per analyzed
band (disabled by default). Both values are passed to the report writers; a
disabled primary figure also suppresses the per-band figures. Band analysis adds a pattern section per band and
keeps the 2D cuts only. A single-cut or missing grid reports an explicit
unavailable state instead of synthesizing a surface. See UX26 and UX40 in
`AUTONOMOUS_BACKLOG.md`.

## Family optimizer flow

```text
AntennaDesignParameters + base SimulationSpec
        │
        ▼
optimizer_availability(parameters)
  ├─ explicit family descriptor, or
  └─ explicit unavailable reason (no fallback)
        │
        ▼
FamilyOptimizationDialog
  ├─ all variables, lock controls, topology shown as context
  ├─ objective, weights, soft constraints
  └─ budget profile, seed, solver-run estimate
        │
        ▼
OptimizeAntenna (application use case)
  ├─ descriptor builder and hard-constraint validation
  ├─ per-candidate model, segmentation, and solver run
  ├─ metric extraction and objective scoring
  └─ deterministic hybrid engine:
       differential evolution + bounded local pattern search
       + feasibility ranking + cache + sensitivity
        │
        ▼
Apply Best through exhaustive UI adapter ──► family editor ──► full simulation
```

Optimization runs in a worker thread with cancellation. The final
full-sweep/pattern simulation is performed after applying the result so the
normal result/report path remains the single source of truth. The UI adapter
registry is exhaustive: a supported optimizer cannot silently write into the
basic dipole form.

## Geometry families and persistence (completed; physical validation deferred)

The geometry work started with a vertical center-fed dipole in the existing
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
solver adapter does not need geometry-specific branches. Schema version 63 is
current: parameter payloads are additive within the current container. A
design may also store an optional analysis band plan; it is intent metadata
and never changes the canonical geometry. Series RLC loads are
optional antenna payloads and are emitted as `LD 0` cards by the solver
adapter. The canonical model also carries optional additional sources with
amplitude and phase; the NEC adapter emits one `EX` card per effective source
while the primary feed remains the impedance/SWR reference port. The phased
vertical array family uses that multi-source model with an ideal linear phase
and amplitude progression. The stacked Yagi composes two to four identical
Yagi level models with the same multi-source model; level 1 is the primary
port, while the splitter and phase-line hardware are ideal and not modeled.
The quad beam uses a reflector loop, a driven loop,
and an optional director loop on a single feed. The log-periodic family uses
one `TransmissionLine` between adjacent element centers with the generic
`phase_reversal` flag; the rear element terminates the line and the front
element is fed. The NEC adapter maps that flag to a negative TL characteristic
impedance.

The form exposes an antenna-type selector with conditional spacing/sides
fields. The geometry view is renderer-neutral: `ui/geometry/builder.py`
projects the canonical wires with an orthographic basis, attaches semantic
dimensions and detail insets, and `ui/geometry/layout.py` places the dimensions
in screen space using font metrics and collision avoidance. The geometry panel
exposes a single **Construction** view plus **3D**. Construction resolves to the
principal projection (front for vertical planes, top for horizontal arrays and
beams, top for the cubical quad, front plus a top inset for non-planar models),
and changing the model resets zoom, pan, and vertical exaggeration. Reports,
construction sheets, and comparison use type-aware dimensions and a wire
schedule with each wire's endpoints, length, diameter, material, and the feed
point.

The main window uses a `QUndoStack` with immutable project snapshots for
Undo/Redo. Simulation runs are kept outside the undoable editable snapshot and
merged back on restore, so undoing a design edit does not delete completed
solver history. `ResultsView` shares a reusable `ChartCursor` across the
impedance, SWR, pattern, currents, and measurement charts.

Measurement sessions are project metadata: `MeasurementSession` groups
imported `Measurement` records, and `Measurement.session_id` is the only link.
The sessions dialog edits a local immutable `Project` and returns it to the main
window, where it enters the normal undo history. The before/after comparison is
a pure `measurement_comparison` function over two measurements; the dialog only
formats its points and warnings.

The project journal is also project metadata. `JournalEntry` records are
created and edited in a local immutable project copy and returned to the main
window through the normal undo history. The reporting layer captures snapshot
rows once, at explicit request; the comparison dialog only renders the stored
rows and never recaptures them. Images remain local file references. The
timeline, editor, and comparison dialogs do not modify the design or run the
solver.

The tuning assistant runs the
`TuneMeasurement` application use case in a worker thread. It executes three
bounded solver probes around the primary dimension plus one verification probe,
then applies the proposed parameters through the existing family UI adapter.
The estimate is a local finite-difference result; no measurement path performs
electromagnetic calculations itself. The measurement uncertainty card uses a
pure `measurement_uncertainty` assessment that reports documentation gaps,
resonance count, sweep spacing, and simulated comparison coverage. It does not
invent numerical uncertainty values. Parameter sweeps use the family optimizer
descriptor for bounded variable sets and parameter construction; the
`RunParameterSweep` use case runs each grid point through the solver in a
worker thread. The dialog only renders the points and applies the selected
parameters through the normal family adapter. Guided experiments are curated
`SweepPlan` presets from `design/guided_experiments.py`; the chooser opens the
same sweep dialog with those axes and a guide banner, so plotting, validation,
cancellation, and apply behavior remain single-sourced. The reference design
library is a thin chooser over `design/reference_library.py`: entries return
existing family parameters, the dialog displays the evidence registry and
published/modeled text, and the main window creates a project through the same
project-creation path before optionally running the normal simulation. It adds
no alternate solver or persistence path. Tolerance analysis uses the same
descriptor contract: `RunRobustness` evaluates nominal, corner, and seeded
Monte Carlo scenarios in a worker thread, and the dialog is read-only. It does
not change the project or persist its transient grid and sample results.

The frequency-first estimator layer is domain code: `DesignIntent` and
`DimensionEstimate` are Qt-free, and `EstimateAntennaDimensions` is an
application use case. The UI displays the estimate and applies the resulting
`AntennaDesignParameters`; numerical refinement remains in the existing
optimization and synthesis use cases.

The geometry presentation layer has no Qt dependency in `scene.py`,
`views.py`, or `builder.py`; only the layout and widget use Qt. The same scene
can therefore be tested headlessly and reused for future SVG/PDF/DXF export.


The UI is bilingual through `ui/i18n.py` and supports an adaptive metric or
imperial length display policy with a fixed-unit escape hatch. Project files
and the domain remain in canonical units. See
[`DISPLAY_UNITS_SPEC.md`](DISPLAY_UNITS_SPEC.md).

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

Project files use the `antennadesk.project` ZIP container with container
version 1 and schema version 63. Saves are atomic: build the container in
memory, write a temporary file in the target directory, flush and `fsync`,
then replace the destination with `os.replace`. Autosave uses the
application-data recovery folder: it writes a design-only project container
(without completed simulation runs or raw solver output) atomically, then a
small JSON metadata sidecar, and never replaces the project file. It is
debounced after design edits and skipped above 2 MB. A normal save or close
removes both; startup offers recover or discard. Recording a simulation result
alone does not trigger autosave. The schema and container history is
single-sourced in [`DOMAIN_MODEL.md`](DOMAIN_MODEL.md#schema-policy); the
current build has no gzip/plain-JSON reader and migrates schema 59 and 60 in
place on open.

Simulation runs are persisted as immutable runs (introduced in schema 30). Raw
solver text is stored in optional separate entries so it can be omitted without
rewriting the normalized result. Project files are versioned ZIP containers
(container version 1, schema version 63) with a manifest, project metadata,
designs, runs, raw text, and optimization summaries as separate validated
entries. Saves are atomic and deterministic. The UI warns at 32 MB, blocks a
container above 64 MB, blocks total expanded entries above 256 MB, and offers
simulation-history compaction. Opening reads the manifest, metadata, and
designs, then exposes runs through a `ProjectSession` that loads only the
selected design's latest run or batch. The reader verifies every loaded entry's
size, CRC32, and SHA-256 against the manifest through a bounded stream, so a
zip bomb or a manifest mismatch is rejected before the domain model is built.
An optional project-level `SiteGroundProfile` is carried by the simulation
specification; the NEC adapter emits the second-medium/cliff fields and
`RP 2`/`RP 3`, with the explicit far-field-only limitation.
`prepare_payload()` returns a `PreparedProject` with the exact payload,
compressed and expanded sizes, entry count, and limits; the UI reports both
sizes. Saving a `ProjectSession` copies unchanged run entries directly from the
source container, serializes only new runs, and reopens the session from the
saved file. Compaction uses the same path with the retained run ids. If a custom
run store or new in-memory runs make the copy ambiguous, the repository falls
back to materializing the run tuple. Gzip, plain
JSON, and schema 58 and older are rejected; the project has not shipped to
users. See [ADR-0050](ADR/0050-zip-project-container.md).

Multiband analysis is an application-level batch over the existing single-band
solver boundary. `AnalyzeBands` runs one `SimulationSpec` per selected band,
keeps completed results when another band fails or is cancelled, and groups
them in an immutable `BandAnalysisResult`. Independent bands may run in a
bounded worker pool while results and progress stay in selection order; the
command defaults to the sequential path. The adapter still receives one
contiguous `FrequencyPlan` at a time, so no NEC deck or parser change is
required. OCFD and custom designs can carry an optional ideal feed-transformer
ratio in the same `SimulationSpec` cascade used by end-fed and T2FD designs. Each band run carries a stable `band_id` and shared `batch_id`; the
project reconstructs the latest batch from those runs. Band plans default to
100 frequency points per band. Pattern resolution is global and snapshots are
one per band by default; the batch pattern budget coarsens or disables patterns
to stay within its 24 MB working estimate. After fitting, the UI classifies the
estimated compressed project size: above 32 MB it asks for confirmation, and
above the 64 MB project limit it blocks the run before starting any worker. The
architecture leaves a future segmented `FrequencyPlan` or multi-`FR` deck as an
optimization, not a prerequisite for the user workflow.

## Current limitations

- `nec2c` is bundled in the native AppImage, Debian package, and Windows zip,
  but remains an external runtime dependency for wheel installs. Native release
  artifacts are unsigned by default.
- Measurement import is file-based (CSV or one-port Touchstone `.s1p`), and the
  simulated sweep can be exported as Touchstone. There is no live VNA or
  instrument-control adapter.
- Series and parallel RLC loads are supported on one wire segment. L/Pi/T
  matching networks are post-processed at the feedpoint. Horizontal wire
  dipoles support an optional sampled parabolic sag; other wire families remain
  straight. Yagi elements support optional tapered tips; boom-mounting
  correction is not modeled. General transmission-line geometry is modeled as
  NEC `TL` two-ports between wire points; physical parallel-line coupling is not
  modeled.
- Far-field samples are NEC power gains. Directivity and realized gain are
  derived per frequency and stored with the result; the pattern charts can
  display power gain, directivity, or realized gain. See
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
- Custom and imported designs, magnetic loops, random wires, and
  log-periodic arrays have an explicit unavailable optimizer reason. Typed
  G5RV, ZS6BKW, Zepp, biquad,
  double biquad, Beverage, and loaded/linked dipole have family optimizers; the
  doublet radiator uses the dipole
  optimizer. Space
  constraints are limited to variable bounds, family geometry rules, and the
  Yagi minimum-gap rule. Band-aware and robust modes evaluate multiple
  operating points; the Pareto front is descriptive; and each run stores a
  compact summary with the design.
- One full-wave engine (NEC-2) is supported; additional engines are deferred.
