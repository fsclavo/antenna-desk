# ADR-0054 — N-port feed-network solver for splitter isolation and matching

- **Status:** accepted 2026-11-25; N-port solver and stacked-Yagi Wilkinson
  mode implemented, tested, and exposed
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

The feed-network spike showed that a geometry-only NEC port builder is not
reliable. A first probe was lifted by the ground-clearance rule and left the
loads in floating wires. A T-junction probe came close with the isolation
resistor effectively open, but loaded with the real resistor. A later clean
T-junction probe produced a negative input resistance and an invalid passive
model. Those results are diagnostics, not references. The geometry-only path
is closed.

## Selected path

Use a small **pure-Python N-port circuit solver** for the feed network instead
of persuading NEC's wire/segment model to behave as a circuit simulator:

1. NEC computes the **antenna short-circuit admittance matrix** at the existing
   level feed ports. Each port is driven with 1 V while the other ports are held
   at a near-zero 1 µV source. The 1 µV value is a nec2c workaround because a
   zero EX voltage is treated as the default 1 V excitation.
2. The feed network (transmission lines, resistors, and later matching
   networks) is solved as a nodal admittance network in Python.
3. The antenna admittance matrix is connected to the feed-network output ports;
   the input port is driven by a current source. The solver returns the input
   impedance, per-port powers, and network loss.
4. The feed-network S-matrix is available for validation against the standard
   Wilkinson equations or a trusted circuit solver.

The solver is bounded to small networks (a few ports and internal nodes) and
uses dense Gaussian elimination. It adds no runtime dependency. `scikit-rf` is
a development-only cross-check.

## Reference

The bounded splitter uses the standard Wilkinson topology (E. J. Wilkinson,
"An N-Way Hybrid Power Divider", *IRE Transactions on Microwave Theory and
Techniques*, 1960). The solver's S-matrix is compared with the standard
equations and with scikit-rf in the tests; no numeric tolerance is invented.

## Decision

1. **Use the N-port solver as the feed-network engine** for splitter isolation
   and per-level matching.
2. **Extract the antenna Y-matrix through NEC at the existing level feed ports.**
   No NEC port geometry, ground-clearance change, or adapter port type is
   required for this feature.
3. **Model a bounded equal N-way Wilkinson** at a declared design frequency:
   - quarter-wave branches of `Z0 * sqrt(N)` and a star of `N` isolation
     resistors of `Z0`;
   - two-, three-, and four-way dividers share the same solver.
4. **Keep the current ideal/excess-loss splitter as the default and fallback.**
   The Wilkinson mode is opt-in and narrowband; the UI and reports must state
   its design frequency and range limitation.
5. **Do not add a scalar isolation or return-loss post-processing correction.**
6. **Do not add an external circuit engine or a general S-parameter dependency**
   in this ADR. The bounded Python solver covers the DL6 splitter; a wider engine
   needs its own cost, license, and benefit ADR.
7. **Keep per-level matching, folded driven elements, and per-level
   transformers out** until the single-level L/Pi/T matching slice is validated.

## Implementation (2026-11-25)

- `domain/antennas/feed_network.py`:
  - `NPortNetwork` with series, shunt, and ideal transmission-line branches;
  - port Y-matrix with internal-node elimination;
  - port S-matrix for equal real reference impedances;
  - `solve_feed_network` combining the feed network with an antenna Y-matrix;
  - `two_way_wilkinson` builder.
- `application/feed_network_y.py`:
  - `extract_antenna_y_matrix` drives each port with 1 V and the others with
    1 µV, then reads the source currents.
- Validation:
  - the two-way Wilkinson S-matrix matches the standard equations and
    scikit-rf at the design frequency;
  - a single 50 Ω line into a 50 Ω load is matched, and a quarter-wave 70.71 Ω
    line transforms 50 Ω to 100 Ω;
  - a real two-level stack Y-matrix plus the existing 3-port TL feed network
    matches the NEC co-simulation input impedance within 0.01 Ω and the port
    power ratio within 1e-3;
  - the Wilkinson with the real antenna Y-matrix satisfies the power balance.

The solver is exposed in the stacked-Yagi **Wilkinson divider** mode:

- `FeedNetworkSpec` in `SimulationSpec` and schema 64;
- `WilkinsonFeedSolver` wraps the NEC solver, extracts the antenna Y-matrix,
  solves the N-way Wilkinson and feed lines, and reconstructs the pattern with
  ideal sources at the solved port voltages;
- the editor, help, design summary, and construction sheet show the divider
  design frequency, branch impedance, isolation resistors, feed-line lengths,
  and the ideal/narrowband limitation; the conductor BOM remains
  conductor-only;
- the primary SWR is the splitter input; per-level source results are the
  solved port distribution; the reconstructed power budget is intentionally
  omitted;
- the existing NEC TL network mode remains available.

The solver-side per-level matching branch is also validated: a `TwoPortBranch`
inserts an L/Pi/T network between each feed line and its level port. A common
L-network designed from the real antenna port self-impedance reduced the
two-level stack input SWR from about 14.7 to 1.09 in the real NEC Y-matrix
test. The editor/schema fields for per-level matching remain pending.

## Implementation phases

### Phase 1 — Solver and antenna Y-matrix (done)

- Pure-Python N-port solver.
- Antenna Y-matrix extraction at the existing level feed ports.
- Unit tests against the standard Wilkinson and scikit-rf.
- Real `nec2c` cross-check against the existing TL co-simulation.

### Phase 2 — Three- and four-way N-way divider (done)

- The equal N-way Wilkinson with star isolation covers two to four outputs.
- A frequency sweep shows the expected narrowing; no broadband claim.

### Phase 3 — UI, schema, reports, and BOM (done)

- The Wilkinson mode and design frequency are in schema 64.
- The editor, help, design summary, and construction sheet show the divider
  design frequency, branch impedance, isolation resistors, feed-line lengths,
  and the ideal/narrowband limitation; the conductor BOM remains
  conductor-only.
- The ideal/excess-loss mode remains selectable.

### Follow-up — Per-level matching (solver validated; UI pending)

- Reuse the N-port solver and antenna Y-matrix.
- A `TwoPortBranch` inserts one L/Pi/T network between a feed line and a level
  port; the same network can be applied to every level.
- The branch is validated against the analytic matching-network two-port and
  scikit-rf; a real two-level stack test reduced the input SWR from about 14.7
  to 1.09 with a common L-network.
- The editor/schema fields, per-level values, and optimizer integration remain
  pending.

## Acceptance criteria

### Solver slice (done)

- A two-way Wilkinson compared with the standard equations and scikit-rf.
- A single TL and a quarter-wave transformer validated analytically.
- A real `nec2c` antenna Y-matrix combined with a 3-port TL network matches the
  existing NEC co-simulation input impedance and port power ratio.
- Power balance holds with a mismatched antenna load and with the isolation
  resistor.

### User-facing splitter slice (done)

- Explicit input and output ports with the N-port solver.
- Equal N-way 2–4 dividers with star isolation resistors.
- A real `nec2c` regression for the antenna Y-matrix and feed network.
- A frequency sweep showing the expected narrowing; no broadband claim.
- The current ideal/excess-loss mode remains selectable.
- The UI, reports, and documentation state the design frequency and the
  narrowband limitation.

### Per-level matching follow-up

- A single-level L/Pi/T branch validated against the analytic two-port or
  scikit-rf.
- Antenna currents and pattern change with the match, not only a reported SWR.
- A two-level stack test with per-port results.
- No post-processing-only claim.

## Consequences

- Splitter isolation and return loss can be modeled without NEC port geometry.
- The current ideal/excess-loss model stays the default; no existing result is
  invalidated.
- The Wilkinson mode will be narrowband and opt-in. It is not a general
  S-parameter block.
- Per-level matching and folded driven elements remain unavailable until the
  follow-up slice. The beta/hairpin match remains the only per-level match.
- A schema migration is required when the splitter fields are added.
- The Wilkinson mode is not yet exposed to the family optimizer; optimize the
  spacing and line length in phase-line/network mode and switch.

## Risks

| Risk | Mitigation |
|---|---|
| The NEC Y-matrix extraction is expensive (N runs per frequency) | Keep N at 2–4; cache per design/frequency; document the cost |
| The near-short 1 µV source biases the Y-matrix | Validate against the existing NEC co-simulation; use a small voltage and check reciprocity |
| The solver is not a general circuit simulator | Bound it to small networks; add components only with tests |
| Narrowband splitter surprises users | Require a declared design frequency and a frequency-sweep limitation in the UI/report |
| Per-level matching changes the pattern | Validate currents and pattern, not only SWR |
| Schema growth | Plan and test the migration before implementation |
