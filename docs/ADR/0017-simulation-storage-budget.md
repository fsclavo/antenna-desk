# ADR-0017 — Simulation storage budget and automatic pattern resolution

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none

## Context

A G5RV run with 301 frequencies and a 5° far-field pattern produced
53,214,361 bytes of NEC output. The solver limit is 50 MB, so the run failed
with an opaque `solver.execution_error`. Even a run below 50 MB may exceed the
project's 10 MB storage limit because the project persists both the raw solver
output and the normalized far-field/current records.

The user should not have to discover these limits by trial and error, and the
application should use the finest pattern resolution that can be stored safely.

## Decision

1. Estimate the persisted project size before a run:
   - `base + frequency_count * (far_points * 430 + segment_count * 360 + 20)`;
   - the constants are calibrated against measured G5RV runs and are
     deliberately conservative.
2. Use a **9.5 MB** budget, below the 10 MB hard project limit and above the
   8 MB warning threshold. Runs near the warning are allowed; the existing save
   warning still applies.
3. Treat the user's selected pattern resolution as a **maximum**:
   - try the requested step and coarser steps only;
   - use the finest step that fits;
   - never choose a finer step than requested unless the user selects
     **Auto (max)**.
4. **Auto (max)** tries 1°, 2°, 5°, 10°, 15°, 20°, and 30°, finest first.
5. Preserve the frequency plan. Do not silently reduce the number of
   frequencies to make room for a pattern.
6. If even the coarsest candidate does not fit, disable the far-field request
   and keep the impedance/SWR sweep. Record a warning diagnostic.
7. Record an informational diagnostic when the pattern is coarsened from the
   requested step.
8. Expose the effective custom pattern step and estimated project size in the
   custom design panel.
9. Keep the solver's hard output error as a specific
   `solver.output_too_large` diagnostic for paths outside the main simulation
   flow.

## Consequences

Positive:

- The default G5RV configuration uses 41 frequencies and a 10° pattern, runs in
  under a second, and produces a project around 7.2 MB.
- Larger sweeps remain usable without a pattern.
- The user can request a finer pattern for a shorter sweep.
- Oversized runs fail less often and explain the adjustment when they do.

Limitations:

- The estimate is calibrated for the G5RV and may be conservative for other
  models.
- Runs above 8 MB still trigger the project save warning.
- The pattern may be coarser than the user selected; the diagnostics explain it.
- Optimization and synthesis dialogs use their own specs and are not all routed
  through the main-window budget. The specific solver error remains the safety
  net there.

## Follow-ups

- Split a wideband impedance/SWR run from a separate pattern run at selected
  frequencies.
- Add band-centered frequency plans instead of a dense linear sweep.
- Optionally exclude or compress raw solver output for large runs.
- Apply the same budget policy inside optimization and synthesis dialogs.
