# ADR-0022 — Multiband analysis by per-band batches

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none

## Context

The simulation domain has one contiguous `FrequencyPlan` per `SimulationSpec`.
The G5RV could be inspected over 3.5-30 MHz only because its custom panel
exposed a wide sweep. Other multiband families used a narrow sweep around one
design frequency, so their other bands were invisible.

ADR-0019 and ADR-0020 already decoupled the impedance sweep from band-aware
far-field snapshots. They did not provide a way to create several impedance
bands or to present the results together.

A segmented `FrequencyPlan` and a multi-`FR` NEC deck were considered. That
would touch the adapter, parser, normalization, budget, charts, CSV, reports,
persistence, optimization, and tests at once. It would also make a failure in
one frequency block harder to isolate.

## Decision

1. Model a multiband request as a validated `BandPlan` of `BandSelection`
   values. Each selection carries one `AmateurBand` and a sweep point count.
2. Run the existing single-band `RunSimulation` once per selected band in an
   application-level `AnalyzeBands` service. No adapter or deck change is
   required.
3. Keep completed results when another band fails. Cancellation stops between
   bands and returns a partial batch.
4. Group results in an immutable `BandAnalysisResult`. Each band result keeps
   its own spec, diagnostics, pattern snapshot, and storage budget.
5. Apply the global **Simulation pattern** policy inside each band: Auto uses
   the band snapshots and a fixed pattern-frequency count uses that many
   snapshots per band. The storage budget and pattern step are chosen for the
   whole batch.
6. Persist each completed band run with a stable `band_id` and shared
   `batch_id`. Project reconstruction groups the latest batch. Schema version 4
   adds both fields as optional metadata.
7. Keep the UI in the central analysis area: a **Band analysis** group beside
   the global **Simulation pattern** group, a selection dialog, and a **Bands**
   results tab. The top action bar remains Apply/Estimate/Optimize.

## Consequences

Positive:

- No solver-adapter risk; each band uses the already-tested single-band path.
- A failed band does not discard the rest of the analysis.
- Existing pattern snapshots, storage budgeting, diagnostics, and result views
  are reused.
- Single-band Simulate and the G5RV continuous sweep remain available.
- The persistence change is additive and old projects load through migration.

Limitations:

- A batch performs N solver invocations instead of one.
- Raw solver output is stored per band, so a large band set still consumes
  project space.
- The project schema gains optional run metadata.
- The doublet still lacks a persisted preset identity, so it has no family
  default yet.
- Cross-band design comparison and per-band pattern PNG export remain
  follow-ups.
- A segmented frequency plan in one deck remains a future optimization if
  measurements show that per-band startup or raw output is a problem.

## Amendment 2026-11-04 — pattern navigation and per-band snapshot policy

The **Pattern** frequency selector now lists the snapshots from every analyzed
band and switches the active band when one is selected; the **Bands** table
stays synchronized. Band analysis no longer forces a single snapshot per band:
it applies the global pattern-frequency policy inside each band, and the batch
budget uses the resulting counts per band. The global pattern and sweep controls
were moved into **Advanced simulation**.
