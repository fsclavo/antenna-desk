# Historical backlog — optimizer and high frequency

> **Historical design notes, captured 2026-11-20.** Not current
> guidance. Current status: [`../../STATUS.md`](../../STATUS.md); active
> queue: [`../../AUTONOMOUS_BACKLOG.md`](../../AUTONOMOUS_BACKLOG.md).

## High-frequency optimizer bounds and Moxon gap (design note, 2026-11-18)

**Status:** HF1–HF10 are implemented on 2026-11-18;
[ADR-0046](../../ADR/0046-frequency-aware-optimizer-bounds.md) is the accepted
contract. The high-frequency bounds and Moxon-gap track is complete.

**Related:** [ADR-0026](../../ADR/0026-family-optimizer-architecture.md),
[ADR-0043](../../ADR/0043-design-versus-analysis-frequency.md),
[ADR-0044](../../ADR/0044-adaptive-length-display-units.md), and
[`ANTENNA_DESIGN_ESTIMATORS.md`](../../ANTENNA_DESIGN_ESTIMATORS.md).

**Trigger:** a user-visible inconsistency in the family optimizers at VHF/UHF.
The first confirmed case is a 2.4 GHz Moxon whose optimized tip gap is tens of
millimetres, far outside a plausible Moxon rectangle. The same bound pattern
exists in other families.

**Evidence:** reproduced with the real NEC2C adapter and the domain/application
optimizer. At 2.4 GHz the reference-scaled Moxon starts at width 44.99 mm,
depth 17.22 mm, tip gap 1.296 mm, but the optimizer bounds are
`width=[100, 101] mm` and `depth=[100, 101] mm`. The resulting gap is
76.1–93.0 mm (0.61–0.74 λ) for every feasible candidate. A production
`MULTI_OBJECTIVE` run returned gap 86.96 mm, SWR 15.50, 4.19 dBi, and 2.11 dB
front-to-back. An in-memory control that changed only the bounds to relative
values returned gap 4.86 mm, SWR 1.05, 6.06 dBi, and 25.06 dB front-to-back.
The control is exploratory and is **not** a numerical reference. The 1.5 GHz
case is the same: 2.07 mm reference gap versus a 61.8–88.3 mm optimizer range.

The root cause is the absolute length policy in the descriptors:

- `_length()` defaults to `minimum=0.1` m and `_length`/`around` treats that
  floor as the lower search bound, not as a physical constraint.
- When `value * (1 + fraction) <= minimum`, `around()` returns a degenerate
  interval above the current design (`high = low + 1 mm`).
- `OptimizationVariable.to_fraction()` silently clamps the current value into
  that interval; the engine evaluates the clamped design, not the editor
  design.
- The Moxon validator only checks `reflector_tip + driven_tip < depth`; a
  0.67 λ gap is feasible.
- Yagi element lengths have an absolute 0.05 m floor, which starts clamping
  15+ element arrays at 2.4 GHz and every element at 5.8 GHz.
- Many other families have absolute 0.1 m or 0.5 m floors and show the same
  behavior at 1.5/2.4 GHz.

### HF1 — Bound contract (accepted)

[ADR-0046](../../ADR/0046-frequency-aware-optimizer-bounds.md) is the accepted
contract. It defines:

- the difference between a **physical/construction floor** (a real minimum for
  a buildable design) and a **search bound** (the interval the optimizer may
  explore around the current design);
- how search bounds are derived from the current value and/or
  `wavelength_m(parameters.frequency_hz)`, including a minimum non-degenerate
  span;
- the invariant `variable.minimum <= initial_value <= variable.maximum` and a
  second invariant that rejects a degenerate span;
- whether an out-of-bounds or unsupported design produces an
  `OptimizerAvailability` reason with a translated key or a typed hard error,
  and the user-facing message;
- why the current design must never be silently clamped;
- the Moxon gap contract (direct `gap_m` variable versus derived gap, the
  allowed gap/λ, gap/radius, and gap/depth/width ranges, and how the Cebik
  14.17 MHz reference remains exact);
- the high-frequency validity policy for the Moxon linear scaling and the
  Yagi reference, including confidence and tolerance downgrades;
- the thin-wire kernel/segmentation policy and which warnings are hard;
- the no-invented-reference rule: high-frequency checks use invariants,
  published references, or measurements; they do not turn an exploratory
  control into a golden value.

ADR-0046 explicitly rejects a blanket `minimum=0` change. Removing every
construction floor would restore the search interval but could produce
unbuildable HF designs; the two concepts must stay separate.

### HF2 — Descriptor invariant and no silent clamp

**Implemented 2026-11-18.** `AntennaOptimizerDescriptor` validates its default
search scope in the constructor. `OptimizerAvailability` carries a translated
reason plus the family, variable, value, and bounds; the optimizer dialog checks
the selected variables again when the user unlocks a default-locked one. The
engine validates the active initial values and start points and returns
`OptimizationStatus.ERROR` without evaluating a clamped design. Locked
variables remain context and are exempt. The numerical span floor is 1 µm for
length/radius units and a smaller unit-relative floor for F, H, ratios, angles,
and counts. Tests cover Moxon 2.4 GHz, vertical 2.4 GHz, Yagi 5.8 GHz, the valid
Cebik 20 m Moxon, engine guards, the use case, and the UI message.

Implementation requirements:

- Add a shared descriptor validation helper or constructor check that rejects
  an initial value outside its variable bounds, a non-finite value, or a
  degenerate span.
- Surface the failure through the existing optimizer availability/error path
  with the family, variable, current value, and bounds. The UI must show it
  before starting a solver run.
- Change `optimize_design()` so the first candidate is the actual current
  design. If an active variable is outside bounds, do not clamp it; fail the
  run with a clear status/message.
- Preserve the existing behavior for intentionally locked variables: locked
  variables are context and must remain at their initial values.
- Add tests that would fail on the old code for Moxon 2.4 GHz, vertical
  2.4 GHz, and Yagi 5.8 GHz, plus a valid HF case that still converges.
- No solver or schema change.

### HF3 — Frequency-aware bounds across families

**Implemented 2026-11-18.** The shared `around()` keeps the interval relative to
the current value; `_length()` defaults to a 1 µm numerical floor and computes
its step from the search span. Practical 0.1/0.5/0.05 m floors were removed from
the descriptors. Gaps, spacings, tips, and discone dimensions use a
conductor-clearance floor; heights/base planes use zero; the end-fed
feed-section structure and the biquad small-feature minima remain. A matrix at
1.8/14/144/2400/5800 MHz covers every supported optimizer family and verifies
that initial values stay inside their bounds and that steps do not exceed the
span. Genuine physical-floor
violations still return the HF2 unavailable reason; no family-specific
frequency envelope was invented without evidence.

At minimum:

- `_length()` and `around()` gain an explicit, tested policy for a physical
  floor versus a search interval.
- Every `OptimizationVariable` length uses relative bounds or a λ-scaled
  floor; steps are also normalized where they are exposed in the UI.
- Families with a published normalized design (Yagi, Moxon, quad, hexbeam,
  discone, vertical, J-pole, Ringo) derive their search ranges from the
  design's normalized dimensions and the current frequency.
- Families that are not meaningful at a frequency return an explicit
  unavailable reason rather than a clamped search range. The decision is
  recorded in HF1; do not invent frequency envelopes without evidence.
- The biquad remains the reference for small-feature minima; do not regress
  its 0.01 m/0.001 m behavior.
- Cover all registry families in the matrix; a family is not exempt because
  it is usually HF-only. If it remains available at 2.4 GHz, it must either
  produce a sane bound set or explicitly say it is unsupported.
- No schema change.

### HF4 — Moxon geometry and optimizer contract

**Implemented 2026-11-18.** The shared validator is
`validate_moxon_geometry()` in `domain/antennas/moxon.py`. The optimizer now
uses `width_m`, `depth_m`, `gap_m`, `reflector_tip_m`, `height_m`, and the
conductor radius; the driven tip is derived. The geometry envelope is:

- gap/λ 0.004–0.10;
- gap/depth 0.03–0.40;
- gap/width 0.01–0.15;
- width/depth 1.5–4.5;
- reflector-tip/depth and driven-tip/depth 0.20–0.75;
- tip-sum/depth 0.50–0.97;
- gap greater than one conductor diameter.

These are construction-validity limits anchored to the Cebik 20 m reference
(gap/λ 0.0104, gap/depth 0.075, gap/width 0.029) and the exploratory 2.4 GHz
control (gap/λ 0.039, gap/depth 0.282, gap/width 0.108). They are not
performance values and do not encode the control's 4.86 mm gap. The domain
constructor, optimizer validation, and editor warning share the same function;
a 0.67λ gap is rejected before optimization. The estimator scales the Cebik gap
directly; HF6 adds a radius-aware two-diameter starting clearance and a
high-frequency confidence/tolerance policy, so an unbuildable thin-wire gap is
reported explicitly rather than silently changing the wire radius.

Requirements:

- Make the gap a first-class part of the Moxon optimizer contract. Either
  expose `gap_m` directly and derive the tips, or keep the current fields but
  enforce a documented relationship so the optimizer cannot independently
  move two redundant tip lengths into an implausible geometry.
- Add a shared Moxon geometry validator used by the domain, descriptor, and
  UI. It must check:
  - `gap_m > 0` (existing);
  - a documented minimum clearance relative to `wire_radius_m`;
  - a documented gap/λ range;
  - documented width/depth and tip/depth proportions;
  - the published 14.17 MHz reference dimensions still pass exactly.
- Do not hard-code the exploratory 4.86 mm or 7.27 mm values. The limits must
  be justified by the reference geometry, the thin-wire model, or a traceable
  source, and the ADR must state the evidence level.
- Ensure a 0.67 λ gap is rejected or reported as an invalid Moxon, not
  silently optimized.
- Add tests at 14.17 MHz (exact reference), 28.5 MHz, 144 MHz, 435 MHz,
  1.5 GHz, and 2.4 GHz. The high-frequency tests assert invariants and
  completion, not an invented performance target.
- No schema migration unless a new persisted field is unavoidable; prefer
  keeping the current `MoxonParameters` fields and changing only the
  optimizer variables/validation.

### HF5 — Yagi wavelength-relative bounds

**Implemented 2026-11-18.** The descriptor already used relative bounds after
HF3; HF5 removes the last absolute 0.05 m element floor and adds the missing
high-element-count QA. Element lengths, inter-element gaps, height, folded
spacing, and beta-hairpin dimensions are relative to the current scaled design;
conductor-spacing minima use the actual element radius. A 15-case matrix covers
5/10/15/20/32 elements at 1.5/2.4/5.8 GHz and asserts initial-in-bounds, the
DL6WU length/gap taper constraints, span-normalized steps, and exact rebuild.
Real NEC2C smoke runs cover 2.4 GHz 15/32 elements and 5.8 GHz 5/15 elements;
they assert completion, finite R/X, and no error, not a published gain.

Requirements:

- Remove the absolute 0.05 m element-length floor and the 0.01 m search
  steps from the Yagi descriptor; derive element/gap/height bounds from the
  current normalized design and λ.
- Keep the existing director length/gap taper constraints and the minimum
  conductor spacing; make the minimum spacing relative to the actual radius.
- Verify the DL6WU starting design for 5, 10, 15, 20, and 32 elements at
  1.5, 2.4, and 5.8 GHz: every initial value is inside its bounds, the taper
  constraints still pass, and the initial design rebuilds exactly.
- Add real NEC2C smoke coverage for 2.4 GHz 15/32 elements and 5.8 GHz 5/15
  elements. The test asserts completion, finite R/X, and no error; it does
  not claim a published gain.
- Check folded and beta/hairpin variables at high frequency; their minima
  remain tied to the conductor radius.
- No solver or schema change.

### HF6 — Moxon high-frequency estimator

**Implemented 2026-11-18.** The Cebik 20 m reference is reference-scaled only
inside the 20 m amateur band (14.0–14.35 MHz). Outside that band the estimate is
`Confidence.HEURISTIC`, carries `estimator.assumption.moxon_extrapolation`, and
emits `estimator.warning.moxon_high_frequency`. Its tolerance is
`max(5% width, gap)`, so it is never smaller than the gap. The wire radius is
not scaled; the starting gap must clear two conductor diameters or the estimate
is explicitly unsupported. The 14.17 MHz reference remains exact, the 28.5 MHz
editor default remains heuristic, and no high-frequency published reference was
invented.

Requirements:

- State the validated range of the Cebik 20 m linear scaling in
  `ANTENNA_DESIGN_ESTIMATORS.md` and the ADR. If no independent source exists
  for 1.5/2.4 GHz, the result is a heuristic, not a reference-scaled design.
- Make the starting geometry radius-aware. At minimum, detect when the scaled
  gap is smaller than a documented multiple of the wire diameter and either
  raise `UnsupportedEstimateError` or return a clearly labelled experimental
  estimate with a starting gap adjustment derived from a documented rule.
- Do not leave `REFERENCE_SCALED` confidence and a tolerance smaller than the
  gap for an extrapolation that is not validated. Downgrade confidence and
  make the tolerance meaningful.
- Add a strong EN/ES warning that the wire radius is not scaled and that the
  high-frequency Moxon needs independent verification; explain the
  construction implication when the gap is comparable to the conductor
  diameter.
- Keep 14.17 MHz exact and keep the 28.5 MHz editor default a documented
  heuristic.
- Do not invent a 2.4 GHz published reference. If a traceable source or
  measurement is added later, record it separately.

### HF7 — Thin-wire model-quality gate

**Implemented 2026-11-18.** `resolve_model_quality()` is the shared policy:

- Short wires whose segment/radius ratio is below 8 reduce their segment count
  when the resulting segment is still at most 0.1λ. This removes the 2.4 GHz
  Moxon tip warning without changing the gap geometry.
- If reduction is not possible and the solver supports it, the extended
  thin-wire kernel is selected automatically.
- Ratio below 2 is always blocking; an over-segmented wire shorter than
  1e-3λ blocks only when the whole wire is at least 0.01λ. Tiny feed gaps,
  loading-coil sections, and return stubs keep their structural segments.
- The main simulation, band-analysis, and optimizer specs use the policy. The
  optimizer rejects a blocked candidate with `optimize.constraint.model_quality`
  instead of scoring it.
- NEC2C comparisons at 1.5/2.4 GHz Moxon and 2.4/5.8 GHz Yagi complete with
  both kernels and record deterministic impedance changes; no accuracy claim is
  made.

Requirements:

- Define a shared quality policy for segment length versus wire radius,
  Moxon tip/gap resolution, and the extended thin-wire kernel.
- Expose the extended kernel in the simulation UI or select it
  automatically for families/frequencies where the default thin-wire kernel
  is outside its stated range. Record the chosen behavior and its effect.
- Make the optimizer treat model-quality failures as infeasible or as a
  blocking warning; do not silently optimize a model with
  `segmentation.radius_ratio_low` or `segment_too_short` when that invalidates
  the objective.
- Refine the Moxon tip/gap region or document why the current segmentation is
  sufficient. The 2.4 GHz Moxon tip segments are currently shorter than the
  gap and have a segment/radius ratio below 8.
- Test 1.5/2.4 GHz Moxon and 2.4/5.8 GHz Yagi with and without the extended
  kernel; assert deterministic completion and record the impedance change.
- No universal numerical accuracy claim; use convergence and invariant checks.

### HF8 — Diagnostics, defaults, and Apply Best

**Implemented 2026-11-18.** Bound-hit recommendations are now enabled for every
descriptor. The optimizer variable table uses `DisplayUnits` for adaptive
length and radius values, and a visible hint states that Current is the start
and is never silently clamped. Moxon dialogs show initial gap/λ and gap/radius;
**Apply Best** and **Apply Best SWR** revalidate the selected geometry and ask
for confirmation when it is within 5% of an envelope edge or below two conductor
diameters. The Moxon default objective changed from maximum gain to **Target
impedance**, matching the 50Ω reference and keeping the first run
match-focused. EN/ES labels and tests cover the note, guard, adaptive units, and
default objective.

Requirements:

- Set `recommends_bound_hits=True` for Moxon, Yagi, and the other families
  where a bound hit is actionable, or make the recommendation universal.
  The current Moxon result sits at the width/depth bounds without a warning.
- Show the initial value, the optimizer value, and the bounds for every
  active variable; show the Moxon gap and gap/λ/gap-radius in the results and
  the optimizer table.
- Review the Moxon default objective. `MAX_GAIN` can select a poor match/F/B
  design even after the bounds are fixed. Record the decision; a
  multi-objective default or an F/B target with an SWR constraint are the
  candidate options. Do not change the Yagi default without the same review.
- Block or require confirmation for **Apply Best** when the selected design
  violates the Moxon geometry contract or has a critical model-quality
  warning.
- Do not present `converged` as a physical-validity claim. Pair the status
  with the geometry contract, bound-hit diagnostics, model-quality result, and
  high-SWR recommendation; a converged search can still be an unusable
  antenna.
- Use `DisplayUnits(AUTO)` in the family optimization dialog and pass it from
  `MainWindow`; the table must not hide sub-centimetre values in fixed meters.
- Add EN/ES help for every new warning/field and update the help coverage
  manifest.
- UI tests cover the warning, the bound table, the apply guard, and the
  adaptive units.

### HF9 — Regression matrix, evidence, and documentation

**Implemented 2026-11-18.** `tests/unit/optimization/test_frequency_family_matrix.py`
holds 238 family/frequency combinations (243 tests including coverage and
contract checks). Every required frequency and every
`SUPPORTED_OPTIMIZER_TYPES` entry is covered. Families whose published geometry
is band-specific are exercised at meaningful frequencies rather than scaled
into an invalid band; the frequency-scalable families cover the full range.

Each combination asserts the descriptor bound invariant, a non-degenerate
span, a rebuilt initial vector (with floating-point tolerance for the derived
Moxon driven tip), and an empty geometry validation. The 2.4 GHz Moxon
regression checks the frequency-relative width/depth bounds, caps the gap at
`0.10 λ`, rejects a `0.67 λ` candidate in both validators, and runs the
optimizer with a fixed fake solver to confirm the returned gap stays inside
the envelope.

`tests/integration/simulation/test_nec2c_hf_matrix.py` runs eight priority
designs through NEC2C after `resolve_model_quality`: 2.4 GHz Moxon, 2.4/5.8 GHz
Yagi, 2.4 GHz quad beam and biquad, 1.296 GHz discone, 144 MHz dipole, and
435 MHz vertical. It asserts no blocking quality code, completion, and finite
positive resistance. These are invariants and completion evidence, not
accuracy references.

Required matrix:

- Frequencies: 1.8, 3.5, 7, 14, 28, 50, 144, 435, 1296, 2400, and 5800 MHz.
- Families: every optimizer registry type, with priority on Moxon, Yagi,
  vertical, dipole, folded dipole, inverted V, J-pole, Ringo, quad beam,
  discone, hexbeam, and biquad.
- Assertions:
  - every initial value is within its variable bounds;
  - no variable span is degenerate;
  - `build_parameters(initial_values)` reproduces the current parameters;
  - `validate(initial_values)` is empty for valid designs;
  - the optimizer does not silently change the initial design;
  - a real NEC2C run completes for the high-frequency priority cases;
  - Moxon gap/λ and gap/radius are inside the documented contract;
  - Yagi lengths/λ and gaps/radius are inside the documented contract.

Add an old-behavior regression that fails on the current code: at 2.4 GHz,
the Moxon initial width/depth must be inside their bounds and the optimizer
must not return a gap of 0.67 λ. The test must not depend on an invented
performance reference; it asserts the bound and geometry invariants.

Documentation:

- ADR-0046 and the estimator guide record the bound contract, the Moxon
  high-frequency validity, the thin-wire policy, and the confidence downgrade.
- The user guide explains why a high-frequency Moxon/Yagi may be marked
  experimental or unsupported, and how to rebuild a valid starting design.
- `CHANGELOG.md` records the behavior change when the implementation lands.
- Do not promote evidence levels or claim measured accuracy without a
  traceable source.

### HF10 — Design-frequency/geometry consistency

**Implemented 2026-11-18.** The Moxon form now tracks its managed width, depth,
and tip fields with the shared `StartingDimensionsState`. A pristine frequency
change regenerates the scaled 20 m reference; after an edit, the geometry is
preserved and the stale message names the reference button. The Yagi table
tracks positions, lengths, radius, add, and remove. A pristine frequency change
keeps the existing wavelength-ratio scaling; an edited table is preserved and
shows the stale message. The NBS preset and Moxon reference reset pristine.
`set_parameters` locks loaded projects and optimizer results; new templates and
applied estimates mark pristine.

The Moxon form warns when width/λ is outside the gross `0.15–0.60` guard.
`yagi_gross_frequency_mismatch` uses a wider `0.20–0.80` guard than the
editor's advisory `0.35–0.65` warning. `optimizer_availability` returns
`optimize.unavailable.frequency_mismatch` after the ordinary bound invariant
passes, so a 20 m Yagi left at 2.4 GHz is rejected before the solver starts.

Tests cover pristine and edited frequency changes, preset reloads, loaded
parameters, newly created templates, and the optimizer preflight. This is a
geometry-consistency guard, not a performance or accuracy claim.

### File plan

- `src/antennadesk/domain/optimization/families/common.py`
- `src/antennadesk/domain/optimization/families/typed.py`
- `src/antennadesk/domain/optimization/families/yagi.py`
- `src/antennadesk/domain/optimization/families/dipole.py`
- `src/antennadesk/domain/optimization/families/vertical.py`
- `src/antennadesk/domain/optimization/families/scv.py`
- `src/antennadesk/domain/optimization/descriptor.py`
- `src/antennadesk/domain/optimization/registry.py`
- `src/antennadesk/domain/optimization/engine.py`
- `src/antennadesk/application/use_cases/optimize_antenna.py`
- `src/antennadesk/domain/antennas/moxon.py`
- `src/antennadesk/domain/design/estimators.py`
- `src/antennadesk/domain/simulation/segmentation.py`
- `src/antennadesk/simulation/discretization.py`
- `src/antennadesk/domain/simulation/spec.py`
- `src/antennadesk/ui/dialogs/family_optimization_dialog.py`
- `src/antennadesk/ui/main_window.py`
- `src/antennadesk/ui/i18n.py`
- `tests/unit/optimization/`, `tests/integration/simulation/`, `tests/ui/`
- `docs/ADR/0046-frequency-aware-optimizer-bounds.md`
- `docs/ANTENNA_DESIGN_ESTIMATORS.md`, `docs/USER_GUIDE.md`,
  `docs/VALIDATION_PLAN.md` (only if evidence changes), `CHANGELOG.md`

### Acceptance for the track

- HF1’s ADR is accepted and linked from the queue.
- Every descriptor passes the initial-in-bounds and non-degenerate-span
  invariants across the frequency matrix; no silent clamp remains.
- A 2.4 GHz Moxon no longer produces a 0.67 λ gap; its gap is inside the
  documented contract and the optimizer can explore a physically plausible
  design.
- Yagi 15/32 elements at 2.4 GHz and 5/32 elements at 5.8 GHz start inside
  bounds and complete a real NEC2C run.
- Other families either have sane bounds at 2.4 GHz or an explicit
  unsupported reason; no family silently evaluates a clamped design.
- Model-quality warnings are either resolved or block the optimizer.
- The optimizer UI shows bounds, gap ratios, and bound-hit diagnostics; Apply
  Best cannot silently accept a geometrically invalid design.
- The full gate passes: `ruff check`, `ruff format --check`, both `mypy`
  passes, and `NEC2C=... pytest`.

### Out of scope

- New antenna families or new solver engines.
- A universal frequency envelope without evidence.
- Inventing high-frequency Moxon/Yagi reference values.
- Automatic scaling of tuned geometry; ADR-0043 remains the policy.
- Multi-band Moxon/Yagi optimization.
- Matching-network optimization.
- Claiming measurement-grade accuracy for 1.5/2.4/5.8 GHz results.

### Risks and mitigations

- **Removing construction floors makes HF designs unbuildable.** Keep a
  separate physical floor and test HF construction values; do not equate
  “search bound” with “buildable minimum”.
- **Changing Moxon parameterization could break persistence.** Prefer the
  existing fields and change only optimizer variables/validation; if a new
  field is unavoidable, add schema migration and round-trip tests.
- **The extended kernel changes results.** Treat it as a modeling decision
  with regression and convergence evidence; do not enable it silently without
  documenting the effect.
- **Many families are affected.** Migrate incrementally, but do not close the
  track until every registry family passes the matrix or has an explicit
  unsupported reason.
- **The exploratory control is not a reference.** Do not turn 4.86 mm,
  7.27 mm, or 25 dB into golden values without a traceable source.


## EF1–EF9 — Shortened-EFHW optimizer and model-confidence queue (2026-11-13)

**EF1–EF6, EF7a, EF7b, EF8a, the bounded EF8 feedpoint choke model, and EF9
L/Pi/T matching are implemented.** Automatic L/Pi/T synthesis is available in
the project matching dialog and the design-specific end-fed action. The ordered
plan is:

| ID | Scope | Why it is separate |
|---|---|---|
| EF1 | Preserve model-defined wire partitions in optimizer candidates | Correctness fix; only shortened EFHW descriptors opt in |
| EF2 | Diagnose input-shunt matching-network topology limits | Explains the fixed-network SWR floor without changing results |
| EF3 | Warn about the installation-return proxy and SWR confidence | Visibility only; no numerical change |
| EF4 | Clarify objective semantics and expose best-SWR selection | Product/UI decision; other families keep their defaults |
| EF5 | Recommend action when an optimum hits a search bound | Optimizer guardrail gated by descriptor |
| EF6 | Investigate 40-10 convergence | Needs a segment/load-placement spike before changing the model |
| EF7a | Measured 49:1 transformer reactive preset | Implemented from Squash Practice measurements |
| EF7b | Measured transformer loss and frequency dependence | Implemented from the Squash Practice band-loss table |
| EF8a | User-selectable end-fed return path | Implemented; `auto` preserves legacy behavior |
| EF8 | Common-mode return / coax-shield model | Bounded feedpoint choke model implemented; shack-end/shield-transfer model remains deferred |
| EF9 | Design-specific matching-network optimization | L/Pi/T implemented with automatic synthesis and design Q |

### EF1 — Optimizer structural segmentation (implemented)

The optimizer recalculates candidate segmentation from the target frequency and
the base policy. That is correct for geometry, but it discarded `wire_segments`
entries that are part of the numerical model. In a shortened EFHW the fixed
0.5 m feed section and the 0.10 m loading-coil section must keep three segments
each; otherwise the lumped load lands on a different part of the wire and the
optimizer evaluates a different model from the one the user applies.

Implementation contract:

- `AntennaOptimizerDescriptor` has an optional `structural_segmentation`
  callback. The default is `None`, so every existing family follows the previous
  code path exactly.
- Only the shortened EFHW descriptors (`SHORTENED_80_10` and
  `SHORTENED_40_10`) set the callback. Standard end-fed, sloper, random wire, and
  every other family keep `None`.
- The callback returns the fixed partition counts from
  `endfed_segmentation_overrides()`; the optimizer merges them into the
  recalculated policy and leaves the radiator and other wires on the normal
  target-based counts.
- The merge validates that the wire exists in the candidate model. It lowers
  only the policy's validation minimum when a structural count is below it; all
  wire counts are explicit, so no other wire changes.
- `MAX_BANDWIDTH` sweeps also receive the structural partitions; `None` and
  empty overrides are a no-op.

Acceptance: the 80-10 and 40-10 candidate specs keep the feed and coil sections
at three segments; standard end-fed and a representative non-end-fed family
remain `None` and follow the old path; the full gate is green; no schema,
solver, or UI change. Because the optimizer no longer evaluates a different
mesh, its reported best SWR can shift slightly; the applied design is now the
same model the optimizer scored. Tests:
`tests/unit/application/test_optimize_endfed_segmentation.py`.

### EF2 — Matching-topology diagnostic (implemented)

The internal EFHW unit is an input-shunt L-section (100 pF) plus series leakage
(198 nH), with no output shunt. When the ideal transformer presents a load with
R above the source reference, that topology cannot match it even with ideal C/L.

Implementation contract:

- `MatchingNetworkOrigin` distinguishes `NONE`, `INTERNAL_ENDFED`, and
  `PROJECT` at runtime. It is set by the matching resolver and the end-fed spec
  builder; it is not persisted and is excluded from the model fingerprint.
- `input_shunt_l_network_swr_floor()` returns `R / source` only when the network
  is a two-element input-shunt L-section (or a Pi with no output shunt), the
  series and input-shunt branches are active, and `R > source`. Otherwise it
  returns `None`.
- `LinkBudget` carries the floor so normalization can emit
  `matching_network.topology_limit` with the expected value.
- The diagnostic is emitted only for `INTERNAL_ENDFED` and only when the
  project network is not overriding it. A project network or another family's
  spec never sees the new warning. The model fingerprint is unchanged.

Acceptance met: a shortened EFHW candidate with a high transformed load emits
the warning and its theoretical floor; the same design without the internal
origin emits no topology warning; domain, link, fingerprint, resolution, and
real NEC2C tests pass; EN/ES text is present.

### EF3 — Proxy return and confidence warnings (implemented)

When a shortened EFHW uses the 0.1 m installation-return proxy instead of a real
counterpoise, the editor now adds an explicit warning and the confidence card
marks absolute SWR as informational.

Implementation contract:

- `endfed_model_warning_keys()` adds `endfed.warning.return_proxy` only when
  `installation_return_active` and the preset is `SHORTENED_80_10` or
  `SHORTENED_40_10`.
- `design_evidence_rows()` adds a **Model confidence** row for the shortened
  presets. With the proxy active, it states that the installation return is not
  a physical counterpoise and the real coax/mast/earth path dominates SWR.
  Without the proxy, it states that SWR is informational and the preset is
  judged by R/X convergence.
- The row reaches the Diagnostics confidence card and HTML/PDF reports through
  the existing localized row path. EN/ES report text is present.
- No solver, impedance, SWR, gain, schema, or fingerprint change. Standard
  end-fed, sloper, random wire, and every other family are unchanged.

### EF4 — Objective clarity and best-SWR action (implemented)

`TARGET_IMPEDANCE` minimizes `|Z−50|`, not SWR. The shortened EFHW descriptors
now open in **Minimum SWR**; standard end-fed, sloper, random wire, and every
other family keep their previous default. The dialog shows a hint when the
selected objective candidate has a higher SWR than another feasible candidate,
and adds **Apply Best SWR** independent of the objective. The objective help
states the difference explicitly.

Implementation contract:

- `endfed_descriptor()` selects `MIN_SWR` only when the preset is
  `SHORTENED_80_10` or `SHORTENED_40_10`.
- The dialog selects the feasible candidate with the lowest `metrics["swr"]`,
  builds its parameters through the descriptor, and accepts it. It does not
  change the objective, scoring, or stored result.
- The hint compares the selected candidate's `best_metrics["swr"]` with the
  lowest feasible candidate and appears only when the difference exceeds 0.05.
- The new action has EN/ES text and accessible help.
- No solver, schema, fingerprint, or other-family default changes. A new
  `MIN_MISMATCH` objective based on `|Γ|` remains a separate ADR.

### EF5 — Bound-hit recommendation (implemented)

When the best candidate is at a continuous-variable bound, report it and add a
recommendation to widen the range only if the result is buildable.

Implementation contract:

- `variables_at_bounds()` reports unlocked continuous variables within 1 % of
  their search interval. Integer and choice variables are not reported.
- `AntennaOptimizerDescriptor.recommends_bound_hits` is opt-in and is set only
  by the shortened EFHW descriptors.
- `RecommendationContext.at_bounds` feeds the new
  `optimize.recommend.bound` warning; the dialog already maps variable names to
  localized labels.
- No automatic bound expansion. Other families produce the same recommendations
  as before.

### EF6 — 40-10 convergence investigation (implemented as a documented spike)

The 40-10 preset remains R/X-sensitive at 10/21/51 radiator segments. The spike
tested the two plausible model fixes:

| Coil-section change | 40-10 result | 80-10 result |
|---|---|---|
| 0.10 m, 1–5 segments | no meaningful improvement | — |
| 0.15 m, 3 segments | R spread 1.16 Ω, X spread 4.38 Ω | not tested |
| 0.20 m, 3 segments | R spread 0.71 Ω, X spread 2.85 Ω | not tested |
| 0.30 m, 3 segments | R spread 0.36 Ω, X spread 1.54 Ω | not tested |
| 0.50 m, 3 segments | R spread 0.13 Ω, X spread 0.63 Ω | R/X degrades strongly and does not converge |

A wider section makes 40-10 converge but changes the 80-10 model for the worse,
so there is no single section length that improves both presets. The section
length is a numerical partition, not a measured coil dimension; changing it to
pass the check would be tuning the mesh without a traceable reference. The
decision is therefore:

- keep the 0.10 m section and the R/X convergence policy;
- keep absolute SWR informational for 40-10;
- add a static editor warning `endfed.warning.convergence_40_10` for the
  40-10 preset;
- do not relax the convergence thresholds;
- leave any future model change to a measured transformer/coil reference.

The existing NEC2C integration test continues to assert that 80-10 converges and
40-10 does not. No solver, schema, or numerical change was made.

### EF7a–EF9 — Implemented / blocked

- **EF7a (implemented):** optional measured 49:1 transformer preset from
  Squash Practice's 2xFT114-43, 5T/30T build. It models 198 nH leakage,
  2.7 pF secondary winding capacitance, and 25.8 µH magnetizing inductance as a
  primary-referred shunt/series network. The preset is clearly labeled as a
  reference build, not the user's transformer; the external 100 pF capacitor
  remains separate. Schema 46 adds the persisted model selector.
- **EF7b:** measured transformer loss and frequency dependence. Implemented as
  an optional Squash Practice/AF7NX table at the 80/40/20/10 m band centers,
  with log-frequency interpolation, endpoint clamping, a 49:1 requirement, and
  a separate `transformer_loss_db` result field. KN5L's ~0.3 dB core-loss data
  corroborates the magnitude but was not used to add frequency points.
- **EF8:** common-mode return / coax-shield model. EF8a adds the selectable
  return path and a model-only coax-shield wire approximation; EF8 adds an
  optional measured feedpoint choke R/X as a NEC series load on the shield.
  ADR-0037 records the bounded model. Shack-end placement, frequency-interpolated
  `Zcm(f)`, shield transfer impedance, and absolute common-mode-current
  prediction still require a measurement or a validated model. Do not optimize
  the installation proxy as a physical radial.
- **EF9:** design-specific matching-network optimization. ADR-0038 defines an
  optional design-specific L/Pi/T network with precedence project >
  design-specific > internal. Schema 50, UI, optimizer variables, automatic
  synthesis, and regression coverage are implemented. Do not add loose C/L
  variables to the fixed input-shunt network.

