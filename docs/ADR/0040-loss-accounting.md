# ADR-0040 — Feed-chain loss accounting and double-counting policy

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Fernando Sclavo, development
- **Related:** G27 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md);
  ADR-0039 (coax attenuation); EF7b (transformer loss); EF8 (feedpoint choke)

## Context

AntennaDesk now has several loss mechanisms:

- NEC conductor and load dissipation, including an optional feedpoint
  common-mode choke modeled as a NEC series load;
- source/load mismatch at the transmitter-end two-port;
- feed-line dissipative loss, including the optional frequency-dependent
  attenuation table;
- project matching-network dissipative loss;
- project balun/unun loss;
- optional measured transformer loss.

The risk is double counting: a loss may be present in the NEC power budget, in
the two-port cascade, and in a post-processing row at the same time. A second
risk is the opposite: a row may be missing while the reported realized gain
already includes it.

## Decision

Keep one accounting rule:

1. **NEC power budget:** conductor loss, lumped-load dissipation (including the
   feedpoint common-mode choke), and radiated power. These are antenna-model
   losses and are never subtracted again in the link budget.
2. **Two-port cascade:** source mismatch, feed-line dissipation, and matching-
   network dissipation. `dissipative_loss_db()` excludes input mismatch; the
   input mismatch is reported separately by `reflection_loss_db()`.
3. **Post-processing scalar losses:** project balun/unun loss and measured
   transformer loss. They are not in the ABCD cascade and are subtracted once
   from the transducer gain.
4. **Audit identity:** for a finite transducer gain,
   `mismatch + feed_line + network + balun + transformer` must equal
   `-transducer_gain_db`. `LinkBudget.total_loss_db` and
   `LinkBudget.loss_balance_db` expose this identity.
5. **Disable means zero:** with all optional losses disabled and a matched
   source/load, the total loss and transducer gain are both zero.
6. **UI/report labeling:** the sum is called **Total feed-chain loss** and is
   distinct from the NEC antenna power budget. The common-mode choke is a NEC
   load, not a feed-chain scalar row.

## Consequences

- The audit is testable without new measurements or schema changes.
- A future loss model must declare which layer it belongs to and update the
  audit test.
- The report total is a feed-chain total, not the complete antenna efficiency;
  NEC conductor/load loss and radiated power remain in the power budget.
- A finite but mismatched link can still have a large total loss; that is
  expected and is not double counting.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Add every loss row into realized gain | Double counts mismatch and dissipative losses already in the two-port cascade |
| Put the choke resistance in the link budget | The choke is a NEC load; its dissipation belongs to the antenna power budget |
| Hide the total and show only components | Users cannot see whether the component rows are consistent |
| Make the audit a hard simulation error | Numerical roundoff and future models should not abort a valid simulation; tests enforce the identity |

## Validation plan

1. Test the audit identity for matched, mismatched, line, network, balun,
   transformer, and combined scenarios.
2. Test that all optional losses disabled and a matched link are ideal.
3. Test the report **Total feed-chain loss** row.
4. Keep the full gate green.
