# Pending work plan

**Status:** in progress; completed items are marked below
**Date:** 2026-11-04
**Scope:** remaining work after the multiband, OCFD, and fan-dipole milestones

This plan orders the open work so each phase is independently shippable and
testable. It is not a commitment to implement every item in one session.

## Phase 0 — Close the current change set (complete)

1. Committed the per-band pattern PNG export:
   - `ResultsView.save_band_pattern_images()`;
   - folder export from the Pattern PNG action when a band analysis is active;
   - tests and documentation.
2. Re-run the full gate before starting the next phase:

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy
NEC2C=... uv run pytest -q
```

## Phase 1 — Fan dipole accuracy and tuning (investigation complete; angle work deferred)

**Finding:** a universal V-angle/coupling correction is not justified. See
[`FAN_DIPOLE_CALIBRATION.md`](FAN_DIPOLE_CALIBRATION.md). The isolated V
element has a smooth angle-dependent shift, but the coupled 20/10 fan is
dominated by mutual coupling. Keep the estimator as a starting point, keep the
warning and optimizer guidance, and defer an angle-variable optimizer until a
different antenna model is justified.

### Completed

- Measured standalone V elements from 60° to 180° at 14.1 MHz and 28.4 MHz
  over finite ground.
- Measured a coupled 20/10 m fan and compared it with each element alone.
- Documented that the coupled fan impedance is not a parallel combination of
  independent dipoles.
- Decided against an automatic angle or coupling length correction because it
  would be installation-specific and could hide the interaction.
- Kept the estimator as a starting point, the V-angle/coupling warning, and
  the band-aware optimizer. Unchecked elements remain in the antenna, and the
  optimizer reports the resulting mismatch.

### Deferred

- Angle-variable optimization and any explicit per-element feed model. These
  need a different antenna model, not another scalar correction.
- A 20/10 m preset with measured or optimized dimensions. Add one only with a
  traceable source or documented measurement.

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

## Phase 3 — Modeling and result metrics (complete)

### 3.1 Relative permeability (investigation complete)

- NEC-2 does not accept magnetic permeability for the wire model used here.
- The adapter already emits `solver.permeability_unsupported` when a material
  has `relative_permeability != 1`, and the domain value remains persisted.
- The backlog promise was corrected: this is a documented limitation, not an
  export feature to implement.

### 3.2 Pattern metric selector (implemented)

- Added a selector for **power gain**, **directivity**, and **realized gain**
  in the pattern chart, polar plot, 3D lobe, and cursor readout.
- Directivity and realized gain shift the sampled power-gain pattern to the
  metric value at the maximum direction.
- CSV/HTML/PDF still report the original power-gain columns; report-specific
  metric selection remains optional follow-up work.
- Tests cover the metric offsets, UI selection, cursor labels, and unavailable
  metrics.

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

1. Phase 4 — ZS6BKW and Zepp presets.
2. Phase 5 — independent references for experimental templates.
3. Phase 2 — only if timing measurements justify the multi-`FR` work.
4. Phase 6 — deferred/blocked.

Completed: Phase 0, the Phase 1 investigation, Phase 3.1, and Phase 3.2.

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
