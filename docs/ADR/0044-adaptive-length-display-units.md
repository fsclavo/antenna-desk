# ADR-0044 — Adaptive length display units

- **Status:** Accepted
- **Date:** 2026-11-17
- **Deciders:** Fernando Sclavo, development
- **Related:** U0–U6 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md),
  [`../DISPLAY_UNITS_SPEC.md`](../DISPLAY_UNITS_SPEC.md),
  [ADR-0012](0012-geometry-presentation.md),
  [ADR-0027](0027-construction-view-policy.md), and
  [`../archive/founding-decisions.md`](../archive/founding-decisions.md)

## Context

The UI currently offers two display systems: metric lengths in meters and
wire diameters in millimeters, or imperial lengths in feet and wire diameters
in inches. This is readable for HF antennas but poor for VHF/UHF construction.
A 435 MHz Moxon gap is `0.007 m`; a 25 cm element is `0.25 m`, which also loses
millimeter detail. The same problem exists in imperial, where the gap becomes
`0.023 ft`.

The request that started this decision was to show centimeters for
high-frequency antennas. That exposed three separate issues:

1. The unit should follow the magnitude of the value, not the band or the
   design frequency. A 435 MHz Beverage can be 100 m long, while a 28 MHz Moxon
   has a 10.9 cm gap.
2. The current two-decimal meter display loses construction detail below 1 m.
   Changing only the suffix would hide that precision problem.
3. The UI conversion is centralised in principle but spread across forms,
   tables, scenes, dialogs, and reports. A global centimeter switch would
   create spin-box range and step traps.

The project already stores canonical meters in the domain and project files.
`domain/common/units.py` already has centimeter conversions. The architecture
therefore supports a presentation-only change without a solver or schema
migration.

## Decision

1. **Keep canonical meters.** The domain, solver, project files, and
   machine-readable CSVs remain in meters. No project schema changes.

2. **Never select a unit by frequency or band.** Select it from the value's
   magnitude, or use the explicit fixed-unit preference. This prevents a large
   VHF antenna from being forced into centimeters and a small HF detail from
   being forced into meters.

3. **Add an automatic metric policy.** For lengths:
   - zero: m, unless a field has a small scale hint;
   - below 1 cm: mm;
   - from 1 cm to below 1 m: cm;
   - 1 m and above: m.

4. **Add an automatic imperial policy.** For lengths:
   - zero: ft, unless a field has a small scale hint;
   - below 1 ft: in;
   - 1 ft and above: ft.

5. **Format with fixed per-unit precision.** mm and cm use two decimals, m
   and ft use three, and inches use two. Read-only labels trim trailing zeros.
   Spin boxes keep fixed decimals. The geometry anchor test uses a 0.5 mm floor
   for small dimensions instead of the old 5 mm floor.

6. **Use per-value units for scalars and per-table units for tables.**
   Form fields, dimension labels, and summary rows choose the unit from their
   own value. Editable and report tables choose one unit from the largest
   absolute value in the table and show it in the header. Wire radius and
   diameter remain in mm/in.

7. **Keep forms stable while editing.** A field chooses its unit when the
   model is loaded and keeps it while the user edits. It re-evaluates on model
   load, preset load, optimizer/tuning/synthesis apply, undo/redo, or a
   metric/imperial preference change. The suffix must not switch mid-typing.

8. **Replace global length bounds with per-field bounds.** The current
   `length_bounds` minimum of `0.1 m` cannot represent a 19.9 mm hexbeam tip
   gap or a 1.0 mm feed gap at 435 MHz. Each field declares its own physical
   range and step. The Moxon height field must not inherit Qt's `99.99`
   maximum.

9. **Keep a fixed-unit escape hatch.** The Units preference offers metric
   automatic (default), metric fixed in meters, imperial automatic (default),
   and imperial fixed in feet. A fixed policy applies to every length surface;
   it does not change radius/diameter units.

10. **Make human-readable output follow the display policy.** The construction
    sheet, HTML/PDF simulation reports, and SVG/PNG/PDF figures use the same
    policy as the UI. Their title block states the policy. CSV exports stay
    canonical in meters/mm. DXF stays canonical in meters with `$INSUNITS=6`
    and meter dimension text, so CAD coordinates and labels agree. A future
    DXF scaling option requires a separate decision.

11. **Make `DisplayUnits` explicit, not global.** Pass a `DisplayUnits` value
    object (system plus length policy) to scenes, forms, dialogs, and reporting.
    `UnitSystem` remains the metric/imperial selector; do not add
    `UnitSystem.CM`. Tests must pass fixed or automatic units explicitly rather
    than relying on ambient state.

12. **Document and test the policy.** The normative rules, examples, and test
    matrix live in [`../DISPLAY_UNITS_SPEC.md`](../DISPLAY_UNITS_SPEC.md).
    Implementation is sliced as U1–U6 in
    [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md).

## Consequences

Positive:

- UHF construction values become readable and keep millimeter or better
  precision.
- HF values stay in meters; users are not forced to read `2000 cm`.
- The same value shows the same unit across the form, sketch, summary, and
  construction sheet.
- The change is presentation-only: no solver, domain, or project migration.
- A fixed-unit preference preserves a predictable option for users who dislike
  mixed units.

Negative:

- Scalars and dimensions can mix cm and mm in one view. The explicit suffix
  makes the value unambiguous, and editable tables stay on one unit.
- Every form and dialog with a length field needs a range, step, and suffix
  audit. This is the largest part of the work.
- The geometry layout must be re-tested at the minimum window size because
  `mm` and `cm` labels are longer than `m` labels.
- Reporting needs an explicit formatter parameter, and the construction sheet
  title block must be updated.
- DXF output does not follow the UI unit in this change. That is deliberate,
  because mixing display labels with meter coordinates would be worse.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Global centimeter preference | A 20 m dipole becomes 2000 cm; spin-box ranges and steps break; the 7 mm gap still reads poorly as 0.71 cm |
| Unit selected by frequency or band | Frequency does not determine physical size; a VHF Beverage and a UHF Moxon need different units |
| Per-value units inside editable tables | Table cells would need a suffix or a unit column; one unit per table is compact and predictable |
| Per-project unit preference | Useful eventually, but requires schema/migration and more UI; not needed for the automatic policy |
| Dual labels such as `0.040 m (40 mm)` | Unambiguous but too verbose for every dimension and field |
| Scale DXF to the display unit now | Mixing display text with meter coordinates is unsafe; a correct scaled DXF needs its own coordinate and `$INSUNITS` decision |
| Add `UnitSystem.CM` | `UnitSystem` is a measurement system, not a unit; a separate `LengthPolicy` avoids combinatorial checks |

## Implementation status

U0–U6 are implemented: the normative spec and ADR are accepted, the Qt-free
`DisplayUnits`/`LengthPolicy` formatter plus the four-option Units preference
and QSettings mapping are in place, and geometry scenes, dimension labels,
summaries, detail insets, and the scale bar follow the policy. Family forms,
editable tables, optimization/synthesis/auxiliary dialogs, construction sheets,
and human-readable reports use the same policy. U6 documentation and the help
audit are complete, and the manual light/dark and font-scaling QA closed on
2026-11-24. Legacy `unit_system=` scene callers keep their fixed strings.

## References

- [`../DISPLAY_UNITS_SPEC.md`](../DISPLAY_UNITS_SPEC.md) — normative rules,
  examples, surface matrix, test plan, and execution slices.
- [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) — U0–U6 execution
  queue, dependencies, and acceptance criteria.
- [`../archive/founding-decisions.md`](../archive/founding-decisions.md) — founding product
  decision and canonical-unit boundary.
