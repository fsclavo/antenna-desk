# Domain model

This document describes the current domain. It covers the generated antenna
families (dipoles, loops, verticals, Yagi, Moxon, fan dipole, inverted-V,
inverted-L, end-fed, OCFD, J Pole/Slim Jim, and Ringo), custom wires, one feed
point per antenna, basic ground models, loads, matching networks, feed lines,
imported measurements, and persisted simulation runs.

## Units and coordinates

- Length: meters.
- Frequency: Hz.
- Conductivity: S/m.
- Angles: degrees at the boundary; radians only for trigonometric calculations.
- Coordinate system: right-handed, Z up.
- Azimuth: degrees from +X toward +Y, normalized to `[0, 360)`.
- Height: height of the horizontal wire above ground. For Yagi and Moxon,
  `height_m` is the boom/element centerline height; with vertical polarization
  the elements or rectangle extend symmetrically around it.

The UI may display meters or imperial units; conversion happens at the UI
boundary through `domain/common/units.py`.

## Entities

### Point3D

An immutable point with `x_m`, `y_m`, and `z_m`. All coordinates must be
finite.

### ConductorMaterial

A homogeneous material with a name, conductivity in S/m, and relative
permeability. The `COPPER` and `ALUMINUM` presets use nominal engineering
values.

### Wire

A straight conductor with an identifier, start point, end point, radius, and
material. The wire must have non-zero length and a positive radius.

### SeriesLoad and ParallelLoad

A series or parallel RLC load at a position along a wire:

- `id`
- `wire_id`
- `offset_m` from the wire start
- `resistance_ohm`, `inductance_h`, `capacitance_f` (non-negative)
- At least one of R, L, or C must be non-zero.

The load kind is stored as `series` or `parallel`. The load is mapped to one
solver segment by the NEC adapter (`LD 0` or `LD 1`).

### FeedPoint

A feed point on a wire, expressed as an offset in meters from the wire start.
The offset must be within the wire length. A feed at a wire end is allowed but
produces a warning.

### GroundModel

One of:

- `free_space`
- `perfect`
- `finite` with relative permittivity >= 1 and positive conductivity.

Free-space and perfect ground do not accept electrical parameters.

### Environment

Currently contains only the ground model.

### AntennaModel

The canonical, immutable antenna representation. It contains a name, design
frequency, one or more wires, one feed point, and an environment. Invariants:

- At least one wire.
- Unique wire identifiers.
- The feed references an existing wire.
- The feed offset is inside the wire.
- Every load references an existing wire and is inside that wire.
- All numeric values are finite.

### DipoleParameters

User-facing parameters for a center-fed wire dipole:

- `frequency_hz`
- `total_length_m`
- `height_m`
- `azimuth_deg`
- `wire_radius_m`
- `material`
- `ground`

`to_antenna()` generates the canonical model. For a horizontal dipole the wire
runs from `(-L/2 cos A, -L/2 sin A, H)` to `(L/2 cos A, L/2 sin A, H)`, where
`L` is the total length, `A` the azimuth, and `H` the wire height. For a
vertical dipole the wire runs from `(0, 0, H)` to `(0, 0, H + L)`, where `H` is
the base height; the azimuth is ignored. The feed is always at the center.

### FoldedDipoleParameters

User-facing parameters for a horizontal two-wire folded dipole:

- `frequency_hz`
- `total_length_m`: length of each parallel element
- `height_m`: wire height above ground
- `spacing_m`: center-to-center spacing between the elements
- `azimuth_deg`
- `wire_radius_m`
- `material`
- `ground`

`to_antenna()` generates four wires: two parallel elements and two end
connectors. The feed is at the center of the driven element. The total
conductor length is `2 * total_length_m + 2 * spacing_m`.

### LoopParameters

User-facing parameters for a regular-polygon loop:

- `frequency_hz`
- `circumference_m`: total conductor length
- `height_m`: bottom of a vertical loop or plane height of a horizontal loop
- `sides`: 3–128 straight sides
- `orientation`: `vertical` or `horizontal`
- `azimuth_deg`
- `wire_radius_m`
- `material`
- `ground`

`to_antenna()` generates one wire per side, connected end-to-start into a
closed polygon. A vertical loop lies in a vertical plane with `height_m` as its
bottom above ground; `top_height_m` is the highest actual polygon vertex, which
is not `height_m + diameter_m` for odd side counts. A horizontal or sky loop
lies in a horizontal plane at `height_m`; its `top_height_m` is the plane
height. `azimuth_deg` rotates the vertical loop plane around the vertical axis,
or the horizontal polygon within its plane. The feed is at the midpoint of the
first side. A square loop uses four sides; a larger side count approximates a
circular loop.

### MagneticLoopParameters

A first-class vertical small loop with a top gap and a series tuning capacitor.
Parameters are frequency, diameter, tuning capacitance, bottom height, polygon
side count, gap length, capacitor ESR, azimuth, wire radius, material, and
ground. `to_antenna()` creates the split loop conductor, a short capacitor wire
across the gap, a series capacitor load with optional ESR, and a feed at the
midpoint of the bottom side. Conductor loss is computed by the solver from the
material and radius. A coupling loop, capacitor voltage, and detailed capacitor
loss model are not included. The generator is experimental.

### CustomAntennaParameters

User-defined straight wires with a frequency, feed, ground, optional loads, and
an optional ideal feed-transformer ratio. It is the escape hatch for geometries
outside the guided templates. It has no parameterized topology, so the family
optimizer is explicitly unavailable. Its wire, feed, and load rules are validated by
`AntennaModel`.

### YagiParameters

A first-class parametric Yagi with an ordered tuple of `YagiElement` values,
boom height and azimuth, polarization, driven-element index, optional folded
driven element, material, and ground. Elements store boom position, total
length, and radius. Horizontal polarization places the elements in a horizontal
plane. Vertical polarization keeps the boom horizontal and places each element
in a vertical plane. In both cases `to_antenna()` creates straight wires and a
center feed on the selected driven element. When `driven_folded` is true, the
driven element becomes two parallel conductors separated by
`driven_fold_spacing_m` along the boom, with two end connectors; the feed stays
on the first conductor. When `match_type` is `beta_hairpin`, the straight
driven element is split at its centre and a shorted two-conductor stub is added
along the boom; `match_length_m` and `match_spacing_m` set the stub length and
the driven-element gap. A folded driven element and a beta/hairpin match are
mutually exclusive. Gamma matches are not modeled because NEC-2 close-spaced
gamma assemblies are unreliable; use the matching-network dialog for an
equivalent. Vertical geometry is rejected when the longest element would reach
the ground. The NBS TN-688 5-element 0.8λ preset is a starting geometry; the
published design uses a folded driven element, which can be enabled explicitly.
Edited designs are experimental.

### RingoParameters

A first-class Ringo-style vertical with radiator height, base matching ring
diameter/height/side count, radius, material, and ground. `to_antenna()` creates
the vertical radiator, a ring connector, and the ring polygon. The generator is
experimental.

### JPoleParameters

A first-class J Pole/Slim Jim with radiator height, stub length, spacing, feed
offset, base height, folded flag, radius, material, and ground. `to_antenna()`
creates the J Pole radiator, stub, and base connector. `folded=True` creates a
Slim Jim folded rectangle with top and bottom connectors and a gap in one
vertical leg. The feed offset is measured from the stub base. The generator is
experimental.

### EndFedParameters

A first-class single-wire antenna fed at one end, with separate feed and far-end
heights, azimuth, radius, material, and ground. `length_m` is the physical
conductor length; the horizontal run is derived from the height difference. An
end height outside the wire's vertical reach is rejected. It can model
horizontal wires or slopers. The generator is experimental.

`preset` is `endfed`, `sloper`, or `random_wire`. The preset is metadata for
catalog routing, reports, and the inline editor; the geometry and matching
fields remain fully editable. A doublet is a normal `DipoleParameters` design
with a project-level `FeedLine`; it does not introduce a new design payload.

### FanDipoleParameters

A first-class multi-band fan dipole with one or more `FanElement` pairs, apex
height, azimuth, radius, material, and ground. Each pair has a total length and
included angle. Elements must use distinct included angles; same-angle elements
would overlap and are rejected. `to_antenna()` creates two sloping wires per
pair sharing the apex, with the feed at the first leg. The generator is
experimental.

### MoxonParameters

A first-class two-element Moxon rectangle with element width, spacing,
reflector/driven tip lengths, height, azimuth, polarization, radius, material,
and ground. Horizontal polarization keeps the rectangle in a horizontal plane.
Vertical polarization puts the complete rectangle in a vertical plane while
the boom remains horizontal. `to_antenna()` creates the reflector, driven
element, and four bent tip wires; the feed is at the center of the driven
element. Vertical geometry is rejected when `height_m - width_m / 2` would
reach the ground. The generator is experimental.

### InvertedVParameters

A first-class two-leg inverted-V with frequency, leg length, apex height,
included angle, azimuth, wire radius, material, and ground. `to_antenna()`
creates two sloping wires meeting at the apex, with a center feed at the apex.
The leg ends must stay at or above ground. It is experimental; its geometry and
scaling are tested, but it has no independent numerical performance reference.

### InvertedLParameters

A first-class bent end-fed wire with a vertical section fed at the base and a
horizontal top run. Parameters are frequency, vertical height, horizontal
length, base height, azimuth, wire radius, material, and ground. `to_antenna()`
creates a vertical wire, a horizontal wire meeting at the top corner, and a feed
at the base of the vertical section. `base_height_m` keeps the feedpoint and
corner above ground. The generator is experimental and has no independent
numerical reference yet.

### Antenna families

`AntennaFamily` groups designs as Dipole, Yagi, Loop, Vertical, or Custom.
`antenna_family()` maps native parameters and legacy generator metadata to a
family; `antenna_template_id()` returns the native template or generator
identifier. Current generators are first-class parameters, so the catalog and
the design panel share the same taxonomy.

### VerticalParameters

A first-class vertical radiator with height, base/radial-plane height, optional
radial count/length/angle, wire radius, material, and ground. `to_antenna()`
creates the vertical wire and evenly spaced radial wires connected at the base,
with the feed at the radiator base. The editor's ground, elevated, and screen
radial systems are UI-only starting presets; only the numeric fields are
persisted. It is experimental.

An optional loading coil is described by `loading_coil_enabled`,
`loading_coil_offset_m` (measured from the radiator base),
`loading_coil_inductance_h`, and `loading_coil_resistance_ohm`.
`to_antenna()` adds a `SeriesLoad` with the reserved identifier
`loading-coil` on the radiator, and `from_custom_parameters()` restores the
coil fields when that load is present. The coil is an ideal series RLC load
with zero capacitance; it is not a physical solenoid model.

### TrapDipoleParameters

A first-class center-fed dipole with one parallel LC trap on each side. It
stores the low-band frequency, high-band frequency, total center-section
length, outer-section length per side, target trap frequency, trap inductance,
height, orientation, azimuth, wire radius, material, and ground. The trap
capacitance is derived from parallel resonance:

```text
C = 1 / ((2 * pi * f_trap)^2 * L)
```

`to_antenna()` creates one straight wire, a center feed, and two `ParallelLoad`
objects with the reserved identifiers `trap-left` and `trap-right`. The total
wire length is `inner_length_m + 2 * outer_length_m`. The traps are
template-managed loads: editing the parameters regenerates them, while other
user loads are preserved.

### T2FDParameters

A first-class terminated folded dipole. It stores the lowest and highest design
frequencies, the length of each parallel conductor, the conductor spacing, the
height, orientation, termination resistance, transformer ratio, azimuth, wire
radius, material, and ground. `to_antenna()` creates four wires: two parallel
conductors and two end connectors. The feed is at the midpoint of one
conductor. The other conductor carries a `SeriesLoad` with the reserved
identifier `t2fd-termination` at its midpoint.

The termination is a series `LD 0` resistor in the NEC model. The feed
transformer is an ideal post-processing two-port selected by
`transformer_ratio`; it is not part of the NEC geometry. The template manages
the termination load, so editing the parameters regenerates it while preserving
other user loads. The default starting dimensions use Cebik's wide-long rule,
`300/F(MHz)` feet of span and `10/F(MHz)` feet of spacing at the lowest design
frequency. See [ADR-0018](ADR/0018-t2fd-termination-and-transformer.md).

### G5RV preset

The G5RV catalog preset is a `CustomAntennaParameters` design with
`generator_id="g5rv"` and `generator_name="G5RV"`. It generates a 31.1 m
dipole, a short source wire, and a geometry `TransmissionLine` matching section
(300 Ω / 8.84 m or 450 Ω / 10.36 m). The line is lossless and does not radiate.
The preset is an antenna configuration, not a new first-class parameter type;
the generic custom-wire and transmission-line editors remain available.

### OCFDParameters

A first-class single-wire horizontal dipole with a feed point offset from the
center. It stores frequency, total length, feed ratio, height, azimuth, radius,
material, ground, and an optional ideal feed-transformer ratio. The transformer
ratio is `1.0` for no transformation and can be set to the common OCFD `4.0`.
`to_antenna()` builds the canonical model; `to_custom_parameters()` preserves
the ratio in the generic custom field, and `from_custom_parameters()`
reconstructs OCFD parameters from legacy custom designs.

### AntennaDesignParameters

`AntennaDesignParameters` is the union of `DipoleParameters`,
`FoldedDipoleParameters`, `LoopParameters`, `MagneticLoopParameters`,
`OCFDParameters`, `VerticalParameters`, `InvertedVParameters`,
`InvertedLParameters`, `YagiParameters`, `MoxonParameters`,
`FanDipoleParameters`, `EndFedParameters`,
`JPoleParameters`, `RingoParameters`, `TrapDipoleParameters`,
`T2FDParameters`, and `CustomAntennaParameters`. `antenna_type_for()` maps a
parameter object to its native type; `custom` remains the arbitrary-wire escape
hatch.

### DesignVariant

A named design with an identifier, an antenna type identifier (for example
`wire_dipole`, `trap_dipole`, or `t2fd`), the generating parameters, and the
derived `AntennaModel`. It may also carry an optional analysis `BandPlan`; this
is user intent and does not alter the geometry. Construction validates that the
antenna type matches the parameters and that the derived geometry matches both.

`with_parameters()` returns a new variant and updates both the antenna type and
the derived model; it never mutates the original. `with_band_plan()` updates the
persisted analysis intention independently of the geometry.

### Project

An immutable project with an identifier, name, description, timestamps, and a
tuple of design variants. Invariants:

- Non-empty project name.
- Timezone-aware timestamps.
- `updated_at` is not earlier than `created_at`.
- Unique design identifiers and names.

`with_design()` returns a new project, replacing or appending a design.

## Measurements

`MeasurementPoint` stores a measured frequency and complex impedance.
`Measurement` stores a name, timestamp, reference impedance, source, points,
calibration, reference plane, feed line/accessories, and notes. Measurements are
stored in the project and rendered with SWR computed at their reference
impedance.

## Project file

The native format is versioned JSON, stored losslessly gzip-compressed.
Plain JSON files from older versions are still accepted. The envelope is:

```json
{
  "format": "antennadesk-project",
  "schema_version": 8,
  "project": {
    "id": "11111111-1111-4111-8111-111111111111",
    "name": "40 m dipole",
    "description": "Half-wave dipole for the 40 m band.",
    "created_at": "2026-10-29T12:00:00Z",
    "updated_at": "2026-10-29T12:00:00Z",
    "designs": [
      {
        "id": "22222222-2222-4222-8222-222222222222",
        "name": "Initial",
        "antenna_type": "wire_dipole",
        "parameters": {
          "frequency_hz": 7100000.0,
          "total_length_m": 20.0,
          "height_m": 8.0,
          "orientation": "horizontal",
          "azimuth_deg": 0.0,
          "wire_radius_m": 0.001,
          "material": {
            "name": "copper",
            "conductivity_s_per_m": 58000000.0,
            "relative_permeability": 1.0
          },
          "ground": {
            "kind": "finite",
            "relative_permittivity": 13.0,
            "conductivity_s_per_m": 0.005
          }
        },
        "antenna": {
          "name": "Initial",
          "design_frequency_hz": 7100000.0,
          "wires": [
            {
              "id": "radiator",
              "start": {"x_m": -10.0, "y_m": 0.0, "z_m": 8.0},
              "end": {"x_m": 10.0, "y_m": 0.0, "z_m": 8.0},
              "radius_m": 0.001,
              "material": {
                "name": "copper",
                "conductivity_s_per_m": 58000000.0,
                "relative_permeability": 1.0
              }
            }
          ],
          "feed": {"wire_id": "radiator", "offset_m": 10.0},
          "environment": {
            "ground": {
              "kind": "finite",
              "relative_permittivity": 13.0,
              "conductivity_s_per_m": 0.005
            }
          }
        }
      }
    ],
    "simulation_runs": []
  }
}
```

The complete example lives in
[`examples/dipole_40m.antennadesk`](../examples/dipole_40m.antennadesk). It is
kept as a version 1 fixture so the migration path is exercised; saving it from
the application writes version 16.

## Schema policy

- Current version: `16`.
- Version 1 files are migrated by adding the dipole `orientation` field with a
  default of `horizontal`.
- Version 2 files are migrated by adding an empty `simulation_runs` list.
- Version 3 persists normalized simulation runs, including raw solver text.
  SWR is stored as `null` when it is infinite.
- Version 4 adds optional `band_id` and `batch_id` metadata to simulation runs
  for multiband analyses. Existing runs load with both fields as `null`.
- Version 5 adds optional feed-transformer ratios to OCFD and custom designs.
  Existing designs load with `1.0`, preserving their raw-impedance behavior.
- Version 6 adds optional per-design band-intent metadata: the persisted band
  IDs and sweep point counts chosen for analysis. Existing designs load with
  no stored plan and use the family default.
- Version 7 adds the Yagi and Moxon `polarization` field. Existing arrays load
  as `horizontal`; vertical arrays add ground-clearance validation and
  orientation-aware geometry.
- Version 8 adds the vertical top-hat fields. Existing vertical designs load
  with the top hat disabled; the migration infers the hat radius and wire count
  from any saved `top-hat-*` wires.
- Version 9 adds the inverted-L design type. Existing designs are unchanged.
- Version 10 adds the loop `orientation` field. Existing loops load as
  `vertical`; horizontal or sky loops use `horizontal`.
- Version 11 adds the magnetic-loop design type. Existing designs are
  unchanged.
- Version 12 adds the optional folded Yagi driven element. Existing Yagis load
  with a straight driven element.
- Version 13 adds the optional beta/hairpin Yagi match. Existing Yagis load
  with no matching harness.
- Version 14 adds the optional project-level balun/unun loss model and the
  per-frequency `balun_loss_db` result field.
- Version 15 repairs saved Yagi folded/match spacing values that were smaller
  than twice the driven-element radius. The repair uses four radii spacing and
  eight radii hairpin length to keep the conductors separate and the short
  wires representable by NEC-2.
- Version 16 introduces the half-square and bobtail-curtain self-contained
  vertical-array types. Existing designs are unchanged; the new variants use
  `ScvParametersPayload` with an explicit `kind` discriminator.
- Folded dipole and loop parameters are additive in version 3; existing
  `wire_dipole` documents do not change.
- Series RLC loads are an optional antenna list in version 3; missing loads
  deserialize as an empty list.
- End-fed transformer ratio and counterpoise fields are additive in version 3;
  missing values default to no transformer and no counterpoise.
- Unknown fields are rejected.
- Unknown formats are rejected.
- Future schema versions are rejected with a clear error.
- Older versions are migrated through an explicit registry.
- Saves are atomic and files are size-limited.

## Current limitations

- Generated families and custom straight-wire designs are implemented. There is
  a coordinate editor and NEC/MMANA import, but no interactive wire-drawing
  editor.
- Series and parallel RLC loads are supported on one wire segment. L/Pi/T
  matching networks are post-processed at the feedpoint, and the vertical
  generator has a radial screen. Transmission-line two-ports between wire
  points are modeled as geometry; arbitrary radial screens are not.
- Optimization operates on typed generated parameters. Magnetic loops, random
  wires, arbitrary custom/imported geometry, and G5RV/ZS6BKW/Zepp/doublet
  custom generators have explicit unavailable reasons. Band-aware, robust, and
  Pareto optimizer modes are future work.
- Measurements are imported from CSV; there is no live instrument-control
  adapter.
- No numerical discretization in the domain; the segmentation policy is a
  configuration value, including optional per-wire overrides, and the solver
  adapter builds the actual layout.
- Simulation results are persisted as immutable runs in schema version 16.
  Band analyses store one run per band with a shared `batch_id`; the selected
  analysis band plan is a per-design intention and does not change geometry.
- Far-field values are NEC power gains. Directivity and realized gain are
  derived per frequency and stored alongside the impedance and power budget;
  see [ADR-0015](ADR/0015-realized-gain-and-directivity.md).
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.

## Simulation model

Phase 2 adds solver-independent simulation types:

- `FrequencyPlan`: a single frequency or a uniformly spaced sweep, with
  helpers for evenly spaced and design-frequency-preferred snapshots.
- `FarFieldRequest`: angular sampling for the far-field pattern.
- `AmateurBand` and `band_snapshot_frequencies()`: one representative pattern
  frequency per amateur band inside a sweep, with an evenly spaced fallback for
  narrow plans. `BandSelection` and `BandPlan` validate a multiband analysis
  request; `default_band_plan()` supplies evidence-labelled family defaults.
- `SegmentationPolicy`: explicit global counts, a documented heuristic, or
  per-wire overrides; `aligned_policy_for_model()` aligns the feed wire to a
  segment center and gives short connector wires a sensible minimum.
- `SimulationSpec`: frequency plan, segmentation, reference impedance,
  extended-kernel flag, conductor-loss flag, far-field request, optional
  pattern snapshot frequencies, optional feed line, matching network,
  `BalunLoss`, and timeout.
- `BalunLoss`: a project-level matched balun/unun insertion loss fitted as
  `Lref x (f/fref)^n`; it reduces realized gain but does not change geometry,
  impedance, or SWR.
- `SolverMetadata`: engine name, version, and executable.
- `SolverCapabilities`: what the adapter can represent.
- `TransmissionLine`: a lossless NEC TL two-port between two wire offsets,
  with characteristic impedance, physical length, and velocity factor.
- `SimulationResult`: status, spec, model fingerprint, solver metadata,
  per-frequency results, diagnostics, raw input/output, and timing.
- `FrequencyResult`: impedance, SWR, input power, currents, far field, power
  budget, directivity, realized gain, and mismatch, feed-line, network, and
  balun/unun loss components for one frequency.
- `TransmissionLine`: a mathematical two-port, not a radiating wire. The model
  stores physical length and velocity factor; the NEC adapter writes the
  free-space-equivalent length. Lines are drawn as dashed construction
  polylines and do not appear in far-field calculations.
- `PatternBudget`: an application policy that estimates persisted project size
  from the impedance sweep count, pattern snapshot count, far-field points, and
  segment count, then chooses the finest pattern step that fits. It may disable
  the far-field request when no step fits.
- `CurrentSample`, `FarFieldPoint`, and `PowerBudget`: normalized output
  records.
- `ResonancePoint` and `find_resonances()`: series reactance zero crossings
  from a frequency sweep.
- `OptimizationVariable`: bounded continuous, integer, or choice variable with
  a label, group, unit, bounds, step, and optional default lock.
- `AntennaOptimizerDescriptor`: the family contract: variables, initial values,
  parameter builder, hard validator, supported objectives, default objective,
  start points, and future band-aware/robust flags.
- `OptimizationBudget` and `budget_for()`: Fast, Balanced, and Thorough
  evaluation budgets with stagnation patience and automatic extension.
- `CandidateEvaluation` and `OptimizerRunResult`: feasibility, normalized
  violation, score, metrics, errors, cancellation, seed, evaluation log, and
  sensitivity points.
- `OptimizeAntennaCommand`/`OptimizeAntennaResult`: the application boundary
  that rebuilds the model and segmentation for every candidate, runs the solver
  through the port, extracts metrics, and returns the best parameters.
- The legacy `LengthOptimizationSpec`, `LengthEvaluation`, and
  `LengthOptimizationResult` remain for the old use case and tests, but the
  main UI no longer selects that path for supported typed families.
- `SimulationRun`: immutable snapshot linked to a design, with creation time
  and the normalized `SimulationResult`; optional `band_id` and `batch_id`
  identify a run inside a band analysis.
- `BandResult` and `BandAnalysisResult`: one immutable result per selected band
  and the batch that groups them.
- `BandMetrics`: best SWR, sampled power gain, takeoff angle, efficiency, and
  status derived from one band result.

The far-field values are NEC power gains in dB. For a frequency with a power
budget, directivity is derived from the gain and the structure efficiency. For
a frequency with a far-field pattern, realized gain is the power gain plus the
transducer gain of the feed-line, matching-network, and transformer cascade.
The pattern charts still show NEC power gain; the summary and reports show all
three metrics. See [ADR-0015](ADR/0015-realized-gain-and-directivity.md).

Simulation results are immutable and carry a deterministic fingerprint of the
model and spec. Completed and partial runs are stored in the project as
`SimulationRun` snapshots and reloaded by the GUI. When a project is opened,
the GUI shows the newest single-band run or the newest band batch, whichever is
later. A band batch stores one run per band with a shared `batch_id`; history
compaction keeps the latest single-band run and every run in the latest batch.
Editing a design removes its current result view, but earlier run snapshots
remain in the project. A project can contain multiple design variants; the GUI
edits the selected variant.

Family optimization is a joint bounded search over every declared geometry,
feed, and family-load variable. A family either has a descriptor or an explicit
unavailable reason; there is no generic primary-dimension fallback. The engine
runs deterministic differential evolution followed by bounded local pattern
search, ranks feasible candidates before infeasible ones, caches repeated
evaluations, logs every solver call, and reports sensitivity around the best
design. The final full-sweep/pattern simulation is run separately after the user
applies the optimized result through the family editor adapter.

## Design intent and dimension estimates

`domain/design` contains the frequency-first estimation layer:

- `DesignIntent` describes the requested family, frequency, environment, and
  family-specific subtype or constraint.
- `DimensionEstimate` returns valid `AntennaDesignParameters` plus a method
  identifier, confidence, assumptions, warnings, tolerance, source identifiers,
  and display rows.
- Estimators are pure domain functions registered by antenna type. They do not
  import Qt, the solver, or persistence.
- Applied estimates store `DesignProvenance` on the design; it is optional,
  additive schema metadata and is cleared when the design parameters change.

The resulting estimate is a starting point. Numerical refinement remains in
the optimization and synthesis use cases.
