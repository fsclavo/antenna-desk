# Historical backlog — antennas and feed

> **Historical design notes, captured 2026-11-20.** Not current
> guidance. Current status: [`../../STATUS.md`](../../STATUS.md); active
> queue: [`../../AUTONOMOUS_BACKLOG.md`](../../AUTONOMOUS_BACKLOG.md).

## HexBeam follow-ups (C6/C7 complete 2026-11-18)

C6 and C7 are complete. The former single-band model derived each tip from the
published wire half-length and placed it outside the 130 in frame, producing a
9.03 m span on a 3.30 m turning radius and a 0.67 m drawn tip gap against the
published 0.61 m. The corrected model has a 6.604 m span, a 0.6096 m tip gap,
and every wire point inside the 3.302 m turning radius. C7 adds the published
20/17/15/12/10 preset, editor, nested scene, reports, and NEC2C coverage.

### C6 acceptance (implemented 2026-11-18)

- Driver: two halves from the center feed to the front-side spreaders, then
  along the hexagon sides to the lateral tips; M shape.
- Reflector: one continuous wire around the rear three sides, with its
  midpoint at the rear; U shape.
- Ten canonical wires: feed, four driver segments, and five reflector segments
  (left/right tip, left/right inner, and the full rear side).
- Tip spacer: 24 in between the driver tip and reflector end, on the side.
- Every wire point is at or inside the turning radius; overall span is 2R
  (~6.60 m).
- `total_conductor_length_m` stays `2·(Ld + Lr) + feed_gap` and matches the sum
  of the canonical wire lengths within 1 mm; the invariant is tested.
- The published `element_separation_m` defaults to zero and is applied only as a
  reflector fore-aft trim; it is not a center-to-center spacing.
- Domain and optimizer feasibility checks share one frame helper; the old
  `driver_half > 1.5R` and reflector lower-bound rules are removed.
- Adaptive-unit tests cover both the legacy fixed-metric scene and
  `DisplayUnits` automatic; the 435 MHz drawn gap changes from 2.18 cm to
  1.99 cm.
- C6 keeps the current 219/207/24/130 constants; a parameterized test covers
  both that row and the G3TXQ 218/412/24/130 row. C7 reconciles the five-band
  20 m row.
- Plan dimensions, notes, construction sheet, design summary, and evidence
  agree with the geometry; no "published vs drawn gap" mismatch.
- Tests assert the frame-fit invariant, reflector rear midpoint, exact tip gap,
  and span; the golden scene is updated deliberately.
- Docs/help that describe the W/U or 60-degree ray are corrected. The C2
  family/editor/report scaffolding remains valid.

The detailed reconstruction, source reconciliation, and file-level test matrix
are in [`spikes/c6-hexbeam-geometry.md`](../../spikes/c6-hexbeam-geometry.md). C6 and
C7 are closed; the optional C7d-C7i follow-ups are tracked there, with C7d,
C7e, C7f, and C7g implemented.

### C7 acceptance (implemented 2026-11-18)

- `HexbeamParameters` carries a shared frame plus 1-5 per-band records; schema
  migration maps an existing single-band design to one band.
- An ADR records the shared-frame/band model, the per-band feed approximation,
  and the selected-band optimizer scope.
- The standard preset is the published G3TXQ 20/17/15/12/10 table with its
  vertical offsets; no invented per-band values. C7b reconciled the single and
  multi-band 20 m row to 218/412/24/130 and updated the reference library,
  evidence, tests, and docs together.
- The editor derives the band count from the selected set; it does not infer an
  arbitrary prefix of the published table. It exposes **Load starting
  dimensions** and an editable per-band table. Published checkboxes seed the
  rows; custom labels, frequencies, and dimensions are allowed in the same
  row order, and the report marks the band set as published, reference-scaled,
  or custom.
- Scene draws all bands on the shared frame. C7e adds a transient active-band
  selector: the selected band's dimensions, feed marker, summary, and detail
  inset are shown, its wires are emphasized, and the other bands stay visible.
  Reports and the construction sheet include per-band rows.
- Feed model is explicit. One selected band is driven per analysis and the
  other bands are passive; the real coax harness, coupling, and balun are
  limitations.
- NEC2C integration covers one driven band at a time. Full multi-band
  optimization remains unavailable with a reason; C7d adds a selected-band
  optimizer that leaves the shared frame and the other bands fixed.
- Evidence stays B for published starting dimensions; performance is not
  claimed. Update `VALIDATION_PLAN.md`, `EVIDENCE_AUDIT.md`, user guide, and
  `CHANGELOG.md`.

### C7 implementation notes

C7a is implemented on 2026-11-18: [ADR-0045](../../ADR/0045-multiband-hexbeam.md)
records the shared-frame model, per-band radius, one-driven-band feed, schema
55, and optimizer/scaling limits. The domain accepts 1-5 bands, builds ten wires per
band, derives each band's nested radius from the largest band, and exposes
explicit unavailable reasons for multi-band optimization and frequency scaling.

C7b is implemented on 2026-11-18: the published 20/17/15/12/10 preset, the
218/412 single-band reconciliation, band checkboxes, a read-only per-band table,
nested scene rendering with primary-band emphasis, per-band report rows, and
EN/ES help.

C7c is implemented on 2026-11-18: multi-band optimization remains explicitly
unavailable, the feed-harness/inter-band-coupling/balun limitation is visible
in help/evidence/reports, and real NEC2C 20/15/10 m runs completed with one
driven band per analysis and positive input resistance. C7 is complete.

Post-C7 fix on 2026-11-18: **Analyze Bands** now defaults to the bands selected
in the design and passes a band-specific one-source model per analysis; this
removes the negative input resistance and "Simulation failed" results at 15
and 10 m. **Estimate Dimensions...** is enabled with a single-band
reference-scaled starting design.

C7d is implemented on 2026-11-18: **Optimize** targets the active band of a
multi-band HexBeam. The descriptor varies only that band's driver/reflector
halves, tip gap, and height; the shared turning radius, conductor, and the
other bands stay fixed. Validation checks the band's nested frame, conductor
spacing, and adjacent-radius clearance. Each candidate excites the selected
band and is evaluated at its frequency, and the dialog shows the target band.
Full multi-band optimization remains explicitly unavailable.

C7f is implemented on 2026-11-18: the band table is editable and is the source
of truth. Published checkboxes only seed rows. Rows can be added or removed
within 1–5, labels and frequencies can be custom, and untouched cells keep
their exact canonical values. Rows must be ordered from lowest to highest
frequency; the editor and reports mark custom sets, and replacing them with a
published preset requires confirmation.

### Optional HexBeam follow-ups (queued 2026-11-18)

- **C7d — selected-band optimizer — implemented.** Optimize one band at a time
  with the shared frame and the other bands fixed; full-stack optimization is
  not exposed.
- **C7e — active-band dimensions and scene highlight — implemented.** A
  transient selector chooses the band whose cotas and feed marker are shown;
  its wires are emphasized and the other bands remain visible. Not persisted.
- **C7f — editable per-band table and custom band sets — implemented.** Rows
  are editable, can be added/removed, and carry custom labels/frequencies with
  explicit validation and custom-set provenance.
- **C7g — band-aware starting set / whole-stack scaling — implemented.**
  A frequency-first multiband start is possible only as a *scaled reference
  stack*, not as a new optimized design. The editor's primary-frequency field
  now scales the selected published set uniformly within the primary band and
  shows a reference-scaled warning. **Estimate Dimensions** remains a
  single-band helper; no general multiband estimator is provided.
- **C7h — optional 6 m band.** Add the published 6 m row when a source-backed
  row is carried through the same frame-fit tests.
- **C7i — feed harness and inter-band coupling.** Blocked until a traceable
  harness model or measurement exists; the current one-driven-band model keeps
  the other bands passive.


## Matching-network precedence (2026-11-10 analysis)

G25 models the internal EFHW matching unit. The M queue defines how that model
coexists with the project-level matching network. The agreed policy is an
explicit **Override**, not a cascade:

| Project network | EFHW internal matching | Effective network | Override |
|---|---|---|---|
| none | active | EFHW internal | no |
| none | inactive | none | no |
| active | active | project network | **yes** |
| active | inactive | project network | no |

- The project matching network is global and applies to every design.
- On `EndFedParameters` with `matching_network_active`, it replaces the
  internal matching capacitor and transformer-leakage model. The ideal
  transformer ratio still applies.
- The internal values remain in the design and project file; they are simply
  not applied while the project network exists. Removing the project network
  restores them.
- No cascade of two matching networks is modeled in this stage. This is a
  documented limitation, not a hidden approximation.
- `override_active` is derived from the project network and the design; it is
  not a persisted flag.
- A single resolver must feed every path: simulation, band analysis, family
  optimization, synthesis, the EFHW convergence check, reports, and the UI.
- Before M1, several paths replaced `spec.matching_network` unconditionally, so
  a `None` project network could silently drop the internal EFHW network. M1
  removed that behavior by routing every path through the resolver.


## C1 — Phased verticals / arrays (completed)

**Status:** completed 2026-11-08. Evidence remains experimental pending a
traceable published array or measurement.

The original blocker was the single-feed model (`AntennaModel.feed`) and the
single `EX` source in the NEC adapter. The delivered work crosses the domain
model, solver port, NEC deck, persistence, scene presentation, optimization,
reports, and validation.

Completed slices:

1. **Model and solver — completed 2026-11-08**
   - `Source` value (wire, offset, amplitude, phase) and optional
     `AntennaModel.sources` with the primary feed as source 1;
   - segmentation locates each source independently;
   - the NEC input writer emits one `EX` card per effective source;
   - the primary feed remains the impedance/SWR reference; the total pattern
     and currents include all sources;
   - schema 24 persists the additional sources;
   - unit and real NEC2C two-source tests pass.
2. **Family — completed 2026-11-08**
   - `PhasedVerticalParameters`: count, spacing, height, base height, radial
     system, amplitude taper, phase progression, azimuth, radius, material,
     ground;
   - feed network is an explicit ideal combining model, not a hidden loss;
   - topology (count, radial system) remains a user choice.
3. **Persistence — completed 2026-11-08**
   - schema-25 migration; phase and element-count ranges are validated;
   - round-trip and migration tests.
4. **Presentation — completed 2026-11-08**
   - scene dimensions for spacing and height, and markers for additional
     sources;
   - pattern/current views and reports.
5. **Optimizer — completed 2026-11-08**
   - family descriptor for geometry and phase/amplitude variables;
   - constraints for spacing and phase/amplitude ranges;
   - NEC2C integration and Apply Best adapter.
6. **Evidence — open**
   - a traceable two-element published array or measurement; otherwise the
     family stays experimental with visible limitations.

Do not start C1 by cloning a vertical N times inside a widget. The multi-source
model and solver contract must land first.

