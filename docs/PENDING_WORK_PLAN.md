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

- Family optimizer redesign (ADR-0026): explicit descriptor per typed family,
  joint hybrid search over every geometry/feed/load dimension, explicit
  unavailable reasons, no fallback, and apply-best routing through an exhaustive
  adapter. See `OPTIMIZER_PHASE_A_PLAN.md`.
- T2FD **Estimate Dimensions...** using the Cebik wide-long rule and preserving
  the current termination and transformer.
- G5RV, ZS6BKW, and Zepp are typed families with inline editors and family
  optimizers (schema 17). The old custom-generator designs remain loadable for
  compatibility; the doublet remains a dipole plus a project-level feed line.
- Phase C advanced optimizer quality: band-aware and robust modes, Pareto front,
  persisted summaries, and recommendations. See `OPTIMIZER_PHASE_C_PLAN.md`.

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
6. **Remaining C audit complete (2026-11-06):** the published 102 in mobile-whip
   example promoted `loaded_vertical` to B for that preset. The four previously
   reviewed templates (`ringo`, `fan_dipole`, `random_wire`, and `custom`)
   remain C, and the newly added `inverted_l` starts at C pending a published
   reference; see [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md). The Ringo generator
   now has a Cushcraft AR-6 starting-dimensions preset, but promotion still
   needs a model of the commercial matching ring.

## Phase 6 — Deferred and blocked work

These are not part of the next implementation session unless priorities change:

- Live VNA/hardware control.
- Additional full-wave engines.
- Physical antenna validation, blocked on measurements.
- GPG/Authenticode signing for release artifacts.
- Custom/imported geometry optimization and space constraints.
- General radial-screen and transmission-line geometry beyond the current
  supported subset.

## Phase 7 — Antenna expansion backlog

The ordered antenna backlog lives in
[`ROADMAP.md`](ROADMAP.md#antenna-backlog). The immediate sequence is:

1. **Completed 2026-11-06:** Inverted L as a first-class family with an editor,
   catalog route, persistence, geometry, reports, and tests. Evidence stays C
   until a published reference supplies a traceable numeric metric.
2. **Completed 2026-11-06:** horizontal/sky loop as a loop-orientation option,
   with schema 10 persistence, plan/elevation scene handling, and tests.
3. **Completed 2026-11-06:** elevated-radial and ground-screen starting presets
   over the existing vertical radial fields, with editable numeric values.
4. **Completed 2026-11-07:** magnetic loop as a separate tuned small-loop model
   with a top gap, ideal series capacitor and ESR, conductor-loss simulation,
   efficiency and SWR-bandwidth reporting, and a dedicated editor.
5. **Completed 2026-11-07:** optional folded Yagi driven element with two
   conductors, end connectors, adjustable spacing, and NBS-preset support.
6. **Partially completed 2026-11-07:** beta/hairpin match geometry with a
   split driven element and shorted stub. Gamma remains deferred because NEC-2
   is unreliable for close-spaced gamma assemblies; use the matching network.
7. **Completed 2026-11-07:** project-level balun/unun insertion loss with a
   frequency-dependent power-law fit, applied to realized gain and reports.
8. **Completed:** capacitive top-hat and loading-coil support in the vertical
   template, now included in reports, construction sheets, and the scene
   contract. The hat remains an application starting point, not an
   independently validated loading design.
9. **Completed 2026-11-07:** explicit EFHW labeling and published 40/20/10 m
   preset buttons for the existing EndFed template.
10. **Completed 2026-11-07:** half-square and bobtail-curtain self-contained
    vertical arrays with a shared editor, top-junction feed, schema-16
    persistence, published Cebik dimensions, and a frequency-first estimator
    deliberately deferred until a dedicated estimator is justified.

The remaining medium and large candidates are ordered after those seven in the
roadmap table. Items 15–19 require architectural work or a much larger test
surface and should wait until the single-feed families are stable.

## Recommended execution order

1. Phase 7 — antenna expansion, in the order listed in the antenna backlog.
2. Phase 5 — references for each new family as it lands, plus any remaining
   experimental-template work.
3. Phase 2 — completed; revisit only if the measured limits change.
4. Phase 6 — deferred/blocked.

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
