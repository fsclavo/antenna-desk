# ADR-0009 — Catalog generators and experimental templates

- **Status:** Accepted
- **Date:** 2026-10-30
- **Supersedes:** none

## Context

AntennaDesk is used for experimentation. Most user designs will be modified or
invented geometries with no published reference. Blocking every new template on
an independent numerical reference prevents the product from serving its main
use case, while presenting unvalidated templates as exact would be misleading.

## Decision

1. Separate solver validation from template/generator validation.
2. Keep the NEC adapter and normalization strictly reference-validated.
3. Introduce evidence levels for designs: reference-backed, published/heuristic,
   and experimental.
4. Allow generators and arbitrary geometries without an external oracle, but
   require structural tests, visible limitations, and no unqualified accuracy
   claims.
5. Use metric-specific tolerances when a reference exists. A 10% tolerance is a
   reasonable default for many dimensions and heuristic comparisons, not a
   universal rule for gain or nulls.
6. Prefer parametric generators and editable presets over a closed catalog of
   fixed antennas.

## Consequences

Positive:

- Users can design and simulate original antennas.
- Reference-backed cases remain regression anchors.
- The UI can distinguish confidence levels without blocking experimentation.

Limitations:

- Experimental templates need careful labeling and documentation.
- Structural tests do not prove electromagnetic accuracy.
- Evidence metadata must be maintained as the catalog grows.

## Follow-ups

- Add a persisted evidence level to generated designs.
- Add a catalog browser with filters and preset provenance.
- Expand reference tests where primary sources are available.
