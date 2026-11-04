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
5. Add an **Estimate Dimensions** dialog that estimates, displays assumptions,
   and applies the parameters to the current design without changing its
   template or antenna family. The caller passes the current parameters; the
   dialog preselects the family and preloads its fields.
6. Keep refinement separate: after applying, users can open the existing
   optimizer, Yagi optimizer, or impedance synthesis. The dialog offers an
   optional one-step handoff when a solver is configured.
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
- Yagi (2–32 elements from the DL6WU trimming reference);
- Moxon (Cebik reference scaled by frequency);
- T2FD (Cebik wide-long broadband starting dimensions; lowest and highest
  design frequencies required).

Explicitly unsupported:

- arbitrary custom geometry;
- Yagi element counts outside 2–32 until additional published tables are
  added.

## Alternatives considered

- **One universal formula.** Rejected: it would be wrong for most families.
- **Only solver-based synthesis.** Rejected as the first step: too slow for a
  quick starting point and not available for all families.
- **Persist estimator provenance immediately.** Deferred to avoid a schema
  change in the first milestone.
- **Invent approximations for arbitrary Yagi/Moxon designs.** Rejected:
  unsupported cases must be explicit.

## Amendment 2026-11-04 — estimate only the current template

The dialog originally offered a free family selector and defaulted to a wire
dipole. That made it possible to replace a Ringo or another loaded template
without an explicit template change.

The dialog now receives an `AntennaDesignParameters` instance and derives its
estimator from `estimator_type_for()`. It has no family selector and enforces
that the result keeps the same `antenna_type`. The main window also rejects any
result that changes the template and preserves template-identifying fields such
as the end-fed preset, OCFD feed ratio/transformer, J-Pole folded/gap, Ringo
ring sides, and Yagi driven index. A loaded vertical, arbitrary custom geometry,
or a template without a registered estimator is not eligible; the action is
disabled and explains why.

## Consequences

Positive:

- A user can start from frequency instead of measured dimensions.
- Estimates are fast, deterministic, testable, and traceable.
- The existing optimizer/synthesis remains the numerical refinement path.
- New families get a clear contract.

Limitations:

- Estimates are starting points, not validated construction dimensions.
- Yagi support is limited to the 2–32 element DL6WU trimming reference.
- Ringo and Moxon use scaled presets.
- Height, ground, and matching effects require simulation or measurement.
- Editing a design clears its estimator provenance; re-estimate or refine it
  deliberately.
