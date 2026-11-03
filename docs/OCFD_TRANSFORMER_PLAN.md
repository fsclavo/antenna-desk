# OCFD transformer / 4:1 balun plan

**Status:** implemented
**Date:** 2026-11-03
**Scope:** OCFD matching and result semantics, not antenna geometry

## Problem

The OCFD is fed at about one third of its length and normally presents roughly
200 Ω at the feed point on its fundamental band. A 4:1 current balun is the
usual way to bring that impedance near 50 Ω for the transmitter.

AntennaDesk already models an ideal feed transformer for end-fed and T2FD
designs through `SimulationSpec.feed_transformer_ratio`. The OCFD does not set
that field, so it always reports the raw antenna-side impedance and computes SWR
against 50 Ω without the balun. This makes a correctly matched OCFD look worse
than the real installation and makes the synthesis/optimization target
ambiguous.

## Goals

1. Add an optional ideal feed transformer ratio to OCFD designs.
2. Default new OCFD designs and the OCFD estimator to 4:1, matching common
   practice, while preserving old projects as untransformed (`1.0`).
3. Apply the transformer in the existing link-budget cascade, without changing
   the NEC geometry or the radiation pattern.
4. Make raw antenna impedance and transmitter-side impedance understandable in
   the UI, results, reports, and optimizer.
5. Keep the model honest: it is an ideal transformer, not a lossy balun or a
   common-mode choke.

## Non-goals

- Do not change the OCFD wire geometry or feed-offset formula.
- Do not add a physical balun component, ferrite model, or common-mode current
  solver.
- Do not silently reinterpret old projects.
- Do not force 4:1 on every OCFD; the ratio remains editable, and `1.0` means
  no transformer.
- Do not change the multiband analysis engine.

## Current behavior

- `OCFDParameters` has `feed_ratio` (geometry) but no transformer ratio.
- `estimate_ocfd()` returns a 1/3-feed design with no transformer and warns that
  the feed impedance depends on offset and height.
- `_ocfd_simulation_spec()` builds a normal `SimulationSpec`; the default
  `feed_transformer_ratio` is `1.0`.
- `link_budget()` already divides the antenna impedance by
  `feed_transformer_ratio`, then applies the matching network and feed line.
  The normalized results therefore already support the concept.
- The OCFD synthesis dialog targets 50 Ω by default. Without a transformer it
  tries to make the raw feed-point impedance 50 Ω, which can push the geometry
  toward an unrealistic feed point instead of a realistic ~200 Ω OCFD plus a
  4:1 balun.

## Recommended domain model

Add to `OCFDParameters`:

```text
transformer_ratio: float = 1.0
```

Rules:

- Positive finite value, validated like `EndFedParameters.transformer_ratio`.
- `1.0` means no transformation and preserves the current raw-impedance view.
- `4.0` means an ideal 4:1 transformer.
- Values are not restricted to 4.0; 6:1 or another ratio can be entered for a
  measured or deliberately different design.
- The field is independent of `feed_ratio`: one selects where the antenna is
  fed, the other selects the impedance transformation.

Recommended defaults:

| Context | Default | Reason |
|---|---|---|
| Domain constructor / imported old project | `1.0` | Backward compatibility |
| New OCFD form / catalog preset | `4.0` | Common practical balun |
| OCFD estimator | `4.0` | Frequency-first starting point |
| Converted custom geometry | preserve if possible; otherwise `1.0` with a warning | Do not invent a balun |

### Custom-wire conversion

`OCFDParameters.to_custom_parameters()` currently loses all post-processing
metadata except `generator_id`/`generator_name`. The plan needs an explicit
decision:

- **Preferred:** add a generic `feed_transformer_ratio: float = 1.0` to
  `CustomAntennaParameters`, use it in the custom simulation spec, and preserve
  it in both `to_custom_parameters()` and `from_custom_parameters()`.
- **Fallback:** keep the ratio only on OCFD and warn when converting to custom
  wires that the transformer will be dropped.

The preferred option also benefits imported/custom designs and avoids a hidden
loss of matching information. It is a broader schema change and needs its own
tests.

## Simulation behavior

`_ocfd_simulation_spec()` should set:

```text
feed_transformer_ratio=parameters.transformer_ratio
```

The existing cascade order remains: from the transmitter, feed line → matching
network → ideal transformer → antenna. The transformer scales the antenna
impedance before the feed line and network are evaluated.

Expected effects:

- `FrequencyResult.impedance_ohm` and `swr` become transmitter-side values when
  the ratio is not 1.0.
- The far-field pattern and power gain do not change.
- Realized gain includes the transformer's effect on mismatch.
- A diagnostic reports that an ideal transformer was applied.
- `1.0` reproduces the current results exactly.

## UI

### OCFD form and dialog

Add a field labeled **Transformer ratio** / **Relación del transformador**:

- suffix `:1`;
- range `1.0` to a sensible upper bound;
- decimals suitable for `4.0`, `6.0`, `49.0`;
- default `4.0` for new OCFD designs;
- help text: “Ideal feed-point transformer. Set 1.0 to see the raw antenna
  impedance; 4.0 is the common OCFD balun.”

Do not add another checkbox if a numeric field is enough. The end-fed and T2FD
editors already use the same numeric pattern.

### Results and reports

The results continue to show the transmitter-side impedance and SWR. Add a
clear note/diagnostic that a transformer is included. The gain summary should
state that realized gain includes the transformer mismatch effect.

If the selected result has both raw and transformed values, show both in the
diagnostics or a compact summary row:

- antenna-side Z;
- transformer ratio;
- transmitter-side Z;
- SWR.

This avoids the common confusion where a user sees ~200 Ω in the table and
expects 50 Ω after adding a 4:1.

### Synthesis and optimization

The synthesis dialog currently defaults to 50 Ω. With a transformer:

- define the target as **transmitter-side impedance** by default;
- show the antenna-side target as `target × ratio`;
- when the user sets 1:1, behave exactly as today;
- when the user sets 4:1, a 50 Ω target corresponds to about 200 Ω at the
  antenna, which is the physically meaningful OCFD case;
- keep the feed-ratio and length variables independent from the transformer
  ratio.

If the user combines a transformer with a matching network, show a short note
that both are in the cascade; do not silently stack them.

## Estimator and presets

`estimate_ocfd()` should set `transformer_ratio=4.0` and update its warning to
mention the ideal 4:1 starting point. The warning should still say that the
actual impedance depends on height, ground, and feed offset.

The OCFD catalog preset should start with 4.0. Existing projects and imported
OCFDs should load with 1.0 unless the file contains an explicit ratio.

## Persistence

Add `transformer_ratio` to `OCFDParametersPayload` with default `1.0`.

Two schema options:

1. **Bump to schema version 5** and add a migration that leaves existing OCFD
   payloads at `1.0`. This is the clearest and most consistent with the project’s
   schema policy.
2. Add the optional field at version 4 without a version bump. This is less
   disruptive but weakens the “schema version changes are explicit” rule.

Recommendation: bump to version 5 and add a migration test. Old files must load
unchanged and produce the same raw-impedance results.

If the preferred custom-wire transformer field is added, include it in the same
schema decision.

## Multiband analysis

The existing OCFD band defaults (40/20/10 m or 80/40/20/10 m) remain unchanged.
With a 4:1 ratio, the Bands tab and reports show the transformed SWR, which is
what the transmitter sees. Keep the note that OCFD coverage is heuristic and
depends on height, ground, and feed offset.

## Tests

- Domain: validation of the ratio, default `1.0`, `with_*`/`from_custom`
  preservation, and OCFD estimator setting `4.0`.
- Application/simulation: `_ocfd_simulation_spec()` passes the ratio; link
  budget divides antenna impedance; pattern is unchanged; `1.0` is a no-op.
- UI: form and dialog round-trip; default 4.0 for new designs; loading an old
  project shows 1.0; hint text and translations.
- Synthesis: target semantics at 1:1 and 4:1; displayed antenna-side and
  transmitter-side values.
- Persistence: schema version bump/migration, round trip, old file compatibility.
- Multiband: OCFD 40/20/10 with 4:1 shows transformed SWR; reports/comparison
  label the transformer.
- Regression: existing OCFD projects, reports, and optimization results remain
  unchanged when the ratio is 1.0.

## Acceptance criteria

- A new OCFD starts with an editable 4:1 ideal transformer.
- Setting the ratio to 1.0 shows the raw feed-point impedance and reproduces the
  old behavior.
- Setting 4.0 transforms ~200 Ω to ~50 Ω and changes SWR/realized gain, not the
  pattern.
- The UI and reports state that the transformer is ideal.
- Existing projects load with 1.0 and do not change.
- OCFD synthesis at 50 Ω is interpreted as transmitter-side with the transformer
  active.
- The multiband Bands tab uses the transformed SWR.
- Documentation and `CHANGELOG.md` are updated.

## Risks and open questions

1. **Default policy.** A 4.0 default for new designs is user-friendly, but a 1.0
   domain default is required to avoid changing old results. This split must be
   documented and tested.
2. **Custom conversion.** Without a generic custom transformer field, editing an
   OCFD as custom wires silently loses the balun. Prefer preserving it.
3. **Real balun behavior.** The model remains ideal; losses, common-mode
   current, frequency response, and power handling are not represented.
4. **4:1 versus 6:1.** 4:1 is the common compromise; 6:1 may fit a measured
   300 Ω feed better. Keep the field editable and document the tradeoff.
5. **Target semantics.** Users may think the optimizer targets antenna-side
   impedance. Label both sides explicitly and choose transmitter-side as the
   default target.
6. **Schema version.** Prefer a version bump and migration over an implicit
   default in the current schema.
7. **Matching-network interaction.** A transformer and an L/Pi/T network can
   both be active. The cascade is defined, but the UI should warn against
   accidental double matching.

## Implementation summary

- `OCFDParameters.transformer_ratio` defaults to `1.0`; the OCFD form, catalog
  preset, and estimator use `4.0`.
- `CustomAntennaParameters.feed_transformer_ratio` preserves the ratio when an
  OCFD is converted to custom wires.
- `_ocfd_simulation_spec()` and `_custom_simulation_spec()` pass the ratio to
  `SimulationSpec.feed_transformer_ratio`.
- The synthesis dialog labels targets as transmitter-side and shows the
  antenna-side equivalent when the ratio is not `1.0`.
- Schema version 5 adds optional OCFD and custom transformer fields; old
  projects migrate with `1.0`.
- Tests cover domain validation, custom conversion, estimator defaults, UI
  round trips, synthesis notes, persistence, and migration.
