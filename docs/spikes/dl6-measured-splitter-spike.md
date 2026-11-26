# DL6 measured/broadband splitter S-parameter spike

**Date:** 2026-11-26

**Status:** spike complete; no measured splitter model is implemented.

**Related:** DL6, [ADR-0049](../ADR/0049-stacked-yagi-composed-family.md),
[ADR-0054](../ADR/0054-bounded-multiport-feed-network.md),
[`AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) §DL6

## Question

The bounded Wilkinson mode now models:

- quarter-wave branches with optional matched loss;
- star isolation resistors with optional series inductance and parallel
  capacitance;
- per-level L/Pi/T matching networks and ideal transformer ratios;
- deterministic branch/resistor tolerance corners at the design frequency.

The remaining DL6 item is a **measured or broadband splitter/isolation model**.
This spike asks whether that can be added without inventing data, a dependency,
or a second solver.

## What is missing

The current model still uses ideal quarter-wave branches and ideal star
resistors apart from the user-entered loss and parasitics. It does not model:

- a measured splitter S3P or S4P, including its calibrated reference planes;
- port-to-port isolation that differs from the ideal Wilkinson equations;
- component resonances or a broadband transfer response from measured data;
- the measurement fixture, connector effects, or assembly tolerances.

The current `n_way_wilkinson` S-matrix is a **model**, not a measured splitter
data set. Adding more scalar parasitics would not turn it into a measured model.

## Options

### A. Keep the bounded model and mark the measured model blocked

Keep the current implementation as the supported DL6 result. State that a
measured splitter model requires data and an ADR. No schema or solver change.

**Pros:** honest, no invented data, no dependency, no new failure modes.
**Cons:** no measured S3P/S4P support; the item stays open.

### B. Add a measured two-port S2P branch block

Replace the ideal quarter-wave branch with a user-imported two-port S2P block.
The star isolation network remains the existing R-L || C model.

**Pros:** bounded extension of the existing N-port solver; useful for measured
branch lines or PCB traces; can reuse the existing Touchstone import direction.
**Cons:** it is not a measured splitter/isolation model. It does not capture a
measured S3P/S4P, and a two-port branch cannot represent splitter port-to-port
isolation by itself. It would also require a new embedded data schema, port
reference impedance, interpolation, and range validation.

### C. Add a measured three/four-port splitter block

Replace the ideal Wilkinson network with a measured S3P/S4P (or a
count-specific N-port) block whose input port is the splitter input and whose
output ports are the level ports. The feed lines, per-level matching networks,
and transformers remain separate.

**Pros:** directly addresses measured splitter isolation and return loss; fits
the N-port solver as a black-box admittance block.
**Cons:** largest change. It requires:

- a full multi-port Touchstone parser, not the current two-port VNA helper;
- an embedded data model with frequency, complex S matrix, reference impedance,
  port count, port order, and provenance;
- interpolation and out-of-band policy, plus passivity/reciprocity warnings;
- measured data for every supported port count (2, 3, and 4 outputs);
- UI import, schema migration, reports, and a data-provenance contract;
- a new ADR because ADR-0054 deliberately keeps the solver bounded and avoids a
  general S-parameter engine.

### D. Introduce a general S-parameter engine or external dependency

Use a larger RF circuit library or a general N-port S-parameter engine.

**Pros:** broad capability.
**Cons:** dependency cost, license review, packaging, validation, and a much
larger surface than DL6 needs. ADR-0054 explicitly defers this to its own ADR.

## Data and architecture requirements

Any measured option requires, before implementation:

1. **Provenance:** manufacturer data, VNA measurement, or simulation export;
   part number, fixture, calibration, reference planes, and date.
2. **Port definition:** port count, port order, input/output labels, reference
   impedance, and whether the data includes connectors or feed lines.
3. **Coverage:** frequency range and spacing, behavior outside the measured
   range, and whether interpolation is real/imaginary linear or another defined
   rule.
4. **Physical checks:** passivity, reciprocity, and causality warnings; never
   silently clamp or repair measured data.
5. **Portability:** embed the data in the project file, not an external path;
   enforce size limits and deterministic serialization.
6. **Presentation:** show the source, measurement conditions, reference planes,
   interpolation, and limitations in the UI, reports, and construction sheet.
7. **Validation:** compare the measured block in the N-port solver against an
   independent circuit calculation for a reciprocal test network; no invented
   tolerance values.

## Recommendation

**Do not implement a measured splitter model yet.** The current bounded
Wilkinson mode is the supported result. The measured item is blocked on data,
multi-port Touchstone support, and an ADR for the embedded data/provenance
contract.

If measured data becomes available, pursue **Option C** (measured S3P/S4P)
rather than Option B. Option B is a useful branch-line feature, but it would not
answer the DL6 splitter/isolation question and could be mistaken for a measured
splitter model.

## Acceptance criteria for a future measured splitter slice

- A measured S3P/S4P fixture is embedded with provenance and reference planes.
- The N-port solver consumes it without a second circuit engine.
- A reciprocal synthetic network passes an independent S-to-Y check.
- Out-of-band and non-passive data produce explicit diagnostics, not silent
  corrections.
- The UI, reports, and construction sheet state what the measurement includes
  and excludes.
- Existing ideal, lossy, and tolerance modes remain selectable and unchanged.
