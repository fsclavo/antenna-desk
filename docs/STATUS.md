# Project status

**Updated:** 2026-11-27
**Latest published release:** `0.11.1` (2026-11-27)
**Development schema:** `73`
**Current product track:** 1.2 Site and exploration

## Where we are

- 0.11.1 is **published 2026-11-27** as a patch release. It prevents optimizer
  dialogs from closing while their worker thread is running: Cancel is enabled
  during the run, Close is disabled, and the Close/Esc path cancels instead of
  destroying the `QThread`. Regression tests cover the trapped-Yagi family
  optimizer and the element optimizer. Full gate: **4,790 passed, 1 skipped**;
  real `nec2c` integration: **186 passed**. The tag workflow published and
  checksum-verified the wheel/sdist, Linux packages, and Windows packages. See
  [`RELEASE_QA_0.11.1.md`](archive/releases/RELEASE_QA_0.11.1.md).
- 0.11.0 is **published 2026-11-27**. It packages the UX46–UX57 3D pattern
  and dialog-layout work, the extended DL6 stacked-Yagi feed network and
  tolerance checks, and FP1 with schema 73. Full gate: **4,787 passed, 1
  skipped**; real `nec2c` integration: **186 passed**. The tag workflow
  produced and published the wheel/sdist, AppImage, Debian package, Windows
  installer, portable zip, and checksums. All six published checksums were
  verified on 2026-11-27; the AppImage, wheel, sdist, and Debian package report
  `0.11.0`, and the Windows portable zip contains the bundled `nec2c`. See
  [`RELEASE_QA_0.11.0.md`](archive/releases/RELEASE_QA_0.11.0.md).
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
- UX46–UX49 are **implemented 2026-11-26**: the 3D lobe shows the
  maximum-gain ray, same-elevation back ray with F/B for explicit beam axes,
  antenna azimuth/vertical marker, azimuth reference ring, compact labels, a
  top-view plan inset, and a canonical antenna overlay centered on the beam
  symmetry plane for explicit-forward-axis families (feed-centered otherwise),
  with Auto/Full/Outline modes. The geometry controls include an opt-in **Link 3D
  views** camera link that syncs yaw/pitch only, resets both cameras on design
  change, and turns off with an explanation in Construction view. The
  construction-sheet isometric export keeps a fixed 38°/26° camera.
- UX50 is **implemented 2026-11-26**: the Yagi generator dialog uses a wide
  two-column form (geometry/support left, material/site/feed right) inside a
  scroll area, while the inline sidebar Yagi form stays single-column. The hint,
  evidence, boom note, and OK/Cancel remain visible when the form scrolls. No
  solver, domain, schema, simulation, or report change.
- UX51 is **implemented 2026-11-26**: generator dialogs now share
  `FormDialogFrame` (scroll/action split) and `SectionedForm` (atomic semantic
  columns, label/help binding, and reading-order tab chain). ADR-0056 records
  the 640 px height budget, 920 px target width, sidebar exception, and
  rejected alternatives. The Yagi dialog is the reference implementation. The
  layout guard covers 25 family dialogs in English and Spanish with no
  exceptions, and negative tests prove it rejects a 1087 px form without a
  scroll area and the old single-column Yagi shape. No solver, domain, schema,
  simulation, or report change.
- UX52 is **implemented 2026-11-26**: loaded dipole, biquad, Moxon, and
  magnetic loop now use the shared `FormDialogFrame` and `SectionedForm` with
  two semantic columns, a scroll fallback, and actions outside the scroll. All
  four open at 920×640 with the full form and actions visible, no horizontal
  scrollbar in English or Spanish, and unchanged parameter round-trips. The
  loaded-dipole orientation selector now shows its labels immediately. No
  solver, domain, schema, simulation, or report change.
- UX53 is **implemented 2026-11-26**: Beverage, SCV, J-pole, and OCFD now use
  the shared scaffold and two semantic columns, with the form scroll fallback
  and actions outside. All four fit the 920×640 budget without a horizontal
  scrollbar in English or Spanish, preserve parameter round-trips, and keep
  the OCFD band-plan footer outside the scroll. At the large Spanish preset,
  Beverage and SCV use a small vertical scroll while actions stay visible. No
  solver, domain, schema, simulation, or report change.
- UX54 is **implemented 2026-11-26**: the twelve scroll-heavy generator dialogs
  now use the shared `FormDialogFrame` and keep a single semantic column with
  the action box outside the scroll. The audit in ADR-0056 records each
  decision; no two-column migration was needed. Stacked Yagi now shows its
  level/spacing/feed controls above the embedded Yagi editor. Primary controls
  are visible at 1920×1080 and the 1366×768 cap, with no horizontal scrollbar.
  No solver, domain, schema, simulation, or report change.
- UX55 is **implemented 2026-11-26**: fan dipole, Ringo, inverted V, and
  inverted L use the shared scaffold without a form scroll, and all 26 family
  generator dialogs now use `FormDialogFrame`. The layout guard has no
  exceptions. A 400-check offscreen matrix (25 dialogs × light/dark ×
  Medium/Large × EN/ES × 1366×768/1920×1080) passed with no visible action
  outside the dialog and no horizontal scrollbar. See
  [`archive/qa/QA_PASS_2026-11-26_ux55.md`](archive/qa/QA_PASS_2026-11-26_ux55.md).
  The manual desktop 125%/150% confirmation passed on 2026-11-26, including
  the Large font preset.
- A general QA and technical-debt pass on 2026-11-26 kept the full gate,
  lockfile, dependency audit, and package build green. It corrected stale
  project-bundle schema, release, and DL6 documentation and added a schema
  guard; see
  [`archive/qa/QA_PASS_2026-11-26.md`](archive/qa/QA_PASS_2026-11-26.md).
- UX56–UX57 are **implemented 2026-11-26**: the schematic 3D antenna overlay
  now centers on the beam symmetry plane for families with an explicit forward
  axis while keeping the feed marker at its real offset, and the dashed
  same-elevation back ray ends at the actual rear gain. The back ray and label
  are hidden when F/B is unavailable or the marker is too close to the origin.
  No solver, domain, schema, or report change.
- FP1 is **implemented 2026-11-26** (schema 72; feed/choke semantics revised at
  schema 73, ADR-0055). The half-wave Flower Pot is a first-class VHF family:
  two collinear wires forming the radiating arms, a physical feed at the bottom
  of the choke, the construction-only choke height (45 mm at 2 m, 63 mm at 6 m),
  an ideal common-mode choke, published 2 m/6 m physical cut rows, an explicit
  **1.087 NEC electrical model scale** with its source at the arm junction and
  kept separate from the 0.88 construction factor, scaled-tip ground validation,
  catalog/editor routes, EN/ES help, estimator, top/bottom optimizer, elevation
  scene with physical feed/choke and a choke inset, design summary, construction
  cut list, BOM choke row, integrated-choke feed detail, and real `nec2c` 2 m/6 m
  regression. No 50 Ω, gain, bandwidth, or choke-impedance claim is made. See
  [ADR-0055](ADR/0055-flower-pot-half-wave-family.md) and
  [`spikes/fp1-flower-pot-length-representation.md`](spikes/fp1-flower-pot-length-representation.md).
- FP1 QA is **closed 2026-11-27**. The manual pass confirmed the physical feed
  below the choke, the 45/63 mm choke heights, the scene and report split, and
  the 3D pattern overlay anchored at the physical feed. Automated gate:
  **4,787 passed, 1 skipped**; real `nec2c` simulation integration: **186
  passed**. See
  [`archive/qa/QA_PASS_2026-11-27_fp1.md`](archive/qa/QA_PASS_2026-11-27_fp1.md).
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
  project. `.antennadesk` is a deterministic ZIP container (container 1,
  current schema 73) with separate project, design, run, raw-text, and
  optimization entries;
  per-entry limits, CRC32/SHA-256 checks, atomic writes, and no
  gzip/plain-JSON reader or migration from schema 58 and older. Opening is
  lazy through a `ProjectSession`; saving and compaction stream unchanged run
  entries and serialize only new runs. Design-only recovery and
  **File → Save Design Only...** are available, and `PreparedProject` reports
  honest compressed/expanded sizes. PF2 streaming write is **done 2026-11-27**
  (see below). PF3 pattern-level lazy loading is **deferred** because it
  requires a pattern-entry ADR and a container/schema change. See
  [`ADR-0050`](ADR/0050-zip-project-container.md).
- PF2 streaming container write is **done 2026-11-27**. Saving and compaction
  stage entries in a bounded temporary spool, write the manifest-first
  container one entry at a time, and stream unchanged runs from the source
  container. The bytes remain identical to the previous writer, limits and
  atomic replacement are unchanged, and the UI still reports exact compressed
  and expanded sizes. The benchmark's copy-entry save/compact peak RSS fell
  from 174/84 MB to 45 MB; materialized saves remain dominated by the
  materialized domain runs. See
  [`ADR-0057`](ADR/0057-streaming-container-write.md).
- UX58 deterministic layout baseline is **implemented locally 2026-11-27**.
  Tests pin the offscreen 96 DPI / 1× environment, normalize and restore a
  9–10 pt test font, print the resolved font/DPI/DPR/style metrics, and run the
  dense generator-layout files in an isolated 180 s CI batch. The local layout
  batch passes 182 tests; Windows 3.12/3.13 verification is pending. See
  [`ADR-0056`](ADR/0056-antenna-dialog-layout.md) and
  [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md#windows-layout-baseline-and-cross-platform-generator-wrapping-proposed-2026-11-27).
- UX59 long-label wrapping is **implemented locally 2026-11-27**. A shared
  `configure_form_layout()` applies `WrapLongRows`, growing fields, zero
  margins, and explicit spacing to every family `QFormLayout`; one-column
  labels wrap while two-column layouts keep the existing height budget. Local
  layout batch: **226 passed**; full UI suite: **2,017 passed**. Windows
  3.12/3.13 verification is pending. See
  [`ADR-0056`](ADR/0056-antenna-dialog-layout.md).
- UX60 layout-based dialog sizing is **implemented locally 2026-11-27**.
  `FormDialogFrame` grows only to the measured form/chrome minimum and keeps
  the screen cap; the Yagi table uses `AdjustIgnored`; Basic Antenna's
  template/family values are compact. Local layout batch: **247 passed**; full
  UI suite: **2,024 passed**. No width exception or column collapse was needed.
  Windows 3.12/3.13 verification is pending. See
  [`ADR-0056`](ADR/0056-antenna-dialog-layout.md).
- UX61 final layout guard is **implemented locally 2026-11-27**. The fast batch
  covers 26 dialogs × English/Spanish × Medium/Large × (920×640 and each
  initial size), with no horizontal scrollbar and the action box visible and
  outside the form scroll. Local layout batch: **355 passed**; full gate:
  **4,966 passed, 1 skipped**. The Windows 3.12/3.13 run and the manual
  Linux/Windows light-dark and 125%/150% checklist are still pending; see
  [`QA_CHECKLIST_2026-11-27_ux61.md`](archive/qa/QA_CHECKLIST_2026-11-27_ux61.md).
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

1. Close the P1 Windows layout/CI track: UX58–UX61 are implemented locally.
   Run the real Windows 3.12/3.13 layout batch, execute the pending manual
   Linux/Windows light-dark and 125%/150% checklist, and confirm the README
   `tests` badge is green on `main`. No schema or solver change.
2. Verify the published 0.11.1 artifacts and checksums on the target desktops.
3. Keep the measured broadband splitter/isolation model blocked until measured S3P/S4P data and an embedded-data ADR exist; see the [measured-splitter spike](spikes/dl6-measured-splitter-spike.md).
4. Keep PF3 deferred until its pattern-entry ADR and container/schema decision
   exist; PF2 is done and closed.
5. Keep the FP1 5/8, double 5/8, sleeve, and high-gain variants blocked until
   their own spikes and ADRs exist.
6. Keep DL8 blocked until a validated terrain model or second engine exists.

Active execution details, acceptance criteria, and blockers live in
[`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md). Product direction lives in
[`ROADMAP.md`](ROADMAP.md). Historical records are in [`archive/`](archive/).
