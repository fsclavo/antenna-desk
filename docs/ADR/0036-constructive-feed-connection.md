# ADR-0036 — Constructive feed-connection detail

- **Status:** Accepted
- **Date:** 2026-11-13
- **Related:** [ADR-0030](0030-feed-chain-topology.md),
  [ADR-0031](0031-folded-dipole-feed-transformer.md),
  [ADR-0033](0033-yagi-folded-driven-transformer.md),
  [ADR-0034](0034-current-balun-record.md)

## Context

`AntennaModel.feed` stores one `FeedPoint(wire_id, offset_m)`. The NEC deck
applies an ideal source across the segment at that point. The canonical model
has no two-terminal port, no center/shield assignment, no balun topology, and
no common-mode current. The construction sheet can therefore describe
dimensions and give prose notes, but it cannot show the physical feed wiring.

The Yagi is the clearest example. A straight driven element without a balun is a
center-fed dipole: one half goes to the coax center and the other to the shield.
That is a direct but unbalanced feed of a balanced antenna; the shield carries
common-mode current unless a current balun/choke is installed. A folded driven
element is different: it has two parallel conductors joined at both ends, and
the feed is a gap in one conductor. A beta/hairpin is a shorted matching stub
across the driven-element gap; it is not a balun. A gamma match is not modeled.

## Decision

1. Add a read-only `FeedConnectionDetail` resolved from the design parameters,
   the canonical model, and the existing project feed records. It is a
   construction artifact, not a solver input.
2. Keep four states separate: **modeled**, **recorded**, **recommended**, and
   **not modeled**.
3. Resolve detailed terminals for the supported topologies and return an
   explicit `UNKNOWN` connection for families whose physical mapping is not
   encoded. Never infer the center/shield assignment from the wire count.
4. Show the result in the Feed & matching summary, a read-only
   `FeedConnectionDialog`, the HTML construction sheet, the native PDF, and the
   ZIP package.
5. Render the schematic from a renderer-neutral SVG builder. The schematic is
   marked **not to scale** and is separate from the canonical geometry scene.
6. Do not change `FeedPoint`, the NEC deck, the solver, simulation results, or
   the project schema in this phase. Common-mode current, real balun balance,
   frequency response, power handling, and gamma/delta matches remain
   unmodeled.

## Consequences

Positive:

- The user can see which conductor goes to which terminal and whether the
  family normally needs a current balun, a transformer, or a direct coax feed.
- The construction sheet and PDF carry the same connection table and limits as
  the UI.
- The detail is derived, so existing projects need no migration.
- Unsupported or custom geometries are explicit instead of guessed.

Limitations:

- The connection table is a construction aid, not a validated electrical model.
- The balun/unun loss remains a matched scalar attenuation.
- The current-balun record is project-global.
- The feed gap and real hardware dimensions are not modeled; they can be
  recorded as as-built data.
- Multi-port arrays and balanced feed lines are represented only at a summary
  level.

**Update 2026-11-17 (UX31):** the schematic now draws a real coax cable with a
cross-section and uses a distinct drawing per interface. The data model,
connection table, and the decision above are unchanged.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Put the connection text only in the user guide | It is easy to miss and does not appear in the construction sheet |
| Change `FeedPoint` to a two-terminal port | It would ripple through the solver, importers, persistence, and every family; the constructive detail does not need it |
| Draw a synthetic feed gap in the canonical sketch | It would violate the geometry presentation contract and misrepresent the solver geometry |
| Model common-mode current and a real balun now | No traceable frequency-dependent balun or common-mode dataset is available; G27 remains blocked |
