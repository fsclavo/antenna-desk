# ADR-0013 — Frequency-first dimension estimation

- **Status:** Accepted
- **Date:** 2026-10-31
- **Supersedes:** none

## Context

AntennaDesk required users to know the initial dimensions of every antenna.
That is useful for experienced builders but mismatches the main amateur-radio
use case: start from a frequency and a design intent, then adjust.

A single formula cannot define an “ideal” antenna. Height, ground, wire
diameter, insulation, nearby objects, matching, and the desired gain/bandwidth
all matter. The application therefore needs a traceable starting estimate and
an optional numerical refinement.

## Decision

1. Add a pure-domain `DesignIntent` and `DimensionEstimate` model.
2. Register one estimator per antenna type in `domain/design/estimators.py`.
3. Return a valid `AntennaDesignParameters` plus:
   - method id;
   - confidence level;
   - assumptions and warnings;
   - dimension tolerance;
   - source identifiers;
   - display rows.
4. Expose the estimators through the `EstimateAntennaDimensions` application
   use case.
5. Add a **Design from Frequency** dialog that estimates, displays assumptions,
   and applies the parameters to the current design.
6. Keep refinement separate: after applying, users use the existing optimizer,
   Yagi optimizer, or impedance synthesis.
7. Use only sourced or explicitly labelled heuristic factors. Do not invent
   numerical reference values.
8. Persist estimator provenance as optional design metadata in the existing
   schema. Older projects without provenance remain valid.

## Initial family coverage

Supported:

- wire dipole;
- folded dipole;
- loop, quad, delta;
- vertical 1/4 and 5/8;
- inverted-V;
- fan dipole;
- end-fed;
- OCFD;
- J Pole and Slim Jim;
- Ringo (heuristic preset);
- Yagi (NBS five-element reference);
- Moxon (Cebik reference scaled by frequency).

Explicitly unsupported:

- arbitrary custom geometry;
- Yagi element counts other than the five-element NBS reference until
  published tables are added.

## Alternatives considered

- **One universal formula.** Rejected: it would be wrong for most families.
- **Only solver-based synthesis.** Rejected as the first step: too slow for a
  quick starting point and not available for all families.
- **Persist estimator provenance immediately.** Deferred to avoid a schema
  change in the first milestone.
- **Invent approximations for arbitrary Yagi/Moxon designs.** Rejected:
  unsupported cases must be explicit.

## Consequences

Positive:

- A user can start from frequency instead of measured dimensions.
- Estimates are fast, deterministic, testable, and traceable.
- The existing optimizer/synthesis remains the numerical refinement path.
- New families get a clear contract.

Limitations:

- Estimates are starting points, not validated construction dimensions.
- Yagi support is limited to the reference preset in this milestone.
- Ringo and Moxon use scaled presets.
- Height, ground, and matching effects require simulation or measurement.
- Editing a design clears its estimator provenance; re-estimate or refine it
  deliberately.
