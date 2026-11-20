# Project status

**Updated:** 2026-11-20
**Latest published release:** `0.9.0` (2026-11-17)
**Development schema:** `58`
**Current product track:** 1.1 Station

## Where we are

- 1.0 Confidence is complete (TS1–TS7, DL9).
- DL1 Smith chart and DL2 tuner matchability are complete.
- DL5 support structures are partial: Yagi mast and guy wires are modeled;
  the conductive boom is deferred, and tower/attachment hardware is not modeled.
- DL3 live tuning is partial: the primary dimension has a coarse preview.
- DL6 stacked Yagi is a domain prototype only.
- DL7 is a completed spike; implementation is pending and the native radial
  screen remains unvalidated for SWR.
- A full QA and technical-debt sweep on 2026-11-20 left the complete gate green
  with no functional defect; see
  [`archive/qa/QA_PASS_2026-11-20.md`](archive/qa/QA_PASS_2026-11-20.md).
  The follow-up extractions moved typed-family simulation-spec assembly,
  far-field pattern presets, and pattern-budget planning into the Qt-free
  application layer, catalog/template routing into `ui/catalog.py`, export
  dialogs/writer dispatch into `ui/exporters.py`, VNA/NEC/MMANA import parsing
  into `ui/import_actions.py`, project open/save workers into
  `ui/project_io.py`, autosave/recovery cadence into
  `ui/recovery_actions.py`, element-optimizer dialogs into
  `ui/element_optimization_actions.py`, and family/length/synthesis dialogs
  into `ui/optimization_actions.py`.

## Next

1. Close the remaining DL5 slice or explicitly narrow it.
2. Decide the DL7 bounded cliff slice after a reproducible evidence check.
3. Continue DL4 and the remaining 1.2 items.

Active execution details, acceptance criteria, and blockers live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Product direction lives in
[`ROADMAP.md`](ROADMAP.md). Historical records are in [`archive/`](archive/).
