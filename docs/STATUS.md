# Project status

**Updated:** 2026-11-24
**Latest published release:** `0.9.0` (2026-11-17)
**Development schema:** `60`
**Current product track:** 1.1 Station

## Where we are

- 1.0 Confidence is complete (TS1–TS7, DL9).
- DL1 Smith chart and DL2 tuner matchability are complete.
- DL5 support structures are **explicitly narrowed**: the Yagi mast and guy
  wires are the delivered 1.1 slice; the conductive boom, tower, attachments,
  and structural hardware are deferred pending a dedicated ADR/spike.
- DL3 live tuning is partial: the primary dimension has a coarse preview.
- DL6 stacked Yagi is a domain prototype only.
- DL7 is implemented as the bounded cliff/second-medium far-field profile
  (ADR-0051): project-level Site Ground dialog, schema 60 metadata migration,
  `GN`/`RP 2`/`RP 3` adapter, and far-field-only/SWR-unchanged notes. The native
  radial screen remains unvalidated for SWR and is not exposed.
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
  `ui/element_optimization_actions.py`, family/length/synthesis dialogs into
  `ui/optimization_actions.py`, and recent-list behavior into
  `ui/recent_actions.py`. The standalone main-window decomposition is
  **closed**; the remaining UI-construction debt is left for extract-on-touch
  work, not another standalone refactor.
- PF1 is **closed 2026-11-24** after manual validation of the incident-scale
  project. `.antennadesk` is a deterministic ZIP container (container 1, schema
  60) with separate project, design, run, raw-text, and optimization entries;
  per-entry limits, CRC32/SHA-256 checks, atomic writes, and no
  gzip/plain-JSON/migration reader. Opening is lazy through a
  `ProjectSession`; saving and compaction copy unchanged run entries and
  serialize only new runs. Design-only recovery and
  **File → Save Design Only...** are available, and `PreparedProject` reports
  honest compressed/expanded sizes. Optional follow-ups are streaming the
  container write and pattern-level lazy loading. See
  [`ADR-0050`](ADR/0050-zip-project-container.md).

## Next

1. Validate the DL7 cliff slice with a real site case or published reference.
2. Continue DL4 (near-field/RF exposure) after its ADR/spike.
3. Continue DL3 managed dimensions and the remaining 1.2 items.
4. Close the pending manual U6 visual QA before the next release decision.

Active execution details, acceptance criteria, and blockers live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Product direction lives in
[`ROADMAP.md`](ROADMAP.md). Historical records are in [`archive/`](archive/).
