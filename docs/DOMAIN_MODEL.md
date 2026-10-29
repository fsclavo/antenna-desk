# Domain model

This document describes the current domain. It covers straight-wire dipoles,
folded dipoles, regular-polygon loops, one feed point per antenna, and basic
ground models. The full blueprint contains additional antenna types and
measurements that are not implemented yet.

## Units and coordinates

- Length: meters.
- Frequency: Hz.
- Conductivity: S/m.
- Angles: degrees at the boundary; radians only for trigonometric calculations.
- Coordinate system: right-handed, Z up.
- Azimuth: degrees from +X toward +Y, normalized to `[0, 360)`.
- Height: height of the horizontal wire above ground.

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

User-facing parameters for a vertical regular-polygon loop:

- `frequency_hz`
- `circumference_m`: total conductor length
- `height_m`: bottom of the loop above ground
- `sides`: 3–128 straight sides
- `azimuth_deg`
- `wire_radius_m`
- `material`
- `ground`

`to_antenna()` generates one wire per side, connected end-to-start into a
closed polygon in a vertical plane. `height_m` is the bottom above ground;
`top_height_m` is `height_m + diameter_m`. `azimuth_deg` rotates the loop plane
around the vertical axis. The feed is at the midpoint of the first side. A
square loop uses four sides; a larger side count approximates a circular loop.

### AntennaDesignParameters

`AntennaDesignParameters` is the union of `DipoleParameters`,
`FoldedDipoleParameters`, and `LoopParameters`. `antenna_type_for()` maps a
parameter object to `wire_dipole`, `folded_dipole`, or `loop`.

### DesignVariant

A named design with an identifier, an antenna type (`wire_dipole`,
`folded_dipole`, or `loop`), the generating parameters, and the derived
`AntennaModel`. Construction validates that the antenna type matches the
parameters and that the derived geometry matches both.

`with_parameters()` returns a new variant and updates both the antenna type and
the derived model; it never mutates the original.

### Project

An immutable project with an identifier, name, description, timestamps, and a
tuple of design variants. Invariants:

- Non-empty project name.
- Timezone-aware timestamps.
- `updated_at` is not earlier than `created_at`.
- Unique design identifiers and names.

`with_design()` returns a new project, replacing or appending a design.

## Project file

The native format is versioned JSON:

```json
{
  "format": "antennadesk-project",
  "schema_version": 3,
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
the application writes version 3.

## Schema policy

- Current version: `3`.
- Version 1 files are migrated by adding the dipole `orientation` field with a
  default of `horizontal`.
- Version 2 files are migrated by adding an empty `simulation_runs` list.
- Version 3 persists normalized simulation runs, including raw solver text.
  SWR is stored as `null` when it is infinite.
- Folded dipole and loop parameters are additive in version 3; existing
  `wire_dipole` documents do not change.
- Unknown fields are rejected.
- Unknown formats are rejected.
- Future schema versions are rejected with a clear error.
- Older versions are migrated through an explicit registry.
- Saves are atomic and files are size-limited.

## Current limitations

- Wire dipoles, folded dipoles, and regular-polygon loops are implemented.
- No loads, networks, radials, or free-form conductors.
- Folded and loop geometry are parametric templates; free-form wire editing is
  not implemented.
- VNA CSV import and measurement records are not implemented yet.
- No numerical discretization in the domain; the segmentation policy is a
  configuration value, including optional per-wire overrides, and the solver
  adapter builds the actual layout.
- Simulation results are persisted as immutable runs in schema version 3.
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.

## Simulation model

Phase 2 adds solver-independent simulation types:

- `FrequencyPlan`: a single frequency or a uniformly spaced sweep.
- `FarFieldRequest`: angular sampling for the far-field pattern.
- `SegmentationPolicy`: explicit global counts, a documented heuristic, or
  per-wire overrides; `aligned_policy_for_model()` aligns the feed wire to a
  segment center and gives short connector wires a sensible minimum.
- `SimulationSpec`: frequency plan, segmentation, reference impedance,
  extended-kernel flag, conductor-loss flag, far-field request, and timeout.
- `SolverMetadata`: engine name, version, and executable.
- `SolverCapabilities`: what the adapter can represent.
- `SimulationResult`: status, spec, model fingerprint, solver metadata,
  per-frequency results, diagnostics, raw input/output, and timing.
- `FrequencyResult`: impedance, SWR, input power, currents, far field, and
  power budget for one frequency.
- `CurrentSample`, `FarFieldPoint`, and `PowerBudget`: normalized output
  records.
- `ResonancePoint` and `find_resonances()`: series reactance zero crossings
  from a frequency sweep.
- `LengthOptimizationSpec`: min/max length, target reactance, evaluation and
  tolerance limits, and sensitivity offsets.
- `LengthEvaluation`: length, impedance, SWR, error, and iteration index.
- `LengthSensitivityPoint`: length offset and resulting impedance/SWR.
- `LengthOptimizationResult`: status, best length/impedance/SWR, evaluation
  log, and sensitivity points.
- `SimulationRun`: immutable snapshot linked to a design, with creation time
  and the normalized `SimulationResult`.

The far-field values are NEC power gains in dB. They are not realized gain or
directivity unless the model and losses justify that interpretation; the
adapter documents this explicitly.

Simulation results are immutable and carry a deterministic fingerprint of the
model and spec. Completed and partial runs are stored in the project as
`SimulationRun` snapshots and reloaded by the GUI. The latest run per design is
shown when a project is opened. Editing a design removes its current result
view, but earlier run snapshots remain in the project. A project can contain
multiple design variants; the GUI edits the selected variant.

Dimension optimization is a bounded one-dimensional search over the primary
dimension (dipole/folded element length or loop circumference)
at the design frequency. It uses the solver through the same application port,
logs every evaluation, and computes ±10/25 mm sensitivity probes around the
best dimension. The final full-sweep/pattern simulation is run separately after
the user applies the optimized dimension.
