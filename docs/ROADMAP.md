# AntennaDesk roadmap and backlog

**Updated:** 2026-11-02
**Status:** active roadmap after catalog, measurement, optimization, and
packaging work.

## Product direction

AntennaDesk is a design and experimentation tool for radio amateurs, not a
catalog of reference-approved antennas. The solver must remain trustworthy, but
users must be able to create, modify, and simulate geometries that have never
been built and therefore have no external reference.

Validation therefore applies at two different levels:

1. **Solver validation:** the NEC adapter and normalization must match
   independent references. This remains strict.
2. **Template/generator validation:** a template is not blocked because no
   independent result exists. It must be labeled with its evidence level and
   must not claim more accuracy than it has.

## Evidence levels

| Level | Meaning | Required evidence |
|---|---|---|
| A. Reference-backed | Compared with an independent source | Traceable source, metric, tolerance |
| B. Published or heuristic | Based on a published design rule or starting point | Source or documented heuristic |
| C. Experimental | Arbitrary geometry or unverified generator | Structural tests and visible warning |

A 10% tolerance is acceptable for many dimension/heuristic comparisons. It is
not a universal rule for gain, nulls, or impedance; each metric keeps its own
tolerance.

## Current state

Completed:

- Solver adapter, normalized results, persistence, imports, and reports.
- Guided dipole, folded dipole, loop (generic, delta, quad), vertical (1/4λ and
  5/8λ with radials), inverted-V, fan dipole, end-fed, OCFD, J Pole, Slim Jim,
  Ringo, Yagi, Moxon, and custom-wire designs.
- Series/parallel RLC loads and traps; L/Pi/T matching networks with component
  Q/loss; uniform feed-line post-processing.
- Frequency-first dimension estimation for every current family, with source
  identifiers, confidence, assumptions, warnings, and a loop polygon correction
  calibrated with NEC-2.
- Single-dimension and multi-element optimization, target impedance, gain,
  front-to-back, efficiency, weighted multi-objective search, Pareto ranks, and
  integer variables.
- Yagi element-count optimization: trailing directors are added from the
  DL6WU reference or removed, with the driven element preserved.
- VNA CSV import, measurement conditions/reference plane, measured/simulated
  comparison, resonance differences, and project measurement records.
- Construction sheets, CSV/HTML/PDF reports, PNG/SVG/DXF exports, and
  project-level Undo/Redo with chart cursors.
- Wheel/sdist packaging, packaging CI, application icon, and Linux desktop
  entry.
- Native Linux AppImage, Debian package, and Windows bundle recipes with
  bundled `nec2c`, checksums, and a tag-triggered release workflow.
- Reference anchors for NEC examples, selected ARRL dipole/folded/loop
  properties, the published Cebik 20 m wire Moxon, and the NBS Yagi preset.

In progress:

- Release hardening: configure project signing keys and publish the first
  tagged release. The AppImage/Windows build recipes, `.deb`, bundled `nec2c`,
  and signing automation are implemented.

Deferred:

- Live VNA/hardware control.
- Additional full-wave engines.
- Physical antenna validation until measurements are available.

## Milestones

### M1 — Parametric Yagi generator (completed)

- Element table: position along boom, total length, radius.
- Add/remove elements and arbitrary driven-element index.
- NBS 0.8λ five-element starting preset.
- Generate a first-class editable Yagi design.
- Structural tests plus a reference-backed NEC check for the NBS preset.
- UI: Yagi entry in the **New Antenna** catalog with an inline element editor.

### M2 — Inverted-V generator (completed)

- Apex height, included angle, leg length, azimuth, wire radius, ground.
- Free-space and ground simulations.
- Structural and scaling tests; reference only when a primary numeric source is
  available.

### M3 — Catalog expansion (completed)

- Delta loop and quad presets.
- Moxon rectangle.
- Off-center-fed dipole and fan dipole.
- Vertical with radial ground-screen options.
- End-fed wire, J Pole, Slim Jim, and Ringo.
- Each entry records its evidence level and limitations.

### M4 — Advanced design and measurement (completed)

- Multi-element optimization and constrained geometry, including Yagi,
  fan-dipole, Moxon, vertical, inverted-V, Ringo, and loop variables.
- Weighted multi-objective search with Pareto ranks and candidate selection.
- Integer variables for radial count, loop side count, and Ringo ring sides.
- Yagi element count as a discrete search variable, with reference-based
  director addition and driven-element preservation.
- VNA CSV import and measured/simulated SWR, R, X, and |Z| comparison.
- Measurement conditions and reference-plane metadata.
- Bounded impedance synthesis for OCFD, J Pole, and Slim Jim.

### M5 — Release hardening (in progress)

- Linux AppImage, Debian `.deb`, and Windows onedir bundle recipes (completed).
- Bundle `nec2c` next to the frozen executable (completed).
- Install the icon and desktop entry in the AppImage; embed the Windows icon
  (completed).
- Tag-triggered release workflow with wheel/sdist, AppImage, Debian package,
  Windows zip, and checksums (completed).
- Optional GPG detached signatures and Windows Authenticode signing hooks
  (completed).
- Configure project signing keys and publish `v0.1.0` (pending).
- Keep the wheel/sdist smoke test as the fallback distribution path
  (completed).

## Backlog

| Priority | Item | Evidence | Status |
|---|---|---|---|
| P0 | Configure signing keys and publish `v0.1.0` | n/a | pending |
| P1 | End-fed transformer/unun and counterpoise modeling | C | pending |
| P1 | Transmission line as geometry, not only feed-line post-processing | B | pending |
| P1 | Realized gain and directivity separated from NEC power gain | A | pending |
| P1 | Independent references for remaining experimental templates | A/B | partial |
| P2 | Relative permeability export to NEC | B | pending |
| P2 | Custom/imported geometry optimization and space constraints | n/a | pending |
| P2 | Live VNA/hardware control | n/a | deferred |
| P2 | Additional full-wave engines | n/a | deferred |
| P2 | Physical antenna validation | A | blocked: no measurements |

## Next

Modeling track:

1. End-fed transformer/unun and counterpoise, followed by transmission-line
   geometry.
2. Realized gain/directivity and relative-permeability export.

Release track:

1. Configure GPG and Authenticode signing keys.
2. Sign artifacts, tag `v0.1.0`, and publish the release.

Validation track:

1. Independent references for remaining experimental templates.
2. Physical measurements when the project owner has data.

## Definition of done for a generator

- Domain generator is independent of Qt and the solver.
- Geometry invariants and feed connectivity are tested.
- Scaling with frequency is tested.
- Presets identify their source or heuristic.
- Experimental generators show a visible limitation/warning.
- A reference test is added when a traceable numeric oracle exists.
- Documentation and changelog are updated.
