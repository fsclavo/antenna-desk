# Phase A — Family optimizer foundation

- **Status:** Implemented 2026-11-07
- **Date:** 2026-11-07
- **Scope:** Foundation plus every first-class typed family
- **Related:** [ADR-0026](ADR/0026-family-optimizer-architecture.md)

> **Implementation note.** The original plan used four pilots. During
> implementation, disabling the other typed families or leaving their incomplete
> legacy paths exposed would have been a user-facing regression. Phase A was
> therefore widened to cover every family with a first-class typed parameter
> model. Magnetic loop, random wire, arbitrary custom/imported geometry, and the
> G5RV/ZS6BKW/Zepp/doublet custom generators remain explicitly unavailable.

## Goal

Replace the current split between the one-dimensional length optimizer and the
per-family coordinate search with a single family-driven optimization system.
Phase A establishes the contract, engine, registry, UI, and QA harness, and
migrates all first-class typed families. The four representative families used
for the initial design remain:

- wire dipole (simple continuous design space);
- vertical (mixed continuous/integer variables and optional loads);
- Yagi (high-dimensional array with constraints);
- half square / bobtail curtain (recent family and the source of the fallback
  bug).

At the end of Phase A no optimizer path may fall back to the basic dipole form.

## Non-goals

- Converting G5RV, ZS6BKW, Zepp, or doublet to typed parameters (Phase B).
- Band-aware, robust, or Pareto optimization (Phase C).
- Persisted optimization summaries (Phase C).
- Matching-network or transmission-line optimization (separate stage).
- Optimizer support for magnetic loop, random wire, custom, or imported
  geometry.

The unsupported families keep the Optimize action disabled with an explicit
reason. They do not use a temporary fallback. All first-class typed families are
migrated in this phase.

## Deliverables

### A1. Domain optimizer model

Proposed modules:

- `src/antennadesk/domain/optimization/variables.py`
- `src/antennadesk/domain/optimization/descriptor.py`
- `src/antennadesk/domain/optimization/constraints.py`
- `src/antennadesk/domain/optimization/engine.py`
- `src/antennadesk/domain/optimization/registry.py`
- `src/antennadesk/domain/optimization/families/`

Core types:

```text
OptimizationVariable
  name, label_key, group, unit
  kind: continuous | integer | choice
  minimum, maximum, step
  choices
  locked_by_default

ConstraintViolation
  name, severity, normalized_amount, message_key

AntennaOptimizerDescriptor
  key, variable tuple, builder, validator
  supported objectives, default objective
  start_points, budget profile
  supports_band_aware
  unavailable_reason

OptimizeAntennaCommand
  descriptor, base spec, parameters, objective, weights, soft constraints
  budget, seed, cancellation, progress callback

OptimizeAntennaResult
  status, best values, best parameters, best metrics
  evaluations, sensitivity, budget, seed, warnings
```

Requirements:

- no Qt, SciPy, solver, or project imports in the domain;
- deterministic and immutable result objects;
- clear distinction between hard and soft constraints;
- no generic parameter type dispatch outside the registry.

### A2. Hybrid engine

The engine implements:

1. variable normalization and bound repair;
2. initial population from the current design, published start points, and
   deterministic low-discrepancy sampling;
3. Differential Evolution over all active variables;
4. local pattern-search refinement from the best candidates;
5. feasibility-first ranking;
6. cancellation, evaluation cache, budget accounting, and stagnation stop;
7. sensitivity probes around the best feasible design.

The engine receives an evaluator callback. It does not know about antennas,
Qt, or NEC directly.

Required tests:

- sphere and Rosenbrock synthetic convergence;
- constrained optimum with a hard constraint;
- integer and discrete-choice variable handling;
- deterministic reproducibility with a fixed seed;
- cancellation at every stage;
- budget and auto-extension behavior;
- cache hit behavior;
- infeasible-only result handling.

### A3. Family registry and coverage tests

`OptimizerRegistry` returns either a descriptor or an explicit unavailable
reason. The registry covers canonical antenna types and legacy generator IDs.

Required global tests:

- every parameter type is registered or explicitly unavailable;
- every known `generator_id` is registered or explicitly unavailable;
- every field of every parameter dataclass is classified as optimized,
  context, derived, or topology;
- no UI or application optimizer code contains a family fallback.

The field-coverage test is the guard against future dimensions being added
without an optimizer update.

### A4. Application use case

Proposed module:

- `src/antennadesk/application/use_cases/optimize_antenna.py`

Responsibilities:

- resolve the descriptor and build the evaluation plan;
- rebuild the model and segmentation for every candidate;
- run the solver through the existing `AntennaSolver` port and cancellation
  token;
- aggregate metrics for the selected frequency mode;
- report solver failures without aborting the whole run;
- return a typed `OptimizationResult`.

The existing `RunSimulation` use case and solver boundary remain unchanged.

### A5. UI adapter registry

Proposed module:

- `src/antennadesk/ui/optimization_adapters.py`

Each adapter provides:

- the editor/form that can apply a parameter object;
- the simulation-spec builder;
- the label and helper text for the optimizer dialog.

The adapter registry is exhaustive and independently tested. `Apply Best`
must call the adapter, never `self._form.set_parameters()` directly.

### A6. Generic optimization dialog

Replace the current length-oriented dialog and the separate element dialog
with one family-driven dialog:

- variables grouped by geometry, feed, family loads, and conductor;
- every variable unlocked by default; locking marks the run as partial;
- topology shown read-only;
- supported objectives and weights;
- hard and soft constraints;
- budget profile and solver-run estimate;
- progress, best candidate, cancel;
- before/after table, sensitivity, warnings;
- Apply Best.

The dialog does not contain family-specific `isinstance` dispatch.

### A7. Family descriptors

#### Wire dipole

Variables:

- total wire length;
- height;
- conductor radius (lockable, unlocked by default).

Fixed context: orientation, azimuth, material, ground, frequency.

Constraints: positive length and height, radius bounds, minimum ground
clearance if the family requires it.

#### Vertical

Variables, depending on the selected topology:

- height;
- base height;
- radial length;
- radial count (integer);
- radial angle;
- loading-coil offset and inductance when the coil is enabled;
- top-hat radius and wire count (integer) when the top hat is enabled;
- conductor radius (lockable).

Fixed context: loading-coil resistance, material, ground, frequency, and
whether the coil/top hat exists.

Constraints: base and radial heights, coil offset within the radiator, top-hat
radius and count bounds, radial count bounds, positive dimensions.

#### Yagi

Variables:

- every element length;
- every inter-element gap;
- height;
- folded driven-element spacing when the driven element is folded;
- beta/hairpin match length and spacing when that match is selected;
- conductor radius only in advanced mode; otherwise fixed.

Fixed topology: element count, driven index, polarization, folded/straight,
match type.

Constraints: positive element lengths, monotonic positions, minimum gap,
minimum match spacing relative to conductor radius, positive heights.

#### SCV (half square / bobtail curtain)

Variables:

- overall horizontal span;
- vertical height;
- base height;
- feed offset below the top junction;
- conductor radius (lockable).

Fixed topology: half square versus bobtail curtain, azimuth, material, ground,
frequency.

Constraints: feed offset shorter than the vertical height, positive
dimensions, minimum top-to-bottom spacing, valid junction geometry.

The same explicit contract covers the other typed families: folded dipole,
loop, inverted-V, inverted-L, J Pole/Slim Jim, Ringo, OCFD, EndFed/EFHW/sloper,
fan dipole, trap dipole, T2FD, and Moxon.

### A8. Adapter and spec coverage

The following must be explicit and tested for every supported family:

- domain descriptor;
- editor/apply adapter;
- simulation spec builder;
- objective support list;
- unavailable reason `None`;
- `Apply Best` route.

No supported family may use `optimize_length`, `_form.simulation_spec()`, or
`_form.set_parameters()` as a fallback.

### A9. Tests

New or updated test areas:

- `tests/unit/optimization/test_engine.py`
- `tests/unit/optimization/test_descriptors.py`
- `tests/unit/optimization/test_registry.py`
- `tests/unit/application/test_optimize_antenna.py`
- `tests/ui/test_family_optimization_dialog.py`
- `tests/ui/test_main_window_optimization.py`
- `tests/integration/simulation/test_optimizer_families.py`

Coverage:

- synthetic engine convergence;
- descriptor field coverage;
- builder round-trip from current parameters;
- invalid geometry and constraint violations;
- deterministic seed;
- cancellation and budget;
- solver failure handling;
- single-frequency evaluation;
- Apply Best for the representative families and an exhaustive adapter test;
- NEC2C optimization smoke tests with a small budget;
- runtime benchmark for each pilot.

### A10. Documentation and gate

- ADR-0026 is the design source.
- This phase plan is updated with actual results.
- User guide explains the generic dialog, topology handling, locking, budget,
  and the unavailable reasons.
- `CHANGELOG.md` records the replacement of the fallback optimizer.
- `AGENTS.md` and `GEOMETRY_PRESENTATION.md` now require the future-family
  optimizer descriptor and QA, or an explicit unavailable reason.

Quality gate:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run mypy --config-file mypy_ui.ini
uv run pytest
```

## Sequencing

1. Domain variable/descriptor/constraint model and synthetic engine tests.
2. Registry, coverage tests, and unavailable-reason plumbing.
3. Application evaluation use case and fake-solver tests.
4. Pilot descriptors and unit tests.
5. UI adapter registry and generic dialog.
6. Main-window migration and removal of the old fallback paths.
7. NEC2C integration, benchmarks, and documentation.
8. Full gate and review.

Each step must leave the application runnable. During steps 1–5, unmigrated
families remain explicitly unavailable; they must not silently use an old
optimizer path.

## Acceptance criteria

Phase A is complete only when:

1. Every supported typed family exposes every agreed dimension in one joint
   search.
2. No optimizer path falls back to a basic dipole form or a generic primary
   dimension.
3. Every family action is either descriptor-backed or disabled with a visible
   reason.
4. Registry, adapter, and field-coverage tests pass for every supported family.
5. Engine synthetic tests, determinism tests, cancellation tests, and budget
   tests pass.
6. Apply Best routes to the correct editor through the exhaustive adapter.
7. NEC2C integration tests complete for representative families.
8. The Balanced profile is the default and auto-extension is observable in a
   test.
9. The full quality gate passes.
10. The user guide and changelog describe the new behavior and limitations.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Optimization becomes much slower | Budget profile, time estimate, cancellation, caching, and explicit solver-run count |
| DE is poorly tuned | Synthetic convergence tests and adaptive population settings |
| Descriptor closures duplicate family logic | Shared descriptor factories and field-coverage tests |
| UI dispatch regresses to fallbacks | Exhaustive adapter registry and a test that forbids `_form` fallback in optimizer paths |
| Existing tests depend on removed optimizers | Update tests to expect explicit unavailable reasons, not hidden fallbacks |
| Solver failures abort a run | Per-candidate error capture; continue until failure threshold |
| High-dimensional Yagi is expensive | Joint DE with adaptive population; local refinement; budget visible to the user |

## Out of scope for Phase A

- Band-aware, robust, Pareto, and persisted optimization summaries.
- Matching-network and transmission-line optimization.
- Typed G5RV, ZS6BKW, Zepp, and doublet models.
- Magnetic-loop, random-wire, custom, or imported optimizers.

## Verification (2026-11-07)

- `ruff check .` and `ruff format --check .` pass.
- `mypy` passes for 147 source files; `mypy --config-file mypy_ui.ini` passes
  for 93 UI files.
- Full suite: **1610 passed, 1 skipped**. The skip is the PyNEC cross-engine
  comparison because PyNEC is not installed.
- NEC2C family-optimizer smoke tests: **8 passed** across dipole, vertical,
  inverted-V, loop, EndFed, SCV, Yagi, and Moxon.
- New coverage includes engine convergence, determinism, constraints,
  cancellation, budget formulas, registry and field coverage, adapter
  exhaustiveness, descriptor round-trips, dialog execution, Apply Best routing,
  and a real NEC2C run for representative families.
- Unsupported optimizers are explicit: magnetic loop, random wire, arbitrary
  custom/imported geometry, and G5RV/ZS6BKW/Zepp/doublet custom generators.

## Definition of done for Phase A

- Every supported typed family has a complete descriptor, adapter, spec, tests,
  and documentation.
- The old fallback path is removed.
- All other families are explicitly unavailable with a reason.
- The engine is deterministic, cancellable, bounded, and cached.
- The Phase A benchmark and full gate are recorded in this document.
