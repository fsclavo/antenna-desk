# ADR-0010 — First-class generator templates

- **Status:** Accepted
- **Date:** 2026-10-30
- **Supersedes:** none

## Context

Generated antennas (Yagi, inverted-V, vertical, OCFD) were initially stored as
`CustomAntennaParameters` plus generator metadata. The left design panel then
showed the generic custom-wire view, while parameters could only be changed in
modal generator dialogs. This was inconsistent with native dipole/folded/loop
templates and made the catalog experience feel fragmented.

## Decision

1. Promote generated antennas to first-class entries in
   `AntennaDesignParameters`.
2. Persist each type with its own schema payload and antenna type.
3. Provide inline design-panel editors for Yagi, inverted-V, vertical, and OCFD.
4. Keep `CustomAntennaParameters` for arbitrary wires and legacy generated
   designs.
5. Keep `Edit Generator...` only as a compatibility path for legacy custom
   generated designs; new designs edit inline.
6. Add reporting and construction-sheet branches for each first-class type.

## Consequences

Positive:

- The catalog, Family/Template fields, and design panel now agree.
- Generated designs behave like native templates for save/open and editing.
- Custom wires remain the escape hatch, not the default representation.

Limitations:

- More parameter types and schema mappings must be maintained.
- Legacy custom generator designs are not automatically migrated.
- Yagi and other complex editors need dedicated UI tests.
