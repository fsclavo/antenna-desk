# ADR-0048 — Yagi mast conductor

**Status:** accepted 2026-11-20.
**Scope:** first support-structure slice for the Yagi family.

## Decision

A Yagi may include one optional vertical mast conductor behind the reflector.
The mast is a normal `Wire` from ground to the boom centerline, with an
operator-entered diameter and horizontal offset. It uses the element material
and radius/diameter fields already modeled by the canonical wire. Zero diameter
disables the mast.

The mast is not connected to the elements. It is a nearby passive conductor,
not a boom or a structural tower model. Boom mounting, guy wires, lattice
towers, insulated/bonded attachments, and interaction with the real rotator or
mast hardware remain unmodeled and are visible limitations.

## Consequences

- No new solver or analysis code; the mast is ordinary wire geometry.
- Schema 57 adds `mast_diameter_m` and `mast_offset_m` with zero defaults.
- The scene, wire schedule, and BOM include the mast when enabled.
- Evidence remains B/C: the mast is a construction starting model, not a
  validated mechanical or electromagnetic reference.
