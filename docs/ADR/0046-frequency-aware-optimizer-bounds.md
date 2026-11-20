# ADR-0046 — Frequency-aware optimizer bounds and high-frequency family validity

- **Status:** Accepted
- **Date:** 2026-11-18
- **Deciders:** Fernando Sclavo, development
- **Related:** HF1–HF10 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md),
  [ADR-0026](0026-family-optimizer-architecture.md),
  [ADR-0043](0043-design-versus-analysis-frequency.md),
  [ADR-0044](0044-adaptive-length-display-units.md), and
  [`../ANTENNA_DESIGN_ESTIMATORS.md`](../ANTENNA_DESIGN_ESTIMATORS.md)

## Context

The family optimizers were introduced for HF designs. Their descriptors use
absolute bounds in metres, including `_length(..., minimum=0.1)` and explicit
floors of `0.5 m` and `0.05 m`. Those values were practical at HF, but they are
not a valid search policy at VHF/UHF.

At 2.4 GHz the reference-scaled Moxon starts at width 44.99 mm, depth
17.22 mm, and tip gap 1.296 mm. Its optimizer bounds are
`width=[100, 101] mm` and `depth=[100, 101] mm`. Because
`gap = depth - reflector_tip - driven_tip`, every feasible candidate has a gap
between 76.1 and 93.0 mm (0.61–0.74 λ). A production `MULTI_OBJECTIVE` run
returned gap 86.96 mm, SWR 15.50, 4.19 dBi, and 2.11 dB front-to-back. An
in-memory control that changed only the bounds to relative values returned gap
4.86 mm, SWR 1.05, 6.06 dBi, and 25.06 dB front-to-back. The control is
exploratory, not a numerical reference.

The mechanism is general:

- `_length()` defaults to `minimum=0.1` m.
- `around()` uses that floor as the lower search bound. When
  `value * (1 + fraction) <= minimum`, it returns a degenerate interval above
  the current design (`high = low + 1 mm`).
- `OptimizationVariable.to_fraction()` silently clamps the current value into
  that interval, so the engine evaluates a different design from the editor.
- The Moxon validator only checks `reflector_tip + driven_tip < depth`.
- Yagi element lengths have an absolute 0.05 m floor. This starts clamping
  15+ element arrays at 2.4 GHz and every element at 5.8 GHz.
- Absolute floors of 0.1 m and 0.5 m affect many other families at 1.5/2.4 GHz.

The project supports HF, VHF, and UHF without promising accuracy outside the
model supported by the engine. The optimizer must therefore distinguish a
buildable/modelable minimum from a search interval, and it must say when a
family is outside its valid envelope instead of silently moving the search.

## Decision

1. **Separate physical floors from search bounds.** A physical floor is a
   real construction or modeling minimum for a family (for example, conductor
   clearance or the smallest representable wire). A search bound is the interval
   the optimizer may explore around the current design. A physical floor must
   not be used to move a valid current design into a different region.

2. **Every descriptor must satisfy a bound invariant.** For every variable:

   ```text
   finite(minimum)
   finite(maximum)
   maximum > minimum
   minimum <= initial_value <= maximum
   span >= max(1e-6 m, 0.001 * max(abs(initial_value), 1e-6 m))
   ```

   The final line is a non-degeneracy rule, not a physical reference. A
   variable with a current value of zero uses `1e-6 m` as its scale.

3. **Never clamp the current design silently.** If an active variable is
   outside its bounds, or the descriptor cannot produce a non-degenerate
   search interval, the optimizer must not run. The failure must identify the
   family, variable, current value, and bounds, and the UI must show it before
   starting a solver run. Locked variables remain context and stay at their
   initial values.

4. **Search bounds are relative to the current design.** For a positive
   current value `v` and fraction `f`:

   ```text
   low  = max(physical_floor, v * (1 - f))
   high = v * (1 + f)
   ```

   If `v < physical_floor`, the current design is outside the family's
   buildable/modelable envelope. Do not widen the interval above the design;
   report the design as unsupported or ask the user to change the dimension or
   conductor. If `v == 0`, use a documented zero-centre interval with the
   minimum span.

5. **Frequency-aware floors are allowed; frequency-only floors are not.**
   A family may use a wavelength-normalized lower bound when its geometry is
   normalized by a published reference (Yagi, Moxon, quad, hexbeam, discone,
   vertical, J-pole, Ringo). A family that has no normalized reference uses
   relative bounds around the current design and an explicit supported
   envelope. Do not add a minimum merely because the design is HF.

6. **Declare a supported envelope per family.** A family remains available at
   a frequency only when its descriptor can build valid bounds and its
   estimator/evidence supports that frequency. Outside the envelope,
   `optimizer_availability()` returns a translated reason rather than a
   clamped search range. The envelope is family-specific and must be
   documented; do not invent a universal HF/VHF/UHF cutoff.

7. **The Moxon gap is a first-class geometry contract.** Keep the existing
   `MoxonParameters` fields for compatibility, but make the optimizer treat
   the gap as the primary invariant. The implementation may expose `gap_m`
   directly and derive one tip, or keep the two tips with a documented
   relationship; it must not allow two redundant tip variables to create a
   non-Moxon geometry. The contract must:

   - keep the published 14.17 MHz Cebik dimensions exact;
   - require a positive gap;
   - require a documented clearance relative to `wire_radius_m`;
   - reject a gap of `0.2 λ` or more as a Moxon geometry;
   - constrain the gap/depth and gap/width proportions to documented ranges
     anchored to the reference and the high-frequency control;
   - make a `0.67 λ` gap infeasible, not merely a warning.

   The exact lower/upper numerical ranges are fixed by HF4 with tests. They
   are geometry-validity limits, not new performance references.

8. **The Moxon estimator is radius-aware outside its reference case.** The
   14.17 MHz Cebik case remains exact and reference-backed. Linear scaling to
   another frequency does not scale the wire radius; at 2.4 GHz a 1 mm radius
   makes the scaled gap comparable to the conductor diameter. Outside a
   documented scaling envelope, the estimator must downgrade its confidence,
   make its tolerance meaningful, and warn that the gap and radius need
   independent verification. If the scaled gap is below the modeling
   clearance, it must return an explicit unsupported estimate or a clearly
   labelled experimental estimate, never a `REFERENCE_SCALED` claim.

9. **Yagi bounds are wavelength-relative.** Replace the absolute 0.05 m
   element floor and the 0.01 m search steps with bounds and steps derived
   from the current normalized design and `wavelength_m(frequency_hz)`. Keep
   the existing director length/gap taper constraints and the minimum
   conductor spacing relative to the actual radius. Verify the DL6WU 2–32
   element designs at 1.5, 2.4, and 5.8 GHz; at 5.8 GHz the current 50 mm floor
   is approximately one wavelength and cannot remain.

10. **High-frequency model quality is part of feasibility.** A candidate whose
    segment length/radius ratio is below the documented thin-wire limit, or
    whose Moxon tip/gap region is not resolved, must be either modelled with
    the supported extended thin-wire kernel or rejected with an explicit
    diagnostic. The optimizer must not silently optimize a model that the
    solver itself flags as numerically unreliable. The exact hard/soft warning
    list is fixed by HF7.

11. **Bound hits and geometry warnings are visible.** A best design within
    1 % of a search bound must be reported, regardless of the objective. The
    UI must show the initial value, the optimized value, the bounds, the Moxon
    gap and gap/λ, and the model-quality result. `converged` describes the
    search, not physical validity. **Apply Best** must be blocked or require
    confirmation when the selected design violates the geometry contract or
    has a critical model-quality warning.

12. **No invented high-frequency references.** The 14.17 MHz Cebik dimensions
    remain the only exact Moxon reference in this track. The exploratory
    4.86 mm/7.27 mm control, the 2.4 GHz solver diagnostic, and the 25 dB
    front-to-back value are not golden values. A high-frequency performance
    claim requires a traceable published reference or a measurement. Tests
    assert invariants and completion, not an invented gain or SWR.

13. **Design-frequency consistency remains ADR-0043.** A frequency change must
    not silently resize tuned geometry. The Moxon manual reference-preset
    action and the Yagi auto-scale exception are reconciled in HF10. If the
    geometry is grossly inconsistent with λ, the optimizer warns or blocks
    and offers the explicit starting-dimension action.

## Consequences

Positive:

- The optimizer can search a physically meaningful Moxon at 1.5/2.4 GHz.
- A current design is always the first candidate, or the run does not start.
- VHF/UHF families either have valid bounds or an explicit reason.
- The high-frequency Moxon no longer claims reference-scaled confidence when
  the wire radius makes the geometry non-equivalent.
- Thin-wire and segmentation limitations become visible instead of being
  hidden inside an optimization score.
- Existing HF behavior is preserved by keeping physical floors separate from
  search bounds.

Negative:

- Every descriptor needs an explicit physical floor, search policy, and
  supported envelope; this is a broad migration.
- Some families that previously “optimized” at 2.4 GHz will become unavailable
  until a valid high-frequency design is documented.
- The Moxon optimizer parameterization may change, and old optimization
  summaries may not be directly comparable.
- Testing requires a frequency/family matrix and real NEC2C runs for priority
  cases.
- The extended thin-wire kernel changes numerical results and needs its own
  regression/convergence evidence.

No project schema change is required by this decision unless the Moxon
implementation can only satisfy the contract with a new persisted field. The
preferred implementation keeps `MoxonParameters` unchanged and changes only
the optimizer variables/validation.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Set every minimum to zero | Restores the search interval but removes construction/modeling guardrails and can produce unbuildable HF designs |
| Clamp the current design to the nearest bound | The current behavior; it silently optimizes a different antenna and made the Moxon gap bug invisible |
| Scale every minimum by wavelength | A construction clearance and a wire-spacing minimum are not electrical dimensions; a blanket scale would be wrong |
| Keep absolute HF floors and disable the optimizer above a cutoff | Simpler, but the app supports VHF/UHF and many families have valid normalized designs; a family-specific envelope is more accurate |
| Only fix Moxon and Yagi | The same bound pattern affects vertical, quad, discone, hexbeam, J-pole, Ringo, dipole, and other families; a local fix would leave the class of bug |
| Use the 2.4 GHz exploratory control as a golden reference | It is a diagnostic, not a traceable source; the project forbids invented numerical references |
| Enable the extended kernel for every model silently | It changes results and needs regression evidence; the policy must be explicit |

## Execution

The implementation is sliced in
[`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md):

| Slice | Scope | Status |
|---|---|---|
| HF1 | This ADR and the bound contract | Implemented 2026-11-18 |
| HF2 | Descriptor invariant and no silent initial clamp | Implemented 2026-11-18 |
| HF3 | Frequency-aware bounds across all families | Implemented 2026-11-18 |
| HF4 | Moxon geometry contract, gap variable, and constraints | Implemented 2026-11-18 |
| HF5 | Yagi wavelength-relative bounds and high-element-count QA | Implemented 2026-11-18 |
| HF6 | Moxon high-frequency estimator, radius, and confidence | Implemented 2026-11-18 |
| HF7 | Thin-wire model-quality gate | Implemented 2026-11-18 |
| HF8 | Diagnostics, default objective review, Apply Best, adaptive units | Implemented 2026-11-18 |
| HF9 | Regression matrix, evidence, and documentation | Implemented 2026-11-18 |
| HF10 | Design-frequency/geometry consistency | Implemented 2026-11-18 |

### HF2 implementation note

The descriptor validates its default search scope when it is constructed:
default-locked variables are context and keep their initial values, while every
default-active variable must be finite, inside its bounds, and represented by a
non-degenerate span. `OptimizerAvailability` returns a translated reason with
the family, variable, value, and bounds instead of constructing an unusable
descriptor. When the user unlocks an additional variable in the dialog, the
same check runs before a solver thread starts. The engine independently rejects
an out-of-bounds active initial value or start point with
`OptimizationStatus.ERROR` and never evaluates a clamped design.

The span floor is 1 µm for length/radius units and a smaller unit-relative floor
for capacitance, inductance, ratios, angles, and counts; a blanket metre floor
would falsely reject valid picofarad and nanohenry variables.

### HF3 implementation note

`around()` is relative to the current design, which already carries the
generator's frequency scaling. `_length()` uses a 1 µm numerical floor by
default and a span-normalized step. Practical 0.1/0.5/0.05 m floors were removed;
the remaining hard floors are genuine construction/model limits: zero for
heights and base planes, conductor clearance for gaps/spacings/tips, the fixed
end-fed feed section, electrical component minima, and the biquad small-feature
reference. A matrix at 1.8/14/144/2400/5800 MHz covering every supported
optimizer family checks that initial values are inside their bounds and that
every step is no larger than its span.

No universal frequency cutoff or invented family envelope was added. A family
that violates a genuine physical floor remains available at the registry level
but returns the HF2 translated bound reason for that design; a family-specific
envelope can be added later only from traceable evidence.

### HF4 implementation note

The Moxon geometry contract is implemented once in
`validate_moxon_geometry()` and shared by `MoxonParameters`, the optimizer
descriptor, and the editor warning. The optimizer exposes `gap_m` and derives
the driven tip; it no longer moves two redundant tip variables.

The geometry-validity envelope is gap/λ 0.004–0.10, gap/depth 0.03–0.40,
gap/width 0.01–0.15, width/depth 1.5–4.5, each tip/depth 0.20–0.75, tip-sum/depth
0.50–0.97, and gap greater than one conductor diameter. These limits are
anchored to the Cebik 14.17 MHz reference (gap/λ 0.0104, gap/depth 0.075,
gap/width 0.029) and the exploratory 2.4 GHz control (gap/λ 0.039, gap/depth
0.282, gap/width 0.108), with margin. They are construction-validity limits,
not gain/SWR references, and they do not encode the control's 4.86 mm gap.

The 0.67λ failure is rejected by the gap/λ and gap/depth checks. Tests cover
the exact Cebik dimensions, 28.5/144/435/1500/2400 MHz scaled references, the
0.67λ and conductor-clearance rejections, the optimizer rebuild, and the UI
warning. HF6 adds a radius-aware two-diameter starting clearance and the
high-frequency confidence/tolerance policy; the estimator still scales the
Cebik gap directly, but rejects a gap that cannot clear the conductor instead
of silently changing the wire radius.

### HF5 implementation note

The Yagi descriptor has no absolute element-length or step floors. All element,
gap, height, folded-spacing, and beta-hairpin bounds are relative to the current
frequency-scaled design; conductor-spacing minima use the actual element radius,
and every step is span-normalized. The DL6WU taper constraints remain.

The QA matrix covers 5/10/15/20/32 elements at 1.5/2.4/5.8 GHz with a
source-scaled 4 mm-at-432-MHz element radius. It asserts initial-in-bounds,
empty taper violations, span-normalized steps, and exact rebuild. Real NEC2C
smoke runs cover 2.4 GHz 15/32 elements and 5.8 GHz 5/15 elements and assert
completion, finite R/X, and no solver error; they make no gain or pattern
claim.

### HF6 implementation note

The Cebik 20 m Moxon estimator is reference-scaled only inside the 20 m
amateur band (14.0–14.35 MHz). Outside it, the estimate is explicitly
heuristic: `Confidence.HEURISTIC`, an extrapolation assumption, a high-frequency
warning that states the wire radius is not scaled, and a tolerance of
`max(5% width, gap)` so the tolerance is never smaller than the gap. The
14.17 MHz dimensions remain exact; the 28.5 MHz editor default remains a
documented heuristic. No 2.4 GHz published reference was invented.

The starting geometry is radius-aware at the construction boundary: if the
scaled gap is below two conductor diameters, the estimate raises
`UnsupportedEstimateError` instead of returning a design whose gap is
comparable to the wire. This is a starting-clearance rule, not a performance
claim. A later source or measurement can be recorded separately if one becomes
available.

### HF7 implementation note

`resolve_model_quality()` in `application/discretization.py` is the shared
thin-wire policy. It reduces the segment count of short wires whose
segment/radius ratio is below 8 when the resulting segment is still at most
0.1λ. This removes the 2.4 GHz Moxon tip warning without changing the gap or
feed geometry. If reduction is not possible and the solver advertises the
extended thin-wire kernel, the policy enables it automatically. The main
simulation, band-analysis, and optimizer specifications use the resolved spec.

The optimizer treats a candidate as infeasible with
`optimize.constraint.model_quality` when a segment/radius ratio is below 2 or a
wire at least 0.01λ long has segments shorter than 1e-3λ. Short structural
wires (feed gaps, loading-coil sections, return stubs) are exempt from the
short-segment rule because their fixed segmentation is intentional. The model
quality report records adjusted wires and the kernel flag for tests and
diagnostics.

NEC2C checks at 1.5/2.4 GHz Moxon and 2.4/5.8 GHz Yagi run with both kernels.
Observed impedance changes on 2026-11-18 were 3.44/4.62 ohm for the two Moxons
and 11.06/14.68 ohm for the 2.4/5.8 GHz Yagis. These values document the
kernel's effect; they are not accuracy references. The tests assert completion,
finite R/X, and a deterministic non-zero change.

### HF8 implementation note

Bound-hit recommendations are no longer restricted to the shortened end-fed
descriptors; every descriptor opts in by default. The optimizer table uses
`DisplayUnits` for adaptive length/radius values and states that Current is the
initial value with no silent clamp.

For the Moxon, the dialog shows the initial gap/λ and gap/radius. **Apply Best**
and **Apply Best SWR** revalidate the selected parameters; invalid geometry is
blocked, and a geometry within 5% of an envelope edge or below two conductor
diameters asks for confirmation. The default Moxon objective is now
**Target impedance**, not maximum gain: the Cebik reference is a 50Ω beam and a
match-focused first run is less likely to drift toward an envelope edge. Gain
and front-to-back remain selectable objectives.

### HF9 implementation note

The frequency/family matrix lives in
`tests/unit/optimization/test_frequency_family_matrix.py`. It builds 238
family/frequency combinations (243 tests including the coverage and contract
checks) covering all eleven required frequencies and every
`SUPPORTED_OPTIMIZER_TYPES` entry. Families with band-specific geometry
(hexbeam, Beverage, trap dipole, trap Yagi, SCV, T2FD, G5RV doublet) are
exercised only at frequencies where the preset is meaningful; every frequency
is still covered by the frequency-scalable families. Each combination asserts
the descriptor bound invariant, a non-degenerate span, an exact initial-vector
rebuild (with floating-point tolerance for the derived Moxon driven tip), and
an empty geometry validation.

The 2.4 GHz Moxon regression encodes the old failure mode without a performance
reference: the initial width and depth are inside their frequency-relative
bounds, the gap is at most `0.10 λ`, and a `0.67 λ` gap is rejected by both the
descriptor validator and `validate_moxon_geometry`. A full optimizer run with a
fixed fake solver also asserts that the returned gap stays inside the envelope.
The matrix checks the Moxon gap/wavelength, gap/radius, and geometry envelope,
and the Yagi element lengths and inter-element gaps against the documented
conductor clearance.

`tests/integration/simulation/test_nec2c_hf_matrix.py` runs eight high-frequency
priority designs through real NEC2C: 2.4 GHz Moxon, 2.4/5.8 GHz Yagi, 2.4 GHz
quad beam and biquad, 1.296 GHz discone, 144 MHz dipole, and 435 MHz vertical.
The test applies `resolve_model_quality`, requires no blocking code, and asserts
completion plus finite positive resistance. These are completion and invariant
checks, not accuracy references. No evidence level is promoted.

### HF10 implementation note

The Moxon and Yagi forms now follow ADR-0043's pristine policy. A pristine
frequency change regenerates the Moxon 20 m reference or scales the Yagi table;
after an edit, add, remove, or loaded design, the geometry is preserved and the
form shows the stale message. The Moxon reference button and the Yagi NBS preset
reset the pristine state. New designs and applied estimates are marked pristine;
loaded projects and optimizer results are not.

`moxon_frequency_mismatch` reports when the rectangle width is outside the
gross `0.15–0.60 λ` guard, and the Moxon form shows a dedicated warning with the
explicit rebuild action. `yagi_gross_frequency_mismatch` uses a wider `0.20–0.80
λ` guard than the editor's `0.35–0.65 λ` warning. `optimizer_availability`
returns `optimize.unavailable.frequency_mismatch` for a Yagi outside the gross
guard after the ordinary bound invariant passes, so a 20 m Yagi left at 2.4 GHz
is rejected before the solver starts. This is a consistency guard, not a
performance or accuracy claim.

## Test contract

The matrix uses 1.8, 3.5, 7, 14, 28, 50, 144, 435, 1296, 2400, and 5800 MHz
and every optimizer registry type. Priority families are Moxon, Yagi, vertical,
dipole, folded dipole, inverted V, J-pole, Ringo, quad beam, discone, hexbeam,
and biquad.

For every valid design:

- every initial value is inside its variable bounds;
- no span is degenerate;
- `build_parameters(initial_values)` reproduces the current parameters;
- `validate(initial_values)` is empty;
- the optimizer does not silently change the initial design;
- a real NEC2C run completes for the priority high-frequency cases;
- Moxon gap/λ and gap/radius are inside the documented contract;
- Yagi lengths/λ and gaps/radius are inside the documented contract.

The old-behavior regression is the 2.4 GHz Moxon: its initial width/depth must
be inside bounds, and the optimizer must not return a gap of `0.67 λ`.

## References

- [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) — HF1–HF10 execution
  queue, detailed acceptance, and file plan.
- [`../ANTENNA_DESIGN_ESTIMATORS.md`](../ANTENNA_DESIGN_ESTIMATORS.md) — Moxon
  and Yagi sources, assumptions, confidence, and tolerances.
- [ADR-0026](0026-family-optimizer-architecture.md) — descriptor and shared
  engine architecture.
- [ADR-0043](0043-design-versus-analysis-frequency.md) — design versus
  analysis frequency and pristine geometry.
- [ADR-0044](0044-adaptive-length-display-units.md) — canonical meters and
  adaptive presentation; the optimizer table must use the same display policy.
