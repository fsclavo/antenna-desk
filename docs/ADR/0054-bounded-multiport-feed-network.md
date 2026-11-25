# ADR-0054 — Bounded multiport feed-network ports and Wilkinson splitter

- **Status:** proposed 2026-11-25; implementation gated by the prototype and
  acceptance criteria below
- **Date:** 2026-11-25
- **Related:** DL6, [ADR-0049](0049-stacked-yagi-composed-family.md),
  [`spikes/dl6-feed-network-spike.md`](../spikes/dl6-feed-network-spike.md),
  [`AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) §DL6

## Context

The current DL6 feed model is a bounded co-simulation:

- an ideal N-way splitter with a user-entered excess loss;
- lossless NEC two-port TL cards from a numerical splitter node to every level;
- per-port network connection results;
- a matched line loss plus a load-mismatch correction from each level port
  impedance.

It does **not** model splitter return loss, port-to-port isolation, internal
S-parameters, per-level matching networks, folded driven elements, or per-level
transformers.

A scalar "isolation loss" or a post-processing return-loss correction is not
acceptable. Isolation is not a through-path loss, and a scalar correction would
not re-solve the antenna currents, mutual coupling, or combined pattern. It
would be a number, not a model.

The feed-network spike found that a temporary two-way Wilkinson probe using the
current canonical model was invalid: the ground-clearance rule lifted the node
wires and the 50 Ω loads sat in series in floating wires instead of across
explicit ports. The topology is expressible with NEC TLs and a resistor, but
the canonical model needs an explicit port/reference abstraction first.

## Reference

The bounded splitter uses the standard Wilkinson topology (E. J. Wilkinson,
"An N-Way Hybrid Power Divider", *IRE Transactions on Microwave Theory and
Techniques*, 1960) and NEC-2 `TL`/`LD` cards. The prototype must be compared
with that reference or a trusted circuit solver; no numeric tolerance is
invented here.

## Decision

1. **Add an explicit network port/reference abstraction** to the canonical model
   before any splitter isolation work. A port is defined between a node and a
   common reference; the NEC adapter must preserve that reference and report
   per-port voltage, current, impedance, and power from the network connection
   table.
2. **Model a bounded Wilkinson/corporate splitter** at a declared design
   frequency using canonical TLs and a resistor:
   - a two-way Wilkinson prototype first;
   - then three- and four-way corporate networks built from validated two-way
     sections.
3. **Keep the current ideal/excess-loss splitter as the default and fallback.**
   The Wilkinson mode is opt-in and narrowband; the UI and reports must state
   its design frequency and range limitation.
4. **Do not add a general N-port S-parameter engine or an external circuit
   solver in this ADR.** That path needs its own cost, license, and benefit
   ADR.
5. **Do not add a scalar isolation or return-loss post-processing correction.**
6. **Keep per-level matching, folded driven elements, and per-level
   transformers out** until the port model and a single-level matching
   subcircuit are validated.

## Implementation phases

### Phase 1 — Port/reference abstraction

- Add a canonical port type or an explicit reference-node convention.
- Make the NEC adapter emit the reference without the ground-clearance lift
  breaking the circuit.
- Keep the existing antenna feed, splitter node, and TL behavior unchanged when
  the new abstraction is unused.

### Phase 2 — Two-way Wilkinson prototype

- Build a two-way divider from two quarter-wave TLs and one isolation resistor.
- Compare the input impedance, output power split, and isolation with the
  standard Wilkinson equations or a trusted circuit solver.
- Derive the acceptance tolerance from that reference; do not invent a numeric
  tolerance.
- Add a real `nec2c` regression for the prototype.

### Phase 3 — Three- and four-way corporate splitter

- Build three- and four-way networks from validated two-way sections.
- Report each output port and the input port from the network connection table.
- Add a frequency sweep that shows the expected narrowing; make no broadband
  claim.

### Phase 4 — UI, schema, reports, and BOM

- Add the splitter mode and design frequency to the stacked-Yagi feed
  specification with a schema migration.
- Show the design frequency and narrowband limitation in the editor, help,
  design summary, construction sheet, and BOM.
- Keep the ideal/excess-loss mode selectable and clearly labeled.

### Follow-up — Per-level matching

- Reuse the port/reference abstraction.
- Synthesize one L/Pi/T network as a canonical subcircuit at a single level.
- Compare its input impedance with the analytic two-port or a trusted circuit
  solver.
- Only then apply it to every level; require the currents and pattern to change
  with the match, not only a reported SWR.

## Acceptance criteria

### Splitter slice

- Explicit input and output ports with a common reference.
- A two-way Wilkinson compared with the standard equations or a trusted circuit
  solver; tolerance derived from that reference.
- A three- or four-way corporate network built from validated two-way sections.
- A real `nec2c` regression for input impedance, output power split, and
  isolation.
- A frequency sweep showing the expected narrowing; no broadband claim.
- The current ideal/excess-loss mode remains selectable.
- The UI, reports, BOM, and documentation state the design frequency and the
  narrowband limitation.

### Per-level matching follow-up

- A single-level L/Pi/T subcircuit validated against an analytic two-port or a
  trusted circuit solver.
- Antenna currents and pattern change with the match, not only a reported SWR.
- A two-level stack test with per-port results.
- No post-processing-only claim.

## Consequences

- Splitter isolation remains unavailable until Phase 1 and Phase 2 pass.
- The current ideal/excess-loss model stays the default; no existing result is
  invalidated.
- The Wilkinson mode will be narrowband and opt-in. It will not be a general
  S-parameter block.
- Per-level matching and folded driven elements remain unavailable in the
  meantime. The beta/hairpin match remains the only per-level match.
- A new schema migration is required when the splitter fields are added; this
  ADR does not change the schema.

## Risks

| Risk | Mitigation |
|---|---|
| Port/reference change breaks the existing antenna feed | Add it as an additive abstraction; keep the current path unchanged when unused |
| Ground-clearance rule lifts port reference wires | Define the reference explicitly and test it in the adapter |
| Narrowband splitter surprises users | Require a declared design frequency and a frequency-sweep limitation in the UI/report |
| Component synthesis changes the pattern | Validate currents and pattern, not only SWR |
| New dependency for a general S-parameter solver | Separate ADR with cost, license, and benefit |
| Schema growth | Plan and test the migration before implementation |
