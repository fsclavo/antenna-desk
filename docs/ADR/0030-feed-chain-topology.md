# ADR-0030 — Feed-chain topology and loss budget

- **Status:** Accepted
- **Date:** 2026-11-11

## Context

The original post-processing model always placed the project matching network
at the antenna feedpoint, before the feed line:

```
transmitter → feed line → matching network → antenna
```

That is one valid installation, but many operators use a **shack tuner** before
the coax:

```
transmitter → matching network → feed line → antenna
```

The difference is not cosmetic. With a feedpoint network the line can be
matched and its loss stays close to the matched-line value. With a shack tuner
the line carries the antenna mismatch, so the same coax can dissipate
substantially more power. Reporting the matched-line loss in both cases is
misleading.

The old loss breakdown also reported the matched feed-line loss as the line
component, even under mismatch. Users could not see which stage was responsible
for the largest loss.

## Decision

1. Add **`MatchingNetworkPosition`** with `FEEDPOINT`, `SHACK`, and `NONE`.
   Existing projects and simulation specs default to `FEEDPOINT`, preserving
   the previous behavior.
2. The chain order is:
   - `FEEDPOINT`: transmitter → feed line → matching network → ideal
     transformer → antenna.
   - `SHACK`: transmitter → matching network → feed line → ideal transformer →
     antenna.
   - `NONE`: the matching network is ignored.
3. The family feed transformer remains an ideal impedance ratio at the antenna.
   The project `BalunLoss` remains a **matched insertion loss**. It is not given
   a shack/antenna position because a matched scalar attenuation is
   position-independent. A future measured frequency-dependent balun model may
   justify a position control; the current model does not.
4. `LinkBudget.feed_line_loss_db` and `network_loss_db` are **actual
   dissipative losses** computed from the two-port power balance under the
   modeled source and load impedances, not the matched-line loss. The source
   mismatch at the transmitter reference plane is reported separately.
5. A loss-budget dialog shows the chain order, per-frequency SWR, mismatch,
   line, network, balun, delivered power at the antenna, radiated power, and the
   dominant loss stage. The user can change the transmitter power to scale the
   power columns.
6. The matching-network dialog exposes the position. The feed/matching summary,
   construction sheet, HTML report, and native PDFs include the position.
7. Schema 37 persists the matching-network position in the project and in every
   stored simulation spec. Older projects migrate to `FEEDPOINT`.

## Consequences

Positive:

- A shack tuner no longer silently inherits the low line loss of a feedpoint
  match.
- The loss table identifies the dominant stage under the actual modeled
  impedances.
- The change is backward compatible: old projects and results keep their
  previous feedpoint behavior.

Limitations:

- The shack-tuner line source is modeled as the line's characteristic
  impedance; a real tuner is not perfect, so the input mismatch is approximate.
- The loss components are evaluated under the modeled impedances and may not add
  exactly when mismatch changes between stages.
- Balun position is not modeled because the current balun model is a matched
  insertion loss. Common-mode choke behavior and measured balun data remain out
  of scope.
- The dialog uses the current simulation result; change the chain and simulate
  again to refresh it.
