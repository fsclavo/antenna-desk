# ADR-0006 — Series RLC loads on wires

- **Status:** Accepted
- **Date:** 2026-10-29
- **Supersedes:** none

## Context

The antenna templates generate straight-wire geometries. Users need to model
loading coils, traps (as a first approximation), and resistive loads without
editing a NEC deck. NEC-2 supports a series RLC load through the `LD 0` card,
applied to a segment or segment range.

The canonical model and project schema must stay independent from the solver.
Loads also need to survive template changes, persistence, reports, and edits.

## Decision

1. Add `SeriesLoad` with a stable identifier, wire identifier, position along
   the wire, and non-negative `R`, `L`, and `C`. At least one element must be
   non-zero.
2. Store loads on `AntennaModel`. `DesignVariant` compares the generated
   geometry plus the design's loads, and `with_parameters()` preserves loads
   when the wire identifiers still exist.
3. Persist loads as an optional list in the existing schema v3 antenna payload.
   Older projects load with an empty list; no migration is required.
4. Map a load position to the containing segment and emit one `LD 0` card.
   The mapping is explicit and visible in the generated NEC input.
5. Provide a load editor in the UI. Inductance is entered in µH and
   capacitance in pF; the domain and project file remain in henries and farads.
6. Include loads in HTML/PDF reports and construction sheets.
7. Treat a load as a one-segment approximation. Do not model distributed
   loading, networks, or transmission lines in this decision.

## Consequences

Positive:

- Users can add loading coils and resistive loads without editing NEC files.
- Loads are part of the immutable design and are persisted/reported.
- The solver adapter remains isolated from the UI.

Limitations:

- The load is attached to one segment; effective position depends on
  segmentation.
- A trap is represented as a series RLC approximation, not as a full network.
- Changes to a wire template can invalidate a load's wire reference; the
  design then fails validation until the load is edited or removed.
- No mutual coupling, distributed loads, or per-unit-length parameters.

## Follow-ups

- Consider RLC networks and transmission-line feeds separately.
- Add reference cases for a center-loaded dipole when an independent source is
  available.
