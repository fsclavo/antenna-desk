# ADR-0002 — Report and data export formats

- **Status:** Accepted; native PDF added later (see Update)
- **Date:** 2026-10-29
- **Deciders:** Fernando Sclavo, development
- **Phase:** 4 — Comparison and reports

## Context

AntennaDesk needs reproducible artifacts from immutable simulation results:
a frequency-sweep data export and a human-readable report with design
parameters, solver metadata, diagnostics, impedance, resonance, and charts.
The application already has PySide6 and PyQtGraph, but adding a plotting/report
stack such as Matplotlib or a PDF engine would add packaging cost and a new
dependency.

Simulation results are currently session-only; the native project schema does
not store simulation runs yet.

## Decision

- Export the frequency sweep as **CSV** with explicit SI unit suffixes in the
  header.
- Generate a **self-contained HTML report** with inline CSS and dependency-free
  inline SVG charts.
- Defer native PDF generation. The HTML report is print-friendly and can be
  saved as PDF from a browser.
- Do not embed the raw NEC input/output in the report; the report references
  the fingerprint and solver metadata. Raw data remains available in the
  application.
- Do not add Matplotlib or a PDF library for Phase 4.

## Consequences

### Positive

- No new runtime dependency for reporting.
- Reports are portable, readable, and reproducible from the immutable result.
- The report includes the model/spec fingerprint and solver version.
- CSV is easy to import into spreadsheets and analysis tools.

### Negative

- Native PDF export was not available when this decision was made.
- The HTML report does not include the raw solver files.
- The SVG chart implementation is intentionally basic.
- Reports require a simulation result from the current session.

### Neutral

- A future PDF adapter can render the same report model without changing the
  domain.
- Persisting simulation runs would allow reports to be regenerated after
  reopening a project; that is a separate schema change.

## Update — native PDF implemented

The HTML structure stabilized, simulation runs were persisted in schema v3, and
the application now has native PDF construction sheets and simulation reports.
The PDF adapter draws the report directly with `QPdfWriter`/`QPainter` and
rasterizes the existing SVG charts; no Matplotlib or HTML rendering dependency
was added. The HTML report remains available for browser printing.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Matplotlib + PDF | Adds a heavy plotting dependency and packaging cost for Phase 4 |
| Qt PDF writer + QTextDocument | Limited HTML/SVG rendering and extra platform testing |
| Plain-text report | Not sufficient for charts, units, and a reproducible presentation |
| Embed raw NEC files in HTML | Bloats the report and duplicates session data |

## Follow-up

1. Evaluate a PDF adapter when the HTML structure is stable.
2. Add a project schema version and migration for persisted simulation runs.
3. Add a comparison report or export if users need to archive A/B results.
