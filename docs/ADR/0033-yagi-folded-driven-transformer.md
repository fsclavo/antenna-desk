# ADR-0033 — Yagi folded-driven feed transformer

- **Status:** Accepted
- **Date:** 2026-11-12
- **Related:** [ADR-0018](0018-t2fd-termination-and-transformer.md),
  [ADR-0031](0031-folded-dipole-feed-transformer.md)

## Context

A Yagi can use a folded driven element. The folded element is a balanced,
higher-impedance feed, and a 4:1 current balun is a common starting choice. The
same antenna can instead use a straight driven element with a beta/hairpin
matching stub. Those two driven-element topologies are mutually exclusive in
the model.

Before this decision, `YagiParameters` had no transformer ratio. The editor
exposed the folded option and the beta/hairpin match, but the simulation always
used `feed_transformer_ratio = 1.0`. The UI help therefore said the feed
impedance was not the reference impedance and told the user to tune the
matching.

A blind 4:1 default is not safe for every Yagi. The folded element's impedance
depends on element length, spacing, and height, and the NBS starting preset is
not necessarily resonant at the scaled frequency. A 4:1 transformer helps the
resistive part but does not cancel a large reactance. A beta/hairpin match also
transforms impedance, so combining it with a 4:1 transformer can double-match.

## Decision

1. Add `transformer_ratio: float = 1.0` to `YagiParameters`. The domain default
   remains 1.0 so straight Yagis and existing projects keep their raw feed.
2. When the editor's **Folded driven element** option is enabled, set the
   transformer ratio to 4:1 if it is currently 1.0. The field remains editable
   to 1:1, 6:1, or another value.
3. Show the transformer field only when folded is active. With a beta/hairpin
   match, force the ratio to 1.0 so the two matching mechanisms are not
   cascaded silently.
4. Apply the ratio through `SimulationSpec.feed_transformer_ratio` in the Yagi
   simulation spec. Keep it out of the NEC geometry. The existing link budget
   then reports transmitter-side impedance, SWR, mismatch loss, and realized
   gain.
5. Include `transformer_ratio` in the Yagi optimizer only when the driven
   element is folded. It is a choice variable and is locked by default. The
   optimizer target remains transmitter-side. The default Yagi objective stays
   MAX_GAIN; users who choose TARGET_IMPEDANCE or MIN_SWR see the transformer
   effect.
6. Preserve the ratio through `YagiParameters.to_custom_parameters()` and
   `from_custom_parameters()` via the generic custom `feed_transformer_ratio`.
7. Persist the ratio in the Yagi payload and bump the project schema to 43. The
   migration writes 1.0 so existing Yagis keep their behavior; new folded
   designs and the NBS folded preset start at 4:1.
8. Document that the transformer is ideal. Balun insertion loss can be entered
   separately through the project balun/unun loss model; common-mode current,
   choking, and balance are not modeled.

## Consequences

Positive:

- A folded driven element now has an explicit, editable 4:1 starting
  transformer instead of an unexplained raw-impedance SWR.
- The beta/hairpin match and the folded transformer cannot be combined
  accidentally in the editor.
- The ratio is visible in the design summary, construction sheet, project file,
  and optimizer.
- Custom-wire conversion preserves the transformer ratio.

Limitations:

- A 4:1 transformer alone may not bring a reactive folded Yagi to a low SWR.
  The element geometry, beta/hairpin match, or a matching network may still be
  required.
- The model is an ideal transformer. It does not represent a real balun's
  frequency response, losses, power handling, or common-mode choking.
- The folded Yagi is a balanced antenna. A real installation still needs a
  balun or choke for the balanced-to-unbalanced transition.
- The default Yagi optimizer objective remains MAX_GAIN; the transformer is a
  feed choice, not a gain mechanism.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Default every folded Yagi to 4:1 in the domain | A folded Yagi with a reactive or mistuned feed may not improve, and existing projects would change silently |
| Always show the transformer field | It invites double-matching with a beta/hairpin and adds noise to straight Yagis |
| Use a 1:1 transformer field for every Yagi | A 1:1 ideal transformer does not change the modeled SWR and would imply a common-mode model that does not exist |
| Model a physical balun | No traceable frequency-dependent balun model is available; an ideal ratio plus the existing loss model is honest and testable |
