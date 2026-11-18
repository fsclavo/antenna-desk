# Adaptive length display units

- **Status:** Accepted
- **Date:** 2026-11-17
- **Decision:** [ADR-0044](ADR/0044-adaptive-length-display-units.md)
- **Execution:** U0–U5 complete; U6 documentation, help audit, and manual
  visual QA in progress in [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md)

## Purpose

Define how AntennaDesk presents lengths in the UI and in human-readable
reports. The domain, solver, project files, and machine-readable exports keep
canonical meters. The display policy adapts the unit to the magnitude so a
7 mm gap is not shown as `0.007 m` and a 20 m dipole is not shown as
`2000 cm`.

The policy is based on **the value being displayed**, never on the antenna
band or the design frequency. A 435 MHz Moxon and a 435 MHz Beverage have very
different physical sizes; frequency is not a unit selector.

## Non-goals

- No frequency/band-based unit switching.
- No per-project unit preference; the project schema is unchanged.
- No change to solver, domain values, or project storage.
- No decimal-separator change. Diagrams and reports keep the dot; spin boxes
  keep the Qt locale. Locale-aware decimal separators are a separate
  localization task.
- No inch fractions and no feet-inches compound notation.
- No automatic unit change for wire radius or diameter; they stay in mm/in.
- No DXF scaling to the display unit in this change.

## Canonical units

All stored lengths remain in meters. `domain/common/units.py` remains the
conversion source. The formatter is a pure presentation helper and does not
change any domain value.

## Unit policy

`UnitSystem` remains `METRIC`/`IMPERIAL`. Add an explicit length policy and a
`DisplayUnits` value object; do not add `UnitSystem.CM`. `UnitSystem` is a
measurement system, not a unit.

### Metric automatic

| Condition | Unit |
|---|---|
| value is zero | m, unless the field declares a small scale hint |
| `0 < abs(value) < 0.01 m` | mm |
| `0.01 m <= abs(value) < 1 m` | cm |
| `abs(value) >= 1 m` | m |

### Imperial automatic

| Condition | Unit |
|---|---|
| value is zero | ft, unless the field declares a small scale hint |
| `0 < abs(value) < 0.3048 m` | in |
| `abs(value) >= 0.3048 m` | ft |

Negative values use the absolute value for unit selection and keep their sign
in the formatted text.

### Fixed policy

- Metric fixed: all lengths in m.
- Imperial fixed: all lengths in ft.

The fixed policy is an escape hatch for users who do not want mixed units. It
does not change the wire-radius/diameter units.

## Precision and trimming

| Unit | Decimals | Nominal resolution | Example |
|---|---:|---:|---|
| mm | 2 | 0.01 mm | `7.15 mm` |
| cm | 2 | 0.1 mm | `3.97 cm` |
| m | 3 | 1 mm | `3.789 m` |
| in | 2 | 0.01 in (0.254 mm) | `0.28 in` |
| ft | 3 | 0.001 ft (0.305 mm) | `32.808 ft` |

- `QDoubleSpinBox` fields use fixed decimals.
- Read-only labels trim trailing zeros and a trailing decimal point:
  `4.00 cm` becomes `4 cm`; `20.000 m` becomes `20 m`.
- Editable table cells use fixed decimals; read-only report tables may trim.
- Rounding is standard decimal formatting. Tests compare within a tolerance,
  not by exact binary representation.
- The formatter must never display a rounded value that violates the
  geometry dimension-anchor contract. For values below 50 mm, the anchor test
  uses `max(0.5 mm, 1%)`, not the old 5 mm floor.

## Surface rules

### Scalar fields and dimension labels

Use **per-value** automatic selection. The same physical value must show the
same unit in a form, a dimension label, a summary row, and a human-readable
report.

Examples with the current Cebik-scaled Moxon reference:

| Value | Display |
|---:|---|
| 0.248219 m width | `24.82 cm` |
| 0.095018 m depth | `9.50 cm` |
| 0.048155 m reflector tip | `4.82 cm` |
| 0.039715 m driven tip | `3.97 cm` |
| 0.007149 m gap | `7.15 mm` |
| 10 m height | `10 m` |

At 28.5 MHz the same reference gives `3.789 m` width, `1.450 m` depth,
`73.5 cm` reflector tip, `60.6 cm` driven tip, and `10.91 cm` gap. Mixed units
are expected and every value carries its suffix.

Wire radius and diameter keep the existing mm/in presentation.

### Editable tables

Use **one unit per table**, chosen from the largest absolute value in the
table. Show the unit in the column header, for example `Length (cm)`.

- A Yagi table at 435 MHz uses cm.
- A Yagi table at 28.5 MHz uses m.
- A fan-dipole table for 40/20/10 m uses m.
- A table whose largest value is below 1 cm uses mm.
- If all values are zero, use m/ft or the table's scale hint.
- Radius columns remain mm/in.

The table unit is frozen while the table is edited and re-evaluated when the
model, preset, optimizer result, undo/redo state, or unit preference is loaded.
Table cells keep fixed decimals and do not carry per-cell suffixes.

### Geometry views

- Dimension labels and the header summary use per-value automatic selection.
- The scale bar uses the unit of the largest projected extent (the dominant
  unit). Candidate steps must be unit-aware; do not reuse the meter candidate
  list for cm/mm.
- Detail insets use per-value automatic selection. They are not to scale and
  have no scale bar.
- Layout tests must cover the standard size and the minimum supported size,
  including the longer `mm`/`cm` labels. The hidden-dimension strip remains the
  fallback and must stay authoritative.
- The scene contract still requires every dimension value to match its anchor
  distance within the tightened tolerance above.

### Forms

- Each length field declares a `LengthFieldSpec` with physical minimum,
  maximum, step, and an optional scale hint. Do not use one global
  `length_bounds` for small features.
- Choose the field unit when the model is loaded. If the value is zero, use the
  field's scale hint when provided; otherwise use m/ft.
- Freeze the field unit while the user edits that field. Re-evaluate on model
  load, preset load, optimizer/tuning/synthesis apply, undo/redo, or a
  metric/imperial preference change. The suffix must not flip from cm to m
  while the user is typing.
- Configure range, decimals, step, suffix, and value through one helper.
- Default steps, expressed in the display unit: mm `0.1` (0.1 mm), cm `0.01`
  (0.1 mm), m `0.001` (1 mm), in `0.01` (0.254 mm), and ft `0.001`
  (0.305 mm). A field may override the step.
- Fix known under-ranges while wiring the policy:
  - the Moxon height field must not inherit Qt's default maximum of `99.99`;
  - the hexbeam must represent UHF tip/feed gaps below the current `0.1 m`
    minimum;
  - audit every family and every small-feature field, not only the examples.

### Preferences

Present one **Units** control with four options:

1. Metric — Auto (mm/cm/m) — default
2. Metric — Meters (fixed)
3. Imperial — Auto (in/ft) — default
4. Imperial — Feet (fixed)

Store the measurement system and the policy in QSettings. Existing `metric`
and `imperial` values map to the automatic policy. The exact key layout is an
implementation detail, but the project file remains unchanged.

A fixed-unit preference applies to every length surface. It does not change
the radius/diameter units.

### Reports and exports

- The construction sheet and the HTML/PDF simulation reports follow the
  display policy.
- The title block states the policy:
  - `Units: Metric auto (mm/cm/m, MHz, Ω)`
  - `Units: Metric fixed (m, MHz, Ω)`
  - `Units: Imperial auto (in/ft, MHz, Ω)`
  - `Units: Imperial fixed (ft, MHz, Ω)`
- Design-summary rows are scalar values and use per-value automatic selection.
- Wire-schedule, BOM, and other report tables use one unit per table and show
  the unit in the header.
- SVG, PNG, and PDF figures follow the display policy because they are
  human-readable output.
- CSV exports keep canonical meters for lengths and mm for diameters. Do not
  add display units to machine-readable columns; document the canonical units.
- DXF exports keep canonical meters and `$INSUNITS=6`. DXF dimension text is
  formatted in meters regardless of the display policy, so CAD coordinates and
  labels agree. A future opt-in may scale DXF coordinates and set another
  `$INSUNITS`, but that requires a separate decision.

## Architecture

- Put the formatter in a shared, Qt-free module consumed by both `ui` and
  `reporting`. Reporting must not import PySide6 or UI widgets.
- `DisplayUnits` carries the system, the policy, and the formatting helpers:
  `unit_for`, `format_length`, `decimals_for`, `meters_per_unit`, and
  `table_unit`.
- Pass `DisplayUnits` explicitly to scenes, forms, dialogs, and reporting.
  Do not introduce a global mutable "current units" value; tests must be able
  to choose fixed or automatic units explicitly.
- `UnitSystem` remains the system selector; `DisplayUnits` adds the length
  policy. Existing conversion functions stay in use.
- `Dimension.text` remains a display string generated at scene-build time.
  No numeric unit field is added to the project or solver models.
- Reporting functions accept a formatter. Their default remains canonical
  meters so machine-readable callers and old tests are explicit; the UI passes
  the current `DisplayUnits` for human-readable output.
- No schema, solver, or domain change is required.

## Implementation inventory

The slices will touch these existing boundaries; the list is a map, not a
promise that every file changes.

| Area | Files |
|---|---|
| Formatter and policy | `ui/units.py`, `ui/preferences.py`, a shared Qt-free formatting module |
| Form helpers | `ui/widgets/form_units.py`, family editors and dialogs |
| Geometry | `ui/geometry/builder.py`, `ui/widgets/geometry_view.py`, `ui/geometry/dxf_export.py` |
| Human-readable reports | `reporting/design_summary.py`, `reporting/construction_sheet.py`, `reporting/wire_schedule.py`, `reporting/bom_costs.py`, `reporting/construction_package.py`, `ui/construction_pdf.py` |
| Help and tests | `ui/i18n.py`, help coverage tests, form/geometry/report tests |

`domain/common/units.py` already provides the centimeter conversions; it does
not need a schema or solver change.

## Test plan

- Formatter unit tests: zero, negative values, exact threshold values
  (`1 cm`, `1 m`, `1 ft`), rounding, trimming, metric/imperial, automatic/fixed,
  and table-unit selection.
- Geometry tests: 28.5, 144, and 435 MHz Moxon; 20 m dipole; 435 MHz hexbeam;
  main view and inset; scale bar; minimum-size layout; dimension-anchor values;
  fixed-unit strings unchanged.
- Form tests: every length field and editable table; range, decimals, step,
  suffix; freeze-while-editing; metric/imperial switch; external reload;
  Moxon height; hexbeam UHF gaps.
- Dialog tests: optimization, family optimization, synthesis, parameter sweep,
  robustness, tolerance, design-from-frequency, and feed-line dialogs.
- Report tests: design summary, construction-sheet title block, wire schedule,
  BOM, HTML/PDF, CSV canonical units, DXF canonical units.
- Help tests: EN/ES help for the Units preference and the automatic behaviour;
  table-header unit text.
- Full gate: `ruff check`, `ruff format --check`, both `mypy` passes, and the
  full `pytest` suite. Light/dark and scaling QA remains manual.

## Acceptance examples

| Surface | Metric automatic | Imperial automatic |
|---|---|---|
| Moxon 435 MHz width | `24.82 cm` | `9.77 in` |
| Moxon 435 MHz gap | `7.15 mm` | `0.28 in` |
| Moxon 435 MHz height | `10 m` | `32.808 ft` |
| Moxon 28.5 MHz width | `3.789 m` | `12.430 ft` |
| Moxon 28.5 MHz gap | `10.91 cm` | `4.30 in` |
| 20 m dipole length | `20 m` | `65.617 ft` |
| 10 m dipole height | `10 m` | `32.808 ft` |
| Hexbeam 435 MHz tip gap | `1.99 cm` | `0.78 in` |

With the current Cebik-scaled reference, the Moxon drive tip at 435 MHz is
`3.97 cm`; the value read as "4 cm" is that tip, not the gap. The real gap is
`7.15 mm` and therefore stays in mm under the automatic policy. If a different
design has a genuine 4 cm gap, the same policy shows it as `4 cm`.

## Execution slices

| Slice | Scope | Depends on |
|---|---|---|
| U0 | This spec, ADR-0044, backlog and roadmap links | none |
| U1 | Pure formatter, `DisplayUnits`, QSettings policy, Units preference, help | U0 |
| U2 | Geometry scenes, dimension labels, scale bar, insets, layout | U1 |
| U3 | Antenna-family forms, editable tables, ranges and steps | U1 |
| U4 | Optimization, synthesis, sweep, robustness, tolerance, and auxiliary dialogs | U1, U3 |
| U5 | Construction sheet, human-readable reports, CSV/DXF policy | U1, U2, U3 |
| U6 | User guide, changelog, help audit, visual QA, full gate | U2–U5 |

U2 and U3 may proceed in parallel after U1. U5 must not start until the scene
and form policies are stable. All slices through U5 are implemented; U6 closes
the track.
