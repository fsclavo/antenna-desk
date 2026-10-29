# Domain model

This document describes the Phase 1 domain. It is intentionally smaller than
the full blueprint: only horizontal half-wave dipoles, straight wires, one feed
point, and basic ground models are implemented.

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

User-facing parameters for a horizontal center-fed dipole:

- `frequency_hz`
- `total_length_m`
- `height_m`
- `azimuth_deg`
- `wire_radius_m`
- `material`
- `ground`

`to_antenna()` generates the canonical model. The wire runs from
`(-L/2 cos A, -L/2 sin A, H)` to `(L/2 cos A, L/2 sin A, H)`, where `L` is the
total length, `A` the azimuth, and `H` the height. The feed is at the center.

### DesignVariant

A named design with an identifier, an antenna type (`wire_dipole`), the
generating parameters, and the derived `AntennaModel`. Construction validates
that the derived geometry matches the parameters.

`with_parameters()` returns a new variant; it never mutates the original.

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
  "schema_version": 1,
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
    ]
  }
}
```

The complete example lives in
[`examples/dipole_40m.antennadesk`](../examples/dipole_40m.antennadesk).

## Schema policy

- Current version: `1`.
- Unknown fields are rejected.
- Unknown formats are rejected.
- Future schema versions are rejected with a clear error.
- Older versions are migrated through an explicit registry; the registry is
  empty until a second schema version exists.
- Saves are atomic and files are size-limited.

## Current limitations

- Only horizontal center-fed dipoles are implemented.
- No loads, networks, radials, or free-form conductors.
- No numerical discretization in the domain; the segmentation policy is a
  configuration value and the solver adapter builds the actual layout.
- Simulation results are not persisted yet.
- Relative permeability is not emitted to NEC. Conductor conductivity is
  emitted when `SimulationSpec.include_conductor_losses` is true.

## Simulation model

Phase 2 adds solver-independent simulation types:

- `FrequencyPlan`: a single frequency or a uniformly spaced sweep.
- `FarFieldRequest`: angular sampling for the far-field pattern.
- `SegmentationPolicy`: explicit segment count or a documented heuristic.
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

The far-field values are NEC power gains in dB. They are not realized gain or
directivity unless the model and losses justify that interpretation; the
adapter documents this explicitly.

Simulation results are immutable and carry a deterministic fingerprint of the
model and spec. They are cached in the GUI by design-variant ID for the current
session and are not yet stored in the `.antennadesk` project file; that will
require a schema version and migration in a later phase. Editing a design
removes its cached result. A project can contain multiple design variants; the
GUI edits the selected variant.
