# Pending work plan

**Status:** planned, not executed
**Date:** 2026-11-03
**Scope:** remaining work after the multiband, OCFD, and fan-dipole milestones

This plan orders the open work so each phase is independently shippable and
testable. It is not a commitment to implement every item in one session.

## Phase 0 — Close the current change set

1. Commit the per-band pattern PNG export:
   - `ResultsView.save_band_pattern_images()`;
   - folder export from the Pattern PNG action when a band analysis is active;
   - tests and documentation.
2. Confirm the working tree is clean before starting the next phase.
3. Re-run the full gate:

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy
NEC2C=... uv run pytest -q
```

## Phase 1 — Fan dipole accuracy and tuning

### Problem

The fan estimator uses straight half-wave lengths. A fan element is built as a
V with a different included angle, and it is coupled to the other elements.
For a 20/10 m fan, the 10 m element alone would have a reasonable SWR, but the
20 m element loads the feed at 28 MHz. The current optimizer only varies
lengths; it does not vary angles or explain the interaction strongly enough.

### Tasks

1. **Calibration spike, no code change first**
   - Measure the resonance of a single V element versus included angle at
     representative heights and ground models.
   - Compare with the straight half-wave formula.
   - Document whether a simple correction is defensible or whether the effect
     is too installation-dependent.
   - Do not invent a correction factor without a traceable NEC calibration or
     published source.
2. **Estimator improvement (only if the spike supports it)**
   - Add an optional angle-aware length correction to
     `estimate_fan_dipole()`.
   - Label it as an application calibration, not a universal resonance rule.
   - Add tests for every supported angle/band combination used in presets.
3. **Angle optimization**
   - Add fan element angles as optimizer variables with constraints:
     distinct angles, no overlapping wires, ends above ground.
   - Keep the existing length variables.
   - Show angle and length in the variable table.
   - Warn that angles affect both resonance and coupling.
4. **Interaction diagnostics**
   - Make the “all elements remain in the antenna” behavior explicit in the
     optimizer and results.
   - Add a diagnostic or summary note when a high-band element is being
     optimized with lower-band elements present.
5. **Acceptance criteria**
   - A 20/10 m fan estimate gives a documented starting point.
   - The user can select the 10 m band, see its coupling effects, and optimize
     both length and angle without manually converting units.
   - The 40 m band is rechecked after tuning 10 m.
   - No geometry overlap or below-ground ends are produced.
   - Tests cover estimator, optimizer constraints, UI synchronization, and
     regression of single-element fans.

### Risk

A simple length correction may not solve the 20/10 interaction because the
coupling is physical, not a formula error. If the spike shows that angle
optimization is the only reliable path, implement that and keep the estimator
honest as a starting point.

## Phase 2 — Multiband performance decision

Measure before changing the architecture.

1. Time and size a batch for 3, 5, and 8 bands on representative designs
   (OCFD, G5RV, fan dipole).
2. Record solver invocations, build time, peak memory, and compressed project
   size.
3. If the batch is acceptable, keep the current per-band architecture.
4. If not, implement a segmented `FrequencyPlan` and a multi-`FR` NEC deck
   behind the existing `SimulationSpec` boundary.
5. Add an ADR before changing the frequency-plan contract.
6. Acceptance: a measured decision, regression tests for single-band and
   multi-band paths, and no UI regression.

## Phase 3 — Modeling and result metrics

### 3.1 Relative permeability

- Verify what NEC-2 can actually accept for conductor/permeability data.
- If supported, extend the material card writer and round-trip tests.
- If not supported, document the limitation and remove the misleading
  “relative permeability export” backlog promise.
- Keep the domain value even if the solver cannot consume it.

### 3.2 Pattern metric selector

- Add a selector for **power gain**, **directivity**, and **realized gain** in
  the pattern charts and 3D lobe.
- Keep the current power-gain default.
- Make the active metric explicit in the chart title, legend, cursor readout,
  CSV, HTML, and PDF.
- Add tests for metric selection, cursor readouts, and report labels.

## Phase 4 — New multiband presets

1. **ZS6BKW**
   - Derive from the G5RV architecture with its published dimensions.
   - Use geometry transmission lines, not a lossy lumped approximation.
   - Add catalog routing, estimator status, evidence, and tests.
2. **Zepp**
   - End-fed multiband preset with a matching section.
   - Document the tuner/feed arrangement and limitations.
3. Add both to the multiband default resolver only when their evidence and
   band coverage are documented.

## Phase 5 — Validation and references

1. Inventory experimental templates without an independent numeric reference.
2. Add references where a traceable source exists:
   - impedance, SWR, gain, or pattern metric as appropriate;
   - explicit tolerance per metric.
3. Keep unverifiable templates labeled experimental.
4. Do not invent values or copy numbers from another geometry.

## Phase 6 — Deferred and blocked work

These are not part of the next implementation session unless priorities change:

- Live VNA/hardware control.
- Additional full-wave engines.
- Physical antenna validation, blocked on measurements.
- GPG/Authenticode signing for release artifacts.
- Custom/imported geometry optimization and space constraints.
- General radial-screen and transmission-line geometry beyond the current
  supported subset.

## Recommended execution order

1. Phase 0 — commit and clean tree.
2. Phase 1 — fan dipole calibration spike, then estimator/angle work.
3. Phase 3.2 — pattern metric selector (small, high user value).
4. Phase 3.1 — relative permeability investigation.
5. Phase 4 — ZS6BKW and Zepp.
6. Phase 5 — references.
7. Phase 2 — only if measurements justify the multi-`FR` work.
8. Phase 6 — deferred/blocked.

## Quality gate for every phase

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy
NEC2C=... uv run pytest -q
```

Each phase also updates:

- `CHANGELOG.md`;
- the relevant user-guide section;
- the roadmap/backlog status;
- an ADR when a contract or architecture changes.
