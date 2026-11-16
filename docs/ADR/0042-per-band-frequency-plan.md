# ADR-0042 — Keep per-band frequency-plan execution

- **Status:** Accepted
- **Date:** 2026-11-16
- **Deciders:** Fernando Sclavo, development
- **Related:** P7 and D4 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md),
  [`../MULTIBAND_PERFORMANCE.md`](../MULTIBAND_PERFORMANCE.md)

## Context

`AnalyzeBands` runs one solver process per band and stores one
`SimulationResult` per band. P7 proposed true per-frequency progress, and D4
proposed a segmented frequency plan in one NEC deck. Both were deferred until a
benchmark showed a practical need.

The 2026-11-09 benchmark used 15 sweep points and five pattern frequencies per
band at a 5° step. Eight bands completed in about one second on the test
machine, and the project stayed well below the 32 MB warning limit. The
decision was to keep the per-band architecture.

The 0.8.0 release added the LPDA family and automatic Pi/T matching, but did
not change the multiband execution path. This review re-ran the benchmark with
a denser representative sweep and added a solver-only comparison against a
single uniform deck.

## Decision

Keep the current **one solver process per band** architecture.

- Do **not** implement a segmented multi-`FR` deck for normal band analysis.
- Do **not** implement incremental solver-output parsing for per-frequency
  progress.
- Keep the bounded parallel band workers. The four-worker path is the preferred
  way to reduce wall time.
- Keep the existing pattern budget, which reduces the pattern step or disables
  patterns when the estimated project size would exceed the storage limit.

## Measurements

Environment: Linux, AMD Ryzen 7 5825U, 16 threads, `nec2c 1.3.3`.
The benchmark runs the real `AnalyzeBands` path, records every band run in a
project, and reports wall time, compressed project size, and peak RSS.

Representative dense sweep: 101 impedance/SWR points per band and five pattern
frequencies per band at a 5° step.

| Design | Bands | Sequential s | 4 workers s | Compressed MB | Peak RSS MiB |
|---|---:|---:|---:|---:|---:|
| G5RV | 8 | 3.18 | 1.18 | 7.05 | 129 / 139 |
| Fan dipole wide | 8 | 1.80 | 1.15 | 8.53 | 129 / 139 |

The 4-worker path is **2.7×** faster than sequential for the G5RV case and
**1.6×** faster for the fan dipole. Both compressed projects remain far below
the 32 MB warning limit.

Solver-only comparison, same G5RV model, patterns disabled, 808 total
frequencies:

| Execution | Median wall time |
|---|---:|
| 8 bands × 101-point decks | 2.43 s |
| 1 uniform 3.5–30 MHz × 808-point deck | 1.48 s |

The single deck saves about **0.95 s** for the same number of frequencies. The
per-band run times are 0.13–0.18 s each, so the progress display already updates
every fraction of a second at this density. A single deck would provide one
progress event, and per-frequency progress would require parsing partial output.

A stress run with ten pattern frequencies at a 1° step produced an unbudgeted
70 MB project; the UI pattern budget reduces the step or disables patterns
before that size is recorded. The benchmark script is intentionally unbudgeted
and is not a UI-representative run.

## Rationale

- The four-worker path is faster than a sequential single deck and avoids a new
  multi-`FR`/multi-`RP` deck contract.
- The per-band progress granularity is already sufficient at realistic
  densities; true per-frequency progress adds parser complexity without a
  demonstrated user benefit.
- The per-band result is the existing regression and storage unit. A segmented
  deck would require careful aggregation of source, pattern, feed-line,
  matching-network, and cancellation semantics.
- The pattern budget already protects the project size limit. The dense stress
  case is not representative of the budgeted UI path.

## Revisit triggers

Reconsider P7/D4 only if one of these becomes true:

- a routine **budgeted** run takes more than about 10 seconds on the reference
  machine, or a representative low-end machine shows user-visible delays;
- the product explicitly requires per-frequency progress for a single solver
  invocation;
- the supported band count or pattern density grows enough that per-band
  process startup becomes a measurable fraction of the total;
- a measured single-deck implementation can preserve the current result,
  pattern, cancellation, and project-size contracts without a cross-cutting
  rewrite.

## Validation plan

1. Extend `scripts/benchmark_multiband.py` with density options so the
   representative dense sweep is reproducible.
2. Record the dense per-band and solver-only measurements in
   [`../MULTIBAND_PERFORMANCE.md`](../MULTIBAND_PERFORMANCE.md).
3. Keep the existing `AnalyzeBands` unit, integration, cancellation, and
   project-storage tests unchanged.
4. Run the full gate.
