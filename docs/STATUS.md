# Project status

**Updated:** 2026-11-25
**Latest published release:** `0.10.1` (2026-11-24)
**Development schema:** `71`
**Current product track:** 1.2 Site and exploration

## Where we are

- 0.10.1 is published (2026-11-24) with the refreshed application icon and
  the live-tuning GUI-thread worker fix. Windows 3.11/3.12/3.13 and Linux CI
  pass; the Release workflow built and checksum-verified every artifact.
- UX45 is **closed 2026-11-25**. Every UI `QThread` site now runs through
  `ui/workers/task_runner.TaskRunner`: one controller owns start, queued
  delivery, generation checks, cancellation, completion, failure, bounded
  close, and detached teardown. The modal project-I/O and end-fed paths use
  the same controller through `run_worker_blocking()`. An architecture test
  forbids `QThread(` and `moveToThread(` outside the controller. See
  [`ADR-0053`](ADR/0053-qt-worker-task-lifecycle.md).
- 1.0 Confidence is complete (TS1–TS7, DL9).
- DL1 Smith chart and DL2 tuner matchability are complete.
- DL5 support structures are **explicitly narrowed**: the Yagi mast and guy
  wires are the delivered 1.1 slice; the conductive boom, tower, attachments,
  and structural hardware are deferred pending a dedicated ADR/spike.
- DL3 live tuning now covers managed length and non-length values plus an
  optional coarse pattern preview; **Apply and Simulate closes the dialog**.
  Remaining items are optional: non-modal tool window and more family values.
- VR1 adds one uniform radial droop to the vertical template (ADR-0052):
  physical radial length, ground-tip validation, schema 61 migration, editor
  and help, scene/report rows, managed live-tuning value, and a locked
  optimizer variable with a hard tip-clearance constraint. No performance
  claim; the phased vertical does not share the field. See
  [`ADR-0052`](ADR/0052-uniform-radial-droop.md).
- DL6 stacked Yagi first slice is **implemented 2026-11-25** (ADR-0049):
  two to four identical Yagis on one vertical stack, ideal per-level sources,
  schema 71, form and both catalog routes, per-port **Sources** results, front
  elevation scene, design/construction reports, multi-boom BOM, a real `nec2c`
  two-port test, a bounded spacing/phase optimizer constrained by the
  user-set maximum top height, and an optional splitter + phase-line feed
  (reference/increment lengths, velocity factor, Z0, and splitter excess loss),
  plus a co-simulated network mode with a 1 cm numerical splitter node,
  lossless NEC TL cards including the reference line, a matched line loss plus
  a per-port mismatch correction applied to realized gain, and per-port network
  connection results. The
  splitter node is the primary input in network mode; the primary SWR remains
  the lossless input. A Wilkinson divider mode uses the pure-Python N-port
  solver: equal N-way quarter-wave branches, a star of isolation resistors,
  feed-line loss, and a reconstructed pattern from the solved port voltages.
  Its primary SWR is the splitter input; the editor, schema 71, reports, and
  tests expose it, including an optional L/Pi/T matching network, an optional
  ideal transformer ratio on each level, a matched branch loss, isolation
  resistor series/parallel parasitics, and a deterministic component-tolerance
  corner check.
  A single shared mast and optional guy set are modeled once
  across every level, and a beta/hairpin match or a folded driven element is
  modeled at every driven element. Folded elements are geometry-only; use the
  per-level ideal transformer ratios or matching networks in Wilkinson mode,
  or the feed network in the other modes. The bounded spacing/phase optimizer
  also works in Wilkinson mode by rebuilding the feed-network spec per
  candidate. The tolerance check is limited to divider/feed-line S-parameters at
  the design frequency; the loss-induced input-impedance shift and a
  measured broadband splitter/isolation model remain unavailable. Evidence is C; no stacking gain is claimed.
- DL7 is implemented as the bounded cliff/second-medium far-field profile
  (ADR-0051): project-level Site Ground dialog, schema 60 metadata migration,
  `GN`/`RP 2`/`RP 3` adapter, and far-field-only/SWR-unchanged notes. No
  external site reference is available, so the evidence stays B/C; the native
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
  64) with separate project, design, run, raw-text, and optimization entries;
  per-entry limits, CRC32/SHA-256 checks, atomic writes, and no
  gzip/plain-JSON reader or migration from schema 58 and older. Opening is
  lazy through a `ProjectSession`; saving and compaction copy unchanged run
  entries and serialize only new runs. Design-only recovery and
  **File → Save Design Only...** are available, and `PreparedProject` reports
  honest compressed/expanded sizes. Optional follow-ups are tracked as PF2
  (streaming container write) and PF3 (pattern-level lazy loading). See
  [`ADR-0050`](ADR/0050-zip-project-container.md).
- The adaptive length display-units track is **closed (U1–U6)**; the manual
  desktop light/dark and font-scaling QA was completed on 2026-11-24 with no
  blocking findings.
- A follow-up QA and technical-debt pass on 2026-11-24 kept the full gate green
  and closed the retired `JsonProjectRepository` alias, stale gzip/schema
  claims, two live-tuning preview races, the vertical-optimizer droop bound at
  the tip-clearance limit, and the multiband benchmark import. See
  [`archive/qa/QA_PASS_2026-11-24.md`](archive/qa/QA_PASS_2026-11-24.md). The
  Qt worker-lifecycle duplication found there became UX45 and is now closed.

## Next

1. Keep the measured broadband splitter/isolation model blocked until measured S3P/S4P data and an embedded-data ADR exist; see the [measured-splitter spike](spikes/dl6-measured-splitter-spike.md).
2. Choose the next release slice after the 0.10.1 publication.
3. Keep DL8 blocked until a validated terrain model or second engine exists.
4. Keep the optional PF2/PF3 maintenance items separate from the release gate.

Active execution details, acceptance criteria, and blockers live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Product direction lives in
[`ROADMAP.md`](ROADMAP.md). Historical records are in [`archive/`](archive/).
