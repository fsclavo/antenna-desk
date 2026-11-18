# ADR-0045 — Multi-band HexBeam model

- **Status:** Accepted
- **Date:** 2026-11-18
- **Deciders:** Fernando Sclavo, development
- **Related:** C7 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md),
  [`../spikes/c6-hexbeam-geometry.md`](../spikes/c6-hexbeam-geometry.md),
  [ADR-0026](0026-family-optimizer-architecture.md), and
  [ADR-0044](0044-adaptive-length-display-units.md)

## Context

The single-band HexBeam uses a six-spreader frame and one M-shaped driver plus
one rear U-shaped reflector. C6 corrected that wire path on 2026-11-18. Common
construction practice stacks two to five G3TXQ bands (20/17/15/12/10 m) on the
same six spreaders, with smaller pairs nested inboard and separated vertically.

The existing `HexbeamParameters` is scalar: one frequency, one driver half, one
reflector half, one tip gap, and one feed gap. Reports, editors, the scene, and
the optimizer all assume that shape. Adding bands therefore needs an explicit
model, persistence, and presentation decision rather than a UI-only checkbox.

## Decision

1. **Keep one `hexbeam` family and one `HexbeamParameters` type.** Add an
   optional tuple of `HexbeamBand` records. The existing scalar fields remain
   and mirror the primary band (`bands[0]`). A design with no band tuple keeps
   the current single-band behavior.

2. **Share the frame, vary the band radius.** `turning_radius_m` is the outer
   frame radius, defined by the first/largest band. Each higher band uses
   `band_radius = turning_radius × f_first / f_band`, the same linear
   frequency-scaling rule as the published single-band reference. This keeps
   the nested paths inside the frame and matches the approximate construction
   radii published by QuickAntenna. It is a starting layout, not a CAD export.

3. **Band fields.** Each `HexbeamBand` stores a short label, frequency, driver
   half, reflector half, tip gap, feed gap, and vertical offset above the
   reference plane. The first band is the lowest-frequency/largest element and
   must match the scalar fields. Labels and frequencies must be unique. The
   current limit is five bands. The preset frequencies are common band centers
   (14.184, 18.118, 21.2, 24.94, and 28.5 MHz); the published table supplies the
   lengths and spacing, not a unique design frequency for each row.

4. **Height and vertical offsets.** `height_m` is the reference plane of the
   lowest band in the stack (10 m for the standard five-band set). Each band
   sits at `height_m + vertical_offset_m`. The published offsets are 38 in for
   20 m, 15 in for 17 m, 9 in for 15 m, 5 in for 12 m, and 0 for 10 m. A
   single-band design has offset 0 and keeps the previous height meaning.

5. **Feed model.** The first band's feed wire is the primary `FeedPoint`. Each
   additional band's feed wire is an ideal `Source` with unit amplitude and
   zero phase. The real coax harness, jumper lengths, coupling between bands,
   and the balun are not modeled. The UI and reports must state that
   limitation.

6. **Published rows.** The multi-band preset uses the G3TXQ five-band table:
   20 m 218 in driver half / 412 in reflector total / 24 in end spacing,
   17 m 169.5/321/18.5, 15 m 144.5/274.4/16, 12 m 121.7/232/13.5, and
   10 m 106.8/204.4/12, with a 130 in turning radius. C7b reconciled the
   single-band reference from 219/207 to 218/412 and updated the reference
   library, evidence text, tests, and docs together. Do not mix the two rows
   inside one preset.

7. **Schema version 55.** Add an optional `bands` list to the hexbeam payload.
   Existing single-band payloads migrate with an empty list and keep using the
   scalar fields. New multi-band payloads store the shared frame plus the band
   list; the scalar fields mirror `bands[0]`. No old project values are
   rewritten.

8. **Optimizer scope.** Multi-band optimization is explicitly unavailable in
   this slice. The family registry returns a translated reason; the existing
   single-band descriptor remains for one-band designs. A later slice may
   optimize one selected band with the others fixed.

9. **Frequency scaling scope.** `Design → Scale Geometry to Frequency` is
   disabled for a multi-band HexBeam until a band-aware rule exists.
   `with_primary_dimension()` still scales the whole stack for tuning/resize
   workflows, but it does not change the band frequencies.

10. **Presentation.** The scene draws every band's canonical wires. Dimensions
    and the selected-band highlight are a follow-up UI slice; reports add a
    per-band table. Adaptive display units apply to every per-band value.

## Consequences

Positive:

- The common 20/17/15/12/10 construction fits one family and one shared frame.
- Existing single-band projects parse and render unchanged.
- The per-band radius rule keeps every band inside the 130 in frame.
- The feed and optimizer limitations are explicit instead of implied.

Negative:

- Scalar fields duplicate `bands[0]`; validation must reject drift.
- The per-band radius is a derived starting rule, not a published CAD layout.
- Multi-band gain, SWR, front-to-back ratio, and feed interaction remain
  unvalidated.
- The UI, scene, reports, and selected-band optimizer still need their own
  slices.

## Execution slices

| Slice | Scope | Status |
|---|---|---|
| C7a | ADR, `HexbeamBand`, optional `bands`, sources, schema v55, domain/persistence/registry tests | Implemented 2026-11-18 |
| C7b | Published 20/17/15/12/10 preset, 218/412 reconciliation, band table/editor, nested scene rendering, per-band reports | Implemented 2026-11-18 |
| C7c | Selected-band optimizer, feed-harness limitations, validation/evidence audit | Queued |

## References

- Steve Hunt, G3TXQ, *A Broadband Hexbeam*:
  <http://karinya.net/g3txq/hexbeam/broadband>.
- G3TXQ, *Wire Beams*: <https://karinya.net/g3txq/wire_beams>.
- K4KIO, *HEXBeam build guide*:
  <https://hex-beam.com/wp-content/uploads/2014/08/HEXBeam_by_K4KIO.pdf>.
- QuickAntenna, approximate per-band radial layout:
  <https://quickantenna.com/hexbeam>.
- [`../spikes/c6-hexbeam-geometry.md`](../spikes/c6-hexbeam-geometry.md) — C6
  single-band frame reconstruction.
