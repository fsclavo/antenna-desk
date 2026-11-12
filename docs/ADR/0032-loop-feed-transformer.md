# ADR-0032 — Full-wave loop feed transformer

- **Status:** Accepted
- **Date:** 2026-11-12
- **Related:** [ADR-0018](0018-t2fd-termination-and-transformer.md),
  [ADR-0031](0031-folded-dipole-feed-transformer.md)

## Context

A resonant full-wave loop normally presents roughly 100–150 Ω at the feed point.
A 50 Ω transmitter therefore sees an SWR of about 2–3 without a matching stage.
The common practical choices are a 2:1 balun or an L/Pi/T matching network.

Before this decision, `LoopParameters` had no transformer field. The estimator
and the user guide warned that a 2:1 balun or matching network is typical, but
the simulation always used `feed_transformer_ratio = 1.0`. The family optimizer
therefore tried to drive the raw loop impedance to 50 Ω, which can detune the
loop, while the separate element optimizer used a 100 Ω target as a workaround.

## Decision

1. Add `transformer_ratio: float` to `LoopParameters`. The default is `2.0`,
   the common full-wave-loop balun. The ratio remains editable; 1.0 shows the
   raw loop impedance, and 4:1 or another value can be entered for a different
   feed.
2. Keep the transformer out of the NEC geometry. Apply it through the existing
   ideal transformer in `SimulationSpec.feed_transformer_ratio`. The link budget
   then reports transmitter-side impedance, SWR, mismatch loss, and realized
   gain.
3. Show the ratio in the shared basic-antenna editor when the loop template is
   selected. The estimator, catalog, and change-template routes start at 2:1.
   The frequency-first **Estimate** action preserves an existing edited ratio.
4. Include `transformer_ratio` in the loop optimizer descriptor as a choice
   variable, locked by default. Unlocking it lets the optimizer compare 1:1,
   2:1, 4:1, and other practical ratios. The optimizer target remains
   transmitter-side: with a 2:1 transformer, a 50 Ω target corresponds to about
   100 Ω at the loop.
5. Change the loop element optimizer default target from 100 Ω to 50 Ω because
   its base spec now applies the default 2:1 transformer. Its hint states that
   targets are transmitter-side and that 1:1 can be selected for raw loop
   impedance.
6. Persist the ratio in the loop payload and bump the project schema to 42. The
   migration writes the 2:1 reference value. The current workspace has no
   pre-existing loop projects that require the old 1:1 behavior.
7. Document that the transformer is ideal. Balun insertion loss can be entered
   separately through the project balun/unun loss model; common-mode current,
   choking, and balance are not modeled.

## Consequences

Positive:

- New loops no longer report an avoidable 2–3 SWR floor caused by the missing
  2:1 transformation.
- The 50 Ω optimizer target becomes physically meaningful: with a 2:1
  transformer, it seeks about 100 Ω at the loop.
- The ratio is explicit in the design, project file, reports, and construction
  sheet.
- The family and element loop optimizers now use the same transmitter-side
  target semantics.

Limitations:

- A 2:1 transformer on a 150 Ω loop leaves 75 Ω, so the residual SWR is about
  1.5. An exact 50 Ω match still requires a matching network or a different
  ratio.
- The model is an ideal transformer. It does not represent a real balun's
  frequency response, losses, power handling, or common-mode choking.
- A full-wave loop is a balanced antenna. A real installation still needs a
  balun or choke for the balanced-to-unbalanced transition; an L-network alone
  does not provide that function.
- The 2:1 default is a starting point. The actual feed impedance depends on the
  loop shape, side count, height, ground, and feed position.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Keep the raw 1:1 model and rely on the user to add a matching network | The family optimizer target is misleading and new designs start with a known, avoidable mismatch |
| Default to a matching network instead of a balun | A balun is the common physical feed for a balanced loop; the project matching network remains available for exact 50 Ω |
| Hard-code 2:1 in the solver | It would hide the design choice and prevent 1:1 or measured-ratio designs |
| Model a physical balun | No traceable frequency-dependent balun model is available; an ideal ratio plus the existing loss model is honest and testable |
