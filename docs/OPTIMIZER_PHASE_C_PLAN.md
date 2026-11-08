# Phase C — advanced optimization quality

- **Status:** Implemented 2026-11-07
- **Date:** 2026-11-07
- **Scope:** Band-aware and robust modes, Pareto front, persisted summaries, and
  post-run recommendations
- **Related:** [ADR-0026](ADR/0026-family-optimizer-architecture.md)

## Purpose

Phase A established the family descriptors and the shared hybrid engine. Phase
B converted the remaining custom-generator presets to typed families. Phase C
adds the quality layer: evaluate more than one operating point, show
non-dominated trade-offs, keep a compact audit record, and explain what the
result means.

The phase deliberately does not add a matching-network optimizer, frequency
optimization, or topology search. Those remain separate decisions.

## Operating modes

`OptimizationMode` is part of the application command and the persisted
summary.

| Mode | Evaluations per candidate | Purpose |
|---|---|---|
| `single` | 1 | Default; one design-frequency solve |
| `band_aware` | one per listed edge | Worst-case behavior across a band set |
| `robust` | 3 per edge | Nominal and ± dimensional-tolerance corners |

Band edges are supplied explicitly by the dialog. They default to the current
project band plan (start, center, and stop of each selected band). If no plan is
available, the application falls back to the design frequency and ±5 %.

Robust tolerance applies to every continuous variable whose presentation unit
is a length (`m`) or conductor radius (`radius`). The three scenarios are
`-tolerance`, nominal, and `+tolerance`; all dimensional variables move
together, so the result is a deterministic worst-case corner, not a random
Monte Carlo sample.

Bandwidth optimization and the bandwidth soft constraint remain single-frequency
features because they already require a sweep. Multi-point modes reject them
explicitly.

## Metrics and scoring

For each scenario the application runs one simulation per band edge and
aggregates:

- maximum SWR, target error, and target SWR;
- minimum gain, front-to-back ratio, and efficiency;
- `swr_spread` across the evaluated points;
- the worst-case frequency;
- the multi-point count.

The reported resistance and reactance come from the point nearest the design
frequency. The score uses the worst scenario. In robust mode a variance penalty
is added:

```text
score = worst_scenario_score + 0.1 * (worst_scenario_score - best_scenario_score)
```

The 0.1 coefficient is an explicit search heuristic, not a physical model. It
is applied in the same units as the selected objective. Soft constraints are
evaluated on the aggregated worst-case metrics.

## Pareto front

`pareto_front()` keeps feasible candidates that are not dominated on every
metric shared by all feasible evaluations. Supported metrics are SWR (minimize),
target impedance error (minimize), gain (maximize), front-to-back (maximize),
efficiency (maximize), and bandwidth (maximize). At least two common metrics
are required; otherwise the front is empty rather than a misleading
single-objective list.

The front is descriptive. Apply Best still uses the ranked best score, and the
front is not persisted in full.

## Persisted summary

A successful or attempted run creates an `OptimizationSummary` with:

- method and version;
- mode, objective, status, and budget profile;
- evaluation count and seed;
- band edges and robust tolerance;
- winning values and metrics;
- weights and constraint descriptions;
- deterministic recommendation keys, severities, and variable names;
- completion timestamp.

The summary is stored on the design variant and written to schema version 18.
The full evaluation log is not persisted. A v17 to v18 migration is a no-op
because the new field is optional.

## Recommendations

Recommendations are deterministic and translatable message keys. They cover:

- no feasible candidate;
- cancellation;
- an exhausted budget;
- locked variables;
- SWR above the soft constraint or the 2:1 heuristic;
- strong SWR variation across band edges (spread above 0.5);
- robust score spread above 10 % of the best score's magnitude;
- the single sensitivity probe that changes the score by more than 25 % of its
  magnitude.

They describe the search and the modeled metrics only. They never assert that a
physical antenna will meet a target without measurement.

## UI

The family optimizer dialog adds:

- an operating-mode selector;
- an editable comma-separated band-edge field in MHz;
- a dimensional-tolerance percentage;
- a quality-mode budget estimate;
- a Pareto table when the front has at least two shared metrics;
- a recommendation block;
- the last persisted summary line.

## Verification

- `tests/unit/application/test_optimize_antenna_modes.py` counts solver calls
  for band-aware and robust modes and checks the summary fields.
- `tests/unit/optimization/test_summary.py` covers summary validation,
  recommendation rules, and Pareto ranking.
- `tests/unit/persistence/test_geometry_persistence.py` and
  `tests/unit/persistence/test_migrations.py` cover schema-18 round trips and
  the v17 to v18 migration.
- `tests/ui/test_family_optimization_dialog.py` covers the mode controls, the
  last-summary line, and a band-aware run.
- `tests/ui/test_main_window_optimization.py` covers attaching the summary to
  the project design.
- Full gate at Phase C close: **1666 passed, 1 skipped**; **1700 passed** after
  the subsequent biquad family. The skip is the PyNEC cross-engine comparison
  because PyNEC is not installed. Repeated UI stress runs also cover the
  worker-thread lifetime fix in the optimizer dialogs.

## Limitations

- Robust mode is a three-corner deterministic sensitivity check, not a
  statistical tolerance analysis.
- Band-aware runtime grows linearly with the number of edges and scenarios.
- The Pareto front is not exported to CSV yet.
- Recommendations are heuristics about the search, not validated design advice.
- Physical antenna/VNA validation remains unavailable.
