# ADR-0004 — Persist simulation runs in project schema v3

- **Status:** Accepted
- **Date:** 2026-10-29
- **Deciders:** Fernando Sclavo, development
- **Phase:** 6 — New geometry and persistence

## Context

Phase 4 stored simulation results only in memory. Comparison, reports, and the
construction sheet worked during the session but were lost when the project was
reopened. The blueprint requires exact snapshots, traceability to raw solver
data, and reproducibility.

Project schema version 2 already persists design variants and their geometry.
Simulation results are immutable objects with a model/spec fingerprint, solver
metadata, diagnostics, currents, far-field data, and raw solver text.

## Decision

- Add `SimulationRun` to the project domain: an ID, design ID, creation time,
  and an immutable `SimulationResult`.
- Persist completed and partial runs in the project as `simulation_runs`.
- Store normalized results plus raw solver input/output and stderr. The existing
  10 MB project limit bounds the file size.
- Store SWR as `null` when it is infinite, because strict JSON does not support
  `Infinity`.
- Bump the project schema to **version 3**. Migrate version 2 documents by
  adding an empty `simulation_runs` list.
- Remove a design's runs when the design is deleted; runs must reference an
  existing design.
- On open, show the latest run for each design variant.

## Consequences

### Positive

- Reports, comparison, and construction sheets remain available after reopening.
- Runs are traceable to the model/spec fingerprint and solver version.
- Raw solver text is preserved for diagnosis.
- The migration path is explicit and tested.

### Negative

- Project files grow with result data and raw solver text.
- The 10 MB limit can be reached with many long sweeps.
- Old runs remain after a design is edited; the GUI shows the latest, while the
  current design may differ until the user simulates again.
- No UI for pruning individual runs yet.

### Neutral

- The result schema adds many payload classes but keeps the domain unchanged.
- Deleting a design removes its runs to preserve referential integrity.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Keep results session-only | Breaks reports and comparison after reopening |
| Store only a summary | Loses currents, pattern, diagnostics, and traceability |
| Sidecar result files | More path management and partial-project risk |
| Auto-save after each run | Surprising file writes; explicit save remains user-controlled |
| Database | Overkill for the current local-first JSON model |

## Follow-up

1. Add measurement records in a later schema version.
2. Add run pruning/archiving or compression if project size becomes a problem.
3. Keep migration tests mandatory for every schema change.
