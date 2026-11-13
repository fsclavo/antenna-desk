# ADR-0035 — Project BOM cost record

- **Status:** Accepted
- **Date:** 2026-11-12
- **Related:** [ADR-0027](0027-construction-view-policy.md),
  [ADR-0034](0034-current-balun-record.md)

## Context

The construction sheet and package already derive a conductor BOM and a
practical hardware BOM from the design. Builders still need a place to record
the unit prices they actually pay and see a project total. AntennaDesk is
local-first and does not include a price catalog, supplier API, or currency
conversion service.

## Decision

1. Add an optional project-level `BomCostRecord` with a free-form currency label
   and manual `BomCostLine` records.
2. Key every line by a stable BOM row identifier:
   `conductor:<material>:<diameter_mm>` for grouped conductors and
   `hardware:<row_key>` for the hardware rows. The hardware `Antenna conductor`
   row is not costable because the conductor BOM already carries the
   material/diameter cost.
3. A blank or zero unit cost means **no cost**. The total sums the entered line
   totals (`quantity × unit cost`). There is no tax, shipping, labor, or price
   history.
4. Persist the record with the project and include it in undo/redo. Bump the
   schema to 45; older projects migrate with no record.
5. Show the cost columns and total in the construction sheet and native PDF,
   the total in the construction package notes, and the cost columns in the
   conductor BOM CSV. The hardware BOM costs are shown in the sheet and PDF; the
   existing conductor-only `bom.csv` keeps its historical four-column format when
   no costs are present.
6. Keep the record independent of the solver and the electrical model. It does
   not change impedance, SWR, gain, or any simulation result.

## Consequences

Positive:

- Builders can keep a project-specific budget without a price service.
- Unit costs survive project save/open and design changes.
- The construction sheet, native PDF, and package total show the same manual
  costs as the editor.

Limitations:

- Prices are user-entered; the app does not validate them against a supplier.
- Unknown cost keys are retained when the design changes, but only the current
  design's rows are shown and totaled.
- There is no currency conversion, tax, shipping, labor, or quote history.
- The hardware BOM CSV is not added; hardware costs appear in the sheet and PDF.
