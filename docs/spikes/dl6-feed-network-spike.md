# DL6 feed-network spike — splitter isolation and per-level matching

**Date:** 2026-11-25.
**Status:** design spike; no implementation decision yet. The temporary probe
below is decision context, not a validated reference: the deck was not
committed and the result is intentionally not used as a numeric acceptance
value.
**Question:** how should AntennaDesk model a real splitter (return loss,
isolation, S-parameters) and per-level matching without inventing a
post-processing correction that is not physical?

## Sources

- E. J. Wilkinson, "An N-Way Hybrid Power Divider", *IRE Transactions on
  Microwave Theory and Techniques*, 1960 — original divider topology.
- NEC-2 manual, Transmission Line (`TL`) and Load (`LD`) cards:
  <https://www.nec2.org/part_3/cards/tl.html>,
  <https://www.nec2.org/part_3/cards/ld.html>.
- The project `MatchingNetwork` two-port ABCD model for the existing L/Pi/T
  networks.

## Current model

The shipped DL6 feed model has three modes:

- **Ideal phase step:** ideal per-level voltage sources, no splitter hardware.
- **Splitter + phase lines:** ideal sources, line lengths set the phase at the
  design frequency, splitter excess loss is applied to realized gain.
- **Co-simulated TL network:** a 1 cm numerical splitter node, lossless NEC
  two-port TL cards from that node to every level, and per-port network
  connection results. The primary SWR is the lossless splitter-node input.

The network result now applies a matched line loss plus a load-mismatch
correction estimated from each level port impedance. The loss-induced
input-impedance shift is not re-solved.

This is deliberately bounded:

- the splitter is an ideal N-way junction with one user-entered excess loss;
- splitter return loss, port-to-port isolation, and internal S-parameters are
  not modeled;
- per-level matching networks are not modeled;
- folded driven elements and per-level feed transformers remain unavailable;
- the beta/hairpin match is the only per-level match, and it is geometry, not a
  general matching network.

## Why a scalar "isolation loss" is not acceptable

Isolation is not a loss in the through path. An isolation term describes how
much power leaks from one output port to another. Applying it as an extra
insertion loss would make the combined pattern and realized gain wrong, and
would not reproduce the input return loss or the port-to-port coupling.

A post-processing return-loss correction has the same problem: it can change a
reported SWR number, but it does not re-solve the antenna currents, the mutual
coupling, or the combined pattern. That would be a number, not a model.

The project rule is explicit: approximations and limitations must be visible,
and no numerical reference may be invented. The current limitation is honest;
a scalar isolation correction would not be.

## Engine constraints

NEC-2 provides:

- two-port `TL` cards with characteristic impedance and electrical length;
- series/parallel lumped `LD` loads on wire segments;
- network connection points that report per-port voltage, current, impedance,
  and power.

NEC-2 does not provide a general N-port S-parameter block or an arbitrary
two-port matching-network element. A splitter or a matching network can only be
modeled if it is synthesized from TLs and loads, or solved by a separate
circuit engine.

The current canonical model also has an antenna-centric port convention: the
primary feed and additional sources are voltage sources on wire segments, and
the antenna wires provide the return path. The 1 cm splitter node is a
numerical feed point; it is not a general circuit node with an explicit
reference.

## Feasibility probe: a two-way Wilkinson

A temporary probe tried the standard two-way Wilkinson topology at 14.1 MHz:

- 50 Ω system, two quarter-wave 70.71 Ω TLs;
- a 100 Ω isolation resistor between the outputs;
- 50 Ω output terminations;
- three 1 cm node wires, a source at the input node, and the current NEC
  adapter.

The probe did not produce a valid input impedance. The model was lifted 1 cm by
the ground-clearance rule, and the 50 Ω loads sat in series in floating node
wires rather than across explicit ports. The result was a diagnostic, not a
Wilkinson measurement, and is not used as a reference.

**Lesson:** the topology is expressible with NEC TLs and a resistor, but the
canonical model needs an explicit **port/reference abstraction** before a
splitter can be built correctly. Reusing the antenna feed hack is not enough.

## Second probe: T-junction node ports

A second temporary probe moved to a perfect ground plane and a T-junction node:

- 2 cm vertical port wires from ground to the node;
- source/load on the port wire, with separate 1 cm branch wires for the TLs;
- two quarter-wave 70.71 Ω TLs between the input and output branch ends;
- a 100 Ω isolation resistor on a wire between the output nodes;
- 50 Ω output terminations.

With the isolation resistor effectively open (1 MΩ), the input impedance
approached 49.8 + 3.2j Ω (SWR about 1.07). With the 100 Ω isolation resistor,
the input fell to about 37.8 + 2.4j Ω. The outputs were not balanced/isolated in
the NEC network table, so the probe is **not** a validated Wilkinson. The
numbers are diagnostics, not references.

This is closer than the first probe, but it still fails the acceptance test.
The remaining problem is not the TL equation; it is the port definition:
source/load and TL connections land on different segments, the branch polarity
is not explicit, and the network table reports the TL ports without a reliable
common reference. A geometry-only builder cannot guarantee that the source,
load, TL, and reference meet at the same electrical node.

A later clean 10 cm T-junction probe with the isolation wire routed away from
the input node still produced a negative input resistance and an invalid
passive model. That closes the geometry-only path for this feature. The port
model must be adapter-level or circuit-level, not a set of extra wires.

## Splitter options

| Option | What it gives | Cost / risk | Verdict |
|---|---|---|---|
| A. Keep the ideal N-way junction plus excess loss | Honest current model; no false isolation claim | No return loss, isolation, or S-parameters | Keep as the default and fallback |
| B. Bounded Wilkinson / corporate divider from TLs and a resistor | Real return loss and isolation at a declared design frequency; NEC-solvable; standard topology | Narrowband; needs explicit ports/reference, a splitter design frequency, 2-way prototype, and 3–4 way corporate synthesis | **Recommended next ADR**, gated by a prototype |
| C. General N-port S-parameter block with a circuit solver | Arbitrary measured or simulated splitter; broadband with frequency-dependent data | New engine or dependency, port/reference model, S-parameter import/validation, schema/UI/report work | Out of scope for 1.2; needs a separate ADR |
| D. Scalar isolation/return-loss post-processing | Cheap-looking SWR/isolation rows | Not physical; does not re-solve currents or pattern | Reject |

### Recommended splitter path

Open an ADR for a **bounded Wilkinson / corporate splitter** with:

- an **adapter-level port/reference abstraction**, not a geometry-only set of
  extra wires. A port must define its node, reference, polarity, and network
  branch so the source/load and TL meet at the same electrical node;
- a declared splitter design frequency;
- a **single-TL-plus-load calibration** first, then a 2-way Wilkinson, then
  3–4 way as a corporate network of 2-way sections;
- the current ideal/excess-loss mode kept as the default and fallback;
- no broadband or isolation claim outside the modeled frequency range.

A small N-port circuit solver may be simpler and more accurate than forcing
NEC's wire/segment model to behave as a circuit simulator. That choice needs a
separate cost/license/benefit ADR if it adds a dependency.

The prototype must be compared with the standard Wilkinson equations or a
trusted circuit solver. The acceptance tolerance must come from that reference;
it must not be invented. A real `nec2c` regression must cover the port powers
and the input impedance.

## Per-level matching options

| Option | What it gives | Cost / risk | Verdict |
|---|---|---|---|
| A. Keep per-level matching out | Honest boundary; beta/hairpin geometry remains available | No L/Pi/T match at each level | Keep for now |
| B. Synthesize existing L/Pi/T networks as NEC subcircuits at each level | Real per-level match; pattern and currents change with the network | Needs the same port/reference abstraction, per-level geometry, component-to-load translation, and a single-level validation reference | **Follow-up after the port model** |
| C. Ideal per-level transformer only | Simple impedance scaling at each port | Not a matching network; does not change the pattern; easy to mislabel | Do not call it matching; optional only if explicitly labeled |
| D. Post-process the port impedance | Cheap SWR adjustment | Does not re-solve currents or pattern; false claim | Reject |
| E. External circuit engine | General multiport solution | New dependency and engine boundary | Out of scope; separate ADR |

### Recommended per-level matching path

Keep per-level matching out for now. The beta/hairpin geometry is the current
bounded per-level match. A future slice should:

1. reuse the port/reference abstraction from the splitter work;
2. synthesize one L/Pi/T network as a canonical subcircuit at a single level;
3. compare its input impedance against the analytic two-port or a trusted
   circuit solver;
4. only then apply it to every level and report the per-port results.

Do not apply the project matching network to a multiport stack by post-processing
the reported port impedance.

## Folded driven elements and transformers

The folded driven element geometry already exists for a single Yagi. Its 4:1
transformer is a two-port link-budget element applied at the primary port. In a
stack, a per-level transformer or a folded element with a shared transformer
would need the same multiport application. Keep these unavailable until
per-level matching has a physical model.

## Selected path: N-port solver (2026-11-25)

[ADR-0054](../ADR/0054-bounded-multiport-feed-network.md) now records the
selected path: a small pure-Python N-port circuit solver instead of NEC port
geometry.

1. NEC extracts the antenna short-circuit admittance matrix at the existing
   level feed ports. Each port is driven with 1 V; the other ports are held at
   1 µV (a nec2c workaround because zero EX voltage is treated as the default
   1 V source).
2. The feed network is solved as a nodal admittance network in Python:
   transmission lines, resistors, and later matching networks.
3. The antenna Y-matrix is connected to the feed-network outputs; the input
   port is driven by a current source. The solver returns the input impedance,
   per-port powers, and network loss.

### Validation

- The two-way Wilkinson S-matrix matches the standard equations and scikit-rf
  at the design frequency.
- A single 50 Ω line into a 50 Ω load is matched; a quarter-wave 70.71 Ω line
  transforms 50 Ω to 100 Ω.
- A real two-level stack Y-matrix plus the existing 3-port TL feed network
  matches the NEC co-simulation input impedance within 0.01 Ω and the port
  power ratio within 1e-3.
- The Wilkinson with the real antenna Y-matrix satisfies the power balance.

The solver is not yet exposed in the editor, schema, reports, or BOM. The
current stacked-Yagi network mode still uses the NEC TL co-simulation.

## Risks

| Risk | Mitigation |
|---|---|
| The NEC Y-matrix extraction is expensive (N runs per frequency) | Keep N at 2–4; cache per design/frequency; document the cost |
| The near-short 1 µV source biases the Y-matrix | Validate against the existing NEC co-simulation; check reciprocity |
| The solver is not a general circuit simulator | Bound it to small networks; add components only with tests |
| Narrowband splitter surprises users | Require a declared design frequency and a frequency-sweep limitation in the UI/report |
| Per-level matching changes the pattern | Validate currents and pattern, not only SWR |
| Schema growth for new splitter fields | Plan a schema migration before implementation |

## Next step

Add the user-facing Wilkinson mode on top of the validated solver: a declared
design frequency, three- and four-way corporate networks, schema/UI/reports,
and a real `nec2c` regression. Per-level matching remains a follow-up.
