# ADR-0051 — Bounded cliff/second-medium site ground

- **Status:** accepted 2026-11-24; implementation pending
- **Date:** 2026-11-24
- **Related:** DL7, [`spikes/dl7-ground-gn-spike.md`](../spikes/dl7-ground-gn-spike.md)

## Context

The DL7 spike separated three NEC-2 ground features:

1. The native radial screen (`NRADL > 0`) is a reflection-coefficient
   approximation. It disagreed strongly with the dense-wire radial model for
   input impedance in the spike case and has no traceable validation. It must
   not be presented as an accurate radial-system or SWR model.
2. A second-medium/cliff profile (`NRADL = 0`, `F3/F4` second medium, `F5/F6`
   edge) changes only the far-field pattern. Impedance and currents stay on the
   first medium. This is a bounded, honest site feature.
3. Full terrain remains out of scope.

Ground is currently stored per design in every family form. Copying cliff
fields into every form would duplicate the same site decision and make the
project-level site ambiguous.

## Decision

1. Implement only the **cliff/second-medium far-field profile** in the first
   DL7 slice. Do not implement the native radial screen and do not claim an SWR
   or impedance effect from the second medium.
2. Add one optional **project-level `SiteGroundProfile`**:
   - first medium remains the design's existing `GroundModel`;
   - `second_medium_relative_permittivity`;
   - `second_medium_conductivity_s_per_m`;
   - `edge_shape`: `linear` or `circular`;
   - `edge_distance_m` (circle radius or distance along +X);
   - `edge_height_m` (how far medium 2 is below medium 1);
   - optional label and notes.
3. Expose it once through **Tools → Site Ground...**, not through each family
   form. The dialog edits the project profile; it does not mutate a design's
   ground. Changing the profile marks the project dirty.
4. Apply the profile to the canonical model only at simulation/export time.
   The NEC adapter emits the first medium on `GN` and appends the second medium
   and edge fields. It uses `RP 2` for a linear cliff and `RP 3` for a circular
   cliff instead of the current `RP 0`. The domain design remains unchanged.
5. The UI, report, and NEC provenance state: **far-field only; SWR and currents
   unchanged**. The radial screen remains unavailable, with its dense-wire
   warning.
6. Schema 60: add `site_ground` to the project metadata with a `null` default.
   Add a metadata-only 59→60 migration that injects `site_ground: null`; design,
   run, and optimization entries keep their current shape. The container reader
   accepts 59 through that migration and writes 60.
7. Evidence is B/C: NEC-2 manual semantics plus the spike comparison. Add a
   committed reference case for the `GN`/`RP` deck and the far-field-only claim.

## Consequences

Positive:

- A real site feature with a small, testable electromagnetic claim.
- One site decision instead of duplicated fields in every family form.
- No silent SWR change: the second medium cannot affect impedance.
- The native radial screen is not presented as validated.

Costs:

- New schema 60 and a container metadata migration.
- New project-level dialog, persistence, report, and scene notes.
- The NEC adapter needs `RP` mode plumbing.
- The first medium remains per design, so a user who changes designs must keep
  the design ground consistent with the site profile; the UI should show both.

## Out of scope

- Native radial screen as an SWR/radial-system model.
- Faceted terrain, diffraction, buildings, vegetation, multiple edges, buried
  conductors.
- A gain or pattern accuracy guarantee beyond the B/C evidence label.

## Acceptance

- A project with a cliff profile round-trips through schema 60.
- The NEC deck contains the first-medium `GN` fields, the second-medium fields,
  the edge fields, and `RP 2` or `RP 3`.
- The impedance result is identical to the same design without a cliff profile
  at the same frequency; the far-field pattern may differ.
- A schema-59 container opens, gains `site_ground: null`, and saves as 60.
- The dialog and report state the straight-edge and far-field-only limitations.
- The native radial screen is not exposed.
