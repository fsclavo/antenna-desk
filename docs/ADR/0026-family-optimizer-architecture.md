# ADR-0026 — Family optimizer descriptors on a shared hybrid engine

- **Status:** Accepted
- **Date:** 2026-11-07
- **Deciders:** Fernando Sclavo, development
- **Phase:** Optimization redesign
- **Related:** [ADR-0011](0011-bounded-impedance-synthesis.md) remains the
  separate bounded impedance-synthesis feature

## Context

AntennaDesk currently exposes several optimization paths:

- a generic one-dimensional length search over
  `primary_dimension_m()`/`with_primary_dimension()`;
- per-family element optimizers built on a bounded coordinate search;
- bounded impedance synthesis for OCFD, J Pole, and Slim Jim.

This split has three problems.

1. **The search is not joint.** `optimize_bounded()` moves one variable at a
   time with a small number of samples. It captures interactions poorly:
   element length versus spacing, vertical height versus radial system, SCV
   horizontal span versus vertical height, or Yagi geometry versus height.

2. **The design vector is incomplete.** Several families expose only a subset
   of their dimensions. Examples: the Yagi optimizer does not expose height or
   matching hardware; the vertical optimizer does not expose base height, top
   hat, or loading-coil position; the inverted-V optimizer does not expose apex
   height or included angle; the SCV path exposes only the horizontal span.

3. **Dispatch is open-ended.** The generic length optimizer falls back to the
   basic dipole form for both its simulation spec and the Apply Best target.
   That produced the `ScvParameters` failure. The error was a UI write-back
   bug, but its cause was an `else: self._form` fallback that allowed a new
   family to run with an incomplete contract.

The catalog also contains G5RV, ZS6BKW, Zepp, and doublet designs represented
as `CustomAntennaParameters` with a `generator_id`. A family cannot have a
robust optimizer while its dimensions exist only as arbitrary wire geometry.

The agreed requirements are:

- every family has its own optimizer contract;
- no generic fallback;
- if a trustworthy optimizer is not possible, the family has no optimizer;
- all geometry, feed, and family-load dimensions are searched jointly;
- the user chooses topology;
- more iterations are acceptable when they improve the result;
- future families must include optimizer QA in their definition of done.

## Decision

### 1. One descriptor per family, one shared engine

Each optimizable family registers an `AntennaOptimizerDescriptor`:

```text
AntennaOptimizerDescriptor
  key
  variables
  build_parameters(values)
  validate(values)
  objectives
  default_objective
  start_points(current_parameters)
  budget_profile
  supports_band_aware
  unavailable_reason
```

The descriptor owns the family-specific design space, constraints, parameter
builder, supported objectives, and default starting points. The search engine
is shared.

A family either has a descriptor or an explicit unavailable reason. There is
no implicit fallback, no "use the dipole form", and no generic primary-dimension
path for an unregistered family.

### 2. Exhaustive registries

Three registrations are mandatory and independently tested:

- domain optimizer descriptor;
- UI editor/apply-Best adapter;
- simulation-spec builder.

The domain registry is keyed by the canonical `antenna_type` and by legacy
`generator_id` values where they still exist. A test enumerates every supported
parameter type and every known generator identifier and fails when one lacks a
descriptor or an explicit unavailable reason.

A second coverage test introspects each parameter dataclass and classifies
every field as one of:

- optimized;
- design context;
- derived;
- topology.

Adding a new field without updating the optimizer contract must fail the test.

### 3. Optimization scope

The optimizer searches:

- geometry: lengths, heights, separations, diameters, gaps, angles, offsets;
- feed dimensions: feed height and feed offset;
- family loads: loading coil, top hat, T2FD termination, ideal transformers,
  counterpoise, and match hardware exposed by the family;
- integer geometric counts: radial count and top-hat wire count;
- conductor radius as a lockable design variable; per-element Yagi radii are
  fixed unless an advanced conductor mode is enabled.

The optimizer does not search by default:

- design frequency or analysis band plan;
- ground model;
- conductor material;
- azimuth or pointing direction;
- parasitic component values such as capacitor ESR or coil Q;
- arbitrary custom wire geometry.

Ground, frequency, material, and pointing remain context. They may appear in
sensitivity analysis, but they are not silently optimized to manufacture a
better score.

### 4. Topology is user-selected

The following are topology, not optimizer variables:

- SCV variant;
- Yagi element count;
- folded or straight elements;
- polarization and orientation;
- match type;
- loop side count;
- EndFed preset;
- enabled/disabled top hat, loading coil, or radial system.

The optimizer searches the dimensions of the selected topology. Comparing
topologies means duplicating the variant and optimizing each separately. The
optimizer must not silently change the family or wire graph.

### 5. Hybrid deterministic engine

The shared engine has four stages:

1. Normalize continuous, integer, and discrete-choice variables to a common
   bounded representation and repair invalid candidates.
2. Run Differential Evolution over all variables jointly.
3. Refine the best three to five candidates with a bounded local pattern
   search.
4. Run sensitivity, tolerance, and constraint analysis around the best result.

The engine is pure Python, deterministic with a fixed seed, and independent of
Qt, SciPy, and solver adapters. Invalid geometry never reaches the solver.

The population is adapted to the number of active variables. Initialization
includes the current design, any published starting points, and deterministic
low-discrepancy sampling.

### 6. Budget and stopping

The budget is expressed in solver evaluations, not wall-clock time. For `n`
active variables:

| Profile | Global exploration | Local refinement |
|---|---:|---:|
| Fast | `max(60, 12n)` | `max(40, 8n)` |
| Balanced | `max(120, 30n)` | `max(80, 20n)` |
| Thorough | `max(300, 80n)` | `max(200, 40n)` |

Balanced is the default. If the best score improves during the final 20% of the
budget, the run extends by 25%, up to a maximum of twice the initial budget.

The search stops on budget exhaustion, stagnation, population convergence, or
a normalized step below `1e-4`. Cancellation is checked between evaluations.

The UI shows both candidate count and total solver runs. In band-aware mode,
each frequency is a separate solver run.

### 7. Constraints and objectives

Hard constraints include valid geometry, minimum conductor spacing, element
ordering, feed inside the conductor, positive dimensions, family-specific
bounds such as feed offset shorter than the fed element, an optional maximum
turning radius, and an optional maximum boom length for Yagi/Moxon arrays. The
turning radius is measured from the boom midpoint for arrays and from the feed's
horizontal projection for other families. An infeasible design can never become
the best result.

Soft constraints include maximum SWR, minimum gain, minimum efficiency, minimum
front-to-back ratio, and minimum bandwidth. They are normalized penalties.

Supported objectives:

- target complex impedance `R + jX`;
- minimum SWR;
- maximum gain;
- maximum front-to-back ratio;
- maximum efficiency;
- maximum bandwidth;
- normalized weighted multi-objective score. For the weighted mode, gain is
  normalized by 3 dB, front-to-back by 10 dB, SWR by `max(SWR - 1, 0)`, and
  efficiency by its fraction, so the user weights are comparable.

Feasibility is ranked before score. If no feasible candidate exists, the run
reports the best violation and does not offer Apply Best.

### 8. Frequency modes

The default is a single design frequency. Optional modes are:

- band-aware: center and edges, or the project's band plan;
- robust: several frequencies plus manufacturing tolerances, with a variance
  penalty.

Band-aware and robust modes are explicit because they multiply the number of
solver runs.

### 9. UI contract

A single family-driven optimization dialog replaces the length-oriented and
element-oriented dialogs:

- all variables, grouped by geometry, feed, family loads, and conductor;
- current value, bounds, step, unit, and lock control;
- topology shown read-only;
- objective, weights, and constraints;
- budget profile, evaluation estimate, and time estimate;
- progress, best candidate, cancellation;
- before/after table, sensitivity, warnings, and recommendations;
- Apply Best routed through an exhaustive UI adapter registry.

Locking a variable is allowed, but the dialog must label the run as partial.
The optimization action is disabled with a reason when no descriptor exists.

### 10. Persistence and reproducibility

Each applied optimization result persists a compact summary, not every
evaluation. A run that the user discards leaves the design and its previous
summary unchanged:

- method and version;
- seed;
- objective, weights, and constraints;
- budget profile;
- evaluation count;
- status;
- best design vector and metrics;
- timestamp.

The full evaluation log may be exported to CSV but is not embedded in the
project.

### 11. QA and definition of done

Every new family must include, in the same change:

- optimizer descriptor and variable/field coverage;
- constraints and builder;
- supported objectives;
- synthetic convergence tests;
- determinism and cancellation tests;
- invalid-geometry tests;
- NEC2C integration;
- Apply Best UI test;
- performance benchmark;
- evidence and limitations.

Global tests enforce registry completeness and the absence of fallbacks.

### 12. Family availability

Optimizable families:

- wire dipole, folded dipole, loop;
- vertical, inverted-V, inverted-L;
- J Pole and Slim Jim;
- Ringo;
- half square and bobtail curtain;
- biquad and double biquad;
- Beverage receiving wire;
- loaded / linked dipole;
- OCFD, EndFed/EFHW/sloper;
- fan dipole, trap dipole, T2FD;
- Yagi, Moxon;
- typed G5RV, ZS6BKW, and Zepp; the doublet radiator uses the dipole descriptor.

Explicitly unavailable:

- magnetic loop: the ideal tuning capacitor and ESR model are not accurate
  enough to optimize efficiency or bandwidth without risking false precision;
- random wire: deliberately non-resonant and tuner-assisted;
- arbitrary custom geometry and imported designs: topology is not parameterized;
- any future family without a descriptor and QA.

### 13. Matching is a second stage

Geometry and feed optimization runs first. Matching-network and transmission-
line optimization is a separate stage that acts on the chosen antenna. An
ideal matching network must not hide a poor geometry inside the geometry score.

### 14. Custom generator families

G5RV, ZS6BKW, and Zepp are first-class typed parameter models (completed
2026-11-07). The doublet is a typed dipole plus a project-level feed line.
Optimizer adapters over arbitrary `CustomAntennaParameters` are not accepted as
a long-term solution.

## Consequences

### Positive

- Every optimizable family has an explicit, testable contract.
- The search handles interactions instead of tuning one dimension at a time.
- The same bug class that produced the `ScvParameters` failure becomes a
  registry-test failure.
- Users can see which dimensions are optimized, which are context, and why a
  family has no optimizer.
- Future families cannot silently ship with an incomplete optimizer.

### Negative

- Optimization becomes slower. Balanced and Thorough profiles deliberately
  spend more solver calls.
- The generic dialog and the engine are a substantial new subsystem.
- Some families temporarily lose the Optimize action during migration; they
  must show an explicit reason instead of falling back.
- Magnetic loop and random wire will remain without an optimizer.

### Neutral

- Bounded impedance synthesis remains a separate feature.
- Matching-network optimization remains a separate stage.
- The canonical wire model and solver adapter boundaries are unchanged.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| A separate algorithm per family | Duplicated code, inconsistent QA, unmaintainable |
| Keep coordinate search | Captures interactions poorly and exposes incomplete vectors |
| Keep a generic dipole fallback | Caused the SCV bug and hides incomplete family contracts |
| Use SciPy | Adds a dependency and violates the domain boundary |
| Optimize frequency, ground, and material too | Optimizes context instead of the antenna and can hide bad assumptions |
| Let the optimizer choose topology | Combinatorial growth and silently changes the user's design |
| Give every family an optimizer even when the model is weak | False precision; conflicts with the evidence policy |

## Implementation phases

1. **Phase A — foundation and typed families (completed 2026-11-07):**
   descriptor, registry, hybrid engine, generic dialog, and optimizers for every
   first-class typed family. The four initial pilots were dipole, vertical,
   Yagi, and SCV; the amendment above records the widened coverage. The generic
   fallback is removed and unsupported families carry explicit reasons.
2. **Phase B — custom-generator conversion (completed 2026-11-07):** G5RV,
   ZS6BKW, and Zepp became typed parameter models with optimizers. The doublet
   was already typed as a dipole plus a project-level feed line.
3. **Phase C — advanced quality (completed 2026-11-07):** band-aware and
   robust modes, Pareto front, persisted optimization summaries, and
   recommendations. See `OPTIMIZER_PHASE_C_PLAN.md`.
4. **Phase D — permanent policy (completed 2026-11-07):** the new-family
   checklist in `AGENTS.md` and `GEOMETRY_PRESENTATION.md` now requires the
   optimizer descriptor and QA, or an explicit unavailable reason.

## Amendment 2026-11-07 — Phase A coverage

The original Phase A boundary was four pilots. During implementation it became
clear that leaving the other first-class typed families on the old incomplete
paths, or disabling them, would be a user-facing regression. Phase A therefore
migrated every typed family with a first-class parameter model:

- dipole and folded dipole;
- loop;
- vertical, inverted-V, inverted-L;
- J Pole and Slim Jim;
- Ringo;
- half square and bobtail curtain;
- biquad and double biquad;
- Beverage receiving wire;
- loaded / linked dipole;
- OCFD, EndFed/EFHW/sloper;
- fan dipole, trap dipole, T2FD;
- Yagi and Moxon.

Phase B was completed on 2026-11-07: G5RV, ZS6BKW, and Zepp now have typed
parameter models, inline editors, persistence, reports, and family optimizers.
The doublet was already a typed dipole plus a project-level feed line, and its
radiator uses the dipole optimizer.

Phase C was completed on 2026-11-07. Band-aware mode evaluates every listed
band edge and aggregates worst-case metrics. Robust mode evaluates nominal and
± dimensional-tolerance corners and adds a variance penalty. The result exposes
a descriptive Pareto front over shared metrics, deterministic recommendations,
and a compact summary persisted with the design (schema version 18).

The following remain explicitly unavailable:

- magnetic loop;
- random wire;
- arbitrary custom geometry and imported designs.

## Follow-up

- See [OPTIMIZER_PHASE_A_PLAN.md](../OPTIMIZER_PHASE_A_PLAN.md) and
  [OPTIMIZER_PHASE_C_PLAN.md](../OPTIMIZER_PHASE_C_PLAN.md) for the detailed
  implementation records and acceptance criteria.
- Do not add a new antenna family without an optimizer descriptor or an explicit
  unavailable reason and its tests.
- Revisit magnetic-loop optimization only after a more trustworthy capacitor
  and loss model exists.
