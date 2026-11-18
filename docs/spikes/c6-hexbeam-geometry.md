# C6 HexBeam geometry correctness — technical plan and test matrix

**Date:** 2026-11-18
**Status:** implemented 2026-11-18; C6 closed. C7 remains queued.
**Scope:** single-band G3TXQ broadband wire path. No schema, solver, or
multi-band change.

## Question

What single-band wire path is consistent with the six-spreader frame and the
published G3TXQ dimensions, and which tests prove that the canonical model,
scene, reports, persistence, and optimizer all agree?

## Current defect

`HexbeamParameters.to_antenna()` builds each element as a bent dipole whose
tips are solved from the published wire half-lengths. The tips land outside the
130 in (3.302 m) turning radius:

| Quantity | Current model | Physical frame |
|---|---:|---:|
| Turning radius R | 3.302 m | 3.302 m |
| Turning diameter | 6.604 m | 6.604 m |
| Driver tip radius | 4.404 m (133 % R) | ≤ 3.302 m |
| Reflector tip radius | 4.560 m (138 % R) | ≤ 3.302 m |
| Overall span | 9.030 m | 6.604 m |
| Drawn tip gap | 0.669 m | 0.610 m |
| Reflector midpoint | 0.025 m behind feed | ~2.860 m behind feed |

The plan view therefore labels a 3.30 m turning radius and a 9.03 m span at the
same time. The reflector also passes close to the feed instead of wrapping the
rear three sides. The scene note admits the gap mismatch
(`hexbeam.tip_gap_note`), and the domain test asserts the wrong invariant:
`driver_tip_half_span_m > turning_radius_m` and
`reflector_tip_half_span_m > turning_radius_m`.

The current path is **one band with two elements** (driver and reflector).
Multi-band nesting is C7, not part of C6.

## Reference and source reconciliation

The correct topology is documented by G3TXQ and the K4KIO single-band top view:

- six spreaders every 60°, with a flat front side;
- driver: M shape across the front, fed at the center post;
- reflector: one U-shaped wire around the rear three sides;
- tip spacers: 24 in insulating cords between the driver tips and reflector
  ends, on the hexagon sides;
- everything stays at or inside the 130 in turning radius.

At C6 time the repository declared 219 in driver half, 207 in reflector half,
24 in tip gap, and 130 in turning radius. The G3TXQ broadband five-band table
uses 218 in driver half, 412 in reflector total, 24 in end spacing, and 130 in
turning radius. The difference is below 1 %, but the two rows must not be mixed.
C7b later reconciled the canonical row to 218/412.

**C6 decision:** keep the current single-band constants for the topology fix so
the change does not also become a data-source migration. Make the geometry
helper accept any consistent published row, and parameterize one test over both
the current 219/414/24/130 row and the G3TXQ 218/412/24/130 row. C7 must choose
the five-band table for its 20 m preset and reconcile the constants, reference
library, evidence, and docs in one pass.

Sources:

- Steve Hunt, G3TXQ, *A Broadband Hexbeam*:
  <http://karinya.net/g3txq/hexbeam/broadband>.
- G3TXQ, *Wire Beams*: <https://karinya.net/g3txq/wire_beams>.
- K4KIO, *HEXBeam build guide*, single-band top view:
  <https://hex-beam.com/wp-content/uploads/2014/08/HEXBeam_by_K4KIO.pdf>.

## Frame and reconstruction

Use a regular hexagon with a flat front side, six spreaders at ±30°, ±90°, and
±150° from the boom axis. The front pair is 30° from the boom axis; adjacent
spreaders are 60° apart. The feed is at the frame center. The rear three sides
are the reflector path.

Definitions:

- `R` = turning radius (spreader tip radius).
- `Ld` = published driver half-length, measured from the feed center to the
  tip. This is the current parameterization and is the only interpretation that
  fits both published rows with the frame. Each physical driver half starts at
  a feed-gap edge, so its length is approximately `Ld − feed_gap/2`; the two
  halves differ by the gap projection, and the feed wire supplies the gap.
  The total conductor is `2·(Ld + Lr) + feed_gap`, which matches the sum of the
  modeled wires to sub-millimeter accuracy.
- `Lr` = published reflector half-length (rear midpoint to end).
- `g` = published tip gap.
- `e = (2·Lr − 3·R) / 2` = reflector end extension beyond each lateral vertex,
  along the upper side.
- The reflector end is `e` along the upper side from the lateral vertex.
- The driver tip is `e + g` along the same side.
- The reflector midpoint is the middle of the rear side, at
  `x = −R·√3/2` and `y = 0` for a front-facing +X axis.
- The driver knee is on the front spreader at radius `r_k`; solve
  `r_k + |K − T| = Ld`, where `T` is the driver tip.

A reconstruction that preserves the published dimensions:

| Row | `Ld` | Reflector total | `e` | Knee radius | Driver tip radius | Reflector end radius | Span |
|---|---:|---:|---:|---:|---:|---:|---:|
| Current 219/207/24/130 | 219 in | 414 in | 12.00 in | 126.64 in | 116.26 in | 124.43 in | 260 in |
| G3TXQ five-band 20 m | 218 in | 412 in | 11.00 in | 125.27 in | 116.51 in | 124.86 in | 260 in |

Both rows produce a maximum radius of 130 in, a 24 in tip spacer, and a 260 in
span. The exact attach points are a reconstruction from the published lengths
and the K4KIO drawing, not a CAD export. The implementation must therefore test
the invariants (path lengths, gap, frame fit, span), not only one set of
coordinates.

## Result (2026-11-18)

The implemented single-band model used the then-current 219/207/24/130 row and
ten canonical wires: feed, four driver segments, and five reflector segments.
The later C7b multiband preset reconciled the canonical 20 m row to G3TXQ
218/412/24/130; the C6 values below are the historical C6 result. The 20 m
reference had:

- 6.604 m overall span;
- 3.302 m maximum wire radius, with every endpoint at or inside it;
- 0.6096 m drawn tip gap on both sides;
- reflector midpoint at `x = −2.860 m`, with the rear side at the back;
- 3.2166 m knee radius and 2.8448 m driver-tip radius;
- 3.1496 m reflector-end radius;
- 21.67255 m reported total conductor versus 21.67257 m from the wire sum
  (0.02 mm difference, within the 1 mm invariant).

The full gate passed with 3,533 tests and 1 skipped; `ruff check`,
`ruff format --check`, and both `mypy` passes are clean. The NEC2C HexBeam
integration test passed with the solver auto-detected by the test
configuration.

## Implementation plan

1. **Add one pure frame helper.** Build the six spreader unit vectors, the
   outer reflector vertices, the reflector ends, the driver tips, and the
   driver knees. Return the upper-half frame points and derived lengths. Raise
   a domain error when the row has no valid attach point. Use the helper from
   `to_antenna()`, the derived properties, `__post_init__()`, and the optimizer
   validation so the rules cannot drift.
2. **Correct the wire contract.** Use ten canonical wires: `hexbeam-feed`,
   four `hexbeam-driver-*`, and five `hexbeam-reflector-*` (left/right tip,
   left/right inner, and one rear side). The reflector inner wires are the long
   lateral-to-rear sides; the tip wires are the short end segments; the rear
   wire is the full rear side. The reflector no longer passes through the feed
   center. The driver inner wires start at the feed-gap edges.
3. **Correct the derived properties.** `overall_span_m` becomes `2·R`.
   `driver_tip_half_span_m` and `reflector_tip_half_span_m` return the actual
   lateral extent if they are retained; the scene must not use them to choose
   the span anchors. `turning_diameter_m` remains `2·R`.
4. **Keep the conductor total honest.** `total_conductor_length_m` is
   `2·(Ld + Lr) + feed_gap`; the current formula is correct to first order. Add a
   test that it matches `sum(wire.length_m)` within 1 mm, so a future geometry
   change cannot double-count or drop the feed wire.
5. **Replace the constraints.** Remove the old
   `driver_half > 1.5·R` and `reflector_half > R + |R/2 − tip_gap|` rules.
   Validate the frame instead: the reflector extension `e` must be non-negative
   and `e + g` must not pass the front vertex; the driver knee must lie between
   the feed and the spreader tip; every wire point must stay at or inside `R`.
   Mirror the same checks in the family optimizer descriptor; catch the helper's
   domain error and return a field-level `ConstraintViolation` so the optimizer
   cannot accept a row that `HexbeamParameters` rejects.
6. **Repurpose `element_separation_m`.** It is not a driver/reflector
   center-to-center spacing. Keep the persisted field for compatibility, apply
   it as a small fore-aft trim of the whole reflector U, and set the published
   reference default to zero. Update the label/help from “Driver/reflector
   center offset” to a reflector trim. C6 does not change the schema.
7. **Correct the scene dimensions.** The span anchors are the widest frame
   points (the lateral vertices), not the wire tips. The turning radius is a
   radial distance from the frame center to a lateral vertex/spreader tip, not
   the length of a reflector segment. The tip-gap dimension anchors to the
   driver tip and reflector end. The spreader angle is 30° from the boom axis;
   keep a note that adjacent spreaders are 60° apart. Remove the
   “published vs drawn gap” note because the gap now matches.
8. **Correct the wording.** Use “M-shaped driver” for the front view and
   “U-shaped reflector around the rear”; replace “W driver” and the 60°-from-
   boom-axis statements in the catalog description, hint, geometry note,
   construction note, evidence text, and report labels. Keep EN/ES in sync.
9. **Update the scene golden.** Regenerate only the `hexbeam:plan` and
   `hexbeam:elevation` hashes and review that no other family changed.

### Decisions to record during implementation

- Keep the current 219/207/24/130 single-band constants in C6; C7 reconciles
  the five-band 20 m row. If the project chooses to reconcile now, update every
  reference string and test in the same change.
- Use zero as the published `element_separation_m`; existing projects keep
  their stored value and receive a visible fore-aft trim. Do not change the
  schema payload default `0.05`; it only affects legacy documents that omit the
  field.
- Preserve `driver_half_length_m`, `reflector_half_length_m`,
  `turning_radius_m`, and `tip_gap_m` as the public parameter names. C6 changes
  their geometric interpretation, not the schema.

## Test matrix

The tests below are the concrete C6 acceptance set. Values in the table use the
current 219/207/24/130 row; the parameterized source test also covers
218/412/24/130.

### Domain

| File / test | Assertion |
|---|---|
| `tests/unit/domain/test_hexbeam.py::test_published_hexbeam_reference_dimensions` | Reference values remain the declared source; `turning_diameter_m == 2·R`. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_builds_an_m_driver_and_rear_u_reflector` | Nine wire IDs; reflector midpoint at `x ≈ −2.860 m`; no reflector wire near the feed; driver tips near the sides. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_wire_points_stay_inside_the_turning_radius` | Every endpoint has `hypot(x, y) ≤ R + 1e-9`; the maximum radius equals `R`. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_path_lengths_match_the_published_halves` | Driver center→knee→tip length equals `driver_half`; the two physical halves bracket `driver_half − feed_gap/2`; reflector rear-midpoint→rear-vertex→end equals `reflector_half`; tolerance 1e-3. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_tip_gap_matches_the_published_spacer` | Both driver-tip/reflector-end distances equal `tip_gap`; the gap lies on the hexagon side. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_span_is_the_turning_diameter` | `overall_span_m == 6.6040 m`; span equals the distance between lateral vertices. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_total_conductor_equals_the_wire_sum` | `total_conductor_length_m` is within 1 mm of `sum(wire.length_m)`; keep the `2·(Ld + Lr) + feed_gap` formula. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_azimuth_rotation_preserves_frame_invariants` | Rotate 30°; radii, path lengths, tip gap, and span are unchanged. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_rejects_paths_that_do_not_fit_the_frame` | New feasibility errors for negative extension, tip past the front vertex, and knee outside the spreader; old 1.5R message is gone. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_both_published_20m_rows_fit` | Parameterize 219/414/24/130 and 218/412/24/130; both satisfy path, gap, frame, and span invariants. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_scales_with_frequency` | Lengths and radii scale by the frequency ratio; frame invariants survive. |
| `tests/unit/domain/test_hexbeam.py::test_hexbeam_primary_dimension_scales_the_wire_path` | `with_primary_dimension` preserves the ratios and the frame fit. |
| `tests/unit/domain/design/test_frequency_scale.py::test_hexbeam_scales_reference_geometry_and_preserves_installation` | `scaled_to_frequency` still halves the driver half and turning radius at 2× frequency. |

### Scene and adaptive units

| File / test | Assertion |
|---|---|
| `tests/ui/geometry/test_scene.py::test_hexbeam_dimensions_anchor_to_the_named_geometry` | Legacy fixed metric: span text `6.60 m`, anchor distance `6.604 m`; gap text `0.61 m`; no “published … drawn” note. |
| `tests/ui/geometry/test_scene.py::test_hexbeam_plan_dimensions_the_half_and_spreader_angle` | Angular text `30.0°`; turning radius label `3.30 m`; inset labels `Di`, `Do`, `Ri`, `Ro`; adjacent-spreader note says 60°. |
| `tests/ui/geometry/test_scene.py` (new) | Span anchors are the lateral vertices, not the reflector tips; turning-radius anchor is the frame center to a lateral vertex. |
| `tests/ui/geometry/test_adaptive_units.py::test_hexbeam_435_scene_uses_cm_and_keeps_the_small_gap_visible` | `tip gap 1.99 cm`; dimension text no longer `2.18 cm`; driver half `18.14 cm` with the current source (`18.05 cm` if the 218 in row is chosen). |
| `tests/ui/geometry/test_contract.py::test_every_family_has_a_scene_contract` (hexbeam case) | Ten wires, plan view, summary contains driver/reflector/turning-radius/tip-gap strings. |
| `tests/ui/geometry/golden_scenes.json` | Only `hexbeam:plan` and `hexbeam:elevation` hashes change. |

### Dialog, form, and reports

| File / test | Assertion |
|---|---|
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_dialog_builds_the_published_reference` | Ten wires; reference values; geometry summary uses the corrected labels. |
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_form_represents_uhf_tip_and_feed_gaps` | 435 MHz tip/feed gaps survive the per-field units. |
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_form_uses_per_field_units_when_auto` | Tip gap and driver half in `cm`, height in `m`; no clamping. |
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_form_load_starting_preserves_installation_fields` | Reloading the published row still preserves height and azimuth; the fore-aft trim returns to zero. |
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_form_auto_resizes_pristine_geometry` | Pristine frequency changes still recalculate; edited geometry is not silently resized; frame invariants survive. |
| `tests/ui/test_hexbeam_dialog.py::test_hexbeam_dialog_seeds_the_reference_at_the_requested_frequency` | 21.2 MHz seeding still produces the published row and ten wires. |
| `tests/ui/test_main_window_presets.py::test_hexbeam_preset_uses_the_inline_editor` | The reference design still opens with ten wires; the published fore-aft trim is zero; no schema change. |
| `tests/unit/reporting/test_design_summary.py::test_hexbeam_summary_reports_the_bent_elements` | Reference values; feed row says “center of the M driver”; total conductor equals the wire sum. |
| `tests/unit/reporting/test_construction_sheet.py::test_hexbeam_construction_sheet_lists_the_bent_elements` | “Build an M-shaped driver”; “U-shaped reflector”; six-spreader; evidence B; no W wording. |
| `tests/unit/reporting/test_wire_schedule.py::test_wire_schedule_covers_a_bent_multi_wire_family` | Nine rows; feed row; all lengths positive; BOM total equals the wire sum. |

### Persistence, optimizer, solver, and help

| File / test | Assertion |
|---|---|
| `tests/unit/persistence/test_geometry_persistence.py::test_hexbeam_round_trips_through_the_schema` | Single-band schema unchanged; stored values round-trip; reopening uses the corrected path. |
| `tests/unit/persistence/test_migrations.py::test_v29_migration_introduces_the_hexbeam_design_type` | Migration behavior unchanged. |
| `tests/unit/optimization/test_registry.py::test_hexbeam_optimizes_the_bent_wire_path` | Descriptor availability, field coverage, and new frame constraints; no old 1.5R validation. |
| `tests/integration/simulation/test_nec2c_hexbeam.py::test_hexbeam_completes_a_pattern_run` | NEC2C run still completes with ten wires; no gain/F/B claim. |
| `tests/ui/test_help.py` and `tests/unit/ui/test_i18n.py` | EN/ES help and coverage for the corrected geometry note, tip-gap help, and catalog description; no raw keys. |

### Documentation

- `docs/DOMAIN_MODEL.md`: M/U topology, rear reflector midpoint, span `2R`,
  no “reflector just behind the feed”.
- `docs/VALIDATION_PLAN.md`, `docs/EVIDENCE_AUDIT.md`,
  `src/antennadesk/domain/design/evidence.py`: source row and limitation text.
- `docs/USER_GUIDE.md`: M-shaped driver, rear U, tip spacers, 6.60 m span.
- `docs/CHANGELOG.md`: behavior change; existing projects reopen with corrected
  geometry; no schema change.
- `docs/AUTONOMOUS_BACKLOG.md`: close C6 only after the full gate; C7 remains
  blocked until then.

## Out of scope

- Multi-band nesting, per-band tables, and the 20/17/15/12/10 preset (C7).
- Frame, spreader sag, mast, feed balun, coax harness, and performance claims.
- Any solver, schema, or project-format change.
- A new optimizer search or new numerical references.

## Risks and open questions

- **Source row:** C6 keeps the current 219/207/24/130 row; C7 must reconcile
  the G3TXQ five-band 218/412/24/130 row. Do not update only some strings.
- **Existing projects:** the stored parameters are unchanged, but their derived
  geometry changes when reopened. This is the intended bug fix; call it out in
  the changelog and do not add a migration that rewrites user values.
- **Adaptive units:** test both the legacy fixed-unit scene path and the
  `DisplayUnits` automatic path. The 435 MHz drawn gap must become `1.99 cm`;
  the old `2.18 cm` assertion is part of the defect.
- **`element_separation_m`:** confirm the fore-aft-trim interpretation before
  changing the UI label. If the project prefers to deprecate the field, do it in
  a schema-aware change, not inside C6.
- **Golden scenes:** update only the hexbeam entries and verify the diff; a
  global hash rewrite would hide unintended changes in other families.
- **Full gate:** `ruff check`, `ruff format --check`, both `mypy` passes, and
  `NEC2C=... uv run pytest`.

## Definition of done

C6 is complete when the single-band model is an M/U path on the six-spreader
frame, all wire points stay at or inside the turning radius, the span is
`2R ≈ 6.60 m`, the tip gap equals the published spacer, the scene and reports
show the corrected dimensions in both fixed and automatic units, the optimizer
uses the same feasibility rules, the full gate is green, and C7 is the only
remaining HexBeam follow-up.
