# ADR-0012 — Geometry presentation scene and dimension layout

- **Status:** Accepted; view selector superseded by ADR-0027
- **Date:** 2026-10-30
- **Supersedes:** the Plan/Elevation construction-view rule in ADR-0005

## Context

The original construction sketch dispatched on the antenna type and painted a
small set of synthetic shapes: loops became circles or vertical lines, folded
plans were idealized, and planar arrays could collapse to a single horizontal
wire. The view also retained zoom/pan across model changes and placed
dimensions at fixed pixel offsets, so labels could fall outside the drawing or
overlap each other.

The canonical `AntennaModel` already contains every wire segment, the feed, and
the loads. The 3D view proves that the model is sufficient; the problem is the
presentation layer, not the domain model or the solver.

## Decision

1. Keep the canonical model immutable and geometry-agnostic.
2. Add a renderer-neutral presentation layer in `ui/geometry/`:
   - `scene.py`: scene points, polylines, markers, dimensions, insets, bounds.
   - `views.py`: orthographic front/plan bases and the default-view policy.
   - `builder.py`: family-aware semantic dimensions and summaries.
   - `layout.py`: collision-aware screen placement of dimension lines/labels.
3. Always draw the actual wire segments. Antenna-specific code supplies
   dimension requests and labels, never replacement shapes.
4. Select the default view from geometry:
   - single wire and vertical-plane geometry: front/elevation;
   - horizontal planar arrays: plan/top;
   - non-planar geometry: front/elevation with a top-view inset.
   ADR-0027 replaces the manual Elevation/Plan selector with a single
   Construction view that resolves to this default; the internal projections
   remain for tests, exports, and insets.
5. Reset zoom, pan, and vertical exaggeration when the model changes. Reset the
   view to the geometry-derived default at the same time.
6. Place dimensions in screen space using font metrics, reserved regions, and
   candidate offsets. Hide low-priority dimensions when the available space is
   exhausted rather than drawing them over each other.
7. Use detail insets for dimensions that cannot be shown legibly at true scale
   (Slim Jim gap, folded spacing, Ringo top view, radial top view).
8. Reuse the scene for PNG export now and for future SVG/PDF/DXF export. Do not
   add a heavy rendering dependency for the core sketch.

## Alternatives considered

- **Keep the hand-painted per-type view and add more special cases.** Rejected:
  it duplicates the model, keeps failing for new templates, and cannot produce
  correct dimensions for arbitrary geometry.
- **Matplotlib embedded in Qt.** It provides good transforms and export, but
  does not supply CAD-style dimension layout or collision avoidance. It adds a
  large dependency and a second rendering toolkit without fixing the root cause.
- **PyVista/VTK for 3D.** Useful for a future 3D inspection mode, but the
  reported defects are in the 2D construction sketch. VTK is large and does not
  solve dimension placement.
- **Shapely for offsets and collisions.** The layout needs text metrics and
  screen-space rectangles, not planar polygon overlay. Not justified.
- **ezdxf.** A good optional export target for construction drawings, but not
  an interactive widget. Deferred.
- **Qt Graphics View.** A valid future substrate for selection and export; the
  current QPainter renderer already consumes the scene. Re-evaluate when
  interactive CAD editing is in scope.

## Consequences

Positive:

- Shapes are always derived from the same model the solver receives.
- Quad, delta, Slim Jim, Ringo, Yagi/Moxon, end-fed, and custom geometry keep
  their real topology.
- Dimension values and placement are testable without a GUI.
- New antenna families add a dimension builder, not another painting branch.
- Zoom/model changes no longer leave the new antenna off-screen.

Negative and limitations:

- Dimension layout is heuristic; it avoids overlaps and keeps text inside the
  safe area, but it is not a full CAD constraint solver. Angular dimensions
  currently use a fixed screen-space radius with collision-aware candidates.
- Orthographic views cannot show all 3D relationships; insets and 3D remain
  necessary.
- Custom/imported geometry only gets overall dimensions, feed, and loads.
- The loop is still a polygon approximation; the view draws its real segments
  rather than an idealized circle.
- The existing 3D isometric view remains a secondary inspection mode.

## Follow-ups

- SVG, PDF, and layered DXF export are available from the same scene. `ezdxf`
  (MIT) is used only for DXF interchange.
- Evaluate Qt Graphics View if interactive dimension editing is required.
- The isometric 3D view now supports mouse rotation; evaluate PyVista/VTK only
  if a true 3D scene with depth and lighting is required.
- Keep golden and scene-level tests in sync when new antenna families are added.
- `docs/GEOMETRY_PRESENTATION.md` is the normative checklist for new families.
- Catalog routing is covered by automated tests; adding a catalog entry without
  routes for New Antenna and Change Template fails the suite.
