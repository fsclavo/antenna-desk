# Multiband analysis plan

**Status:** proposed, not implemented
**Date:** 2026-11-03
**Revised:** 2026-11-03 after the centralized design-panel action bar and
global **Simulation pattern** group.
**Scope:** analysis workflow, not new antenna geometry

## Problem

The G5RV can be inspected over 3.5–30 MHz because it is stored as a custom
design and the custom design panel exposes an editable frequency sweep. Most
other multiband families use a fixed 31-point sweep of ±5 % around one design
frequency, so the user cannot see what happens on their other bands.

This is a workflow gap, not a solver limitation. NEC already runs over any
frequency range, and ADR-0019/ADR-0020 already decouple the impedance sweep
from band-aware pattern snapshots. What is missing is a band-aware analysis
request and a way to present several band results together.

## Current behavior

| Family | Current sweep | Can the user see other bands? |
|---|---|---|
| G5RV | Custom panel, 41 points over 3.5–30 MHz by default | Yes, but as one continuous sweep |
| OCFD | 31 points, 0.95–1.05 × design frequency | No |
| End-fed, random wire, sloper | 31 points, 0.95–1.05 × design frequency | No |
| Fan dipole | 31 points, 0.95–1.05 × `frequency_hz` | No, even though each element is a different band |
| Trap dipole | 31 points from low × 0.95 to high × 1.05 | Partially, with many unused points between bands |
| T2FD | 31 points from the low to the high limit | Broadband, but sparse and not labelled by band |
| Doublet | Dipole form, 100 points, 0.95–1.05 × design frequency | No |
| Dipole, folded dipole, vertical, Yagi, Moxon, loops | Narrow sweep around the design frequency | Not by default; manual sweep editing varies by family |

The G5RV is therefore not special because it is "more multiband" than the
others. It is special because its implementation happens to expose the generic
custom sweep controls.

The recent GUI consolidation is part of the baseline for this plan: the design
panel now has one action bar (**Apply design**, **Estimate Dimensions...**,
**Optimize...**) and one global **Simulation pattern** group. Per-form pattern
controls and the duplicate bottom Apply/Optimize buttons were removed. The
frequency sweep remains family-specific. Band analysis must join this central
area and must not reintroduce per-form pattern or band controls.

## Goals

1. Let the user select a set of amateur bands for analysis.
2. Give each naturally multiband family a documented default band set.
3. Keep single-band designs and the existing Simulate action unchanged.
4. Show a compact per-band summary: best SWR, frequency at best SWR, gain,
   takeoff angle, efficiency, and run status.
5. Reuse the existing per-band result views, global pattern settings, storage
   budget, reports, and undo/redo model.
6. Keep every default and limitation visible; do not claim that an antenna is
   resonant on a band just because the band is selected.

## Non-goals

- Do not add new antenna geometry in this milestone.
- Do not replace the NEC adapter or the normalized result model.
- Do not infer resonance from a band label. Defaults are starting points.
- Do not implement live VNA control, automatic tuner control, or physical
  validation.
- Do not make every family look multiband. Narrowband families keep their
  current behavior and can opt into manual band selection if useful.

## Candidate families

The first wave should include families that are explicitly designed for more
than one band, plus presets that are commonly used with a tuner.

### Explicit multiband geometry

| Family | Why it qualifies | Proposed default bands | Notes |
|---|---|---|---|
| G5RV | 102 ft dipole plus 300/450 Ω matching line | 80, 40, 20, 15, 10 m; optional 30, 17, 12 m with tuner; also "All HF" 3.5–30 MHz | Published preset; current continuous sweep remains an option |
| OCFD | Off-center feed at about 1/3; classic 40/20/10 coverage | 40, 20, 10 m for a 40 m design; use 80, 40, 20, 10 for an 80 m design | Heuristic; floor plan depends on length and feed ratio |
| Fan dipole | One half-wave element per band | Derive from element lengths or `DesignIntent.fan_bands_hz` | Add band metadata to `FanElement` or persist the estimator bands |
| Trap dipole | Two resonant sections separated by traps | Low band from `frequency_hz`; high band from `high_band_frequency_hz` | Both frequencies already exist in the model |
| T2FD | Terminated folded dipole, broadband by design | 160–10 m, 80–10 m, or "All HF" | Broadband, not a set of narrow resonances |
| Doublet | Center-fed doublet with open-wire line and tuner | 80–10 m; optional 160–6 m | Requires preserving the doublet identity and modelling the tuner as an external limitation |

### Tuner-assisted or non-resonant

| Family | Why it qualifies | Proposed default bands | Notes |
|---|---|---|---|
| End-fed | 49:1 transformer plus counterpoise, commonly 40/20/10 | 40, 20, 10 m for a 40 m design; 80, 40, 20, 10 for an 80 m design | Defaults must be labelled as starting points |
| Random wire | 9:1 transformer, non-resonant wire, external tuner | 80, 40, 30, 20, 17, 15, 12, 10 m | Wire length and tuner range matter; show a warning |
| Sloper | End-fed sloper geometry | Same as end-fed, conservative 40/20/10 | A sloper is a geometry, not a guarantee of multiband operation |

### Future presets

- **ZS6BKW**: G5RV-derived multiband preset already listed as a roadmap
  candidate.
- **Zepp**: end-fed multiband preset using a matching section.
- **Loop on harmonics**: possible, but high feed impedance and pattern changes
  make it a separate study; do not include it in the first wave.
- **Trap vertical / multiband vertical**: not modelled yet; add only after a
  dedicated template exists.

Narrowband families remain unchanged: dipole, folded dipole, vertical, Yagi,
Moxon, J Pole, Slim Jim, Ringo, and generic loops. A user may still add a
manual band set later, but there is no family default that implies multiband
operation.

## Recommended architecture

### Option A: one solver run per band (recommended for the first milestone)

Add an application-level band-analysis service that runs the existing
single-band `RunSimulation` once per selected band.

- Domain:
  - Reuse `AmateurBand` and `AMATEUR_BANDS` from
    `domain/simulation/bands.py`.
  - Add a validated `BandSelection`/`BandPlan` value containing the selected
    bands and per-band frequency-sweep point counts.
  - Add a family-default resolver that maps a design to candidate bands and
    an evidence/limitation note.
- Application:
  - Add `BandResult` and `BandAnalysisResult` values.
  - Add an `AnalyzeBands` use case that loops over band specs, calls the
    solver, and returns partial results when a band fails or the user cancels.
  - Keep `RunSimulation` as the only solver-facing use case.
- UI:
  - A compact **Band analysis** group in the central design area, beside the
    existing global **Simulation pattern** group. The top action bar stays at
    three buttons: Apply design, Estimate Dimensions..., Optimize...
  - A band-selection dialog with checkboxes, per-band frequency-sweep points,
    and preset buttons (for example 40/20/10, 80–10, All HF).
  - A band-analysis worker that reports "band 2 of 3" progress and supports
    cancellation between bands.
  - A **Bands** results tab with one row per band. Selecting a row reuses the
    existing ResultsView for that band.
- Persistence:
  - Extend `SimulationRun` with optional `band_id` and `batch_id` fields.
  - Add a schema migration with null defaults so old projects load unchanged.
  - Compact the latest run per design and band, not just per design.

Advantages:

- No changes to the NEC adapter, deck writer, parser, or normalization.
- A failure in one band does not discard the other bands.
- Each band gets its own representative pattern snapshot, storage budget, and
  diagnostics while sharing the global angular resolution.
- Existing single-band Simulate remains the regression baseline.
- The G5RV can keep its continuous "All HF" mode while gaining a band-list
  mode.

Costs:

- N solver invocations for N bands. For 3–8 HF bands and 11–31 points per band,
  this is small compared with a dense wideband sweep.
- Batch persistence and latest-run semantics need explicit handling.
- Raw solver output is stored per band, so the batch report must stay within
  the project budget.

### Option B: segmented frequency plan in one deck (defer)

Extend `FrequencyPlan` to hold multiple contiguous segments and write several
NEC `FR` blocks in one deck. Normalization would merge the blocks into one
`SimulationResult`.

Advantages:

- One solver invocation and one raw output.
- A single result object for the whole analysis.

Costs:

- `FrequencyPlan` is used by snapshots, budgets, charts, CSV, reports,
  persistence, optimization, and tests. Changing it to a segmented model is a
  cross-cutting change.
- The NEC adapter and normalization would need multi-block tests.
- A failure in one block is harder to isolate.
- The current project already has a working single-band boundary and
  band-aware snapshot policy. Option A adds less risk for the same user value.

Recommendation: implement Option A first. Revisit Option B only if solver
startup or raw-output size becomes a measured problem.

## UX proposal

### Band selection

Use a dedicated **Analyze Bands...** action in the Simulation menu and a compact
control in a central **Band analysis** group. Do not add a fourth equal button
to the action bar: Apply design, Estimate Dimensions..., and Optimize... are the
only top-level design actions. The dialog should contain:

- a preset selector: **Current band**, **40/20/10**, **80–10**, **All HF**,
  **Custom**;
- a checkbox per band from 160 m to 6 m;
- a per-band frequency-sweep point count, defaulting to 11 or 15 for narrow
  bands and 31 for broadband families;
- a short note showing the family default, its evidence level, and any
  limitation (for example "tuner required", "starting point only");
- a warning if the selection includes a band outside the design's documented
  coverage.

Defaults should be preselected from the family resolver, not hard-coded in the
dialog.

### Pattern settings

The global **Simulation pattern** group remains the single place for angular
resolution and pattern-frequency policy. Band analysis must not duplicate it or
reintroduce per-form controls.

- In band-analysis mode, each band gets one representative pattern snapshot at
  its design or band-center frequency by default. This mirrors the existing
  G5RV "one pattern per band" behavior without multiplying patterns by the
  narrow-band minimum.
- The global angular step (Auto max, 1°, 2°, 5°, and so on) applies to every
  band. The budget check uses the total pattern count of the batch.
- The existing **Pattern frequencies** count remains meaningful for a single
  contiguous plan. When band analysis is active, the dialog shows "one per
  band" and the total pattern count; a later enhancement can allow more
  snapshots per band if users need pattern-versus-frequency detail inside one
  band.
- The first milestone keeps the band dialog limited to band selection and
  frequency-sweep points. Pattern resolution and snapshot policy stay in the
  global group, so the GUI does not grow a second pattern editor.
- `band_snapshot_frequencies()` selects snapshots inside one plan; it does not
  create multiple impedance bands. Band analysis creates the frequency plans;
  the pattern group decides how much far-field data to keep.

### Results

Add a **Bands** tab to `ResultsView`:

| Band | Range | Best SWR | At frequency | Gain | Takeoff | Efficiency | Status |
|---|---|---|---|---|---|---|---|

- Clicking a row selects that band and feeds its `SimulationResult` into the
  existing Impedance/SWR, Pattern, Currents, Measurements, Diagnostics, and Raw
  data tabs.
- A band analysis with one selected band behaves exactly like today's
  Simulate.
- Failed or cancelled bands remain visible with a status and diagnostic.
- A later enhancement can overlay band ranges on the SWR chart and compare
  variants per band.

### Simulation action semantics

- **Simulate** keeps the current-band or current-sweep behavior.
- **Analyze Bands...** runs the selected band set from the Simulation menu and
  the central **Band analysis** group.
- The top action bar is unchanged; band analysis is not a fourth primary
  button.
- Both use the same worker-thread and cancellation model.
- The status line and progress dialog identify the active band.
- If the user cancels, keep completed bands and report a partial analysis.
- If the solver is unavailable, both actions follow the existing disabled and
  error behavior.

## Per-family defaults and evidence

Defaults must be data, not scattered conditionals in the UI. Each default
should carry:

- band identifiers;
- a source or evidence level;
- a short limitation note;
- an optional "all HF" continuous alternative.

Proposed defaults:

- **G5RV**: 80/40/20/15/10 m, with optional 30/17/12 m when the user has a
  tuner, plus an "All HF" continuous option. Source: published G5RV dimensions
  and the existing preset documentation.
- **OCFD**: the design band plus harmonically related bands, capped to a
  documented set. For a 40 m design, default 40/20/10 m. For an 80 m design,
  default 80/40/20/10 m. Label as a heuristic.
- **End-fed**: the design band plus harmonically related bands. For 40 m,
  40/20/10 m; for 80 m, 80/40/20/10 m. Label as a starting point and show the
  transformer ratio and counterpoise limitation.
- **Random wire**: 80/40/30/20/17/15/12/10 m, with a visible "external tuner
  required" note.
- **Sloper**: same as end-fed, conservative 40/20/10 m; no independent
  multiband claim.
- **Fan dipole**: one band per element, derived from element lengths or from
  persisted estimator bands. If the mapping is ambiguous, ask the user rather
  than guessing silently.
- **Trap dipole**: low band = `frequency_hz`, high band =
  `high_band_frequency_hz`; no band in between.
- **T2FD**: 160–10 m or 80–10 m band set plus an "All HF" continuous option;
  label as broadband.
- **Doublet**: 80–10 m default, with a tuner-required note. This requires
  preserving the doublet identity instead of storing it as a plain dipole.
- **Future ZS6BKW/Zepp**: add defaults with the preset and its source.

No default may be copied from another family without evidence. If a family has
no documented multiband behavior, it gets the current-band default only.

## Data and persistence

### Band selection

Recommended: store the selected band IDs and point counts as optional
design-level analysis settings, so reopening a project restores the user's
band selection. If design-level settings are too invasive for the first
iteration, derive the initial selection from the latest band batch and add
persistence in a later phase.

### Simulation runs

Extend `SimulationRun` with:

```text
band_id: str | None
batch_id: UUID | None
```

- Single-band runs keep both fields null.
- A band batch shares one `batch_id`.
- `latest_simulation_run(design_id)` keeps its current meaning.
- Add `latest_simulation_run_for_band(design_id, band_id)` and
  `latest_band_analysis(design_id)`.
- History compaction keeps the latest run per design and band, plus the latest
  batch grouping.
- Undo/redo still preserves simulation runs when a design edit is undone; the
  merge logic must retain band and batch metadata.

Schema changes require a version bump and a migration with null defaults.
There is no pickle; the project remains versioned JSON.

## Reports and exports

- CSV: add a `band` column while preserving the existing column order for
  single-band exports. Document the new column in the user guide.
- HTML/PDF: add a band summary table and one pattern image per selected band
  when the analysis contains more than one band.
- Pattern export: allow exporting the selected band's pattern or all bands.
- Comparison dialog: add best-SWR and gain rows per band; keep the existing
  single-frequency comparison when no band analysis exists.
- Project size: apply the existing budget per band and also check the total
  batch size before saving. A batch that exceeds the limit should warn and
  offer fewer bands, fewer points, or a coarser pattern.

## Implementation phases

### Phase 1 — Domain foundations

- Add `BandSelection`/`BandPlan` validation and tests.
- Add the family-default resolver and evidence notes.
- Add table-driven tests for every supported family.
- Document the defaults in `docs/ANTENNA_DESIGN_ESTIMATORS.md` or a dedicated
  section of the user guide.

Exit criteria: no UI or solver change; unit tests cover every default and
invalid selection.

### Phase 2 — Batch engine

- Add `BandResult`, `BandAnalysisResult`, and `AnalyzeBands`.
- Add a worker that runs bands sequentially, reports progress, and supports
  cancellation between bands.
- Reuse the storage-budget policy per band, with one pattern snapshot per band
  by default and an aggregate check.
- Add fake-solver tests for success, partial failure, cancellation, and an
  empty band set.

Exit criteria: a batch returns one result per selected band; a single-band
batch is equivalent to today's Simulate.

### Phase 3 — Band selection UI

- Add the **Analyze Bands...** action and dialog.
- Add a compact **Band analysis** group beside the global **Simulation
  pattern** group; keep the action bar at Apply/Estimate/Optimize.
- Preselect family defaults; allow custom bands and point counts.
- Use one pattern snapshot per band by default and keep angular resolution
  global.
- Add the **Bands** results tab and band switching.
- Add accessibility names, tooltips, and translations in English and Spanish.
- Add pytest-qt tests for defaults, validation, progress, cancellation, band
  selection, and the unchanged action bar.
- Add a regression test that no per-form pattern or band controls return.

Exit criteria: G5RV, OCFD, and end-fed can be analyzed across their default
bands without touching the frequency sweep manually, and the centralized
action bar/pattern layout remains intact.

### Phase 4 — Persistence and reports

- Extend `SimulationRun` and the project schema with band and batch metadata.
- Migrate old projects; add round-trip and compaction tests.
- Add band-aware CSV, HTML, PDF, comparison, and pattern exports.
- Add undo/redo regression tests for band batches.

Exit criteria: save, reopen, report, and compare preserve the band analysis.

### Phase 5 — Remaining families and presets

- Fan dipole band metadata.
- Trap dipole two-band defaults.
- T2FD broadband defaults.
- Doublet identity and tuner-required warning.
- ZS6BKW and Zepp when their presets are added.
- Review loop harmonic analysis separately.

Exit criteria: every family in the candidate table has a documented default
or an explicit exclusion.

### Phase 6 — Performance follow-up (conditional)

- Measure solver invocations and project size for 3, 5, and 8 bands.
- If the batch is too slow or too large, prototype Option B (segmented
  frequency plan in one deck).
- Do not start Phase 6 without measurements showing a problem.

## Test plan

- Domain: band ranges, duplicate selection, custom ranges, family defaults,
  evidence notes, no bands outside the supported catalog.
- Application: per-band specs, partial failures, cancellation, budget,
  aggregation, and deterministic ordering.
- Solver integration: one real NEC run for each representative family; no
  invented reference values. Reuse existing reference anchors where available.
- UI: dialog defaults, action enablement, progress, band switching, empty
  states, error states, English/Spanish text, unchanged action bar, no
  duplicate per-form pattern controls, and no pattern editor inside the band
  dialog.
- Persistence: schema migration, round-trip, compaction, old project loading.
- Reports: CSV column contract, HTML/PDF band sections, pattern export.
- Regression: single-band Simulate, G5RV continuous sweep, pattern snapshots,
  storage budget, undo/redo, and comparison.

## Risks and open questions

1. **What counts as a documented band?** OCFD and end-fed coverage depends on
   length, feed ratio, transformer, counterpoise, and installation. Defaults
   must be labelled as starting points, and the dialog must not imply a
   guaranteed resonance.
2. **G5RV continuous versus band list.** Keep both. The continuous sweep is
   the existing behavior and a useful broadband view; the band list is the new
   focused workflow.
3. **Fan-dipole band mapping.** Element lengths do not identify a band
   unambiguously after manual tuning. Prefer persisted band metadata from the
   estimator, fall back to a user prompt, and never guess silently.
4. **Doublet identity.** The current doublet preset is stored as a plain
   dipole plus a feed line. Add explicit preset metadata before offering
   doublet defaults.
5. **Regional band plans.** The catalog uses generic HF ranges. Allow custom
   ranges and document that the user is responsible for local regulations.
6. **Batch semantics.** A cancelled or partially failed batch must remain
   inspectable and saveable without pretending all bands succeeded.
7. **Storage.** A full HF band set with fine patterns can exceed the project
   budget. Use one pattern per band by default, the existing budget per band,
   and show the aggregate before running.
8. **Solver output.** Each band keeps its own raw output. Truncating or
   compressing raw output remains a separate optimization.
9. **Centralized UI.** The recent GUI correction deliberately removed per-form
   pattern controls and duplicate action buttons. Band analysis must extend the
   central analysis area, not reverse that consolidation. If per-band pattern
   detail is needed, add an explicit per-band override later rather than
   multiplying the global count silently.

## Definition of done

- A user can select bands for G5RV, OCFD, end-fed/random wire, fan dipole,
  trap dipole, T2FD, and doublet.
- Each family default has a source or an explicit experimental label.
- A band summary shows best SWR, gain, and takeoff angle per band.
- Selecting a band reuses the existing charts and pattern views.
- The action bar remains Apply design/Estimate Dimensions.../Optimize..., and
  band controls live in the central analysis area.
- Band analysis uses one pattern snapshot per band by default and respects the
  global angular resolution.
- No per-form pattern or band controls return.
- Single-band behavior is unchanged.
- Cancellation and partial failure are safe and visible.
- Save/open, reports, exports, comparison, and undo/redo preserve the analysis.
- Tests cover domain, application, UI, persistence, reports, and regressions.
- Documentation and `CHANGELOG.md` are updated when the feature ships.
