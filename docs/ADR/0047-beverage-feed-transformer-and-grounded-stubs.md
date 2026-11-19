# ADR-0047 — Beverage feed transformer and grounded stubs

- **Status:** Accepted
- **Date:** 2026-11-19
- **Related:** [ADR-0030](0030-feed-chain-topology.md),
  [ADR-0031](0031-folded-dipole-feed-transformer.md),
  [ADR-0018](0018-t2fd-termination-and-transformer.md)

## Context

A Beverage is a traveling-wave receiving antenna. Its design goal is a
unidirectional end-fire pattern, not a 50 Ω match. The published starting
dimensions are a one-wavelength horizontal wire, a 500 Ω far-end termination,
and a height of 6–10 ft. The 500 Ω resistor terminates the traveling wave; it is
not the feedpoint impedance. A Beverage feedpoint is normally a few hundred
ohms, so a 50 Ω transmitter or receiver needs a transformer (typically 9:1 or
10:1) or a high-impedance feed line.

Before this decision, `BeverageParameters` had no transformer field and the
model fed the first segment of the horizontal wire. The NEC adapter also raised
the whole model by 1 cm whenever any wire touched `z = 0`. The far-end
termination stub therefore ended 1 cm above ground, leaving the 500 Ω resistor
in an open stub. The simulated feedpoint was highly reactive and the family
optimizer, whose default target is 50 Ω, stalled around 34–40:1 even after
moving length, height, and termination resistance.

## Decision

1. Add `transformer_ratio: float` to `BeverageParameters`, default `9.0`. The
   ratio is editable and is applied through the existing ideal transformer in
   `SimulationSpec.feed_transformer_ratio`; it is not part of the NEC geometry.
   A value of `1.0` shows the raw antenna impedance.
2. Add a short vertical feed stub at the near end and put the primary feed on
   the stub's ground-referenced base. This gives NEC a real wire-to-ground port
   instead of a source embedded in the first horizontal segment.
3. Keep the far-end termination stub connected to ground. The NEC ground
   clearance is applied only when a wire lies in or near the ground plane; a
   vertical wire ending on the ground plane keeps its endpoint at `z = 0`.
   Ground-mounted radials and horizontal wires at ground level keep the 1 cm
   approximation and its warning.
4. Include `transformer_ratio` in the Beverage optimizer descriptor as a choice
   variable with 1:1, 4:1, 9:1, and 16:1 choices. The default objective remains
   `TARGET_IMPEDANCE`, now referred to the transmitter side of the ideal
   transformer. The optimizer evaluates the candidate ratio at every point.
5. Expose the ratio in the inline editor, New Antenna dialog, geometry summary,
   design summary, construction sheet, and Spanish/English help. The default
   editor and catalog route use 9:1.
6. Persist the field in `BeverageParametersPayload` and bump the project schema
   to 56. The no-value-rewrite migration adds `transformer_ratio = 9.0` to
   existing Beverage designs.
7. Document the transformer as an ideal matching assumption. Its loss is not
   modeled; the project balun/unun loss model can record an external loss.

## Consequences

Positive:

- The optimizer can now reach a low SWR after the transformer instead of
  chasing a physically impossible 50 Ω feedpoint.
- The termination resistor actually absorbs the traveling wave, so pattern,
  impedance, and termination studies are meaningful.
- The transformer ratio and grounded feed geometry are explicit in the design,
  project file, reports, and construction sheet.
- Real NEC2C regression coverage proves a Beverage can reach a transformed SWR
  below 2.5 with the optimizer.

Limitations:

- The 9:1 default is a practical starting assumption, not a published value.
  The actual feedpoint impedance depends on height, length, ground, and the
  termination, so the optimizer or a measurement should confirm the ratio.
- The transformer is ideal: frequency response, core loss, power handling, and
  common-mode choking are not modeled.
- The feed and termination stubs are short vertical wires, not a complete
  ground system. Soil conductivity and the real ground electrode remain
  approximations.
- NEC-2 does not model buried conductors. The grounded vertical endpoint is a
  wire-to-ground connection at the ground plane, not a buried rod.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Add only a transformer field and keep the old feed model | The termination stub remains disconnected and the source is not a real wire-to-ground port, so the impedance is still wrong |
| Keep the 1 cm lift for every model | It intentionally disconnects the Beverage termination and feed stubs; the existing warning is not sufficient for a grounded antenna |
| Default to 16:1 | The optimizer found 16:1 useful in one test, but 9:1 is the common Beverage unun and a safer starting point; 16:1 remains searchable |
| Model a physical transformer | No traceable frequency-dependent Beverage transformer model is available; an ideal ratio plus external loss is honest and testable |
