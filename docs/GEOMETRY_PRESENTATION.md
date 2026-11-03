# Geometry presentation contract

This document is normative for every antenna family added to AntennaDesk.
It exists because geometry bugs are usually presentation or routing bugs, not
solver bugs: a new catalog entry can work in the domain while the sketch still
shows the previous antenna, or a special view can replace real wires with a
synthetic shape.

## Core rules

1. **Draw the canonical model.**
   The sketch must draw every `AntennaModel.wire` in the selected projection.
   Antenna-specific code may add dimensions, labels, and detail insets, but it
   must not replace the wire shape with a synthetic circle, line, or rectangle.
2. **Preserve every wire.**
   A family builder must not silently drop a wire. If a view is intentionally
   edge-on, the header must say so. If a detail is too small to read, use an
   inset marked *not to scale*.
3. **No invented geometry.**
   Any idealized construction line must be visibly distinguished from a
   canonical wire and must be documented in the family test.
4. **Dimensions are semantic and positive.**
   Every dimension must anchor to real model points or declared parameters,
   have non-zero length, and carry a value derived from the model/parameters.
   Do not label a projection extent as a physical diameter or length unless it
   is that quantity. Angular dimensions use arcs centred on a real vertex and
   the smaller included angle.
5. **Dimensions do not collide.**
   Labels must stay inside the safe drawing area and avoid each other. When
   there is not enough space, hide low-priority dimensions and report the count
   in the header. Never draw a dimension below the ground line.
6. **Default view follows geometry.**
   Vertical planar antennas use a front/elevation view, horizontal planar
   arrays use plan/top, and non-planar models use a front view with a top
   inset. Users may override the view.
7. **State resets with the model.**
   Changing the model resets zoom, pan, vertical exaggeration, and the default
   view so a new antenna cannot remain off-screen.
8. **Presentation types are explicit.**
   A domain type or legacy `generator_id` maps to exactly one presentation
   family. Unknown types fall back to the generic custom view with a visible
   note; they must not guess a loop or folded dipole from the wire count.
9. **Catalog routing is mandatory.**
   Every `CATALOG_TYPE_*` entry must have a route in both `new_antenna()` and
   `change_template()`/`_parameters_from_catalog()`. A catalog entry that
   returns `None` is a bug.
10. **Reports and exports share the scene.**
    SVG, PDF, PNG, and future formats must use the same scene and dimension
    requests as the interactive view.

## Required tests for a new family

Add all of the following before merging a new antenna family:

- Domain tests for parameters, validation, conversion, and persistence.
- A scene contract test asserting wire preservation for elevation and plan.
- A shape signature: segment/vertex count, closure, planarity, or the
  family-specific invariant (for example `sides == len(polylines)`).
- A default-view assertion.
- A dimension assertion: no zero-length dimensions, finite coordinates, and
  semantic values.
- A layout assertion at a standard size and at the minimum size.
- A catalog routing test for both New Antenna and Change Template.
- A legacy custom-generator test if the family can appear as
  `CustomAntennaParameters`.
- A solver integration or sanity test when the family affects the solver.

Pixel-perfect golden images are not the primary contract: fonts, DPI, and
platforms vary. Prefer deterministic scene snapshots and layout invariants.
`tests/ui/geometry/golden_scenes.json` stores normalized scene hashes for every
family and 2D view. After an intentional geometry change, update it with:

```bash
UPDATE_GEOMETRY_GOLDENS=1 uv run pytest tests/ui/geometry/test_contract.py
```

A small number of smoke images for light/dark themes is acceptable.

## Definition of Done for a new antenna family

1. Domain parameters, validation, and `to_antenna()`.
2. Stable `ANTENNA_TYPE_*` identifier and `antenna_type_for()` mapping.
3. Persistence payload and migration decision.
4. Catalog entry and `CATALOG_TYPE_*` constant.
5. `new_antenna()` route.
6. `_parameters_from_catalog()`/Change Template route.
7. Design-panel form or dialog.
8. Simulation spec mapping. Return a normal `SimulationSpec`; the main window
   applies the global pattern snapshot and resolution policy. Do not hardcode a
   pattern step or snapshot count in the family builder.
9. Reporting and construction-sheet rows.
10. Geometry presentation builder and semantic dimensions.
11. Scene, layout, routing, legacy, and export tests.
12. User-guide and changelog updates.

## Anti-patterns

- Dispatch on `len(model.wires)` to decide the antenna type.
- Hard-coded wire IDs outside the family builder or domain module.
- Drawing a loop as a circle regardless of its side count.
- Converting a planar array into one horizontal wire in elevation.
- Fixed pixel offsets for dimension labels.
- Screenshot tests that only assert "some non-white pixels exist".
- Adding a catalog entry without a routing test.
