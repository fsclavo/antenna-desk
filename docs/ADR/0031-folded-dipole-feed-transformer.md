# ADR-0031 — Folded-dipole feed transformer

- **Status:** Accepted
- **Date:** 2026-11-12
- **Related:** [ADR-0018](0018-t2fd-termination-and-transformer.md),
  [ADR-0030](0030-feed-chain-topology.md)

## Context

An equal-conductor folded dipole is an approximately 4:1 impedance
transformation. A resonant 40 m folded dipole presents roughly 260–300 Ω at the
feed point, so a 50 Ω transmitter sees an SWR near 5–6 without a balun. The
common practical solution is a 4:1 current balun.

Before this decision, `FoldedDipoleParameters` had no transformer field. The
estimator warned that a 4:1 balun is typical, but the simulation always used
`feed_transformer_ratio = 1.0`. The family optimizer therefore tried to drive the
raw feed-point impedance to 50 Ω, which is physically unattainable, and the
reported SWR stayed near 5.3–6.0.

The OCFD family already stores an editable `transformer_ratio`, defaults new
designs to 4:1, and applies it through `SimulationSpec.feed_transformer_ratio`.
The same mechanism is available for the folded dipole.

## Decision

1. Add `transformer_ratio: float` to `FoldedDipoleParameters`. The default is
   `4.0`, the common equal-conductor folded-dipole balun. The value remains
   editable; 6:1 is a practical alternative for a 300 Ω feed, and 1.0 shows the
   raw antenna impedance.
2. Keep the transformer out of the NEC geometry. Apply it through the existing
   ideal transformer in `SimulationSpec.feed_transformer_ratio`. The link budget
   then reports transmitter-side impedance, SWR, mismatch loss, and realized
   gain.
3. Make the ratio visible and editable in the basic dipole form only when the
   folded-dipole template is selected. The estimator, catalog, and change
   template routes start at 4:1. The frequency-first **Estimate** action
   preserves an existing 6:1 or other edited ratio, like the OCFD and T2FD
   matching context.
4. Include `transformer_ratio` in the folded-dipole optimizer descriptor as a
   choice variable, locked by default. Unlocking it lets the optimizer compare
   1:1, 4:1, 6:1, and other practical ratios. The optimizer target remains
   transmitter-side: with a 4:1 transformer, a 50 Ω target corresponds to about
   200 Ω at the antenna.
5. Apply the candidate transformer ratio to every optimization point. Before
   this change the optimizer reused the starting spec's ratio, so a changed
   transformer variable did not affect the simulated impedance. The fix also
   applies to OCFD, T2FD, and end-fed descriptors that expose the variable.
6. Persist the ratio in the folded-dipole payload and bump the project schema to
   41. The migration writes the 4:1 reference value. The current workspace has no
   pre-existing folded-dipole projects that require the old 1:1 behavior; if a
   future compatibility policy needs it, the migration can branch on the stored
   ratio instead.
7. Document that the transformer is ideal. Balun insertion loss can be entered
   separately through the project balun/unun loss model; common-mode current,
   choking, and balance are not modeled.

## Consequences

Positive:

- New folded dipoles no longer report an avoidable 5–6 SWR floor caused by the
  missing 4:1 transformation.
- The 50 Ω optimizer target becomes physically meaningful: with a 4:1
  transformer, it seeks about 200 Ω at the antenna.
- The ratio is explicit in the design, project file, reports, and construction
  sheet.
- The optimizer now evaluates the transformer ratio it claims to evaluate for
  every family that exposes the variable.

Limitations:

- A 4:1 transformer on a ~267 Ω folded dipole leaves about 67 Ω, so the residual
  SWR is about 1.3. An exact 50 Ω match still requires a matching network or a
  different ratio.
- The model is an ideal transformer. It does not represent a real balun's
  frequency response, losses, power handling, or common-mode choking.
- The folded dipole is a balanced antenna. A real installation still needs a
  balun or choke for the balanced-to-unbalanced transition; an L-network alone
  does not provide that function.
- The 4:1 default is a starting point. The actual feed impedance depends on
  spacing, height, ground, and the installed environment.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Keep the raw 1:1 model and rely on the user to add a matching network | The optimizer target is misleading and new designs start with a known, avoidable mismatch |
| Hard-code 4:1 in the solver | It would hide the design choice and prevent 6:1 or measured-ratio designs |
| Default to 6:1 | It can fit a 300 Ω feed better, but 4:1 is the common folded-dipole balun; 6:1 remains editable |
| Model a physical balun | No traceable frequency-dependent balun model is available; an ideal ratio plus the existing loss model is honest and testable |
