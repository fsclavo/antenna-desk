# ADR-0027 — Construction view policy and wire schedule

- **Status:** Accepted
- **Date:** 2026-11-09
- **Supersedes:** the manual Elevation/Plan switch described in ADR-0012

## Context

ADR-0012 introduced renderer-neutral front and plan projections and let users
switch between them. That was useful for inspecting a model, but it exposed a
projection problem as a user choice: a vertical antenna is edge-on in plan, and
a horizontal beam is edge-on in elevation. The default view was usually
correct, but the selector still offered the degenerate projection as if it were
an equivalent construction drawing. The inability to show every 3D relationship
in one orthographic view also meant that some build values existed only as
dimension labels, which the layout engine can hide when space is tight.

## Decision

1. The main window exposes two view modes: **Construction** and **3D**.
   Construction is the dimensioned construction drawing; 3D is inspection.
   The construction sheet may also include the complementary orthographic
   view and an isometric view; this does not add a second user-facing selector.
2. Construction resolves to the projection that shows the family's principal
   plane:
   - front/elevation for vertical-plane antennas;
   - top for horizontal planar antennas and beams;
   - top for the cubical-quad boom layout;
   - front with a top inset for non-planar antennas.
3. The scene builder keeps `ELEVATION` and `PLAN` as internal projections for
   tests, exports, insets, and future advanced views. The user-facing selector
   does not expose them.
4. A projection that collapses a canonical wire to zero length is not a valid
   construction view. It must be hidden, replaced by an inset, or reported as
   edge-on; it must not be drawn as a misleading line.
5. Every construction sheet includes a wire schedule with each canonical wire's
   start/end coordinates, length, diameter, and material, plus the primary feed
   point. The schedule is authoritative when a dimension is hidden, too small,
   or ambiguous.
6. Missing frame, boom, balun, matching, or site data is reported as a visible
   limitation. It is never replaced with invented geometry or numbers.

## Consequences

Positive:

- A J-Pole or Slim Jim opens on its front construction elevation instead of a
  top view that looks like an end-fed wire.
- A Yagi, Moxon, hexbeam, or trapped Yagi opens on its top construction layout
  instead of an edge-on elevation.
- The quad beam no longer opens on an edge-on projection; its boom layout is
  the construction view and the schedule carries the loop sides.
- A hidden dimension cannot lose the only copy of a build value.
- The view mode is stable across designs: users do not have to remember which
  projection is the construction view for each family.

Negative and limitations:

- Users lose the one-click secondary orthographic projection. Insets, the 3D
  view, and the schedule compensate; a future advanced view selector can expose
  the internal projections if needed.
- The construction view still cannot show every 3D relationship; non-planar
  families need insets and the schedule.
- The wire schedule is not a substitute for a mechanical frame drawing. It
  describes the canonical wire model only.
- Quad-beam loop squares are not shown in the construction top view; the
  schedule defines each side. A front/boom detail inset remains a follow-up.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Keep Elevation and Plan as equal options | Exposes edge-on projections and caused the J-Pole/Slim Jim confusion |
| Remove the top projection entirely | Breaks Yagi, Moxon, hexbeam, trapped Yagi, T2FD, folded dipole, and horizontal loops |
| Rename Plan to Construction and keep only the front projection | Works for vertical antennas but makes every horizontal beam edge-on |
| Put every possible dimension on the sketch | Clutters the drawing and still hides low-priority values at small sizes |
| Add a full CAD constraint solver | Out of scope; the schedule and a small dimension manifest solve the buildability problem |

## Follow-ups

- Add a boom-axis front inset for the quad beam.
- Add per-family dimension manifests to the scene contract tests for the
  remaining vertical and wire families.
- Revisit an advanced view selector only if users need the secondary
  projection interactively.

Implemented follow-up (2026-11-09): the construction sheet now includes the
complementary orthographic view when available and an isometric 3D view, so the
secondary projection is available in the exported document without restoring
the interactive selector.
