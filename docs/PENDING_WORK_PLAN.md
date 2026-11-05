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
uv run mypy --config-file mypy_ui.ini
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

## Phase 2 — Multiband performance decision (measured)

Benchmark and decision: [`MULTIBAND_PERFORMANCE.md`](MULTIBAND_PERFORMANCE.md).

1. Timed and sized 3, 5, and 8 bands for OCFD, G5RV, and fan dipole.
2. Recorded wall time, compressed project size, and process peak RSS.
3. **Decision:** keep the current one-run-per-band architecture.
4. No segmented `FrequencyPlan` or multi-`FR` deck is needed now.
5. Revisit only if pattern resolution, band count, or target hardware changes
   enough to make batches visibly slow or large.
6. Acceptance: measured data recorded; no UI or solver regression.

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

1. **ZS6BKW (complete)**
   - Derived from the G5RV architecture with the Cebik/W4RNL 28.4 m / 400 Ω /
     13.6 m dimensions and the common 450 Ω commercial variant.
   - Uses a geometry transmission line, catalog routing, evidence, band
     defaults, NEC reference checks, and UI tests.
2. **Zepp (refined preset complete)**
   - Real two-wire quarter-wave stub: one conductor feeds the half-wave
     radiator, the second is open at the antenna end, and a base connector
     carries the balanced feed.
   - A 1:1 common-mode choke is a construction requirement; NEC-2 cannot model
     it. The coax and common-mode current remain outside the model.
   - Odd-harmonic starting plan (40/15 m at 7.1 MHz); even harmonics are not
     recommended because the stub balance degrades.
   - Published starting dimensions, evidence level B.

Completed follow-ups:

- ZS6BKW-specific optimizer for dipole wire length and matching-line length.
- T2FD **Estimate Dimensions...** using the Cebik wide-long rule and preserving
  the current termination and transformer.

## Phase 5 — Validation and references

1. **Inventory complete:** [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) records every
   level C template and why it remains experimental.
2. **Reference passes complete so far:** promoted `delta_loop`, `vertical`,
   `inverted_v`, `j_pole`, `slim_jim`, `endfed`, `trap_dipole`, `sloper`, and
   `doublet` from C to B using published length and deployment rules, with
   explicit tolerances and regression tests. These validate starting dimensions
   only.
3. Add more references where a traceable source exists:
   - impedance, SWR, gain, or pattern metric as appropriate;
   - explicit tolerance per metric.
4. Keep unverifiable templates labeled experimental.
5. Do not invent values or copy numbers from another geometry.

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

1. Phase 5 — independent references for experimental templates.
2. Phase 2 — completed; revisit only if the measured limits change.
3. Phase 6 — deferred/blocked.

Completed: Phase 0, the Phase 1 investigation, Phase 2 measurement, Phase 3.1,
Phase 3.2, the Phase 5 evidence inventory/first reference pass, and the refined
Zepp model.

## Quality gate for every phase

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run mypy --config-file mypy_ui.ini
NEC2C=... uv run pytest -q
```

Each phase also updates:

- `CHANGELOG.md`;
- the relevant user-guide section;
- the roadmap/backlog status;
- an ADR when a contract or architecture changes.
