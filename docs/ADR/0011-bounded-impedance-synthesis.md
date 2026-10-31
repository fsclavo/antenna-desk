# ADR-0011 — Bounded feed-point impedance synthesis

- **Status:** Accepted
- **Date:** 2026-10-30
- **Supersedes:** none

## Context

Users asked for a way to start from a target frequency and feed-point impedance
instead of adjusting dimensions by trial and error. A full inverse solver is
not justified yet: it would need a robust optimizer, careful handling of
non-unique geometries, and independent validation for every supported template.

The first supported families are the OCFD, J Pole, and Slim Jim. Each has two
useful knobs:

- OCFD: total wire length and feed ratio.
- J Pole: radiator height and feed-offset position.
- Slim Jim: radiator height and stub length.

## Decision

1. Implement synthesis as a bounded two-variable grid search in the domain,
   independent of Qt and the solver adapter.
2. Evaluate each candidate at a single target frequency with the far field
   disabled.
3. Rank candidates by the absolute complex impedance error against the target
   `R + jX`.
4. Expose the search in a dialog that shows every evaluation, the best result,
   and its residual error.
5. Apply the best dimensions to the normal design form and run the usual full
   sweep for validation.
6. Label the result as a numerical starting point, not a validated design.

## Consequences

Positive:

- The feature is deterministic, bounded, and easy to test with analytical
  solvers.
- It does not add a new dependency or bypass the canonical model.
- Users can see when a target is not reachable and adjust the bounds.

Limitations:

- The grid can miss a narrow optimum; it is a starting point, not a global
  inverse solver.
- Only two variables are searched per template.
- A target impedance may be physically unreachable; the dialog reports the
  closest candidate and its error.
- Results remain experimental until an independent reference or measurement is
  available.
