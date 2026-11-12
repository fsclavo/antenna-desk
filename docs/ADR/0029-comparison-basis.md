# ADR-0029 — Common comparison basis

- **Status:** Accepted
- **Date:** 2026-11-11
- **Supersedes:** the stored-result comparison behavior of the original A/B dialog

## Context

The first comparison dialog displayed two stored simulation results side by
side. Those results could have been produced with different frequency plans,
ground models, feed lines, matching networks, or installation heights. That is
useful for inspecting two designs, but it is not a fair comparison: the table
could imply that one antenna is better when the difference comes from the
conditions rather than the antenna.

Comparison 2.0 must compare two to four designs under an explicit common basis.
The basis also has to work for different antenna families, whose ``height``
field does not always mean the same thing: a dipole height is the wire height, a
Yagi height is the boom centerline, an inverted-V height is the apex, and a
vertical height is the radiator length above its base.

## Decision

1. A comparison is defined by a **`ComparisonBasis`** with:
   - a common frequency plan (start, stop, points);
   - a common ground model;
   - an optional reference height;
   - a reference frequency used for impedance, SWR, and pattern comparison.
2. The project-level feed line, matching network, and balun loss remain common
   to every selected design. They are part of the project chain, not the basis.
3. The dialog shows the basis explicitly and requires an explicit **Recompute**
   for a new basis. Stored results are not silently presented as comparable.
4. The recompute runs each selected design through the existing solver with the
   common frequency plan and ground. It does not create a new electromagnetic
   model.
5. Height mapping is conservative:
   - Families with a directly comparable height field are moved to the
     reference height: dipole, folded dipole, loop, magnetic loop, OCFD, trap
     dipole, Yagi, Moxon, hexbeam, trapped Yagi, quad beam, doublet, T2FD,
     loaded dipole, and Beverage.
   - Omni horizontal families with an apex are moved at the apex: inverted-V and
     fan dipole, provided the resulting ends stay above ground.
   - Vertical families are shifted by their base height so the radiator top
     reaches the reference height. A reference below the radiator height is
     rejected for that design and its native height is kept with a warning.
   - Ambiguous families keep their native height and show a warning:
     end-fed/sloper/random wire, inverted-L, Zepp, J Pole, Slim Jim, Ringo,
     discone, biquad, half-square/bobtail, loaded vertical, and custom wire
     geometry.
   - The user can choose **Native heights** to disable height mapping
     explicitly. Ground is still normalized.
6. The dialog supports two to four designs. It renders a metric table with
   design columns, a band-summary table when band analyses exist, overlaid SWR
   and pattern charts, and size/BOM rows (footprint, maximum height, conductor
   length, wire/load/line counts).
7. The height and footprint values used by the comparison are heuristics, not
   validated construction dimensions. The basis and its mapping warnings are
   visible in the dialog.

## Consequences

Positive:

- Comparisons are reproducible and state their conditions.
- A design is never presented as better only because it was simulated with a
  lower ground loss or a different frequency plan.
- The height mapping is explicit, testable, and shown to the user.

Limitations:

- Height mapping is conservative and intentionally incomplete for families
  whose native height is ambiguous.
- The common ground may not represent the real site; the user must choose it.
- The common frequency plan can hide band-specific behavior; band analyses and
  the current pattern selector remain the way to inspect individual bands.
- The comparison still uses the project feed chain, so designs with different
  feed hardware require separate projects or variants.
- No new validation is claimed for the recomputed results; the evidence level
  of each template still applies.
