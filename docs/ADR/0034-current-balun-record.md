# ADR-0034 — Project current-balun record and balanced-feed note

- **Status:** Accepted
- **Date:** 2026-11-12
- **Related:** [ADR-0014](0014-l-network-post-processing.md),
  [ADR-0018](0018-t2fd-termination-and-transformer.md),
  [ADR-0031](0031-folded-dipole-feed-transformer.md),
  [ADR-0033](0033-yagi-folded-driven-transformer.md)

## Context

The ideal feed transformers added for folded dipoles, loops, OCFD, T2FD, and
end-fed designs represent impedance ratios. They do not model a real balun's
common-mode choking or the balanced-to-unbalanced transition. Balanced families
such as dipoles, loops, Yagis, Moxons, quads, hexbeams, biquads, fan/trap/loaded
dipoles, inverted Vs, T2FDs, Zepps, and doublets normally need a **current
balun or choke** at the feed.

Before this decision, the application warned about this only in scattered
family help and documentation. The Feed & matching summary showed the project
matching network, feed line, and matched balun/unun loss, but it had no record
of whether the physical current balun was installed. The optimizer and reports
had no common statement of the balanced-feed requirement.

## Decision

1. Add a project-level `current_balun: bool` record. It is a construction note,
   not an electromagnetic model. It does not affect geometry, impedance, SWR,
   gain, or the feed transformer ratio.
2. Classify families with a balanced feed in
   `domain/design/feed_balance.py`. The classifier drives the UI note and the
   construction sheet. It covers dipoles, folded dipoles, loops, inverted Vs,
   Yagis, Moxons, quads, hexbeams, biquads, fan/trap/loaded dipoles, T2FDs,
   off-center-fed dipoles, SCV arrays, Zepps, and transmission-line doublets.
   It excludes unbalanced verticals, inverted Ls, end-fed wires, J Poles,
   Ringos, discones, phased verticals, and Beverages. Custom geometry and
   magnetic loops are classified as **unknown**, so the UI asks the user to
   verify rather than claiming the feed is unbalanced.
3. Add a **Current balun/choke installed** checkbox and a balance note to the
   Feed & matching summary. For a balanced design without the record, the note
   says a current balun/choke is normally required. With the record, it says
   the balun is recorded and that common-mode choking is not modeled. For an
   unbalanced design, it says the family does not require one.
4. Persist the record on the project and include it in the undo/redo snapshot.
   Bump the project schema to 44; older projects migrate with `False`.
5. Include the record in the HTML report, native PDF reports, and construction
   sheet feed/matching rows. Add a construction-sheet note for balanced
   families that states whether the balun is recorded.
6. Keep the matched insertion-loss model (`BalunLoss`) separate. The current
   balun record says the hardware exists; the loss model estimates its
   dissipation. The two are not merged and neither models common-mode current.

## Consequences

Positive:

- The app now states a physical requirement that was previously buried in
  family-specific help.
- The project can record the installed current balun without pretending to
  simulate common-mode behavior.
- The note and record appear consistently in the feed summary and reports.
- The record is undoable and persisted with the rest of the feed chain.

Limitations:

- The record is project-global, like the feed line and matching network. A
  multi-antenna project shares one current-balun record.
- The classifier is a construction heuristic. A user may install a choke on an
  unbalanced antenna or omit one on a balanced antenna; the app does not judge
  the installation.
- Common-mode current, choke impedance, balun balance, and mode conversion are
  still not modeled.
- The current-balun record does not change simulated SWR or gain.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Add a per-family boolean | It would duplicate schema and UI across many families for a project-level feed item |
| Add a `1:1` ideal transformer | A 1:1 ideal transformer does not change the modeled SWR and would falsely imply a common-mode model |
| Use only family help and documentation | The requirement is too easy to miss and does not appear in reports or the feed summary |
| Put the flag inside `BalunLoss` | The flag is hardware presence, while `BalunLoss` is a matched insertion-loss model; keeping them separate is clearer |
