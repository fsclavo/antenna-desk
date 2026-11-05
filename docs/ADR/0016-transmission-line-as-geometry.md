# ADR-0016 — Transmission line as geometry

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none

## Context

AntennaDesk already supported a uniform **feed line** as post-processing at the
transmitter end. That model transforms impedance and SWR but is not part of the
radiating structure. Families such as G5RV/ZS6BKW, Zepp, log-periodic arrays,
and phased elements require a transmission line that connects two points of the
structure and participates in the current solution.

NEC-2 represents such a line with the `TL` card: a mathematical two-port
connected between two segments. It has a characteristic impedance, an
electrical length, optional shunt admittances, and a phase-reversal flag. The
line does not radiate and NEC-2 models it as lossless.

## Decision

1. Add `TransmissionLine` to the canonical `AntennaModel`. A line stores:
   - stable identifier;
   - start wire identifier and offset;
   - end wire identifier and offset;
   - characteristic impedance in ohms;
   - physical length in metres;
   - velocity factor.
2. Store `length_m` as the physical length. The NEC adapter emits
   `electrical_length_m = length_m / velocity_factor` in the `TL` card, because
   NEC interprets the card length as the free-space-equivalent length.
3. Validate wire references, offsets, impedance, length, and velocity factor in
   the domain model. The line may connect two points on the same wire.
4. Persist lines in the antenna payload and in `CustomAntennaParameters` as an
   optional list. Older projects load with an empty list; no schema migration is
   required.
5. Preserve design-level lines when parameters change, like loads. Keep the
   generic load editor and add a generic transmission-line editor.
6. Draw geometry lines as dashed construction polylines. They are not wires and
   do not count toward the radiating structure.
7. Emit one `TL` card per line after the `LD` cards. The adapter maps each wire
   offset to the **local** segment number within its tag.
8. Add a segmentation warning when a line endpoint is not at the center of its
   mapped segment. NEC connects a TL to the segment, not to an arbitrary point.
9. Keep the existing `FeedLine` post-processing model separate. A project can
   have both:
   - geometry TLs inside the structure;
   - a transmitter feed line applied after the solve.
10. NEC-2 TLs are lossless. Document this limitation. Distributed loss belongs
    to the feed-line post-processing model or a future lossy TL model.

## Consequences

Positive:

- G5RV/ZS6BKW, Zepp, LPDA, and phased-array work can now use structural
  transmission lines.
- The canonical model remains solver-independent; only the NEC adapter knows
  the `TL` card.
- The existing feed-line post-processing remains available for transmitter-side
  loss and impedance transformation.

Limitations:

- The TL is a mathematical two-port and does not radiate.
- NEC-2 TLs are lossless.
- Endpoints are attached to segments; off-center endpoints are approximate.
- A line endpoint that no longer exists after a template change invalidates the
  design until the line is edited or removed.
- Physical parallel-wire models and multi-line coupling are not implemented.

## Follow-ups

- Refined Zepp model with a real second matching conductor and an explicit
  unmodeled 1:1 choke requirement (2026-11-05). G5RV and ZS6BKW continue to use
  the mathematical TL; the Zepp now uses real stub wires.
- Add a lossy TL model or map line loss to equivalent shunt/load terms.
- Add crossed-line/phase-reversal support for phased arrays.
- Add a dedicated pattern/geometry distinction between physical wires and
  mathematical connections in exports.
