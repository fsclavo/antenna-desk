# Autonomous execution backlog

**Date:** 2026-11-27
**Status:** active execution queue.

This is the only active execution queue. It contains shippable items,
dependencies, blockers, acceptance criteria, and the current test baseline.
Product scope and the antenna expansion order live in
[`ROADMAP.md`](ROADMAP.md); evidence status lives in
[`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md); architecture decisions live in
[`ADR/`](ADR/). Do not create a second backlog: add product scope to the
roadmap and active work here.

This is the ordered queue for continuing without waiting for new product
decisions. Each item is independently shippable and must leave the full gate
green. Items marked **blocked** require a measurement, a traceable source, or an
external service and must not be invented or simulated into existence.

## Rules

- One coherent milestone per change set.
- Run `ruff check`, `ruff format --check`, both `mypy` passes, and the full
  `NEC2C=... uv run pytest` before declaring an item complete.
- Add domain, persistence/container, UI, scene, reporting, optimizer, and
  documentation coverage proportional to the item.
- No new numerical reference without a traceable source.
- Do not commit or push unless explicitly requested.

## Queue

The 2026-11-19 product trust and station wave is the active product sequence.
Wave 0 (TS1–TS7 and DL9) is **done 2026-11-19**; DL1 and DL2 are done, DL5 is
narrowed, DL7 is implemented as a bounded slice, and DL8 remains post-1.2. DL3
and DL6 are partial; DL4 is canceled. Its rows are in the table; scope,
acceptance, evidence, and risk are in §Product trust and station wave below.

PF1 is a P0 reliability insertion outside the antenna wave; it landed before
any further project-format change. It is closed after manual validation on
2026-11-24. PF2 streaming write is done 2026-11-27; pattern-level lazy loading
(PF3) is deferred 2026-11-27 because it requires a pattern-entry ADR and a
container/schema change.

VR1 is a vertical-geometry enhancement implemented ahead of the remaining 1.1/1.2
items. It is bounded to one uniform droop, physical radial length, schema 61, and
family-optimizer coverage; the phased vertical is not included.

UX46–UX49 are a presentation-only track for 3D pattern orientation, implemented
2026-11-26. The three layers were delivered in the order UX46 → UX48 → UX49;
UX47 is an additional orientation aid after UX46. UX47 is the plan mini-map,
UX48 includes the large-array outline mode, UX49 links the geometry and pattern
cameras, and the shared antenna color/feed marker is introduced in UX46 and
reused by UX47/UX48. They do not change the solver, domain model, project schema,
pattern storage, or report format, and add no 3D engine or dependency. See §3D
pattern orientation and comparison.

UX56–UX57 are implemented presentation-only follow-ups to that track: UX56
centers the schematic antenna overlay on the beam symmetry plane for families
with an explicit forward axis, fixing the plan-view offset visible on side-fed
quad loops; UX57 draws the same-elevation back ray to the actual rear gain
instead of reusing the forward maximum radius. They change no solver, domain
model, project schema, pattern storage, or report format. See §3D lobe
presentation corrections.

UX50–UX55 are implemented and fix the Yagi dialog's unreachable action area
as the reference implementation. The compact-family migration and the
cross-family automated QA matrix are complete, and the manual desktop
125%/150% check passed on 2026-11-26 including the Large font preset. The
track does not force two columns on every
family and does not change the narrow main-window sidebar. It changes no
solver, domain model, project schema, container, report, or numerical
reference. It is not part of the active 1.2 sequence; see §Antenna generator
dialog layout standard.

UX58–UX61 are a P1 CI and layout-quality track opened 2026-11-27. UX58 is
implemented locally 2026-11-27; UX59–UX61 remain proposed and the Windows
verification is pending. The README `tests` badge has been red since the 0.11.0
publication: the Windows 3.12/3.13 jobs fail 22 dialog-layout assertions while
Linux passes the same 1,203 tests, and the 3.12 job then stalls until its
10-minute batch timeout. The track first makes the offscreen test baseline
deterministic, then implements the single-column and nested `WrapLongRows`
behavior already promised by ADR-0056, makes dialog and table sizing
layout-based, and closes with a Large-font guard and a real Windows run. It
changes no solver, domain model, project schema, report, or numerical
reference. It is not part of the active 1.2 sequence; see §Windows layout
baseline and cross-platform generator wrapping.

FP1 is a VHF/portable catalog addition, not part of the active 1.2 sequence.
Its length-representation spike is complete and ADR-0055 is updated;
implementation is the next bounded slice. The 5/8, double 5/8, dual-band
sleeve, and high-gain variants are deliberately excluded.

Completed rows are archived in [`archive/backlog-completed-2026-11-20.md`](archive/backlog-completed-2026-11-20.md).

| ID | Task | Size | Depends on | Acceptance |
|---|---|---|---|---|
| PF1 | ZIP project container and honest size contract | L | none | **Done 2026-11-24; manual validation passed.** A project that saves always reopens; design, runs, and optimizations are separate validated ZIP entries; per-entry/total limits apply on save and load; old runs are compacted by the save flow; oversized projects can be recovered design-only. No backward compatibility. PF2 is done; PF3 is deferred. See §PF1. |
| PF2 | Streaming container write | M | PF1 (closed) | **Done 2026-11-27.** Two-phase temporary spool, manifest-first output, streamed copied runs, exact sizes, and atomic replace. Output remains byte-identical; lazy save/compact peak RSS fell from 174/84 MB to 45 MB. See §PF2 and ADR-0057. |
| PF3 | Pattern-level lazy loading | L | PF1 (closed); pattern-entry ADR; schema decision | **Deferred 2026-11-27.** Requires a pattern-entry ADR and a container/schema change, so it is not scheduled in the 0.11.x patch line. Split far-field patterns into validated per-run entries and load them only for the Pattern/3D/report consumers; distinguish "not loaded/available" from "no pattern". Revisit only when open/select memory becomes a release blocker. See §PF3. |
| B4 | Fan-dipole coupling calibration | M | measurement | A coupled-fan measurement is reproduced; no scalar correction is invented |
| C7h | Optional 6 m HexBeam band | S | C7c; published 6 m row | Add the published 6 m driver/reflector/tip-spacer row and vertical offset, with the same frame-fit validation, editor option, reports, and evidence note. No performance claim. |
| C7i | HexBeam feed harness and inter-band coupling | L | traceable harness data or measurement | Model the parallel coax feed harness/jumper lengths and inter-band coupling, or keep it explicitly unavailable; no invented values. Blocked until a source or measurement exists. |
| G27 | Optional transformer, common-mode choke, and coaxial loss models | L | G25; measured transformer insertion loss/core data; common-mode current model or measurement; manufacturer coax attenuation data | **Partially delivered.** EF7b added the measured transformer-loss table (`BalunLoss`); EF8 added the bounded feedpoint common-mode choke; ADR-0039 adds frequency-dependent feed-line attenuation with source-backed RG-58A/RG-213 tables, log-frequency interpolation, endpoint clamping, and a preflight range warning. The loss-accounting audit is also done (ADR-0040): the feed-chain sum must match the transducer gain, and NEC conductor/load losses including the feedpoint choke stay in the antenna power budget. Still deferred: analytical ferrite core loss with complex permeability/core geometry/winding/load data; frequency-interpolated `Zcm(f)` and shack-end choke placement; the remaining coax/choke evidence audit. All loss fields stay optional and off/zero by default; no invented loss numbers. |
| U6 | Documentation, help audit, and visual QA | S–M | U2–U5 | **Done 2026-11-24.** The user guide, roadmap, units spec, README, changelog, help tests, automated font-scaling/geometry checks, and the manual desktop light/dark/font-scaling checklist are complete. [`QA_PASS_2026-11-18.md`](archive/qa/QA_PASS_2026-11-18.md) and [`QA_PASS_2026-11-24.md`](archive/qa/QA_PASS_2026-11-24.md) record the gate and closure. |
| DL3 | Live tuning preview | M–L | none | **Done 2026-11-27.** Primary and managed dimension sliders, coarse single-frequency preview, optional pattern preview, debounce/cancel, stale-result guard, preview badge, and apply/full-run path. The final follow-up adds Flower Pot feed/choke heights and the trapped-Yagi trap inset. See §DL3. |
| DL5 | Support structures | M–L | ADR | **Done as narrowed 2026-11-24.** Yagi mast conductor plus 2–4 guy wires, geometry, BOM, scene, and schema 57–58. Conductive boom, tower, attachments, and structural hardware are deferred pending ADR/spike; no further 1.1 work. See §DL5. |
| DL6 | Stacked Yagi arrays | L | DL5 (soft), ADR | **First slice implemented 2026-11-25.** 2–4 identical Yagis, schema 71, form and catalog routes, per-port **Sources**, front elevation scene, reports/BOM, a real nec2c two-port test, splitter + phase-line specification, a co-simulated lossless TL network, and a bounded spacing/phase optimizer inside the maximum top-height envelope. A matched line loss plus a per-port mismatch correction is applied to realized gain, one shared mast/guy set is modeled across every level, and a beta/hairpin match is built at every driven element. A pure-Python N-port feed-network solver, antenna Y-matrix extraction, a user-facing Wilkinson divider mode, and per-level L/Pi/T matching networks are implemented. A folded driven element is copied to every level as geometry-only, with optional ideal per-level transformer ratios, matched branch loss, isolation-resistor series/parallel parasitics, and a deterministic tolerance corner check in Wilkinson mode; a measured broadband splitter/isolation model remains explicitly unavailable. Network mode includes the reference line. Evidence C; no gain claim. See ADR-0049 and §DL6. |
| DL7 | Native ground screen and cliff ground | M–L | ADR, spike | **Bounded slice implemented 2026-11-24; evidence B/C.** Cliff/second-medium far-field profile, schema 60, Site Ground dialog, and `GN`/`RP 2`/`RP 3` adapter. No external site reference is available; the native radial screen stays unvalidated for SWR and is not exposed. See ADR-0051, `spikes/dl7-ground-gn-spike.md`, and §DL7. |
| DL8 | Full terrain model | XL | DL7, validated model | **Post-1.2.** Only with a validated terrain model or a second engine; otherwise explicitly unavailable. See §DL8. |
| VR1 | Sloped vertical radials with uniform droop | M | ADR; next schema bump; vertical family | **Implemented 2026-11-24.** One uniform downward droop with physical radial length, ground-tip validation, schema 61, EN/ES editor/help, scene/report/live-tuning coverage, and a locked optimizer variable with a hard tip-clearance constraint. No per-radial angles, no performance claim, and the phased vertical is excluded. See §VR1 and ADR-0052. |
| FP1 | Flower Pot half-wave family | L | ADR-0055; schema 72, revision 73 | **Implemented 2026-11-26; feed/choke revision 2026-11-27.** The length spike selected Option A: an explicit 1.087 NEC electrical scale over the published physical cut lengths, with both factors shown separately. The VK2ZOI-style coaxially fed vertical half-wave dipole for 2 m/6 m is in the catalog with two radiating arms, a physical feed at the bottom of the choke, construction-only choke heights (45/63 mm), a NEC equivalent source at the arm junction, editor/help, scene, reports/BOM, estimator, and a bounded top/bottom optimizer. No 5/8, double 5/8, dual-band sleeve, or high-gain variant. Evidence B for published dimensions, C for the coax/choke equivalent; no 50 Ω or gain claim. See §FP1 and ADR-0055. |
| UX45 | Shared Qt worker lifecycle | M–L | short lifecycle ADR; no active feature slice | **Done 2026-11-25.** All 14 `QThread` sites use `ui/workers/task_runner.TaskRunner`: one controller owns start, queued GUI delivery, generation/stale-result rejection, cancellation, completion, failure, bounded close, and detached teardown. Modal project I/O and end-fed use the same controller. An architecture guard forbids `QThread(` and `moveToThread(` outside the controller. See §UX45 and ADR-0053. |
| UX46 | 3D lobe orientation indicators | S | none | **Implemented 2026-11-26.** First layer. Max-gain ray, same-elevation back ray with F/B, antenna azimuth line/arrow or vertical dot, azimuth-ring labels, and Front/Back only for families with an explicit forward axis. Shared antenna color and feed marker. No solver, domain, schema, or report change. See §UX46. |
| UX47 | Plan mini-map in the 3D lobe | S | UX46 | **Implemented 2026-11-26.** Top-view inset with the canonical footprint, shared feed marker, antenna azimuth, and max-gain azimuth; theme-aware, hidden at minimum size, and suppressed when it would collide with the max label. No synthetic family shape and no new engine. See §UX47. |
| UX48 | Schematic antenna overlay in the 3D lobe | M | UX46 | **Implemented 2026-11-26.** Opt-in "Show antenna"; feed-centered, uniform-scale canonical wireframe with a not-to-scale note; support wires thinner/dashed; Auto/Full/Outline for large arrays; same color and feed marker as UX46. No solver, domain, schema, or report change; no new engine. See §UX48. |
| UX49 | Linked geometry/pattern 3D cameras | S | UX46; UX48 | **Implemented 2026-11-26.** Opt-in link syncs yaw/pitch only; zoom and pan stay independent; reset and model-change propagation; exact projection tests; Construction mode switches to 3D or turns the link off with an explanation. The construction-sheet 3D export keeps a fixed 38°/26° camera. No solver, domain, schema, or report change; no new engine. See §UX49. |
| UX50 | Yagi generator two-column reference dialog | M | none | **Implemented 2026-11-26.** The sidebar `YagiForm` stays single-column; only `YagiDialog` uses the wide two-column layout inside a scroll area. Geometry/support are on the left and material/site/feed on the right; notes and OK/Cancel stay outside the scroll. The default 920×860 layout fits English and Spanish without scrolling or a horizontal bar; at 920×640 the form scrolls and the actions remain visible. Tests cover column order, transformer placement, warnings, ten elements, large Spanish, and the single-column sidebar. See §UX50. |
| UX51 | Antenna dialog layout standard and height guard | M–L | UX50 | **Implemented 2026-11-26.** ADR-0056 records the 640 px height budget, 920 px target width, sidebar exception, scaffold, sectioned layout, accessibility/tab-order contract, and rejected alternatives. `FormDialogFrame` owns the scroll/action split; `SectionedForm` keeps semantic sections atomic with one/two columns and label/help binding. Yagi is the reference. The guard covers 25 family dialogs in EN/ES with no exceptions, and negative tests reject a 1087 px form without scroll and the old single-column Yagi shape. No family migration in this item. See §UX51. |
| UX52 | Complex family dialogs, wave 1 | M | UX51 | **Implemented 2026-11-26.** Loaded dipole, biquad, Moxon, and magnetic loop use `FormDialogFrame` and `SectionedForm` with two semantic columns, a scroll fallback, and actions outside the scroll. All four open at 920×640 with the form and actions visible and no horizontal scrollbar in EN/ES; parameter round-trips and existing family tests are unchanged. The loaded-dipole orientation selector now shows its labels immediately. See §UX52. |
| UX53 | Complex family dialogs, wave 2 | M | UX51 | **Implemented 2026-11-26.** Beverage, SCV, J-pole, and OCFD use `FormDialogFrame` and `SectionedForm` with two semantic columns, scroll fallback, and actions outside. All four fit 920×640 without horizontal scrolling in EN/ES; the OCFD band-plan footer stays outside the scroll; large Spanish adds only a small vertical scroll for Beverage/SCV. Parameter round-trips and family tests are unchanged. See §UX53. |
| UX54 | Scroll-heavy family dialog audit | M–L | UX51 | **Implemented 2026-11-26.** All twelve scroll-heavy dialogs use `FormDialogFrame` with a single semantic column and actions outside the scroll. ADR-0056 records the per-dialog decision; no two-column migration was needed. Stacked Yagi promotes its level/spacing/feed controls above the embedded editor. Primary fields are visible at 1920×1080 and 1366×768, with no horizontal scrollbar. No solver/schema change. See §UX54. |
| UX55 | Compact families, visual QA, and track closure | S–M | UX51 for start; UX52–UX54 for closure | **Implemented 2026-11-26.** Fan dipole, Ringo, inverted V, and inverted L use `FormDialogFrame` without scroll and stay compact/single-column. All 25 family dialogs are in the guard with no exceptions. A 400-check offscreen matrix (light/dark, Medium/Large, EN/ES, 1366×768/1920×1080) passed with no action outside the dialog and no horizontal scrollbar. The manual desktop 125%/150% check passed, including Large font. See §UX55 and `archive/qa/QA_PASS_2026-11-26_ux55.md`. |
| UX56 | 3D overlay centered on the beam symmetry plane | S–M | UX46; UX48 | **Implemented 2026-11-26.** The overlay is centered on the feed projected onto the beam symmetry plane for families with an explicit forward axis; the feed marker keeps its real cross-boom offset. Verticals, dipoles, loops without a declared axis, and custom models remain feed-centered. The uniform 35% scale is measured from the new center. No solver, domain, schema, or report change. See §UX56. |
| UX57 | 3D back ray at the actual rear gain | S | UX46 | **Implemented 2026-11-26.** The same-elevation back ray ends at `max gain − F/B`, not at the forward peak radius. A missing or non-finite F/B hides the ray and label, and the minimum-distance guard hides a degenerate marker. No solver, domain, schema, or report change. See §UX57. |
| UX58 | Deterministic Windows UI layout baseline | S | none | **Implemented locally 2026-11-27; Windows CI verification pending.** Pins `QT_FONT_DPI=96`/`QT_SCALE_FACTOR=1`, normalizes and restores the test font at 9–10 pt, records the resolved font/DPI/DPR/style/metrics, and isolates the dense layout files under a 180 s CI batch. No `skip`/`xfail`. Local layout batch: 182 passed. See §UX58. |
| UX59 | Wrap long form rows across generator dialogs | M | UX58 | **Proposed; P1.** Apply `WrapLongRows` and explicit spacing to single-column `SectionedForm` and every plain `QFormLayout` in the family forms, including nested groups. No horizontal scrollbar at 920 px or the initial 560–620 px widths in EN/ES; Large font keeps no horizontal bar and actions visible. Add a synthetic long-label regression test. See §UX59. |
| UX60 | Layout-based dialog sizing and Yagi table width | S–M | UX59 | **Proposed; P1.** Grow the initial dialog width to the form minimum only when needed, capped by `scaled_dialog_size()`; remove or constrain the Yagi table's `AdjustToContents`; fix the Basic Antenna template control. All 26 dialogs stay free of horizontal scrolling at 920 px and Large font. Document any 1000 px exception or one-column collapse. See §UX60. |
| UX61 | Large-font layout guard, Windows closure, and docs | S–M | UX58–UX60 | **Proposed; P1.** Add the compact Medium/Large EN/ES guard (no horizontal at 920, actions visible, vertical allowed only at Large), update ADR-0056/STATUS/CHANGELOG and the manual QA record, and confirm the README `tests` badge is green on `main` with no platform exclusions. See §UX61. |
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |


## PF1 — ZIP project container and honest size contract

**Status:** **closed 2026-11-24** after manual validation of the incident-scale
project. Slice 1 landed 2026-11-20; lazy open, save/compact by copying entries,
`PreparedProject`, and design-only recovery/save followed. **Priority:** P0
reliability, independent of the antenna waves.

**Motivation:** On 2026-11-20 a 56.9 MB compressed project (409.1 MB expanded)
was written successfully but could not be reopened. `JsonProjectRepository`
rejected the expanded payload at 256 MiB, while `write_payload()` checked only
the 64 MiB compressed limit. The project held six 68 MB runs: each had five 1°
patterns (47.7 MB) and 20.2 MB of raw NEC output; the design itself was 3.5 KB.
At the observed 7.19:1 compression ratio the effective compressed limit was
about 35.6 MB, so the 64 MB check was not a safe proxy for the expanded limit.
This is a save/load contract violation, not a solver or validation failure.

**Slice 1 landed 2026-11-20:** the gzip envelope is replaced by a deterministic
ZIP container (container 1, schema 59) with separate project, design, run,
raw-text, and optimization entries; per-entry, total, manifest, path, and
entry-count limits are enforced on save and load; CRC32/SHA-256 are verified
through bounded reads; writes are atomic; gzip, plain JSON, and schema < 59 are
rejected; and the example is regenerated. **Slice 2 started:** opening uses a
manifest-indexed `ProjectSession` that loads metadata/designs eagerly and runs
on demand, a failed oversized open offers design-only recovery, and
“Save design only” writes metadata/designs without runs or optimizations.
`PreparedProject` now carries the payload, compressed/expanded sizes, entry
count, and limits. Saving and compaction copy unchanged run entries from the
source container and serialize only new runs; they reopen the session after
writing. PF2 (streaming write) is done 2026-11-27; PF3 (pattern-level lazy
loading) is deferred because it requires a pattern-entry ADR and a
container/schema change. PF1's container and save/load contract stay unchanged.
See [ADR-0050](ADR/0050-zip-project-container.md).

**Scale benchmark (2026-11-21):** `scripts/benchmark_project_io.py` generated
four runs with five 2° patterns and 8 MB of raw text each (118 MB expanded,
1.1 MB container). Each operation ran in its own process:

| Step | Time | Peak RSS |
|---|---:|---:|
| open (lazy) | 0.00 s | 41 MB |
| select one run | 3.75 s | 682 MB |
| save (materialized) | 32.8 s | 1,614 MB |
| save (copy entries) | 1.25 s | 174 MB |
| compact (materialized) | 19.3 s | 1,524 MB |
| compact (copy entries) | 0.33 s | 84 MB |
| save design only | 0.01 s | 40 MB |

The remaining cost is the selected run itself: one 2° run with five patterns
still allocates about 400 MB of domain objects. Pattern-level lazy loading is a
separate future decision; the save/compact path no longer multiplies that cost
by the full history. PF2 later reduced the copy-entry save/compact rows to
45 MB; see §PF2.

**Goal:** replace the single gzip JSON envelope with a versioned ZIP container
whose entries can be validated, loaded, and pruned independently; enforce one
set of limits on both save and load; never write a project the application
cannot reopen; keep one portable `.antennadesk` file and atomic saves.

**Non-goals:** no backward compatibility with the gzip/plain-JSON project
format or schema 59; no solver, antenna-model, or numerical-reference change;
no binary pattern store or sidecar database in this item; PF3 covers splitting
pattern data into separate validated entries if that is still needed after the
container lands.

### Container format (container version 1, schema version 63)

```text
manifest.json
project.json
designs/<design-id>.json
runs/<run-id>.json
runs/<run-id>.raw-input.txt        (optional)
runs/<run-id>.raw-output.txt       (optional)
optimizations/<design-id>.json
```

- `project.json`: project metadata, shared feed/matching/balun settings, band
  plans, measurements, journal, installation profiles, construction/BOM
  records. Small.
- `designs/<id>.json`: one `DesignVariant` payload per design: parameters,
  canonical antenna snapshot, provenance, band plan, and optimization summary.
  This lets the UI open the selected design without touching run payloads.
- `runs/<id>.json`: one `SimulationRunPayload` with normalized
  frequencies/currents/patterns and **no raw solver text**. One entry per
  retained run.
- `runs/<id>.raw-input.txt` and `.raw-output.txt`: optional raw solver text as
  separate entries, so it can be pruned or omitted without rewriting the
  normalized result. Persist raw output only when explicitly requested or for
  the latest run; default it off for older runs.
- `optimizations/<design-id>.json`: optimization summaries/history per design.
- `manifest.json` holds `format: "antennadesk.project"`, `container_version`,
  `schema_version`, `project_id`, `application_version`, timestamps, an entry
  table (`path`, `kind`, `uncompressed_bytes`, `compressed_bytes`, `crc32`,
  `sha256`), and retention metadata (latest single run, latest batch id/runs).
  Use `extra="forbid"`.
- Entry paths are relative POSIX names: no leading slash, no `..`, no
  backslash, no drive/colon, no NUL, maximum 255 bytes. Reject duplicate names
  and case-insensitive collisions. Reject directories not listed in the
  manifest, symlinks, encrypted entries, unsupported compression, and unknown
  entries.
- Write deterministically: sorted entry order, fixed ZIP timestamps, compact
  JSON, `ZIP_DEFLATED` level 6. An entry that is already compressed may use
  `ZIP_STORED`; do not double-compress.

### Limits and validation

Keep one source of truth in `application/project_limits.py`:

```text
MAX_CONTAINER_BYTES              = 64 MiB   # compressed on-disk
PROJECT_SIZE_WARNING_BYTES       = 32 MiB
MAX_PROJECT_UNCOMPRESSED_BYTES   = 256 MiB  # sum of entry payloads
MAX_MANIFEST_BYTES               = 1 MiB
MAX_ENTRY_BYTES                  = 64 MiB   # one JSON entry
MAX_ENTRIES                      = 10_000
MAX_PATH_BYTES                   = 255
```

- `MAX_ENTRY_BYTES` fits the current normalized run (~47.7 MB); raw text is a
  separate ~20.2 MB entry. If a future run exceeds it, split pattern snapshots
  into `runs/<id>/patterns/<n>.json`; never raise the total silently.
- Do not trust the manifest's declared sizes. Read each entry through a bounded
  stream, stop at the limit + 1, and verify the actual uncompressed byte count
  and CRC32/SHA-256. Reject early if the manifest totals exceed the limits.
  This is also the zip-bomb guard.
- A manifest with more than `MAX_ENTRIES`, an entry path outside the
  whitelist, or a manifest/ZIP entry mismatch is invalid.

### Save/load contract

- **Implemented:** immutable `PreparedProject` with `compressed_bytes`,
  `expanded_bytes`, `entry_count`, and `limits`. Production values carry a
  `PreparedSpool`; the small in-memory `payload` compatibility path remains for
  callers that already hold bytes. `ProjectRepository.prepare_payload()`
  returns it; `write_payload(path, prepared)` streams it atomically.
- `prepare_payload()` stages entries in a bounded spool, sums the uncompressed
  bytes, and raises `ProjectTooLargeError` **before** the final replace if any
  compressed, expanded, entry, count, or path limit is exceeded. A successful
  `save()` must always produce a file that `load()` accepts; the round-trip
  invariant test covers the streaming path.
- Write to a temporary file in the destination directory, `fsync`, then
  `os.replace`; never leave a partial `.antennadesk`. Keep the previous file
  intact on failure.
- `load()` reads `manifest.json`, `project.json`, and the latest retained run
  (or the selected design's latest run) for the initial session. Older runs
  and optimizations are loaded on demand through a `ProjectResultStore` or
  application-level `ProjectSession`. The domain `Project` remains immutable;
  the session caches materialized runs by id and releases them when no longer
  needed.
- Opening a project with N large runs must not materialize N far-field arrays.
  Acceptance: peak memory scales with the project plus the selected run, not
  with total history; a generated 6 × 68 MB project opens under the existing
  256 MiB expanded limit after compaction and within a documented memory
  budget.
- Update every `prepare_payload`/`serialized_size` call site together:
  `SaveProject`, `ProjectIO`, bundle export/import, and recovery. No caller may
  write raw bytes that bypass the limit check.
- Legacy input: `load()` rejects gzip/plain JSON and schema < 59 with a clear
  `ProjectFormatError("unsupported legacy project format")`. Do not add a
  58→59 migration. Delete the gzip/plain-JSON branches and their tests. The one
  pre-container file from the incident is recovered out-of-band; it is not a
  supported input.

### Retention, UI, and recovery

- Reuse `Project._retained_simulation_runs()` as the default retention policy:
  latest single run per design plus all runs of the latest batch. If the
  container exceeds a limit on save, offer “Compact history and save”, compact
  to that policy, and retry. If it still does not fit, offer “Save design only”
  (no `runs/` or `optimizations/`) or cancel. Never write an unopenable file.
- Before a simulation or band batch, estimate the existing container plus the
  new run (reuse `pattern_planning.py`/`budget.py`). If over budget, compact or
  coarsen/disable patterns before running. The per-run 24 MiB planner is
  retained but is no longer the only budget.
- `MainWindow._save_to` shows compressed and expanded sizes and the open limit.
  The 32 MiB warning remains a warning; the 64 MiB compressed and 256 MiB
  expanded limits are hard blocks handled by the repository. The save dialog
  needs “Compact and save” and “Save design only” paths.
- On `ProjectTooLargeError` during open, offer “Open design only”: read only
  `project.json`/`designs`, discard run entries, and open a repaired copy.
  Never overwrite the original; keep a hard temporary cap for this recovery
  path.
- Autosave remains a design-only sidecar. `AutosaveRecovery` already excludes
  simulation runs; it should use the new container with no runs and keep the
  existing 2 MiB recovery limit. The recovery metadata file stays JSON.
- Reconcile with `.antennadesk-bundle`: preferred bundle is a ZIP containing
  `manifest.json`, the native project entries under `project/`, and
  `assets/...`; import validates both manifests and reconstructs the native
  container. Do not nest a compressed project inside another ZIP unless the
  implementation cost is prohibitive; if nested, document the double
  compression and update `PROJECT_BUNDLE.md`.

### Tests

- New `tests/integration/persistence/test_project_container.py`:
  - round trip project/design/runs/optimizations; lazy loading; missing or
    extra entries; duplicate and case-colliding names; traversal, absolute, and
    backslash names; symlink, encrypted, and unsupported compression; CRC and
    size mismatch; manifest total over limit; per-entry over limit; max
    entries; atomic replace failure; deterministic output.
  - save/load invariant: for generated projects under and over each limit,
    `save()` either raises `ProjectTooLargeError` or produces a file that
    `load()` accepts. No “saved but unopenable” state.
  - generated large project (no committed 409 MB fixture) exercising
    compaction; manual validation with the reported 40 m loaded dipole
    project.
- UI tests with `pytest-qt` and the offscreen platform: save dialog shows both
  sizes; compact-and-save; design-only save; oversized-open recovery; EN/ES
  strings and help coverage for every new dialog or field.
- Replace `tests/integration/persistence/test_json_repository.py` with the
  container tests and remove gzip/plain-JSON compatibility tests. Keep
  round-trip fixtures for the current schema only.
- Real NEC2C is not required for the container tests; keep the existing full
  gate and solver tests green.

### Documentation and acceptance

- New ADR-0050 “ZIP project container and size contract” supersedes ADR-0021.
  Update `ARCHITECTURE.md`, `DOMAIN_MODEL.md`, `PROJECT_BUNDLE.md`,
  `USER_GUIDE.md`, `STATUS.md` (current schema), and `CHANGELOG.md`.
- Acceptance:
  - Saving the reported six-run project either compacts to a reopenable
    container or refuses with an actionable message; it never writes another
    unopenable file.
  - A container with the latest retained runs opens without materializing all
    patterns; the design is available even if every run entry is absent.
  - Per-entry and total caps are enforced on save and load; crafted ZIP bombs,
    traversal, duplicate entries, and symlinks are rejected.
  - `compact_simulation_history` physically removes entries and reduces both
    compressed and expanded size.
  - Project bundle export/import round-trips the new container and assets
    without a double-compression regression.
  - Full gate: `ruff`, `ruff format --check`, both `mypy` passes, and
    `NEC2C=... uv run pytest`.

**Effort:** L (1–2 weeks). **Release:** 1.1, before the next public release.
**Risk:** medium–high because the repository port and lazy-loading path change;
mitigate with the ADR, atomic writes, the save/load invariant test, and a
manual recovery of the one existing pre-container project.

## PF2 — Streaming container write

**Status:** **Done 2026-11-27.** **Priority:** P3 memory and save-time
performance. **Trigger:** the PF1 benchmark showed the copy-entry save path at
174 MB peak RSS and the materialized path at 1,614 MB for the generated
four-run project; `PreparedProject.payload` still held the whole container in
memory.

**Former cost:** `prepare_payload()` built every entry, `_build_container()`
called `_zip_bytes(entries)` once to learn compressed sizes and a second time
with the manifest to produce the final bytes, and `write_payload()` validated
those bytes through `io.BytesIO` before `_atomic_write()` wrote them. Peak
memory therefore included all entry payloads plus the intermediate and final
containers. Copied run entries were read into `bytes` by `copy_entries()` even
though they were not parsed.

**Goal:** write and compact a container directly to the atomic destination (or
to a bounded temporary spool) one entry at a time, so peak memory scales with
the largest entry and I/O buffers rather than the whole history. The saved file
must remain byte-identical to the current deterministic writer and satisfy the
same limits, manifest hashes, and save/load invariant.

**Design (implemented 2026-11-27):**

1. Keep the manifest-first, sorted-entry, fixed-timestamp, ZIP level-6 format.
   Because the manifest needs each entry's compressed size, CRC32, and SHA-256,
   use a two-phase writer rather than a placeholder manifest:
   - phase 1 compresses each entry into a temporary spool and records its
     metadata;
   - phase 2 writes `manifest.json` first and then streams the spooled entries
     into the destination ZIP.
   A one-pass variant that writes the manifest last would be simpler but
   changes byte order and risks reader/golden churn; do not choose it without a
   format decision.
2. The container writer accepts entries as streams/chunks, not only `bytes`.
   Copied run entries stream from the source ZIP to the spool while the existing
   manifest CRC/SHA is verified, without materializing the full entry.
3. `PreparedProject` carries a prepared spool handle that exposes
   `compressed_bytes`, `expanded_bytes`, `entry_count`, `limits`, a binary
   stream, and a cleanup path. The repository keeps the atomic
   `write_payload(path, prepared)` port and streams the spool into the
   destination temporary file. The in-memory `payload` path remains only for
   small callers and test doubles; both produce the same output format.
4. Enforce per-entry, entry-count, expanded, and container limits while
   streaming. If the compressed container exceeds `MAX_CONTAINER_BYTES`,
   abort, unlink the temporary file, and raise `ProjectTooLargeError` without
   touching the previous project. The save/load invariant test covers this
   path.
5. Keep the save dialog's compressed/expanded sizes honest. Phase 1 computes
   the exact compressed sizes and can still prepare the payload in a worker;
   only the final write becomes streaming. Do not replace exact sizes with
   estimates unless the UI contract is explicitly changed.
6. Benchmark the same four-run generated project and the incident-scale
   6×68 MB shape. Record peak RSS for materialized save, copy-entry save, compact,
   and design-only save. A reasonable target to confirm with the spike is peak
   RSS near the largest entry plus roughly 100 MB of Python/ZIP overhead; do not
   promise a number before measuring.

**Scope (MVP):** the streaming writer, the prepared-spool contract, copied-entry
streaming, limit enforcement, atomic failure behavior, and the benchmark.

**Out of scope:** pattern splitting (PF3); changing the container version,
compression level, timestamps, or entry order; a new thread model (UX45);
changing when the UI prepares or saves; a binary pattern store or sidecar
database.

**Dependencies:** PF1 closed. No schema, solver, or domain dependency.
PF3 would benefit from this path but is deferred pending its ADR and schema
decision.

**Acceptance:**

- Saving and compacting a generated project with multiple large runs completes
  without holding all entry bytes and both ZIP passes in memory.
- The output is byte-identical to the current writer for a representative
  project, or an explicitly approved format change updates the golden bytes and
  ADR.
- Copied run entries are streamed and their manifest size, CRC32, and SHA-256
  are verified; a corrupted source entry aborts the save.
- A container over the compressed limit aborts before replacing the destination;
  the previous file remains intact.
- `PreparedProject` still reports honest compressed/expanded sizes and entry
  count, or the UI contract is updated with the same information.
- The save/load invariant test and the full gate pass.

**Tests:** byte-for-byte comparison against the current writer; generated large
project with a memory benchmark; source-entry corruption and size mismatch;
fault injection during the final replace; compressed-limit boundary; copied
entries without materialization; compaction and design-only paths; full
`ruff`, both `mypy` passes, and `pytest`.

**Evidence:** `scripts/benchmark_project_io.py` and a new streaming case; peak
RSS and wall time are report-only, with no numerical or solver claim.

**Risk / mitigation:** medium. The writer and `PreparedProject` port change, and
temporary spool cleanup/disk use add failure modes. Mitigate with a short design
note, byte-identical golden output, bounded spooling, fault injection around
`os.replace`, and a temporary in-memory fallback only if it keeps one output
format.

**Effort:** M (1–2 weeks including benchmark and failure tests). **Release:**
unassigned; optional maintenance after PF1.

**Implementation (2026-11-27):**

- `persistence/container_writer.ContainerSpool` stages each entry in a
  temporary ZIP, records the exact compressed size/CRC32/SHA-256, then writes
  the final manifest-first container by streaming the staged entries.
- Production `PreparedProject` values carry a `PreparedSpool` file handle and
  stream it into the atomic destination. The in-memory `payload` path remains
  for small callers and unit-test doubles; both produce the same ZIP format.
- `ContainerRunStore.copied_entry_streams()` opens the source container once
  and yields each unchanged run entry as a bounded stream; the writer verifies
  the manifest size, CRC32, SHA-256, and kind.
- `_iter_project_entries()` converts one run at a time instead of building a
  second `ProjectPayload` with every run.
- Limits are checked while adding each entry; a failure removes the spool and
  the destination is never replaced.
- ADR-0057 records the two-phase decision and the rejected one-pass and
  raw-deflate-copy alternatives.

**Measured benchmark (2026-11-27):** same generated four-run project
(118 MB expanded, 1.1 MB container), one process per operation:

| Step | Time | Peak RSS |
|---|---:|---:|
| open (lazy) | 0.00 s | 41 MB |
| select one run | 5.38 s | 682 MB |
| save (materialized) | 37.99 s | 1,659 MB |
| save (copy entries) | 1.22 s | 45 MB |
| compact (materialized) | 23.82 s | 1,660 MB |
| compact (copy entries) | 0.30 s | 45 MB |
| save design only | 0.01 s | 42 MB |

The copy-entry save and compact paths no longer scale with the full history.
The materialized paths are dominated by `ProjectSession.materialize()` and the
domain run objects, not by the container writer; PF3 (pattern-level lazy
loading) is deferred pending its ADR and a schema decision.

**Likely files:** `persistence/container.py`, `application/project_payload.py`
(prepared-spool contract), `application/ports/project_repository.py`,
`ui/project_io.py`/save workers if the prepared type changes,
`scripts/benchmark_project_io.py`, and the persistence/container tests.

## PF3 — Pattern-level lazy loading

**Status:** **Deferred 2026-11-27.** Requires a pattern-entry ADR and a
container-format/schema change; not scheduled in the 0.11.x patch line.
**Priority:** P3 memory on open/select and report responsiveness. **Trigger:**
PF1 lazy loading is per run, not per pattern. The benchmark shows a selected 2°
run with five patterns at about 682 MB peak RSS (roughly 400 MB of domain
objects), while impedance, SWR, and currents are much smaller and are usually
needed first.

**Decision (2026-11-27):** do not start PF3 now. PF2 removed the writer-side
duplication; the remaining open/select cost is the selected run itself, which
is a separate container and application-accessor change. Revisit only when
open/select memory becomes a release blocker and the pattern-entry ADR is
accepted.

**Current cost:** `ProjectSession` loads metadata/designs eagerly and runs on
demand, but `ContainerRunStore.load_run()` reads the complete `runs/<id>.json`
and `_read_runs()` materializes every `FrequencyResult.far_field` tuple. The
Pattern tab, 3D view, comparison, and reports all consume the same
fully materialized `SimulationRun`. There is no explicit state for "patterns
exist but are not loaded" versus "this run has no pattern".

**Goal:** store far-field patterns separately from the normalized
impedance/current run, load them only when a Pattern/3D/report consumer asks,
and make the availability state explicit. Pruning patterns must leave a valid
run with an honest "unavailable" state, never a synthetic empty pattern or
zero gain.

**Recommended design:**

1. Write a pattern-entry ADR before changing the container. Decide the entry
   layout, manifest index, container-version policy, and the state model. A
   proposed layout is:
   - `runs/<run-id>.json` keeps run metadata, frequency plan, impedance,
     currents, power, status, and raw-text references, with no pattern arrays;
   - `runs/<run-id>/patterns/index.json` lists frequency, entry path, point
     count, grid shape, and hashes;
   - `runs/<run-id>/patterns/<index>.json` holds one immutable pattern
     snapshot.
   Use the existing relative-POSIX path validation and a new container version
   or a documented extension; current readers reject unknown paths, so a
   version decision is required.
2. Extend the manifest run index with the pattern index metadata (frequency,
   entry path, point count, bytes, CRC32, SHA-256) so opening a project can
   validate and list patterns without reading them. Reject orphan, missing,
   duplicate, and mismatched pattern entries with `ProjectFormatError`.
3. Add an application-level run accessor rather than mutating domain objects:
   - `load_run(run_id)` returns the run summary with an explicit pattern state,
     for example `NOT_LOADED`, `AVAILABLE`, `PRUNED`, or `NO_PATTERN`;
   - `load_patterns(run_id, frequency_hz_or_index)` returns the immutable
     pattern snapshot;
   - cache per selected run and release the cache on design switch or session
     close.
   `SimulationRun`/`SimulationResult` remain immutable. Do not put a lazy proxy
   into the domain model; compose a display result at the application boundary.
4. Migrate consumers one at a time: Pattern tab first, then the 3D view, then
   comparison overlays, then HTML/PDF reports and pattern-bearing CSV. Each
   consumer must show an explicit loading/unavailable state and must request
   patterns explicitly. Do not make a missing pattern look like a flat or zero
   gain pattern.
5. Save and compaction copy unchanged pattern entries without reserializing
   them, just as PF1 copies unchanged runs. Retention/compaction must remove
   pattern entries with their run; a future optional "prune patterns for old
   runs" policy is a separate decision unless the ADR includes it.
6. Keep fingerprints, result status, band/batch ids, and report values
   unchanged when patterns are loaded. The pattern state is presentation and
   storage metadata, not a new electromagnetic result.
7. Measure a selected run before/after. A reasonable target to confirm with the
   spike is that selecting a run without patterns stays well below the current
   ~682 MB peak and that loading one pattern adds only that snapshot; do not
   promise a number before measuring.

**Scope (MVP):** pattern-entry format, manifest/index validation, session
accessor, Pattern-tab and report consumption, save/compact copying, explicit
unavailable state, and the memory benchmark.

**Out of scope:** binary or sidecar pattern storage; per-point lazy loading
inside one pattern; changing pattern resolution or solver output; automatic
pattern pruning without a product decision; changing the 3D rendering or report
layout; a second engine.

**Dependencies:** PF1 closed; pattern-entry ADR; PF2 soft (streaming is useful
when a save writes many pattern entries but is not required). UI consumers and
reports depend on the accessor contract.

**Acceptance:**

- Opening a project and selecting a run without patterns loads metadata,
  impedance, SWR, currents, and status; the UI reports that patterns are not
  loaded or not available, not zeros.
- The Pattern tab, 3D view, comparison, and reports load patterns on demand and
  produce the same values as the current fully materialized path.
- A run whose pattern entries were pruned opens and displays an explicit
  unavailable state; the rest of the run remains usable.
- Saving and compaction copy unchanged pattern entries and remove pruned ones;
  a round trip preserves pattern values, grid shape, frequency, and
  fingerprints.
- Missing, orphan, duplicate, path-traversal, CRC/SHA-mismatched, and
  over-limit pattern entries are rejected.
- Peak memory for a selected run without patterns is materially below the
  current benchmark; the pattern-loading step is measured separately.
- The full gate passes, including real `nec2c` tests; no numerical or
  electromagnetic-model change.

**Tests:** container round trip with patterns; manifest/index mismatch and
corruption; pruned/missing pattern state; lazy accessor and cache release;
Pattern-tab, 3D, comparison, and report output; save/compact entry copying;
per-entry/total limits; memory benchmark; full `ruff`, both `mypy` passes, and
`pytest`.

**Evidence:** `scripts/benchmark_project_io.py` and the PF1 benchmark table;
report-only memory and wall-time measurements. No new numerical reference or
accuracy claim.

**Risk / mitigation:** high. The container format, application accessor, and
multiple consumers change together, and the "not loaded" state can be confused
with "no pattern". Mitigate with an ADR, an explicit state enum, one consumer
per change set, a container-version decision, corruption tests, and a memory
benchmark. Keep the fully materialized path available as a parity oracle until
the last consumer migrates.

**Effort:** L (2–4 weeks including format, accessor, consumers, and tests).
**Release:** deferred; unassigned. Reconsider only after the pattern-entry ADR
is accepted and open/select memory becomes a release blocker.

**Likely files:** `persistence/container.py`, `persistence/schema.py` (run and
pattern payloads), `application/project_session.py`,
`application/ports/project_repository.py`, `ui/main_window.py`,
`ui/widgets/results_view.py`, pattern/3D views, `reporting/`, and the
persistence, session, UI, reporting, and benchmark tests.

**Sequence decision (PF2/PF3, 2026-11-27):**

1. PF2 is done and closed in ADR-0057. Do not reopen the writer for PF3.
2. PF3 is deferred until its pattern-entry ADR is accepted. The ADR must decide
   the entry layout, manifest index, container version, and the explicit
   `NOT_LOADED`/`AVAILABLE`/`PRUNED`/`NO_PATTERN` state before any code change.
3. When it is resumed, migrate consumers one at a time (Pattern tab, 3D view,
   comparison, reports, pattern-bearing CSV) and keep the fully materialized
   path as a parity oracle until the last consumer migrates.
4. Benchmark PF3 with `scripts/benchmark_project_io.py`; record peak RSS and
   wall time for open, select one run, and the affected report/pattern paths.
5. Do not change PF1's container version, entry order, compression level, or
   deterministic output without an explicit ADR; keep the save/load invariant
   test green.

## Product trust and station wave

**Status:** wave 0 (TS1–TS7, DL9) is **done 2026-11-19**; DL1 and DL2 are done,
DL5 is narrowed, and DL7 is implemented as a bounded slice. Wave 2 remains
partial (DL3/DL6); DL4 is canceled. Waves 1–2 are the active product sequence.
**Scope:** product trust, station completeness, and site awareness. **Product
scope:** [`ROADMAP.md`](ROADMAP.md). This wave pauses new antenna families: the
catalog is broad enough, and the next value is answering the questions an
operator asks before building.

This wave is part of the single active queue above. The queue table is
canonical; the subsections below define scope, dependencies, acceptance
criteria, evidence, and risk for each item.

**Priority:** P0 = TS1–TS7 and DL9, **done 2026-11-19**; P1 = DL5, narrowed
2026-11-24; P2 = DL3, DL6, and DL7 (DL3/DL6 partial, DL7 implemented bounded);
P3 = DL8. DL4 is canceled. P0 was the 1.0 gate; P1 and P2 are the 1.1 and 1.2
slices.

**Not in this wave:** the measurement-calibrated model, true multi-band
optimization, parametric custom geometry, CLI/API, a second engine as a
default, macOS packaging, and a large UI refactor. Antenna content work (C7h
6 m HexBeam, the LPDA 7 MHz swept variant, and new catalog presets) also waits
until the trust/station wave closes. These belong to the later platform or
content tracks and must not be smuggled into 1.0.

### Wave map

| Wave | Release | IDs | Exit criterion |
|---|---|---|---|
| 0 | 1.0 Confidence | TS1–TS7, DL9 | **Done 2026-11-19.** Trust and interoperability green; documentation truthful; no new family work |
| 1 | 1.1 Station | DL1, DL2, DL5 | **Done as narrowed 2026-11-24.** Smith and the bounded tuner check are usable; DL5 mast/guys delivered, boom/tower deferred |
| 2 | 1.2 Site and exploration | DL3, DL6, DL7 | Live preview, stacking, and bounded cliff ground with visible limits |
| 3 | post-1.2 | DL8 | Only after a validated terrain ADR; otherwise explicitly unavailable |

**Wave 0 order (completed 2026-11-19):** TS7 → TS3 → TS6 → TS4 → TS1 → TS2 +
DL9 → TS5. The quick wins made the application feel 1.0; convergence and
metrics followed; VNA import closed the interoperability side.

**Wave 1 order:** DL1 and DL2 are done. DL5 is narrowed to mast and guy wires; no further wave-1 work is planned.

**Wave 2 order:** DL7's bounded cliff slice is implemented; DL4 is canceled by
product decision. The DL6 first slice is implemented (form, schema 71, catalog,
per-port Sources, scene, reports, the splitter/phase-line feed specification,
one shared mast/guy set, the bounded spacing/phase optimizer, per-level
L/Pi/T matching, transformer ratios, branch loss, isolation parasitics, and
the deterministic Wilkinson tolerance check). A measured broadband
splitter/isolation model remains unavailable.

### Wave rules

- Table-stakes items land before delight items. DL1/DL2 are done; do not start
  DL5 while the wave-0 trust gate is open unless the owner explicitly reorders.
- Every item must leave `ruff`, both `mypy` passes, and the full `pytest` gate
  green, including real NEC2C integration where the item touches the solver.
- New UI surfaces require EN/ES strings and help-manifest coverage.
- New persisted fields require an explicit schema migration and a round-trip
  test. Items marked "no schema change" must stay schema-free.
- No new numerical reference, tuner range, terrain correction, or safety claim
  without a traceable source or a visible experimental label.
- Do not add a second backlog. Product scope goes to `ROADMAP.md`; execution
  detail and status stay here.

### TS1 — Convergence study for every wire family

**Status:** **Done 2026-11-19.** The 0.10/0.05/0.025/0.0125 λ ladder is
implemented for any canonical model with the existing segmentation policy,
`resolve_model_quality`, and `validate_segmentation`. The dialog reports R, X,
|Z|, SWR, per-wire Δ/a, gain/takeoff at the ends, invalid densities, and
cancellation; CSV export and the self-consistency thresholds are documented in
[`CONVERGENCE_STUDY.md`](CONVERGENCE_STUDY.md). Real NEC2C covers dipole,
vertical with radials, Yagi, and custom wire. Full gate: 4,147 passed, 1
skipped; NEC2C 165 passed. No schema or solver change.

**Goal:** answer "does this model converge?" without pretending that
self-consistency proves accuracy.

**Scope (MVP):**
- Domain `ConvergenceStudy`: run the same canonical `AntennaModel` at 3–5
  segment densities, for example 0.10λ, 0.05λ, 0.025λ, 0.0125λ, or a documented
  per-wire scale factor.
- Reuse `resolve_model_quality` and `validate_segmentation`; do not add a new
  solver or a new accuracy claim. The family adapter is not required; custom
  and imported wire models participate.
- Report R, X, Z magnitude, and SWR at the design frequency; pattern gain and
  takeoff angle at the coarsest and finest densities only (not every density);
  Δ/a per wire; divergent or invalid points; cancellation.
- Application use case and worker; results tab or dialog; CSV export.
- Label the verdict **self-consistency**, not accuracy.

**Out of scope:** cross-engine comparison (separate later item); adaptive mesh
optimization; automatic geometry repair.

**Dependencies:** existing segmentation policy, `resolve_model_quality`, and
`Nec2cSolver`. A short design note or ADR records the density ladder and the
verdict threshold. No schema change.

**Acceptance:**
- A dipole, a vertical with radials, a Yagi, and a custom wire model can be run
  at 3+ densities.
- The result states converged / marginal / not converged and shows the metric
  spread; the threshold is documented.
- Cancellation keeps completed densities but marks the study partial.
- The UI and report say "self-consistency"; no report claims validated accuracy.
- Unit tests cover the domain study; real NEC2C integration tests cover the
  representative models.

**Evidence:** no new numerical reference. Use reference cases and convergence
invariants; an independent reference is required only if a threshold is
presented as an accuracy limit.

**Risk / mitigation:** medium. The risk is interpreting a flat curve as
correct. Mitigation: the self-consistency label, a documented threshold, and a
one-week spike on representative models (dipole, vertical with radials, Yagi,
custom wire) to calibrate it. A later cross-engine check is the stronger test.

**Effort:** M (2–3 weeks). **Release:** 1.0.

### TS2 — Decision metrics, band-plan overlay, and circular polarization

**Status:** **Done 2026-11-19.** The shared metrics module defines the 2:1
bandwidth (with explicit sweep-edge unbracketing), HPBW, front-to-back,
sidelobe level, takeoff, efficiency, directivity, realized gain, pattern
resolution, and descriptive CP metrics. The Diagnostics card, SWR band-edge
markers, frequency CSV, and HTML/PDF reports expose them; missing pattern data
is explicitly unavailable. Full gate: 4,154 passed, 1 skipped; NEC2C 165
passed. See [`RESULT_METRICS.md`](RESULT_METRICS.md).

**Goal:** turn the result tables into a one-screen answer: does this design
cover the band, how wide is it, where does it point, and what polarization does
it produce?

**Scope (MVP):**
- Domain metric module: 2:1 SWR bandwidth (reuse or relocate
  `measure_bandwidth_hz` from the optimizer into a shared metrics module),
  half-power beamwidth in azimuth and elevation, front-to-back, sidelobe level,
  takeoff angle, efficiency, directivity, and realized gain.
- Amateur-band edges on the SWR chart from the existing band catalog;
  region-specific plans remain a later content item.
- CP: axial ratio, polarization sense, CP gain, and cross-polar discrimination,
  using the existing `axial_ratio`, `tilt_deg`, `polarization`, `e_theta`, and
  `e_phi` values.
- Results card and CSV columns; no solver change.
- Definitions documented in `USER_GUIDE.md` and, if the formulas need a
  normative home, a new `docs/RESULT_METRICS.md`.

**Out of scope:** propagation, coverage maps, legal band privileges.

**Dependencies:** TS1 soft (shared result extraction); band-plan data.

**Acceptance:**
- A multiband design shows 2:1 bandwidth against each selected band edge.
- A 2:1 bandwidth that reaches the sweep edge is reported as unbracketed, not
  as a finite value.
- A Yagi shows HPBW in both planes, F/B, and takeoff; HPBW and F/B report the
  pattern resolution and are not presented as more precise than the sampling.
- A circular test case shows axial ratio, sense, and CP gain.
- Missing far-field data produces an explicit unavailable value, never a silent
  zero.
- CSV and HTML/PDF report rows cover the new metrics.

**Evidence:** standard definitions; compare with a reference case for each
formula. CP requires a traceable circular reference or an explicitly heuristic
test; do not invent a gain value.

**Risk / mitigation:** low–medium. Definition ambiguity (HPBW near nulls, F/B
cut choice, band edges) is the main risk. Mitigation: one normative definition
per metric, a test case per definition, and a visible tooltip.

**Effort:** M (2–3 weeks) plus S–M for CP (1–2 weeks). **Release:** 1.0.

### DL9 — Circular-polarization metrics

**Status:** **Done 2026-11-19 with TS2.** Axial ratio, sense, co-pol CP gain, and
cross-polar discrimination are exposed in the decision card, CSV, and reports.
The formulas and the explicit "descriptive, not validated circular gain" label
are documented in [`RESULT_METRICS.md`](RESULT_METRICS.md). Tests cover
perfect-circular and linear cases. No solver change.

### TS3 — NEC-2 deck export and copy

**Status:** **Implemented 2026-11-19.** The export and copy actions use the
current design/spec, the header records provenance without paths or raw output,
and a real NEC2C round-trip reproduces the simulated impedance. Full gate:
4,107 passed, 1 skipped; NEC2C integration: 161 passed. A third-party NEC GUI
reader is the remaining manual release check.

**Goal:** make the canonical model portable and auditable.

**Scope (MVP):**
- **File → Export → NEC Deck...** and **Copy NEC Deck**.
- Reuse `Nec2InputWriter` and the current `SimulationSpec`; include a comment
  header with project, design, frequency plan, ground, segmentation, and
  application/solver version.
- Do not include raw solver output or private paths.
- Tests: export, parse/run with NEC2C, and compare impedance with the simulation
  within the documented tolerance.

**Out of scope:** EZNEC `.ez` export, NEC-4/5 cards, batch export of every
variant.

**Dependencies:** none.

**Acceptance:**
- The exported deck runs in `nec2c` and reproduces the simulation impedance
  within the documented tolerance.
- The file opens in at least one external NEC reader (manual QA).
- The deck is deterministic for the same project and spec.
- The action is disabled with an explicit reason when no design exists.

**Evidence:** NEC2C round-trip; external reader QA.

**Risk / mitigation:** low. Format drift is the risk; the round-trip test is the
guard.

**Effort:** S (3–5 days). **Release:** 1.0.

### TS4 — Autosave and crash recovery

**Status:** **Done 2026-11-19.** Autosave writes an atomic project recovery
payload and metadata to the application-data folder, never overwriting the
project. Startup offers recover or discard; a missing original path falls back
to **Save As**; normal save/close removes the copy; Preferences can disable it.
A follow-up removed the post-simulation CPU regression: recovery snapshots now
exclude completed runs/raw solver output, are debounced after design edits and
capped at 2 MB, and result-only changes do not trigger autosave. Full gate:
4,170 passed, 1 skipped; NEC2C 165 passed. Schema unchanged.

**Goal:** never lose a design to a crash, power loss, or accidental close.

**Scope (MVP):**
- Atomic autosave to a recovery file in the project directory or a
  platform-appropriate recovery folder; never overwrite the project.
- Detect a recovery file on startup; offer restore/discard; preserve the
  original path and dirty state.
- Opt-out in Preferences; clear the recovery file after a successful save.
- Tests: simulated crash, read-only directory, corrupt recovery file, project
  moved or deleted.

**Out of scope:** cloud sync, version history, auto-commit.

**Dependencies:** none; schema unchanged.

**Acceptance:**
- Killing the process mid-edit leaves a recoverable file.
- Restore produces the same project and design state; discard removes it.
- A missing project path falls back to **Save As**.
- No recovery file is left after a normal save/close.

**Evidence:** n/a (reliability).

**Risk / mitigation:** low. The risk is a confusing restore or a stale recovery
file; explicit prompts and tests mitigate it.

**Effort:** S–M (1 week). **Release:** 1.0.

### TS5 — VNA import 2.0

**Status:** **Done 2026-11-19.** CSV, `.s1p`, and port-selected `.s2p` files
import individually or in batches, including drag-and-drop. Parsing handles
locale numbers, semicolon delimiters, thousands separators, per-row units,
NanoVNA Saver/RigExpert/miniVNA/DG8SAQ detection, and a manual mapping fallback
remembered for the session. Duplicate names prompt replace/numbered copy;
malformed rows and oversized files are rejected. Full gate: 4,166 passed, 1
skipped; NEC2C 165 passed. No schema change.

**Goal:** import the sweeps radio amateurs actually have without manual
spreadsheet surgery.

**Scope (MVP):**
- `.s2p` in addition to `.s1p`; for `.s2p`, use S11 only with an explicit
  port selection and never silently use S21. Keep the existing one-port path
  for S11.
- Analyzer presets or auto-detection for NanoVNA Saver, RigExpert, miniVNA, and
  DG8SAQ; keep a manual column-mapping dialog as the fallback.
- Locale-aware number parsing: decimal comma, semicolon delimiter, thousands
  separators; units in headers (Hz–GHz).
- Drag-and-drop and multi-file import; one measurement per file or one session;
  explicit duplicate handling.
- Untrusted-input tests: huge files, malformed rows, mixed units. No archive
  extraction is involved.

**Out of scope:** live VNA control, calibration math beyond the file's
reference plane, S-parameter de-embedding.

**Dependencies:** none; no domain change.

**Acceptance:**
- A NanoVNA Saver CSV with decimal comma and `;` imports without editing.
- A RigExpert `.s1p` and a `.s2p` import with the correct reference impedance.
- Mapping choices are remembered for the session and shown in the measurement
  metadata.
- Malformed data is rejected with a row/column message; no silent drop.

**Evidence:** n/a (data import); keep sample files anonymized in tests.

**Risk / mitigation:** medium. Format variety is the risk; the manual mapping
dialog is the escape hatch.

**Effort:** M (2–3 weeks). **Release:** 1.0.

### TS6 — Recent projects and start-page examples

**Status:** **Done 2026-11-19.** Recent files persist in QSettings, show only
the file name, remove missing entries, and support an optional startup restore.
The start page creates normal dipole/Yagi/vertical example projects and opens
the reference library. No schema change. Full gate: 4,120 passed, 1 skipped;
ruff and both mypy passes green.

**Goal:** reduce the time from launch to a useful design.

**Scope (MVP):**
- Recent list in QSettings with path, name, and last-opened timestamp;
  missing-file handling and **Remove from list**.
- Start page: New, Open, Help me choose, Open example (dipole, Yagi, vertical),
  and Reference design library.
- Optional **Restore last project** toggle in Preferences.
- Show the file name, not the full path, on the start page.

**Out of scope:** cloud recent list, thumbnails, project templates beyond the
existing catalog.

**Dependencies:** none.

**Acceptance:**
- The recent list persists across restarts and removes missing files with a
  message.
- Opening an example creates a normal project through the existing creation
  path.
- No new persistence schema.

**Evidence:** n/a.

**Risk / mitigation:** low. Path privacy is the only concern; the file-name
display is the mitigation.

**Effort:** S (3–5 days). **Release:** 1.0.

### TS7 — Documentation truth pass and status review

**Status:** **Done 2026-11-19.** The known stale claims are corrected, the
pre-alpha label is now pre-1.0, template limitations point to their single
source, schema 56 is documented, and a documentation test guards the corrected
strings. Full gate: 4,098 passed, 1 skipped; ruff and both mypy passes green.

**Goal:** make the documentation match the shipped behavior before 1.0.

**Scope (MVP):**
- Audit `README.md`, `USER_GUIDE.md`, `SOLVER_ADAPTER.md`, `ARCHITECTURE.md`,
  `DOMAIN_MODEL.md`, and the evidence/limitation text for stale claims.
- Known examples: realized gain/directivity separation, boom/turning-radius
  constraints, feed-line loss in realized gain, persisted results, and progress
  reporting.
- Single-source the limitation list where practical; at minimum, link every
  limitation to its ADR or evidence source.
- Review the "pre-alpha" status after the 1.0 gate.
- Add a documentation test or script that fails on the known stale strings.

**Out of scope:** rewriting the user guide, translating docs, marketing.

**Dependencies:** none.

**Acceptance:**
- No known contradiction remains.
- The README status matches the release state.
- The limitation list is generated or checked from one source.
- The changelog records the documentation correction.

**Evidence:** n/a.

**Risk / mitigation:** low. The risk is missing a contradiction; the test and a
checklist of the known examples mitigate it.

**Effort:** S (2–4 days). **Release:** 1.0.

### DL1 — Smith chart and matching workbench

**Status:** **Done 2026-11-19.** The Smith tab, normalized locus,
reference-plane selector, measured overlay, hover readout, marker, editable
feed-line preview, automatic L/Pi/T matching preview, and PNG/SVG/CSV export
are implemented. Manual matching-component entry and network optimization
remain follow-ups; the preview is a starting design, not an optimized network.

**Goal:** make impedance transformation visible and interactive.

**Scope (MVP):**
- Pure domain `smith_chart.py`: Γ from Z, Z from Γ, normalized/denormalized,
  constant-R/X circles, and cursor readout.
- Results view: Smith tab with impedance locus per frequency; measured versus
  simulated overlay; marker at the selected frequency.
- Feed-line transformation preview: length, Z0, velocity factor; before/after.
- Matching network preview: reuse `MatchingNetwork`; L/Pi/T; ideal versus
  lossy; target marker.
- Export PNG/SVG and CSV; no solver change.

**Out of scope:** full circuit editor, arbitrary S2P blocks, network optimizer
(separate).

**Optional follow-up:** per-component branch voltage/current ratings and direct
L/Pi/T value editing. The current ratings are tuner-input and antenna-load
estimates, not per-branch component ratings.

**Dependencies:** existing `MatchingNetwork`, `FeedLine`, and
`FrequencyResult`.

**Acceptance:**
- A 50 Ω load maps to the center; a known L network moves the locus to the
  target; the cursor readout matches the table.
- The measured/simulated overlay uses the same reference impedance and reports
  it.
- Large sweeps are decimated for drawing but keep every point in CSV.
- No electromagnetic calculation in the widget.

**Evidence:** Γ/Z identities and network transformations against known values.

**Risk / mitigation:** low–medium. UI performance and network integration are
the risks; a point cap and pure-domain tests mitigate them.

**Effort:** M–L (3–6 weeks). **Release:** 1.1.

### DL2 — Tuner matchability and realizable components

**Status:** **Done 2026-11-20.** **Tools → Tuner Matchability...** designs a
bounded L/Pi/T network at each simulated frequency or band center, snaps
components to ideal/E12/E24, applies the optional Q loss, and reports status,
SWR, loss, limiting part, and input/load voltage/current at the entered power. Out-of-
range L/Pi/T designs try a bounded best-effort search and bypass when they do
not improve the raw SWR. Per-part voltage/current ratings and a dedicated
per-band sweep remain follow-ups.

**Goal:** answer "will my ATU match this, and what real parts do I need?"

**Scope (MVP):**
- Domain tuner model with C/L ranges, topology (L/Pi/T), best-effort match,
  bypass, loss, voltage, current, and power dissipation.
- Per-band table: matchable / best effort / not matchable, achieved SWR,
  component values, loss, and limiting part.
- Tuner ranges are analysis inputs; persist a selected tuner only if the editor
  needs to remember it, with a schema migration.
- Real component layer: E24/E12 nearest values, Q/ESR, voltage/current ratings,
  ideal versus real comparison; apply to the existing matching network and load
  editors.
- Sources: standard series, manufacturer data, and documented generic ranges
  where a specific unit is unknown; label generic ranges as such.

**Out of scope:** a full ATU database, automatic band switching, thermal model,
price catalog.

**Dependencies:** ADR for the tuner model and component-range policy; DL1 soft
(Smith is the natural front-end); existing `MatchingNetwork`; no solver change.

**Acceptance:**
- A random wire is marked matchable on the bands the selected tuner covers,
  with achieved SWR and loss; unsupported bands are explicit.
- The best-effort state is visible; bypass is never silent.
- Voltage/current warnings appear near ratings.
- The BOM/report shows real values and ratings.

**Evidence:** component series; manufacturer/documented tuner ranges. Do not
claim universal tuner capability without a source.

**Risk / mitigation:** medium. Model fidelity is the risk; keep "generic range"
labels and a visible limitation.

**Effort:** M–L (3–6 weeks). **Release:** 1.1.

### DL3 — Live tuning preview

**Status:** **Done 2026-11-27.** A managed-dimension selector covers the
primary dimension plus family-specific length dimensions such as height,
spacing, radial length, feed height, reflector spacing, the Flower Pot feed and
choke heights, and the trapped-Yagi trap inset. The coarse single-frequency
preview, debounce/cancel, stale-result guard, preview badge, optional coarse
elevation-cut pattern preview, and apply/full-run path are implemented. The
selector also covers managed angles, counts, and transformer/feed ratios.
**Apply and simulate** closes the dialog and starts the full simulation.

**Goal:** make geometry exploration immediate without replacing the full
simulation.

**Scope (MVP):**
- Select and drag a managed length dimension (primary, height, spacing, radial
  length, feed height, reflector spacing, and similar) and run a coarse
  single-frequency solve with pattern disabled; debounce and cancel.
- Preview badge and "preview" label in the status bar; no reports or saved
  results from preview.
- Commit applies the value through the normal adapter and runs the full
  simulation.
- Performance budget: about 200–500 ms for a typical dipole on the development
  machine; large models fall back to "release to update".
- Tests for cancellation, stale responses, and no accidental persistence.

**Out of scope:** continuous full-pattern solving, GPU acceleration, optimizer
replacement. Optional UX follow-up: turn the modal dialog into a non-modal tool
window; that needs explicit stale-baseline and concurrent-simulation handling.
Additional family-specific managed values remain incremental follow-ups.

**Dependencies:** existing worker/cancellation; no solver change.

**Acceptance:**
- Dragging a length updates SWR and impedance in preview; releasing stops the
  worker.
- A stale result never overwrites a newer one.
- Commit produces a normal simulation and undo entry.
- Apply closes the dialog and starts the full simulation.
- Preview values are visibly marked and never exported as final.

**Evidence:** performance benchmark; no accuracy claim.

**Risk / mitigation:** medium. UI latency and stale results; request IDs,
cancellation, and a coarse mode mitigate them.

**Effort:** M–L (3–6 weeks). **Release:** 1.2.

### DL4 — Near-field and RF exposure (canceled)

**Canceled 2026-11-24.** The product owner judged near-field/RF-exposure
compliance modeling not relevant enough to the amateur design workflow to
justify the solver, standards, and safety-claim work. Do not start it.

### DL5 — Support structures

**Status:** **Explicitly narrowed 2026-11-24.** The delivered 1.1 slice is the
optional vertical mast conductor behind the Yagi reflector with editable
diameter and offset, normal wire geometry, optional 2–4 guy wires, scene/BOM
coverage, ADR-0048, and schema 57–58. It is not connected to the elements. The
conductive boom, tower, bonded/insulated attachments, and structural hardware
are deferred pending a dedicated ADR/spike; no further 1.1 work is planned.

**Boom decision (2026-11-20): deferred.** Do not implement a conductive boom
as another mast-like field. It changes the wire graph and feed junction at every
element center, so it needs a dedicated ADR and NEC2C spike before code. A
mechanical/insulated boom is the low-risk fallback if the electromagnetic model
cannot be validated. Tower, attachments, and structural hardware remain open.

**Goal:** include the metal around the antenna in the model.

**Scope (MVP):**
- Domain support objects: boom, mast, tower, and guy wire; material, diameter,
  height, attachment points, insulated/bonded options. This is a model
  extension, not a new catalog antenna family.
- Yagi option **Model boom**; mast/tower object for verticals and beams; guy
  wires as wires.
- Scene, wire schedule, BOM, construction notes, and reports.
- Warnings when a support is visible in the installation profile but not
  modeled.
- ADR for the canonical model extension; schema migration.

**Out of scope:** structural analysis, wind load, concrete, climbing safety.

**Dependencies:** ADR; existing `Wire`/`AntennaModel`; scene/report paths.

**Acceptance:**
- A Yagi with boom and mast simulates and draws both; the wire schedule
  includes them.
- Bonded versus insulated attachment changes the model and is visible.
- The report states what is and is not modeled.
- Existing projects migrate with no support structures.

**Evidence:** structural tests; evidence B/C. No gain/impedance accuracy claim
without a reference.

**Risk / mitigation:** medium. Geometry/attachment complexity; tests and a
narrow MVP (straight cylinders) mitigate it.

**Effort:** M–L (3–6 weeks). **Release:** 1.1.

### DL6 — Stacked Yagi arrays

**First slice implemented (2026-11-25):**
[`ADR-0049`](ADR/0049-stacked-yagi-composed-family.md) composes two to four
identical Yagis with an ideal source progression. The slice delivers the
domain model, schema 71, both catalog routes, the embedded Yagi/stack form,
per-port **Sources** results, front-elevation scene and dimensions, design and
construction reports, a multi-boom BOM, a real `nec2c` two-port test, an
optional splitter + phase-line feed specification, and a bounded spacing/phase
optimizer inside the maximum top-height envelope. A network mode adds a 1 cm
numerical splitter node and co-simulates lossless NEC TL cards to every level,
including the reference line, and reports every network port; a user-entered
matched line loss plus a per-port mismatch correction is applied to realized
gain. One shared mast and optional guy set are modeled across every level, and a
beta/hairpin match or folded driven element is built at every driven element. A
pure-Python N-port
feed-network solver, NEC antenna Y-matrix extraction, and a user-facing
Wilkinson divider mode are implemented and validated against the standard
Wilkinson, scikit-rf, and the existing NEC TL co-simulation. Folded driven
elements are copied to every level as geometry-only, with optional ideal
per-level transformer ratios, matched branch loss, isolation-resistor
series/parallel parasitics, and a deterministic tolerance corner check in
Wilkinson mode. A measured broadband splitter/isolation model remains a
follow-up. Evidence is C and no
stacking gain is claimed. See also
[`spikes/dl6-stacked-yagi-spike.md`](spikes/dl6-stacked-yagi-spike.md).

**Delivered in the first slice:**
- A two-level stack runs with two driven sources; the `Sources` table reports
  R/X/power for each port. In ideal and phase-line mode the primary SWR stays
  on level 1; network mode uses the splitter-node input.
- The scene opens in front elevation, shows the level spacing and the complete
  wire model, and warns that plan view collapses the levels.
- Reports show levels, spacing, top height, phase step, amplitude ratio, and
  the ideal-feed limitation; the BOM uses one boom per level.
- A vertical-polarized stack rejects overlapping levels.
- The base editor can add a folded driven element inside a stack; its mast/guy
  fields are shared by all levels and its beta/hairpin match fields are applied
  to every driven element. Wilkinson mode adds per-level ideal transformer
  ratios and matching networks for the folded geometry.
- Phase-line mode derives the excitation phase from the extra line length per
  level, records the reference length, velocity factor, Z0, and splitter excess
  loss, and applies that loss to realized gain.
- Network mode adds a 1 cm numerical splitter node, co-simulates lossless NEC
  TL cards from that node to every level including the reference line, reports
  every network port, and applies a user-entered matched line loss plus a
  per-port mismatch correction to realized gain while the primary SWR stays the
  lossless node input.
- One shared mast and optional guy set run from ground to the top boom; the
  base Yagi's support fields are interpreted once for the whole stack.
- An N-port feed-network solver and NEC antenna Y-matrix extraction are
  validated; the Wilkinson divider mode exposes them in schema 71, the editor,
  reports, and the construction-sheet feed-network table, with a
  reconstructed pattern, optional per-level L/Pi/T matching networks, optional
  ideal transformer ratios, matched branch loss, isolation-resistor series/parallel
  parasitics, and a deterministic tolerance corner check; the conductor BOM
  remains conductor-only.
- The optimizer searches level spacing and either the ideal phase step or the
  line increment inside the maximum top-height envelope; the level count, base
  Yagi, and amplitude ratio stay context. In Wilkinson mode it rebuilds the
  feed-network spec for each candidate, including the per-level networks.

**Remaining work:** a measured broadband splitter S-parameter/isolation model. The [measured-splitter spike](spikes/dl6-measured-splitter-spike.md) (2026-11-26) concludes that this needs measured S3P/S4P data, multi-port Touchstone support, and an embedded-data/provenance ADR; no measured model is implemented. The earlier [feed-network spike](spikes/dl6-feed-network-spike.md) rejects
scalar isolation post-processing and proposes
[ADR-0054](ADR/0054-bounded-multiport-feed-network.md): an N-port solver and a
bounded equal N-way Wilkinson with star isolation at a declared design
frequency. The per-level L/Pi/T branch and a bounded tolerance corner check are
implemented; a frequency-dependent non-ideal splitter/isolation model and
frequency-dependent component loss remain.

**Goal:** answer "two stacked Yagis or one bigger one?"

**Scope (MVP):**
- Composed family: 2–4 identical Yagis, vertical spacing, phase-line lengths,
  feed split, and optional power-divider loss. This is a composed array
  capability, not a new catalog antenna family; it reuses the Yagi elements.
- Multi-source model and `TransmissionLine` reuse; per-port impedance and
  pattern.
- Optimizer variables for spacing and phase with mechanical constraints.
- Scene, reports, construction notes; ADR.
- Evidence: published stack measurement if available; otherwise B/C and a
  visible limitation.

**Out of scope:** full antenna farm, arbitrary feed networks, tower interaction
(covered by DL5 if enabled).

**Dependencies:** DL5 soft; multi-source model; ADR; schema migration for the
composed stack design.

**Acceptance:**
- **Delivered:** a two-level stack runs with per-port impedance and the
  combined pattern; a three-level stack is covered by the form/domain tests.
- **Delivered:** the report shows the stack dimensions and feed notes.
- **Delivered:** no gain claim beyond the evidence level.
- **Delivered:** spacing/phase optimization respects the maximum top-height
  envelope; spacing cannot overlap vertical-polarized elements.

**Evidence:** traceable stack reference or B/C. Do not invent a stacking gain.

**Risk / mitigation:** medium–high. Feed network and evidence; a one-week spike
with a published stack mitigates it.

**Effort:** L (6–8 weeks). **Release:** 1.2.

### DL7 — Native ground screen and cliff ground

**Decision and implementation (2026-11-24):**
[ADR-0051](ADR/0051-bounded-cliff-site-ground.md) implements only the
cliff/second-medium far-field profile. It adds one optional project-level
`SiteGroundProfile`, applies it at simulation/export time, emits `RP 2`/`RP 3`,
and states that SWR and currents are unchanged. The native radial screen remains
unavailable until a measurement or published reference exists. Schema 60 adds
`site_ground` with a metadata-only 59→60 migration. A real nec2c test confirms
the impedance is unchanged while the far-field pattern differs. No external
site reference is available, so the B/C evidence label stands and no further
validation is planned.

**Goal:** use the ground information the engine already supports before building
a full terrain model.

**Scope (MVP):**
- Extend `GroundModel` with optional radial-screen and second-medium/edge
  fields; emit the extended `GN` card; parse the status.
- UI: ground preset **Radial screen** and **Cliff / second medium**; scene and
  report notes; schema migration.
- Compare with the current dense-wire radial approximation and the NEC-2
  manual examples; label as B/C.
- Do not claim full terrain; this is a straight edge and a radial screen.

**Out of scope:** faceted terrain, diffraction, arbitrary height profiles,
buried conductors.

**Dependencies:** ADR; spike on `GN` semantics; existing input writer.

**Acceptance:**
- A vertical with a radial screen runs with the native card; the result is
  compared with the dense-wire approximation and the difference is documented.
- A two-medium/edge case runs and changes the pattern consistently.
- The UI states the straight-edge limitation.
- Projects without the new fields migrate unchanged.

**Evidence:** NEC-2 manual; dense-wire comparison; reference case if available.
No invented terrain correction.

**Risk / mitigation:** medium–high. `GN` semantics and validation are the risks;
a one-week spike and a strict B/C label mitigate them.

**Effort:** M–L (3–6 weeks). **Release:** 1.2.

### DL8 — Full terrain model

**Goal:** model a real site beyond a straight edge.

**Scope:** only after DL7 and a validated terrain model or a second engine. A
faceted far-field model or an external engine adapter must be selected by an
ADR; the current flat-current solve stays explicit.

**Out of scope until the ADR:** arbitrary terrain, buildings, vegetation,
diffraction, multiple bounces.

**Dependencies:** DL7; ADR; possibly a second engine.

**Acceptance:** the ADR selects a traceable model; the implementation reproduces
the chosen reference; otherwise the feature remains explicitly unavailable. No
fudge factor.

**Evidence:** traceable terrain reference or measurement; B/C at best.

**Risk / mitigation:** high. Do not start before DL7 and the ADR.

**Effort:** XL (8+ weeks). **Release:** post-1.2.

## VR1 — Sloped vertical radials (uniform droop)

**Status:** **implemented 2026-11-24.** **Priority:** bounded vertical geometry
enhancement; see ADR-0052 for the accepted decisions and limitations.

**Motivation:** the vertical and loaded-vertical templates currently generate
all radials in the horizontal plane at `base_height_m`. The existing
`radial_angle_deg` is the azimuth of the first radial, not a droop angle. Sloped
radials are common for elevated quarter-wave verticals and for ground-mounted
radial skirts, and NEC-2 already supports them as ordinary straight wires. The
missing work is parametric modeling, validation, persistence, presentation, and
optimizer coverage, not a solver feature.

**Goal:** add one uniform downward angle to the generated radial set so users
can model a radial skirt without converting to custom wires.

**Implementation (2026-11-24):** schema 61 stores `radial_droop_deg` with a
default of 0. The domain keeps physical radial length, exposes horizontal span
and tip height, rejects tips at or below ground when the base is elevated, and
round-trips droop through custom wires. The editor caps the angle with the
current base/radial length; the scene labels the plan span instead of the
physical length; the design summary and construction sheet add droop and tip
height. Live tuning exposes the angle when the current geometry allows it, and
the locked optimizer variable has a hard tip-clearance constraint. A real
`nec2c` sloped-radial case completes with positive resistance.

**Scope (MVP):**
- Add `radial_droop_deg` to `VerticalParameters`: 0° horizontal, positive tips
  down, bounded below 90°; keep 0° bit-identical to the current geometry.
- Define `radial_length_m` as the physical conductor length. Endpoint:
  `r = L cos(delta)`, `z = base_height - L sin(delta)`; document the horizontal
  footprint and tip height.
- Validate that radial tips stay at or above ground; for ground-backed models,
  decide and document the NEC clearance policy. Do not let a sloped tip bypass
  the current 1 cm clearance silently.
- Reconstruct the droop in `from_custom_parameters()`; today it uses only
  `hypot(x, y)` and would flatten a sloped custom radial.
- Add the editor field, EN/ES label and help, enablement when `radial_count > 0`,
  and preserve it in `_preserve_estimate_context()`.
- Update the scene summary and plan-inset dimension: a physical radial length
  cannot be labelled over a shorter horizontal projection. Use the horizontal
  footprint or a true-length callout; the wire schedule remains authoritative.
- Add design-summary and construction-sheet rows for droop and tip height;
  replace the "in the base plane" construction note.
- Persist with the next schema bump (61 at the time of writing) and a
  no-value-rewrite migration; regenerate the example container and update the
  schema truth tests.
- Add family-optimizer coverage: a bounded variable with a hard tip-clearance
  constraint, or an explicit context classification. Do not leave the field
  uncovered.

**ADR decisions:** `radial_droop_deg`, positive-down convention, range
`0 <= droop < 90`, physical radial length, tips above ground when the base is
elevated, locked optimizer variable with a tip-clearance constraint, and no
`PhasedVerticalParameters` field in this slice.

**Out of scope:** independent angle or length per radial; arbitrary radial
layouts (use custom wires); buried or soil-contact radials; the native NEC `GN`
radial screen; performance claims or an "optimal" droop preset without a
traceable source.

**Likely files:** `domain/antennas/vertical.py`,
`domain/optimization/families/vertical.py`, `persistence/schema.py`,
`persistence/constants.py`, `persistence/container.py`,
`ui/widgets/vertical_form.py`, `ui/widgets/radial_presets.py`, `ui/i18n.py`,
`ui/main_window.py`, `ui/geometry/builder.py`, `reporting/design_summary.py`,
`reporting/construction_sheet.py`, `simulation/assumptions.py`, and the
corresponding domain, persistence, UI, scene, reporting, optimizer, and NEC2C
tests. Include `phased_vertical.py` and its form/payload only if that scope is
accepted.

**Acceptance:**
- A vertical with droop greater than zero has connected radials, exact 3D wire
  lengths, and tips at the declared height; droop = 0 reproduces the current
  canonical wires.
- Invalid tips are rejected with a clear message; a ground-backed simulation
  does not emit a wire endpoint at `z = 0` through the clearance gap.
- `to_custom_parameters()` and `from_custom_parameters()` round-trip the droop.
- Old projects load at 0° with unchanged geometry; the new schema round-trips
  and the previous schema migrates.
- EN/ES help is in the manifest; the estimate-context and preset behavior are
  tested.
- The scene, wire schedule, design summary, and construction sheet agree.
- The optimizer either explores the field with a hard constraint or states why
  it is installation context; field-coverage, determinism, and Apply Best pass.
- A real nec2c sloped-radial case completes with positive input resistance.
- No new numerical reference or performance claim is added.

**Tests:** domain validation and round-trip; schema migration; UI form, help,
and presets; scene contract and plan dimension; reporting; optimizer
registry/constraints; real nec2c integration; documentation truth. Keep the
golden scenes unchanged unless the default scene intentionally changes.

**Evidence:** structural/experimental; the family remains B/C for starting
dimensions. Sloped-radial performance is not independently validated; do not
invent an optimum.

**Risk / mitigation:** medium. The main risks are ground clearance and
presentation semantics, not the geometry formula. An ADR plus one real nec2c
case and explicit tip validation mitigate them.

**Effort:** M (1–2 weeks). **Release:** unassigned; not before the ADR and the
current 1.1/1.2 priorities.

## FP1 — Flower Pot half-wave family

**Status:** **implemented 2026-11-26 (schema 72; feed/choke revision schema
73); QA closed 2026-11-27.** **Priority:** P2 catalog/VHF. The length spike
selected Option A, ADR-0055 is implemented, and the family is in the catalog
with both routes, estimator, optimizer, scene, reports, and real `nec2c`
2 m/6 m coverage. The manual visual pass confirmed the physical feed/choke
split and the pattern overlay anchor; see
[`archive/qa/QA_PASS_2026-11-27_fp1.md`](archive/qa/QA_PASS_2026-11-27_fp1.md).
**Decision:** [ADR-0055](ADR/0055-flower-pot-half-wave-family.md), with the
spike in [`spikes/fp1-flower-pot-length-representation.md`](spikes/fp1-flower-pot-length-representation.md).

**Motivation:** the VK2ZOI Flower Pot is a popular, inexpensive 2 m/6 m portable
vertical. It is a coaxially fed vertical half-wave dipole, not an end-fed wire
and not a vertical with radials. The app can approximate it as a custom vertical
dipole today, but it cannot represent the coax construction, the resonant choke,
the conduit loading, or the physical-versus-electrical cut lengths. The catalog
has J Pole/Slim Jim, Ringo, discone, and vertical templates; a guided Flower Pot
fills a real VHF/portable gap without adding a solver dependency.

**Goal:** add the half-wave Flower Pot as a first-class family with honest
construction guidance and a bounded electromagnetic equivalent. The published
2 m and 6 m dimensions are the starting references; the model must not claim a
validated 50 Ω match, gain, or choke impedance.

**Scope (MVP):**
- Add `FlowerPotParameters` with frequency, physical top and bottom lengths,
  top and bottom radii, a construction shortening factor, a positive feed
  height, a construction-only choke height, material/ground, and construction
  context for the coax/conduit/choke.
- Generate two collinear canonical wires as the radiating arms. The physical
  feed is at the bottom of the choke; the two-wire NEC equivalent source is at
  the arm junction. The lower wire ends at the choke; the feedline below the
  choke is the project `FeedLine`, not antenna geometry.
- Use an ideal common-mode choke in the MVP. The UI, reports, and evidence state
  that the real choke impedance, common-mode current, coax dielectric loss, and
  conduit dielectric body are not modeled.
- Resolve physical versus electrical length in the spike. The selected option
  must keep the canonical solved model and the physical cut list explicit and
  consistent; no hidden simulation-only scale.
- Add the catalog entry and both routes (New Antenna and Change Template), an
  inline editor/dialog, EN/ES labels and help, adaptive length fields, and the
  feed-connection/balance detail for an integrated choke.
- Add the elevation scene with two wires, the physical feed below the choke,
  the choke dimension, the NEC equivalent source at the arm junction,
  top/bottom/total dimensions, a labeled not-to-scale choke detail inset, and a
  conduit note. The feed gap remains an as-built dimension. Do not expose a plan
  view that collapses the vertical wires.
- Add the estimator for the published 2 m/6 m rows: physical total about
  `0.44 λ`, split about `50.5 / 49.5`, shortening factor `0.88`, confidence B
  for the published rows and heuristic outside them. No numeric choke table is
  embedded; the choke stays ideal until measured data exists.
- Add the family optimizer for the top and bottom physical lengths, with
  positive-length, feed/choke-clearance, and construction-envelope constraints;
  target impedance or minimum SWR at the design frequency. The shortening
  factor and choke remain context.
- Persist with the next schema bump and an additive/no-op migration. Existing
  projects load unchanged.
- Add design-summary, construction-sheet, cut-list, BOM, and checklist rows for
  the coax, conduit, choke former, end cap, feedpoint seal, drainage, and
  braided-shield requirement.
- Add a real `nec2c` 2 m/6 m regression with finite impedance and a resonance
  consistent with the selected representation.

**Delivered:** `FlowerPotParameters` with physical top/bottom cuts, both radii,
physical feed height, construction-only choke height, the separate 0.88
construction factor and 1.087 NEC model scale, material, and ground. Two
collinear wires are generated as the radiating arms, with the NEC equivalent
source at their junction and the scaled lower tip validated above ground.
Schema 72 added the payload with an additive 71→72 migration; schema 73 adds
the choke height and the feed-height semantics with an additive 72→73
migration. The catalog, editor/dialog, EN/ES help, estimator, top/bottom family
optimizer, elevation scene with physical feed/choke and a choke inset, design
summary, construction cut list, BOM rows for the coax radiator, conduit,
choke/former, end cap, and feedpoint seal, feed-balance/connection detail for
the integrated choke, and real `nec2c` 2 m/6 m regression are in place. The
conduit and feed gap remain visible construction notes; neither is a synthetic
wire.

**Revision 2026-11-27:** the first implementation used the arm junction as the
reported feed. VK2ZOI and VK4PK place the physical feed at the bottom of the
choke; the junction is the NEC equivalent source. The family now reports the
physical feed and the choke separately, with published construction heights of
45 mm (2 m) and 63 mm (6 m). The solver and the 1.087 scale are unchanged. The
3D pattern overlay is anchored at the physical feed. Manual QA confirmed the
corrected behavior; see
[`archive/qa/QA_PASS_2026-11-27_fp1.md`](archive/qa/QA_PASS_2026-11-27_fp1.md).

**Explicitly out of scope:** single 5/8 (needs a shorted one-port stub), double
5/8 (needs a coax/TL radiator), dual-band sleeve (needs a sleeve/cylinder and
phasing model), experimental high-gain dual-band, 70 cm single-band designs
outside the published choke table, synthesized choke R+jX, common-mode current,
dielectric loss, a 50 Ω/gain/bandwidth claim, and any new solver engine or
dependency. Each deferred variant needs its own spike and ADR.

**Spike (phase 0, complete 2026-11-26):** compared, with the bundled `nec2c`,
the bare physical 904 mm/2518 mm wires, an electrical model scaled by
`1 / 0.88`, an electrical model scaled by `1.087`, an `IS`/`LD 7` coating
model, and a lumped equivalent, with sensitivity to radii, base height,
ground, and segmentation. `nec2c` rejects `IS` and `LD 7`; the naive
`1 / 0.88` scale resonates too low. **Option A with an explicit 1.087 NEC
electrical scale** puts both published bands in range while keeping the
physical cut list separate. See
[`spikes/fp1-flower-pot-length-representation.md`](spikes/fp1-flower-pot-length-representation.md).

**ADR decisions:** half-wave scope only; two-wire canonical model; ideal choke;
feedline below the choke; physical cut list and canonical model both explicit;
positive feed height and construction-only choke height; integrated choke means
no separate current balun; evidence B/C; no 50 Ω or gain claim; schema additive;
estimator and optimizer coverage.

**Likely files:** a new `domain/antennas/flower_pot.py`;
`domain/antennas/design.py`, `family.py`, `feed_connection.py`;
`domain/design/feed_balance.py`, `evidence.py`, `estimators.py`, `formulas.py`;
`domain/optimization/registry.py`,
`domain/optimization/families/typed.py`; `application/simulation_specs.py`;
`persistence/schema.py`; `ui/catalog.py`,
`ui/dialogs/antenna_catalog_dialog.py`, a new form/dialog;
`ui/geometry/builder.py`; `ui/i18n.py`; `ui/help.py`;
`reporting/design_summary.py`, `construction_sheet.py`; and the corresponding
domain, persistence, catalog, scene, reporting, estimator, optimizer, i18n/help,
and real-NEC2C tests.

**Acceptance:**
- The spike compared the four length representations at 2 m and 6 m and
  ADR-0055 recorded Option A; no numerical reference is invented.
- The canonical model, scene, wire schedule, physical cut list, and construction
  sheet keep the 0.88 construction factor and the 1.087 electrical model scale
  distinct and agree on which lengths are electrical and which are physical;
  no build value is hidden or derived only from a display.
- The scaled electrical lower-tip extension is visible and validated against
  the base height.
- The construction view is elevation, preserves both wires and the feed, and
  does not count the choke/conduit overlays as canonical wires; dimensions are
  non-zero and anchored.
- The published 2 m and 6 m starting dimensions are reproduced within the
  documented tolerance; the estimator shows the choke/conduit/feedline
  limitations and does not claim 50 Ω or gain.
- The feed connection says "integrated choke, no separate current balun" and
  does not require the project current-balun record.
- The optimizer covers the top/bottom lengths, passes field-coverage, budget,
  constraint, determinism, Apply Best, and solver QA, and cannot produce an
  unbuildable geometry.
- Old projects load unchanged at the new schema; the new payload round-trips;
  both catalog routes and EN/ES help pass their tests.
- A real `nec2c` 2 m/6 m case completes with finite impedance and a resonance
  consistent with the selected representation.
- No new numerical reference or performance claim is added.

**Tests:** domain validation and `to_antenna()`; physical/electrical round-trip;
schema migration and payload round-trip; catalog routing in both dialogs; scene
contract, construction view, dimensions, layout, and wire schedule; estimator
registry and published-row checks; optimizer registry, field coverage,
constraints, determinism, Apply Best, and solver QA; feed balance/connection;
i18n/help manifest; real `nec2c` 2 m/6 m; report and BOM content.

**Evidence:** B for the published 2 m/6 m starting dimensions; C for the
coax/choke equivalent and for scaled frequencies. The published VSWR curves are
a qualitative band check, not an R+jX reference. No gain or 50 Ω claim.

**Risk / mitigation:** high. The main risk is model fidelity, not UI work. The
spike, explicit evidence level, ideal-choke limitation, and physical cut list
mitigate it. Keep the deferred variants out of the catalog until their
primitives exist. Avoid scope creep into a coax solver or a sleeve model in this
item.

**Effort:** L (about 3–4 weeks including the spike, family, schema, UI, scene,
reports, estimator, optimizer, and tests). **Release:** unassigned; candidate
after the current 1.2 track. The spike alone is 2–4 days.

## UX45 — Shared Qt worker lifecycle

**Status:** **done 2026-11-25.** Implemented through
[ADR-0053](ADR/0053-qt-worker-task-lifecycle.md). **Priority:** maintenance and
reliability, not release-blocking. **Trigger:** the 2026-11-24 QA pass fixed a
stale-result and debounce race inside `LiveTuningDialog`; the same lifecycle
logic existed in other dialogs, so a future fix would not propagate. See
[`archive/qa/QA_PASS_2026-11-24.md`](archive/qa/QA_PASS_2026-11-24.md).

**Delivered:** `ui/workers/task_runner.py` owns one `QThread` and one worker at
a time, queues every worker signal to the GUI thread, carries a generation for
stale-result rejection, emits terminal signals after the thread stops, cancels
cooperatively, closes with a bounded wait, and detaches a stuck worker with a
guard that keeps it alive until it finishes. `run_worker_blocking()` preserves
the modal project-I/O and end-fed behavior on the same controller. All 14 sites
were migrated; `QThread(` and `moveToThread(` are now forbidden outside the
controller by an architecture test. No schema, solver, domain, or
project-format change.

**Follow-ups:** none required. The detach path deliberately lets a stuck solver
outlive its dialog; a future process-exit policy can wait for detached tasks if
the solver ever needs a hard shutdown guarantee.

The migration followed the recommendations below, which are retained as the
record of the original plan; the migration order was convergence, sweep and
tuning dialogs, optimizer dialogs, live tuning, main-window workers, and the
modal project-I/O/end-fed adapters.

**Goal:** replace the copied `QThread`/worker setup with one small, testable
controller that owns thread creation, cancellation, completion, error handling,
cleanup, and close-while-running behavior. Keep the UI responsive and preserve
the current dialog behavior.

**Current duplication:** there are 14 `QThread` construction sites. Ten dialogs
(`convergence`, `element_optimization`, `endfed`, `family_optimization`,
`live_tuning`, `optimization`, `parameter_sweep`, `robustness`, `synthesis`,
`tuning_assistant`), three sites in `ui/main_window.py`, and one in
`ui/project_io.py`. They fall into two styles:

1. **Asynchronous signal/slot workers** used by most dialogs and the main
   window.
2. **Modal `QEventLoop` wrappers** in `endfed_dialog.py` and `project_io.py`
   that block the caller until the worker finishes.

The variants are not cosmetic:

- some call `thread.wait(5_000)`, one calls `thread.wait(100)`, and the modal
  wrappers call `thread.wait()` without a timeout;
- some delete the worker through `thread.finished`, others through a
  `_cleanup`/`_thread_finished` method;
- some keep `self._thread`/`self._worker`, others use local variables;
- double-start protection, cancellation text, progress, and close behavior
  differ per dialog.

**Recommendations:**

1. Write a short ADR for the Qt lifecycle contract before the first migration.
   It should define ownership, cancellation, timeout, deletion, close, and
   error semantics. This is a cross-cutting UI contract, not a drive-by
   refactor.
2. Add one controller in `ui/workers/` (working name `TaskRunner` or
   `WorkerLifecycle`) with a small API:
   - `start(worker, cancel_token=...)`;
   - `is_running`, `cancel()`, `close(timeout_ms=...)`;
   - normalized `started`, `succeeded`, `failed`, `cancelled` signals;
   - one active task at a time, or an explicit rejection with a reason.
   The controller owns the `QThread`, the worker, and the single cleanup path.
3. Delete the worker in its own thread and stop the thread through the same
   path on success, failure, cancellation, timeout, and close. Do not call an
   unbounded `wait()` on the GUI thread. If a bounded wait expires, keep the
   dialog alive and surface a clear close/cancel message instead of destroying
   a running worker.
4. Prevent double starts centrally and let the controller reject a stale
   result by generation/request id. `LiveTuningDialog` already has the
   generation behavior; move it into the shared contract rather than keeping a
   second copy.
5. Keep a thin blocking adapter for `project_io` and the end-fed convergence
   check only if the caller must remain modal. Build it on the same controller;
   do not maintain a parallel `QEventLoop` lifecycle.
6. Add an architecture guard that forbids direct `QThread(`,
   `moveToThread(`, and ad-hoc worker deletion outside the controller, with a
   shrinking allowlist during the migration.
7. Migrate one site per change set, easiest first: `convergence`; then
   `parameter_sweep`/`robustness`/`tuning_assistant`; then the optimizer
   dialogs; then `live_tuning`; then the three main-window workers; finally the
   modal `project_io`/end-fed wrappers. Do not mix this with a feature slice.
8. Keep the existing worker classes; the controller coordinates lifecycle
   only. Do not change solver, progress semantics, or user-visible text.

**Scope (MVP):**

- The shared controller and its tests.
- Migration of every `QThread` site listed above.
- Cancellation, failure, timeout, close-while-running, and double-start
  coverage for each migrated site.
- A successful normal close, a close during work, and a cancellation that
  leaves the window usable.
- Project I/O and end-fed modal behavior preserved, including exceptions and
  progress dialogs.

**Out of scope:**

- A general thread pool, async/await framework, or parallel task scheduler.
- Rewriting worker classes or moving electromagnetic logic.
- Changing dialog layouts, progress wording, or result presentation.
- GPU/solver execution changes.

**Dependencies:** lifecycle ADR (recommended before code); no schema, solver,
or domain dependency. Schedule after the current 1.2 form/schema/UI work or
before a release only if a lifecycle defect appears.

**Acceptance:**

- One shared lifecycle implementation; the migrated call sites no longer
  contain their own thread create/move/cleanup sequences.
- Starting, completing, failing, cancelling, and closing during work are
  deterministic and covered for every migrated site.
- A second start while a task runs is rejected or ignored with a visible
  reason; no worker overlap.
- A stale result cannot overwrite a newer result after cancellation or a
  target change.
- No unbounded GUI-thread wait remains; close-time waits are bounded and
  documented.
- Project open/save/import progress remains modal where it is today and
  returns the same results and errors.
- The architecture guard and the full `ruff`, both `mypy` passes, and
  `pytest` gate are green.
- No schema, solver, domain, or project-format change.

**Tests:** controller unit tests with fake workers (success, failure,
cancellation, timeout, double start, close, generation); UI tests per migrated
dialog for cancel/close/double-start; project I/O tests for the modal adapter;
an offscreen teardown stress test that creates and closes dialogs repeatedly;
the existing full gate and real `nec2c` integration where the site runs the
solver.

**Evidence:** n/a; reliability and maintainability. There is no numerical
reference or performance claim.

**Risk / mitigation:** high. Qt object ownership and teardown are sensitive;
a shared controller can introduce crashes that the current per-dialog code
hides. Mitigate with a short ADR, one-site-per-change-set migration, fake-worker
tests, bounded waits, a temporary dual-path parity check, and manual desktop QA
for close/cancel on light/dark and scaled fonts.

**Effort:** M–L (2–4 weeks including migrations and tests). **Release:**
unassigned; maintenance track.

**Likely files:** a new `ui/workers/task_runner.py` (or similarly named
controller), `ui/dialogs/convergence_dialog.py`,
`ui/dialogs/element_optimization_dialog.py`,
`ui/dialogs/endfed_dialog.py`, `ui/dialogs/family_optimization_dialog.py`,
`ui/dialogs/live_tuning_dialog.py`, `ui/dialogs/optimization_dialog.py`,
`ui/dialogs/parameter_sweep_dialog.py`, `ui/dialogs/robustness_dialog.py`,
`ui/dialogs/synthesis_dialog.py`, `ui/dialogs/tuning_assistant_dialog.py`,
`ui/main_window.py`, `ui/project_io.py`, `tests/unit/ui/`, `tests/ui/`, and an
architecture-boundary guard test.

## 3D pattern orientation and comparison (implemented 2026-11-26)

**Status:** implemented presentation-only track. UX46, UX47, UX48, and UX49
landed in the order **UX46 → UX48 → UX49**, with UX47 as an independent
orientation aid. The full gate is green. **Release:** unassigned; candidate for
the 1.2 visualization track.

**Motivation:** The 3D lobe answers "how strong" but not "where relative to the
antenna". The 2D azimuth polar already draws an antenna line; the 3D view has
only axes, an optional ground ring, and a maximum-gain marker. The user needs a
clear visual front/back and lobe takeoff direction without a numerical-precision
claim. The geometry 3D view and the pattern 3D view already share a right-handed,
Z-up frame and the same orthographic projection; their default camera angles
differed (42°/24° vs 38°/26°), and UX49 unified them at 38°/26°. This track
makes that relationship legible.

**Track non-goals:** no solver, domain-model, schema, container, or pattern
storage change; no new numerical reference; no perspective projection or height
exaggeration in 3D; no inferred front/back from wire count or wire IDs; no
zoom/pan synchronization; no synthetic family shape that replaces the canonical
wires; and no new 3D engine or dependency (OpenGL, Qt3D, VTK, PyVista). Keep the
QPainter renderer and the orthographic projection, as recorded in
[ADR-0012](ADR/0012-geometry-presentation.md). The construction sketch, reports,
and wire schedule keep their current contracts.

**Shared frame and projection:** `GeometryView._project_3d()` in
`ui/widgets/geometry_view.py` and the projection in
`ui/widgets/radiation_pattern_3d_view.py` are identical today; the static report
has a third copy in `reporting/pattern_lobe.py`. UX46 must introduce one pure
shared helper (for example `ui/geometry/orbit_projection.py`) and use it from both
interactive views. If adopting it in the report would change output, keep the
report copy and add an equality test instead. The helper must be Qt-free and
covered by a direction test, not only by pixel smoke tests.

**Evidence:** n/a; presentation-only. There is no new numerical reference or
performance claim. Angular identity is tested against the shared projection,
not against an external reference.

**Risk / mitigation:** low-to-moderate. The main risks are visual clutter, a
false sense of scale or height, overclaiming front/back on omnidirectional
antennas, and camera-link drift. Mitigate with opt-in defaults, explicit
"not to scale" copy, an explicit family registry, reset propagation, projection
equality tests, and minimum-size/theme QA. There is no solver or numerical risk.

**Effort:** UX46 S (about 1–2 days), UX47 S (1–2 days), UX48 M (3–5 days), and
UX49 S (1–2 days), including tests, help, and docs. No external dependency.

**Likely files:** `ui/widgets/radiation_pattern_3d_view.py`,
`ui/widgets/results_view.py`, `ui/widgets/geometry_view.py`, `ui/main_window.py`,
`ui/i18n.py`, `ui/theme.py`, `ui/help.py`, a new Qt-free
`ui/geometry/orbit_projection.py` plus an overlay/footprint helper,
`tests/ui/test_results_view.py`, `tests/ui/test_geometry_view.py`, focused new
UI/projection tests, and the docs listed under the cross-cutting acceptance.

### UX46 — 3D lobe orientation indicators (layer 1)

**Implemented 2026-11-26.** The presentation-only slice adds the shared
projection helper, explicit forward-axis registry, antenna azimuth/vertical
markers, maximum-gain ray, same-elevation back ray with F/B, azimuth reference
ring, compact-label behavior, shared antenna/feed visual tokens, and EN/ES help
and accessibility text. No solver, domain, schema, or report change.

**Scope:** presentation only; `RadiationPattern3DView` and the data that
`ResultsView` already has. No antenna-wire overlay yet. The live-tuning dialog
uses `PolarPatternView`, not this widget, and is out of scope.

- **Projection helper.** Extract `project_world(x, y, z, yaw_deg, pitch_deg)`
  returning the orthographic screen-plane coordinates. Use the same yaw/pitch
  convention, pitch clamp, and screen-Y inversion in both views. Test that a
  set of world vectors projects to the same screen-space direction in the
  geometry and pattern views.
- **Azimuth reference.** Draw a faint horizontal reference ring at pattern
  `z = 0` in both ground and free-space modes. Label it "Ground" when the design
  uses ground and "Azimuth reference" in free space. Add small `φ=0°`, `90°`,
  `180°`, `270°` labels around the ring; hide them at minimum sizes.
- **Antenna azimuth.** Extract `azimuth_deg` and the vertical-orientation flag
  from the design parameters in `ResultsView`, using the same rules as
  `_render_azimuth_cut()`; pass them to the 3D view rather than reading the 2D
  widget. Draw a line or arrow on the horizontal plane at the antenna azimuth.
  For a vertical dipole/vertical orientation, draw a distinct dot/vertical
  marker at the origin instead. For a vertical-polarized beam, keep the azimuth
  line because the boom still defines the front/back axis. Do not label
  "Front/Back" for a dipole, loop, vertical, or custom geometry without an
  explicit forward axis.
- **Explicit forward-axis registry.** Add a presentation helper that returns the
  forward azimuth only for families whose parameters define it. Start with
  Yagi, Moxon, quad beam, hexbeam, log-periodic, and stacked Yagi; add trap Yagi
  only if its typed parameters expose the same convention. Do not hard-code
  wire IDs or infer the family from wire count. All other families return
  `None`.
- **Maximum-gain ray.** Draw a ray from the pattern origin to the existing
  maximum-gain marker, with an arrowhead and a label containing the selected
  metric, gain, and takeoff angle. Add the azimuth when space allows. Reuse and
  extend the existing max-label collision logic.
- **Back ray and F/B.** Draw a dashed ray at the same θ and `φ + 180°`, matching
  `front_to_back_db()` in `domain/simulation/pattern.py`. Label it "Back (same
  elevation)" or the localized equivalent and show the front-to-back value when
  finite. Compute the value once in `ResultsView` from the original
  `FrequencyResult.far_field` and pass it to the view; do not recompute it from
  the decimated or display-filtered mesh. Label it as power-gain F/B. The
  constant power/directivity/realized metric offset cancels, so F/B stays the
  same. Do **not** draw the exact
  antipodal direction and call it "Back": in ground mode the exact antipodal of
  a low-angle lobe falls below the ground plane and is not sampled. If an exact
  antipodal reference is added later, label it "Opposite direction", not
  "Back". **Superseded for back-ray length by UX57 (implemented 2026-11-26):** the
  direction and F/B data path stay; the marker now uses the actual rear gain.
- **Visual identity.** Add one theme-aware antenna color role and one feed-marker
  painter used by both `GeometryView`'s 3D view and `RadiationPattern3DView`.
  The feed marker must have the same color, shape, and radius in both. Do not
  use the green/yellow/red gain ramp for the antenna. UX46 introduces the shared
  painter/token; the pattern view uses it only when UX47/UX48 actually draws the
  feed. Do not draw a feed marker at the pattern origin without the antenna
  overlay or mini-map: the pattern origin is a phase reference, not the feed.
- **Labels and accessibility.** Keep labels inside the safe area and avoid the
  gain legend and max label. At compact sizes, hide secondary labels and keep a
  compact legend. Add EN/ES strings, help entries, the help coverage manifest,
  and an accessible description for the 3D view.

**Acceptance:** with a result, the view shows the maximum-gain direction, the
same-elevation back direction with its F/B value, and the antenna azimuth when
available; a Yagi at azimuth 0 draws its antenna axis along +X and a Yagi at 90°
along +Y; a dipole/loop/vertical gets no front/back claim; the F/B value equals
`front_to_back_db()` for the selected pattern data; the feed marker is visually
identical to the geometry 3D view; labels do not overlap at the minimum size;
light/dark, font scaling, EN/ES, and help tests pass. No solver, domain, schema,
or report change.

### UX47 — Plan mini-map in the 3D lobe

**Implemented 2026-11-26.** The 3D pattern view now receives the canonical
wire footprint and feed point from `ResultsView`, draws a theme-aware top-view
inset, and overlays the shared feed marker plus antenna and maximum-gain azimuth
arrows. The inset is hidden below the compact threshold and when it would
overlap the max-gain label.

**Scope:** an optional top-down reference inset inside the 3D lobe. This is a
parallel orientation aid after UX46, not layer 2; it may land before or after
UX48.

- Draw the canonical wire footprint in the X-Y plane, using the same top-view
  orientation as the geometry plan (X right, Y up). No synthetic family shape.
- Add the shared feed marker, the antenna azimuth arrow, and the maximum-gain
  azimuth arrow. The maximum-gain arrow uses the same φ as the 3D ray; the
  antenna arrow uses the same azimuth as UX46.
- Place the inset in a reserved corner and hide or shrink it automatically when
  it would overlap the max label or the gain legend. Keep it legible at the
  minimum supported size.
- Add a "Show plan" checkbox in the 3D lobe tab, default on. Persisting the
  choice is optional and, if added, belongs in `UiPreferences`, not the project
  schema.
- Use the same antenna color/feed marker as UX46. Theme-aware, EN/ES help, and
  accessible description are required.

**Acceptance:** the inset footprint matches the canonical model's top view for a
Yagi, a dipole, a vertical, and a custom model; the max-gain arrow uses the same
azimuth as the 3D ray; the inset hides or shrinks without covering the lobe at
the minimum size; no synthetic family shape; no new dependency or engine.

### UX48 — Schematic antenna overlay in the 3D lobe (layer 2)

**Implemented 2026-11-26.** The 3D lobe tab now has a default-off **Show
antenna** checkbox and an **Auto / Full / Outline** selector. The overlay uses
the canonical wire snapshot, feed-centers it, applies one uniform scale,
preserves support wires (thinner/dashed), and draws the shared feed marker.
Outline mode is a convex-hull projection of the canonical endpoints. The PNG
export uses the existing `grab()` path and respects the overlay state.
**Superseded for explicit-forward-axis families by UX56 (implemented
2026-11-26):** those families center on the beam symmetry plane; the
feed-centered rule remains the default for non-beam families.

**Scope:** opt-in canonical wireframe inside the 3D lobe.

- Add a "Show antenna" checkbox inside the 3D lobe tab, default off. Do not add a
  project-schema field. Pass the canonical `AntennaModel` (or a small immutable
  presentation snapshot) from `ResultsView.set_design()` to
  `RadiationPattern3DView`; keep `set_points()` as the pattern-data path.
  Showing or hiding the overlay must not trigger a solver run or a new worker;
  it reads the existing design/result snapshot.
- Draw the canonical wires on top of the lobe wireframe with the shared antenna
  color. This is a schematic overlay for legibility, not a depth-sorted scene;
  do not claim occlusion or physical placement. Draw the shared feed marker. Do
  not draw transmission lines as wires. Loads are optional; if drawn, use the
  existing load marker language.
- Translate the wires so the feed is at the pattern origin and apply one uniform
  scale so the largest wire extent occupies about 35 % of the pattern unit
  radius. No non-uniform scale, no height exaggeration, no perspective. Show a
  visible note: "Schematic: orientation exact; size and height are not to
  scale."
- The NEC adapter applies `ground_clearance_offset_m()` (currently 1 cm) to the
  solver geometry. Feed-centering cancels that translation; if a future mode
  uses a world-origin overlay, apply the same offset and document it. Do not mix
  model-space and solver-space z frames.
- Front/back arrows use only the UX46 explicit registry. Do not add front/back
  labels to dipoles, loops, verticals, or custom geometry without a declared
  forward axis.
- Support wires (mast/guy wires) are canonical and must not be silently dropped.
  Full mode draws them; if they dominate, draw them thinner or dashed and say so
  in the legend. Outline mode must state that it is a simplified view and keep
  Full mode available.
- **Outline mode for large arrays.** Add an "Auto / Full / Outline" selector, or
  an "Outline" checkbox with Auto as the default. Auto uses a documented
  wire/segment display budget (a named display constant plus help text), not
  family inference. Outline is a derived
  projection of the canonical endpoints (convex hull or equivalent) plus the
  feed and forward axis; it is not a synthetic family shape and is never used in
  the construction sketch, reports, or wire schedule. Full mode preserves every
  canonical wire; no silent dropping.
- The 3D-lobe PNG export uses `grab()`, so it must respect the checkbox and
  mode. Add a test. No report-format change.

**Acceptance:** a Yagi at azimuth 0 is feed-centered with the boom along +X and
the front arrow toward +X; a dipole shows no front/back claim and its max ray is
perpendicular to the wire; a vertical extends upward with no front/back claim; a
custom model draws its real wires without synthesis; uniform-scale tests
preserve endpoint distance ratios; outline tests derive the envelope from
canonical endpoints; Full mode draws every canonical wire; transmission lines
are absent; support-wire policy is documented and tested; no overlay is drawn
without a design/result; theme, font scaling, minimum size, EN/ES, help, and
accessibility pass. No solver, domain, schema, or report change; no new engine.

### UX49 — Linked geometry/pattern 3D cameras (layer 3)

**Implemented 2026-11-26.** The geometry controls row now has a default-off
**Link 3D** checkbox. Link-on adopts the geometry camera, syncs yaw and
pitch only, and leaves zoom and pan independent. Dragging or double-clicking
either view propagates the camera; a design change resets both cameras and
keeps the geometry view in 3D while linked. Selecting Construction turns the
link off with a status explanation. Both interactive views share the same
precomputed orthographic projection, with an exactness test over +X, +Y, +Z,
and a beam-forward vector. The construction-sheet isometric export uses a fixed
38°/26° camera so the sheet stays reproducible; the live view is unchanged.

**Scope:** opt-in camera synchronization between the geometry 3D view and the
3D lobe.

- Add a "Link 3D" checkable action in the geometry controls row (or a
  shared link control visible to both panels), default off. Persist only as a UI
  preference if desired; no project-schema field.
- Use a single shared camera source of truth (yaw, pitch) or bidirectional
  signals with a guard flag. Sync **yaw and pitch only**; do not sync zoom or
  pan. Keep the existing independent zoom ranges.
- Unify the default angles. Prefer 38°/26° to match the pattern view and the
  report, and update the geometry reset test. If another default is chosen,
  document it and update both views.
- Propagate resets: a double-click in either view resets both when linked;
  `GeometryView.set_model()` resets both when linked. Define the design-change
  reset policy explicitly so the link cannot drift.
- On enabling the link, choose a predictable handoff (for example, the geometry
  camera wins, or the last active view wins) and show the resulting state. Do
  not let the view jump without explanation.
- If the geometry view is in Construction mode, either switch it to 3D with a
  visible state change or disable the link with an explanation. Do not silently
  ignore the request.
- Avoid feedback loops and stale signals. Test a bidirectional drag, reset,
  design change, frequency change, and link off/on sequence.
- Exactness test: with the same yaw/pitch and orthographic projection, a set of
  world vectors projects to the same screen-space direction in both views within
  `1e-9`; include +X, +Y, +Z, and a known beam forward vector.
- **Export decision (resolved).** The construction sheet uses a fixed 38°/26°
  camera for the isometric image and SVG, so the link and the live view cannot
  change exported output. A regression test compares the export with a
  non-default live camera against the fixed-camera export.

**Acceptance:** rotating either linked view updates the other's yaw/pitch
exactly; unlinked views stay independent; reset/model-change propagation keeps
the link synchronized; zoom and pan stay independent; Construction mode is
handled explicitly; exact projection tests pass; EN/ES help, accessible state,
light/dark, font scaling, and docs pass. No solver, domain, schema, or report
change; no new engine.

### Track order and dependencies

1. **UX46 first.** It establishes the shared projection helper, the explicit
   forward-axis registry, the azimuth/F-B data flow, and the shared visual
   tokens. Do not start UX48 or UX49 before UX46 is green.
2. **UX48 after UX46 (layer 2).** It introduces the overlay, the outline mode,
   and the feed-centered schematic scale. UX47 may share drawing helpers, but it
   is not a prerequisite.
3. **UX49 after UX48 (layer 3).** It reuses the overlay's forward-axis helper
   when present; the link must still work with the overlay hidden.
4. **UX47 after UX46, in parallel with UX48/UX49.** It reuses the UX46
   azimuth/max-gain data and visual tokens; it must not block either later
   layer.
5. **UX56–UX57 after UX46, with UX56 also after UX48.** They are implemented
   corrections to the overlay centering and back-ray radius; see §3D lobe
   presentation corrections. They do not change the pattern data or the 3D
   scale. UX56 and UX57 are independent and may land in either order.

If the shared projection helper cannot be extracted without changing output,
keep the existing copies and add a direct equality test before UX48. Do not
"prepare" a later layer by changing the renderer or adding a dependency early.
Each item must leave the full gate green.

### Cross-cutting acceptance for the track

- Update `docs/ARCHITECTURE.md` and `docs/USER_GUIDE.md` with the 3D lobe
  options and the "schematic, not to scale" limitation.
- Add a note to `docs/GEOMETRY_PRESENTATION.md` only if the overlay needs a
  clarification: the pattern overlay is not the construction sketch and does not
  relax canonical-wire preservation. Never use the overlay to replace or hide a
  canonical wire in the sketch, reports, or schedule.
- Every new checkbox, selector, legend, and label has EN/ES strings, help
  entries, the help coverage manifest, and an accessible description through
  `ui/help.py`.
- Theme-aware colors, light/dark, font scaling, and minimum-size layout tests.
- No `pickle`, no new dependency, no schema migration, no solver/domain change.
- Add a short ADR only if the shared camera/overlay helper becomes a
  cross-layer abstraction; otherwise record the decision in
  `docs/ARCHITECTURE.md`.
- Add the user-visible behavior to `CHANGELOG.md` when the slice lands.

## 3D lobe presentation corrections (proposed 2026-11-26)

**Status:** proposed; not started. **Priority:** P2 presentation correctness.
**Release:** unassigned; candidate after the current 1.2 presentation track.
**Dependencies:** UX46 and UX48 (implemented 2026-11-26). UX56 and UX57 are
independent and may land in either order.

**Motivation:** Two orientation aids in the 3D lobe are correct in direction but
misleading in magnitude:

1. The UX48 overlay is translated so the feed is at the pattern origin. A
   side-fed beam such as the quad beam has its feed on one side of the driven
   loop, not on the beam symmetry plane. The overlay's symmetry axis therefore
   appears offset from the lobe axis even though the antenna orientation is
   exact. In a 20 m quad beam regression case at 14.086 MHz, the feed is at
   (5.424, −2.798, 8.113) m, the driven-loop center/symmetry plane is y=0, and
   the overlay scale is 0.0391 m^-1: the symmetry plane lands at +0.109 of the
   pattern unit radius (about 11%) and the boom center at −0.043 of the radius.
   In the plan view the loops sit above the lobe axis while the maximum-gain
   ray starts at the feed.
2. The UX46 back ray uses the same θ and φ+180° as the F/B label but reuses the
   forward maximum gain for its radius. The label says F/B 5.9 dB; the ray
   reaches the forward peak radius, about 14% beyond the actual rear envelope,
   and its label sits at that outer point. The ray visually claims a back lobe
   as strong as the front even though the numeric F/B is correct.

Both are presentation-only. The pattern data, the F/B value, the pattern origin
as a phase reference, and the 3D radial/color scale are correct and stay
unchanged. Do not fold in the 44 dB scale discussion or the plan-envelope
behavior from UX46; they are out of scope.

### UX56 — Center the 3D antenna overlay on the beam symmetry plane

**Implemented 2026-11-26.** `AntennaOverlay` carries a presentation-only
`center` (default: the feed) and `overlay_from_model(..., forward_azimuth=...)`
projects the feed onto the bounding-box symmetry plane of the non-support
wires. `ResultsView.set_design()` supplies the declared forward axis; the view
translates wires by `center`, scales from `center`, and draws the shared feed
marker at its real `(feed - center) * scale` offset. The note and help text
describe the family-aware centering. Pure tests cover azimuth 0/90, the real
cross-boom offset, the 35% extent, a center-fed Yagi, and the non-beam default.

**Goal:** make the schematic overlay's symmetry axis coincide with the lobe
axis in the azimuth/plan projection for families with an explicit forward axis,
while keeping the feed marker at its real transverse position. This corrects
the quad/delta/side-fed-loop case without changing Yagi, vertical, dipole, or
custom placement.

**Current behavior:** `overlay_from_model()` returns a feed-centered snapshot
(`ui/pattern_overlay.py`); `overlay_scale()` measures the largest wire extent
from the feed; `_draw_overlay()` subtracts `overlay.feed` from every point and
draws the feed marker at the pattern origin. The UX48 note says the overlay is
schematic and not to scale, but the symmetry offset is still visible and is
easy to read as a placement error.

**Proposed behavior:** for a family with a declared forward axis, translate the
wires so the **feed projected onto the beam symmetry plane** is at the pattern
origin. The feed itself is drawn at its real cross-boom offset. For all other
families, keep the current feed-centered behavior.

- Let `p` be the forward azimuth in radians and `v = (−sin p, cos p)` the
  horizontal cross-boom direction.
- Let `c` be the bounding-box center of the non-support overlay wires in the
  x-y plane. It defines the symmetry plane; it is a presentation proxy, not a
  phase-center calculation. If there are no non-support wires, use the feed.
- The feed's cross-boom offset is
  `d = (feed_x − c_x)·v_x + (feed_y − c_y)·v_y`.
- `center = (feed_x − d·v_x, feed_y − d·v_y, feed_z)`. Keep the feed's z so the
  overlay's vertical position does not jump.
- For the 20 m quad beam at φ=0: `v=(0, 1)`, `c_y=0`, `d=−2.798`,
  `center=(5.424, 0, 8.113)`, the driven-loop center. The feed marker moves
  down by `2.798 · scale`.
- For a center-fed Yagi at φ=0: the feed is already on the symmetry plane, so
  `d=0` and `center=feed`; the visual result is unchanged. A Yagi fed off-center
  along the element gets the driven-element centerline, which is the intended
  correction.
- For a beam at φ=90: `v=(−1, 0)`; the symmetry plane is x=c_x and the feed's x
  offset is removed. Test the rotated case, not only φ=0.
- For a vertical, dipole, loop without a declared forward axis, or custom model:
  `forward_azimuth` is `None`, so `center=feed` and the behavior is unchanged.
- Do not infer the family from wire IDs or wire counts in the widget. Use the
  existing `forward_axis_azimuth()` registry in `ui/pattern_orientation.py` and
  pass its result from `ResultsView` to `overlay_from_model()`. The widget only
  consumes the snapshot's `center`.
- Add `forward_azimuth: float | None = None` as a keyword-only parameter to
  `overlay_from_model()`; the default preserves the current feed-centered
  behavior for existing callers and tests.
- Add `center` to `AntennaOverlay`. Preserve the two-argument construction used
  by tests and helpers by defaulting `center` to `feed` (for example,
  `center: tuple[float, float, float] | None = None` plus a frozen-dataclass
  `__post_init__`, or update every constructor). Prefer the default so
  non-beam callers do not change.
- `overlay_scale()` measures from `center`, not `feed`, and still puts the
  largest wire endpoint at 35% of the pattern unit radius. For the quad, the
  scale rises from 0.0391 to 0.0476 m^-1 because the center is closer to the
  far reflector corner; the overlay becomes about 22% larger. This is expected;
  the 35% bound is unchanged.
- Keep the current scale policy that includes support wires in the maximum
  extent; a mast/guy set still fits. Do not add a support-wire exclusion in this
  item.
- `_draw_overlay()` translates by `center`, not `feed`, and draws the feed
  marker at `(feed − center)·scale`. The maximum-gain and back rays continue to
  start at the pattern origin; the translation puts the beam symmetry plane
  through that origin, which is a better visual phase-reference proxy. Do not
  move the pattern origin or the phase reference.
- Do not add a "Center on feed / antenna" toggle in this slice. The
  family-aware default is the intended behavior; a toggle can be a later item
  if feedback requires both views.
- Update the overlay note/help text from "feed-centered" to "centered on the
  beam symmetry plane for families with a forward axis; feed-centered
  otherwise; the feed marker stays at its real offset". Keep the "schematic;
  orientation exact; size and height not to scale" limitation.

**Acceptance:**

- A quad beam with a side-fed driven loop at azimuth 0 has its symmetry plane
  on the pattern axis in plan view; the feed marker is below the axis by the
  true cross-boom offset; the max ray starts on the symmetry plane; the overlay
  stays within 35% of the pattern radius.
- A center-fed Yagi at azimuth 0 and 90 is visually unchanged (`center=feed`).
  A Yagi with an off-center feed moves to the driven-element centerline, not to
  the feed.
- A vertical, a center-fed dipole, a loop without a declared forward axis, and
  a custom model remain feed-centered.
- The overlay scale still puts the largest endpoint at 35% of the unit radius;
  endpoint distance ratios are preserved (uniform scale).
- The feed marker remains the shared UX46 painter and is drawn at its real
  offset; it is not forced to the origin for side-fed beams.
- No change to the solver, domain model, schema, report, pattern data, 3D dB
  scale, back ray (UX57), or mini-map.
- EN/ES help, help coverage, accessible description, light/dark, font scaling,
  minimum-size layout, and PNG export pass.

**Tests:**

- `tests/ui/test_pattern_overlay.py`: construct a quad beam with a side-fed
  driven loop; call `overlay_from_model(model, forward_azimuth=0.0)`; assert
  `center` is on y=0 at the driven-loop x/z; assert `feed − center` is the
  expected cross-boom offset; assert the maximum endpoint distance from
  `center` is `OVERLAY_EXTENT_FRACTION`.
- Repeat at `forward_azimuth=90.0` and assert `(center − c)·v ≈ 0`.
- Assert a center-fed Yagi has `center == feed` and a vertical/dipole with
  `forward_azimuth=None` has `center == feed`.
- `tests/ui/test_pattern_3d_orientation.py` or `test_results_view.py`: pass the
  quad overlay through `ResultsView.set_design()`/`set_points()` with a
  synthetic pattern, show the view, and assert the grab is non-null and the
  overlay note/help mentions the symmetry-plane centering. Do not assert pixel
  positions; assert the snapshot's `center` and the pure scale/offset helpers.

**Docs/help:** `docs/USER_GUIDE.md` (overlay paragraph), `docs/STATUS.md`
(UX48 line), `CHANGELOG.md`, `ui/i18n.py` (`help.pattern.overlay_show` EN/ES).
Update the UX48 section with a "superseded for explicit-forward-axis families
by UX56" note. No new help key or schema field. Add a note to
`docs/AUTONOMOUS_BACKLOG.md` UX48 acceptance so a future reader knows the
feed-centered rule is only the non-beam default.

**Likely files:** `ui/pattern_overlay.py`, `ui/widgets/results_view.py`,
`ui/widgets/radiation_pattern_3d_view.py`, `ui/i18n.py`,
`tests/ui/test_pattern_overlay.py`, `tests/ui/test_pattern_3d_orientation.py`,
`tests/ui/test_results_view.py`, and the docs above.

**Out of scope:** the 3D dB/color scale, the plan-envelope interpretation, the
back ray (UX57), the mini-map, the phase reference, any solver/domain/schema
change, any family inference from wire IDs, and any new dependency.

**Risks:** low. The main risk is a visible size/position change for side-fed
beams; mitigate with the help text, the real feed marker, and unchanged
non-beam behavior. There is no numerical risk.

**Effort:** S–M (1–2 days), including tests, help, and docs.

### UX57 — Draw the 3D back ray at the actual rear gain

**Implemented 2026-11-26.** `back_gain_db()` returns `forward - max(F/B, 0)`,
or `None` for a missing/non-finite F/B. `_shows_back_ray()` requires a declared
forward axis and a finite F/B. The paint path uses the rear gain and hides the
ray/label when the projected marker is below the minimum-distance guard. Pure
tests cover finite, zero, missing, non-finite, and anomalous negative F/B, plus
the normalized radius ratio.

**Goal:** make the dashed back ray's length encode the same F/B that its label
reports. The direction is already correct (same θ, φ+180°); only the radius is
wrong.

**Current behavior:** `RadiationPattern3DView.paintEvent()` builds
`back_marker = screen(max_point[0], (max_point[1] + 180) % 360, max_point[2])`.
`max_point[2]` is the forward maximum gain, so the ray reaches the forward peak
radius regardless of the rear gain. The label uses `_back_label()` and correctly
shows `front_to_back_db()`; the numeric value comes from `ResultsView` and is
computed from the original far field at the same θ.

**Proposed behavior:** use the rear gain for the marker radius:

- If `self._front_to_back_db` is finite, `back_gain = max_point[2] −
  self._front_to_back_db`. Draw the marker at `(max_point[0], (max_point[1] +
  180) % 360, back_gain)`.
- If F/B is `None` or non-finite, do not draw the back ray or its label. Do not
  fall back to the forward radius; a full-length ray without a valid F/B is the
  misleading case this item removes. `_shows_back_ray()` should require both the
  explicit forward axis and a finite F/B.
- The metric offset cancels: power, directivity, and realized gain share the
  same F/B and the same shape. Do not recompute F/B from the decimated or
  display-filtered mesh; use the value already passed from `ResultsView`.
- Keep the same θ and φ+180° rule; do not draw the exact antipodal direction
  (below the ground plane in ground mode). The label remains "Back (same
  elevation) · F/B x dB" (or the localized equivalent).
- Keep the existing minimum-distance/arrowhead guard. If the rear marker is too
  close to the origin to be legible (for example, projected distance < 8 px or
  < 3% of the maximum ray), hide the dashed ray and label rather than drawing a
  degenerate marker at the center. Add a named threshold/help note if this
  policy is user-visible.
- The back label moves inward with the marker; the existing `_place_label()`
  collision logic handles the max label, legend, mini-map, and compact sizes.
  If no free rectangle exists, hide the label as today.

**Acceptance:**

- For a pattern with F/B 6 dB, the dashed back ray ends at the rear gain, not
  the forward gain; the label still says F/B 6.0 dB. For the 20 m quad beam at
  14.086 MHz, the ray ends at about −1.4 dBi at θ=74°, not at 4.53 dBi.
- A 0 dB F/B pattern draws a full-length back ray (correct: front and back are
  equal). A negative F/B cannot occur when `max_point` is the global maximum;
  if it does due to a data anomaly, clamp/hide and document.
- An unavailable F/B hides the back ray and label; no full-length fallback.
- The back ray direction is still same θ, φ+180°; no below-ground antipodal
  point.
- The max ray, antenna azimuth marker, overlay, mini-map, legend, and the 3D
  dB scale are unchanged.
- Labels do not overlap at the minimum size; light/dark, font scaling, EN/ES,
  help, and accessible text pass.

**Tests:**

- Add a pure helper or method for the rear gain, e.g.
  `back_gain_db(forward_gain, front_to_back)` or `_back_gain(max_gain)`, and
  test finite, zero, and None cases.
- Test `_shows_back_ray()` is False when `forward_azimuth` is set but
  `front_to_back_db` is None/non-finite.
- Test the synthetic pattern: max 10 dBi, rear 4 dBi, F/B 6 dB; the marker
  radius ratio is `(4 − min)/(10 − min)`, not 1.0. Use a pure projection helper
  if the pixel path is hard to assert.
- Extend `tests/ui/test_pattern_3d_orientation.py` with a view that has a
  finite F/B and assert the back label metadata/geometry; add a compact-size
  grab test to catch label collisions.

**Docs/help:** `docs/USER_GUIDE.md` (the 3D paragraph at the back-ray sentence),
`CHANGELOG.md`, and `docs/STATUS.md` when implemented. The label text and help
key do not change. Add a "superseded by UX57" note to the UX46 back-ray bullet.

**Likely files:** `ui/widgets/radiation_pattern_3d_view.py`,
`tests/ui/test_pattern_3d_orientation.py`, `docs/USER_GUIDE.md`,
`CHANGELOG.md`, `docs/STATUS.md`.

**Out of scope:** the 3D dB/color scale, the plan-envelope interpretation, the
overlay centering (UX56), the F/B definition, the exact antipodal direction,
and any solver/domain/schema change.

**Risks:** low. The label moves inward and may collide at compact sizes; test
the existing collision logic. A very deep F/B produces a very short ray; hide
it below the legibility threshold. No numerical risk.

**Effort:** S (0.5–1 day), including tests and docs.

**Track order:** UX56 depends on UX46/UX48; UX57 depends on UX46. They are
independent and can land in either order. UX56 changes the UX48 overlay
centering rule for explicit-forward-axis families; UX57 changes the UX46
back-ray radius. Both are presentation-only and leave the solver, domain,
schema, reports, pattern data, and 3D scale unchanged. They may be implemented
in one change set if the combined diff stays small, but the acceptance and
tests above are separate.

**Cross-cutting acceptance:** run the full gate; update EN/ES help and the help
coverage manifest; record light/dark and font-scaling QA; add the user-visible
change to `CHANGELOG.md`; no commit or push unless requested.

## Antenna generator dialog layout standard (implemented 2026-11-26; closed)

**Status:** implemented and closed 2026-11-26 by UX50–UX55. **Release:**
unassigned; candidate for the UI quality pass. **Decision:** ADR-0056.
The manual desktop 125%/150% check passed, including the Large font preset.

**Motivation:** The Yagi generator is the only family dialog whose minimum
height exceeds a 1920×1080 screen. `YagiDialog` requests 920×720, but its
single-column form has 23 visible rows and a measured minimum height of
1087 px (form 965 px). Qt clamps the resize to that minimum, so the note block
and the OK/Cancel row fall below the screen. The element table is squeezed to
its 140 px minimum while the form consumes 719 px.

The rest of the family dialogs are not broken at 100% scaling today, but the
set is inconsistent: loaded dipole, biquad, Moxon, magnetic loop, Beverage, SCV,
J-pole, OCFD, fan dipole, Ringo, and inverted V/L have no scroll area; twelve
other generator dialogs already scroll through forms between 493 and 1697 px
tall. Dialog widths range from 560 to 940 px, and the notes/action area moves
between dialogs. The result is not one visual language, and the no-scroll group
has a latent clipping risk at large fonts or high display scaling.

**Measured baseline (2026-11-26, offscreen, default font):**

| Dialog | Visible form rows | Minimum height | Scroll |
|---|---:|---:|---|
| Yagi | 23 | 1087 px | No |
| Loaded dipole | 16 | 616 px | No |
| Biquad | 14 | 610 px | No |
| Moxon | 14 | 591 px | No |
| Magnetic loop | 14 | 584 px | No |
| Beverage | 13 | 579 px | No |
| SCV | 13 | 559 px | No |
| J-pole | 14 | 557 px | No |
| OCFD | 12 | 551 px | No |
| Fan dipole | 9 | 508 px | No |
| Ringo / inverted V / inverted L | 11 | 465–496 px | No |
| End-fed | 30 | 1328 px form | Yes |
| Stacked Yagi | 21 | 1697 px form | Yes |

These are a baseline, not a contract; UX50/UX51 must re-measure with the
actual theme and font presets.

**Track goal:** make the generator dialogs feel and behave like one system
without forcing every family into the same geometry. The common language is the
dialog scaffold, the semantic section order, the field styling and behavior,
and the guarantee that the action area is always reachable. Two columns are a
responsive tool for complex forms, not a brand requirement.

### Layout contract

1. **Dialog scaffold.** Every modal generator dialog uses the same structure:
   window title, optional short intro, a scrollable form area, the limitation
   or evidence notes, and the button box. The button box stays outside the
   scroll area and is always visible. Initial size comes from
   `scaled_dialog_size()` and is capped to the available screen.
2. **Semantic sections.** Fields are grouped in this order where present:
   design/frequency; geometry; installation/site (height, azimuth,
   polarization, material); ground and soil; feed and matching; mechanical
   support. A family may omit a section, but it must not reorder the sections it
   has. Section titles are user-visible strings with EN/ES help coverage.
3. **Responsive columns.** One column is the default. Use two columns only in a
   modal generator dialog when the form has at least 12 visible rows and at
   least 760 px of usable width. Sections are atomic: split whole sections, not
   individual rows. Keep the original top-to-bottom field order: left column
   first, right column second; set an explicit tab order if the widget creation
   order does not match. Do not reflow the form every time a conditional row
   hides.
4. **Height budget.** At Medium font and 100% scaling, a generator dialog's
   `minimumSizeHint().height()` must be at most 640 px; taller content must
   live inside the scroll area. Reference screens are 1366×768 at 100% and
   1920×1080 at 150% (1280×720 logical). At Large font, scrolling is
   acceptable, but the action area must remain outside the scroll and visible.
5. **Width budget.** Two-column generator dialogs target 920 px and must not
   exceed 1000 px without a documented preview/table reason. The content must
   not produce a horizontal scrollbar at the target width in English, Spanish,
   or the Large font preset.
6. **Tables and previews.** A table or preview keeps its own internal
   scrolling. Do not add a horizontal form scrollbar around it. At the default
   size on 1920×1080, the Yagi element table and the action area must be
   visible without scrolling.
7. **Sidebar is not a dialog.** The main-window form panel stays single-column
   at 340–520 px. The same field order and section names are reused, but the
   sidebar never adopts the two-column dialog layout. Do not change
   `_preferred_form_panel_width()` or the sidebar width contract for this track.
8. **No behavior change.** This is layout work only. Parameters, defaults,
   validation, warnings, solver specs, reports, and help keys remain unchanged.

**Track non-goals:** no solver, domain-model, schema, container, pattern, or
report change; no new antenna field or numerical reference; no new dependency;
no forced two-column layout in the sidebar; no redesign of analysis, optimizer,
measurement, construction, or catalog dialogs; and no replacement of canonical
family geometry.

**Task order and dependencies:** UX50 → UX51. UX52, UX53, and UX54 start after
UX51 and may run in parallel. UX55 starts with the compact-family audit after
UX51 and closes the track only after UX52–UX54. Each item must leave the full
gate green and is independently shippable.

### UX50 — Yagi generator two-column reference dialog

**Implemented 2026-11-26.** `YagiDialog` now uses a `YagiForm` wide layout with
two `QFormLayout` columns and a `QScrollArea`; the sidebar form keeps its
single-column path. The dialog opens at 920×860 (capped by
`scaled_dialog_size()`), the form scrolls at 920×640, and the hint, evidence,
boom note, and button box stay outside the scroll area. English and Spanish
fit at the default size without vertical or horizontal scrolling; the table
keeps its 140 px minimum and grows when space is available. No solver,
domain, schema, or report change.

**Goal:** fix the reported off-screen action area and establish the reference
wide-dialog implementation before extracting a general abstraction.

**Scope:**

- Keep `YagiForm`'s default single-column path unchanged for the sidebar. Add
  an explicit wide layout used only by `YagiDialog`; do not make two columns the
  default of the shared widget.
- Split the 24 form rows (23 visible at rest) at the natural midpoint,
  preserving the current top-to-bottom order and tab order:
  - **Left, antenna geometry and support:** frequency, height, azimuth,
    polarization, element radius, tapered tip length, tapered tip radius, mast
    diameter, mast offset, guy count, guy anchor radius, guy wire diameter.
  - **Right, material, site, ground, and feed:** material, ground, soil preset,
    relative permittivity, conductivity, driven element, folded driven, fold
    spacing, transformer ratio (only when folded), feed match, hairpin length,
    hairpin spacing.
- The conditional transformer row stays in its existing reading position and
  hides without reflowing the columns. The folded and match controls keep their
  current enable/disable behavior.
- Put the form in a `QScrollArea`; keep the hint, evidence, boom note, and
  button box outside it. Use an initial size around 920×860, capped by
  `scaled_dialog_size()`. At 1920×1080 the form, element table, notes, and
  actions are visible without scrolling; at 1366×768 or 150% scaling the
  form scrolls and the action area stays visible.
- Keep the element table minimum height at 140 px and let it grow when space is
  available. Avoid nested horizontal scrolling.
- Preserve field order, labels, object names, help keys, validation messages,
  and `parameters()` behavior. Do not change the element table columns or the
  NBS preset.
- If a short private layout helper is needed for the two columns, keep it
  private to the Yagi implementation; UX51 extracts the shared version after
  this slice proves the layout.

**Out of scope:** other families, the shared component, the sidebar, and any
change to the Yagi domain or solver spec.

**Tests:**

- `YagiDialog.minimumSizeHint().height() <= 640` with the scroll area present.
- After showing the dialog at 920×640, the button box is visible and lies
  inside the dialog rectangle; the scroll area provides the missing vertical
  space.
- No horizontal scrollbar at 920 px in English and Spanish.
- With a visible frequency/clearance warning and with ten table rows, the
  action box remains visible at 920×640; overflow stays inside the scroll area.
- Two columns exist and the proposed field groups are in the expected order;
  the folded transformer appears in the right column and disappears cleanly
  when unchecked.
- Existing Yagi dialog tests for the NBS preset, driven mapping, folded driven,
  beta/hairpin, taper, frequency scaling, warnings, and parameter round-trip
  remain green.
- Manual QA at 1920×1080 and 1366×768: table, notes, and OK/Cancel visible or
  reachable; no clipped labels; light/dark.

**Acceptance:** the Yagi dialog never opens with OK/Cancel outside the desktop;
the element table and actions are visible at the default size on 1920×1080; the
sidebar Yagi form remains single-column and unchanged; no solver, domain,
schema, or report change.

**Likely files:** `src/antennadesk/ui/dialogs/yagi_dialog.py`,
`src/antennadesk/ui/widgets/yagi_form.py`, `src/antennadesk/ui/i18n.py` (only if
section titles are added), `tests/ui/test_yagi_dialog.py`, and a new focused
layout test. **Effort:** M (3–5 days including QA).

### UX51 — Shared dialog scaffold, sectioned layout, and height guard

**Implemented 2026-11-26.** Added `FormDialogFrame` and `SectionedForm`, moved
the Yagi dialog onto both with no behavior change, and recorded the standard
in [ADR-0056](ADR/0056-antenna-dialog-layout.md). The layout guard in
`tests/ui/test_dialog_layout.py` covers 25 family dialogs in English and
Spanish; it has no current exceptions. Negative tests prove it rejects a
deliberately tall 1087 px form without a scroll area and the old
single-column Yagi shape. No other family was migrated in this slice.

**Goal:** turn the validated Yagi reference into a small, reusable UI standard
and prevent the same off-screen regression in future dialogs.

**Scope:**

- Write ADR-0056, "Antenna generator dialog layout and height budget". Record
  the measured baseline, the scaffold, the semantic section order, the
  responsive column rule, the 640 px budget, the sidebar exception, the
  rejected alternatives (two columns everywhere; scroll-only as the sole fix;
  tabs or collapsible groups as the default), and the accessibility/tab-order
  contract.
- Extract the common dialog scaffold from the generator dialogs: title, form
  area, notes, button box, `scaled_dialog_size()` use, and the scroll/action
  split. Working name: `AntennaFormDialog` or `FormDialogFrame`. It accepts a
  form widget and the note widgets; it does not know about antenna families.
- Extract the sectioned layout helper used by UX50. Working name:
  `SectionedFormLayout`. It accepts semantic sections with one or more rows,
  chooses one or two columns from an explicit mode plus the width/row
  threshold, keeps sections atomic, and exposes the tab order. It must not
  require duplicating labels or help registration; `FormLabels.bind_form()`
  must keep working for every column.
- Refactor the Yagi dialog to the shared scaffold and helper without changing
  its behavior. If the extraction would require rewriting `YagiForm`'s public
  construction or sidebar path, stop and keep the private UX50 helper; do not
  destabilize the sidebar for consistency.
- Add `tests/ui/test_dialog_layout.py` (or similar) with an explicit registry of
  generator dialogs. The guard must check:
  - a dialog whose form minimum exceeds the 640 px budget contains a
    `QScrollArea` around the form;
  - the button box is outside the scroll area and visible after the dialog is
    resized to the budget;
  - no horizontal scrollbar at 920 px in English and Spanish;
  - the action area stays inside the dialog rectangle at the budget size.
- The guard must be able to fail on a deliberately tall fake form, so it is not
  a no-op. Document any intentional exception next to the registry.
- Document the standard in `docs/ARCHITECTURE.md` and link ADR-0056. Do not add
  a second UI guideline document unless the ADR becomes too large.

**Out of scope:** migrating other families; changing `scaled_dialog_size()`
semantics beyond what the shared scaffold needs; changing the sidebar; adding
new fields.

**Tests:** unit tests for `SectionedFormLayout` (one/two columns, atomic
sections, threshold, tab order, EN/ES width); the generator-dialog guard; the
existing Yagi suite; a fake tall form proving the guard rejects a missing
scroll area; the full gate.

**Acceptance:** Yagi uses the shared scaffold with no behavior change; the
standard is recorded in ADR-0056; the guard catches the original 1087 px Yagi
shape when the scroll area is removed; all currently passing generator dialogs
either pass the guard or are recorded exceptions; no new dependency.

**Likely files:** new
`src/antennadesk/ui/widgets/form_dialog.py` and
`src/antennadesk/ui/widgets/sectioned_form.py` (working names),
`src/antennadesk/ui/dialogs/yagi_dialog.py`,
`src/antennadesk/ui/widgets/yagi_form.py`,
`src/antennadesk/ui/fonts.py` only if the scaffold needs a small API addition,
`docs/ADR/0056-antenna-dialog-layout.md`, `docs/ARCHITECTURE.md`,
`tests/ui/test_dialog_layout.py`, and focused widget tests. **Effort:** M–L
(1–2 weeks).

### UX52 — Complex family dialogs, wave 1

**Implemented 2026-11-26.** Loaded dipole, biquad, Moxon, and magnetic loop
now use the shared scaffold and a two-column semantic split; each has a form
scroll fallback and actions outside it. The four open at 920×640 with no
scrollbar and keep their field order, help, warnings, and parameter
round-trips. The loaded-dipole orientation labels are initialized without
waiting for a language change. No solver, domain, schema, or report change.

**Goal:** apply the standard to the four tallest one-column family dialogs
without scroll areas.

**Dialogs:** loaded dipole (16 rows, 616 px), biquad (14, 610 px), Moxon
(14, 591 px), and magnetic loop (14, 584 px).

**Scope per dialog:**

- Adopt the UX51 scaffold and sectioned layout. Use two columns because each
  form has at least 12 visible rows; keep sections atomic and the original field
  order.
- Add the scroll area and keep the action box outside it. Target 920 px wide;
  do not widen beyond 1000 px without a documented reason.
- Preserve every field, default, validation rule, warning, unit policy, help
  key, and parameter round-trip. Do not change the antenna model.
- Translate any new section title in English and Spanish, add its help entry,
  and update the help coverage manifest.
- Keep family-specific widgets intact (link/coil controls in the loaded dipole,
  loop and capacitor controls in the magnetic loop, and so on).
- Add or update layout tests per dialog: minimum height <= 640, action box
  visible at the budget size, no horizontal scrollbar at 920 px in EN/ES, and
  parameter round-trip unchanged.

**Acceptance:** each of the four dialogs fits the height budget or scrolls with
the action area visible; all fields remain reachable; no horizontal scrollbar;
existing family tests and the full gate are green; manual light/dark and
font-scaling QA is recorded. **Effort:** M (4–6 days).

### UX53 — Complex family dialogs, wave 2

**Implemented 2026-11-26.** Beverage, SCV, J-pole, and OCFD now use the shared
scaffold and a two-column semantic split. The OCFD band-plan selector is a
footer outside the form scroll. All four fit 920×640 with no horizontal
scrollbar in English or Spanish and preserve their parameter round-trips.
Large-font Spanish adds a small vertical scroll for Beverage and SCV while
the actions remain visible. No solver, domain, schema, or report change.

**Goal:** finish the one-column complex-family migration with the same
checklist as UX52.

**Dialogs:** Beverage (13 rows, 579 px), SCV (13, 559 px), J-pole (14, 557 px),
and OCFD (12, 551 px).

**Scope and acceptance:** identical to UX52. Use two columns only if the
semantic split is clear; if a family's form is naturally one continuous
sequence, keep one column, add the scroll safety, and document the decision in
the layout test registry. Preserve every parameter and warning. **Effort:** M
(4–6 days).

### UX54 — Scroll-heavy family dialog audit

**Implemented 2026-11-26.** The audit and per-dialog decisions are recorded in
[ADR-0056](ADR/0056-antenna-dialog-layout.md). All twelve dialogs now use the
shared scaffold and a single column with the action area outside the scroll.
No two-column migration was required. Stacked Yagi now places its stacked
controls above the embedded Yagi editor. Primary controls are visible at the
1920×1080 default and the 1366×768 cap; the guard has no exceptions.

**Goal:** decide, per dialog, whether the existing scroll is sufficient or
whether primary fields should be moved into atomic two-column sections. This is
an audit plus targeted migration, not a blanket rewrite.

**Inventory:** stacked Yagi (form 1697 px), end-fed (1328), vertical (820),
log-periodic (758), HexBeam (732), trap Yagi (653), phased vertical (612), quad
beam (580), trap dipole (570), T2FD (547), discone (493), and basic antenna
(636). These already have a scroll area; their dialog minimum is small, so they
do not block the action area today.

**Per-dialog decision record:** for each family, note the primary rows, the
optional/advanced groups, the current scroll depth at 1920×1080 and 1366×768,
and one of:

- **keep one column + scroll:** the primary fields fit in the first viewport;
  only advanced groups scroll;
- **collapse advanced groups:** optional groups become checkable/collapsible
  (the end-fed form already uses checkable groups); or
- **atomic two-column sections:** scrolling hides primary geometry or feed
  fields, and the form has at least 12 visible rows.

Do not split a `QGroupBox` or a composed-family section across columns. Start
with stacked Yagi and end-fed because they are the tallest composed forms; then
vertical, log-periodic, and HexBeam; the remaining dialogs may need only the
scaffold audit. Each dialog migration is its own change set.

**Acceptance:** every inventory dialog has a written decision; each uses the
shared scaffold and keeps the action area visible; primary fields are visible at
the default 1920×1080 size where the decision says they should be; no horizontal
scrollbar; parameter round-trip and family tests unchanged; no solver or schema
change. **Effort:** M–L (1–2 weeks; much of it is review and QA, not code).

### UX55 — Compact families, cross-family visual QA, and closure

**Implemented 2026-11-26.** Fan dipole, Ringo, inverted V, and inverted L now
use the shared scaffold without a form scroll and keep their compact
single-column layouts. The final guard registry has all 25 family dialogs
with no exceptions. The 400-combination offscreen matrix is recorded in
`archive/qa/QA_PASS_2026-11-26_ux55.md`; the manual desktop 125%/150%
confirmation passed on 2026-11-26, including the Large font preset.

**Goal:** finish the common language for compact generators without widening
them unnecessarily, run the visual QA matrix, and close the track.

**Scope:**

- Audit fan dipole (9 rows, 508 px), Ringo (11, 496 px), and inverted V/L
  (11, 465 px). Keep them single-column and compact. Adopt the shared scaffold;
  add a scroll area only where the height budget fails; do not force a 920 px
  width.
- Verify that field order, section names, spacing, label alignment, warning
  placement, and button placement match the standard.
- Run the cross-family QA matrix: English and Spanish; light and dark; Medium
  and Large font; 1366×768 at 100% and 1920×1080 at 100%, 125%, and 150% where
  the desktop allows. Check that no action button is off-screen, no label is
  clipped, no horizontal scrollbar appears, and the scroll position starts at
  the top.
- Add the final automated registry assertion for every generator dialog and
  remove stale exceptions or document the remaining ones.
- Update `docs/USER_GUIDE.md` if the Yagi dialog's behavior or layout is
  user-visible, and add the layout change to `CHANGELOG.md`.
- Close the track in `docs/STATUS.md` only when all automated checks and the
  manual matrix are recorded.

**Acceptance:** compact families remain compact; all generator dialogs share
the scaffold and always expose their actions; the QA matrix is recorded; the
full gate is green; no solver, domain, schema, report, or numerical change.
**Effort:** S–M (3–5 days including manual QA).

### Cross-cutting acceptance for the track

- The sidebar Yagi form and every other sidebar form remain single-column at
  340–520 px; no sidebar width, form panel, or splitter behavior changes.
- Every generator dialog either fits the 640 px minimum-height budget or wraps
  its form in a scroll area; the button box is never inside the scroll area.
- No horizontal scrollbar at the target width in English, Spanish, or the Large
  font preset.
- Field order, parameter values, defaults, validation, warnings, and help keys
  are unchanged. No antenna model, solver spec, schema, report, or numerical
  reference is modified.
- Any new section title has EN/ES text, help coverage, the manifest entry, and
  an accessible description through `ui/help.py`.
- The layout guard, per-dialog parameter round-trip tests, both mypy passes,
  ruff, and the full pytest gate are green.
- Manual light/dark and font-scaling screenshots are recorded for each changed
  dialog; the offscreen tests are not a substitute for the visual check.
- No new dependency, no `pickle`, and no global current-units singleton.

### Risks and mitigation

- **Tab order and screen-reader order.** Splitting a form can make the visual
  order differ from the widget order. Mitigate with explicit `setTabOrder()`,
  a focus-order test for the Yagi reference, and section construction in
  reading order.
- **Spanish and Large-font width.** Spanish labels are longer than English; a
  two-column form can exceed 920 px. Mitigate by measuring the widest label in
  both languages, keeping the 920 px target, and allowing only a documented
  increase to 1000 px.
- **Conditional rows.** Folded driven, transformer, match, traps, and composed
  groups can unbalance columns. Mitigate by treating sections as atomic and
  keeping conditional rows in their section instead of reflowing the form.
- **Over-wide or sparse dialogs.** Two columns can make a small form feel
  empty. Mitigate with the 12-row threshold and the compact-family exception.
- **Nested scrolling.** A table inside a scrollable form can feel awkward.
  Mitigate by making the default size show the table and actions, keeping the
  table's own scrolling, and treating the form scroll as a small-screen
  fallback.
- **Scope creep across many dialogs.** Mitigate with waves UX52/UX53, a
  per-dialog decision record in UX54, and no forced migration of compact
  families.
- **Qt size hints versus window managers.** Offscreen measurements are a
  guide. Mitigate with layout-based sizing (no fixed pixel heights), the
  `scaled_dialog_size()` cap, and manual QA on the target desktops.

### Effort and likely files

UX50 M (3–5 days); UX51 M–L (1–2 weeks); UX52 M (4–6 days); UX53 M (4–6
days); UX54 M–L (1–2 weeks); UX55 S–M (3–5 days). Total roughly 5–8 weeks
including tests, help, documentation, and manual QA. There is no external
dependency.

Likely files: `src/antennadesk/ui/dialogs/yagi_dialog.py`,
`src/antennadesk/ui/widgets/yagi_form.py`, the other family dialog/form pairs
listed above, new shared widgets under `src/antennadesk/ui/widgets/`,
`src/antennadesk/ui/fonts.py` only if the scaffold needs a small API addition,
`src/antennadesk/ui/i18n.py`, `src/antennadesk/ui/help.py`,
`tests/ui/test_dialog_layout.py`, the existing family UI tests,
`docs/ADR/0056-antenna-dialog-layout.md`, `docs/ARCHITECTURE.md`,
`docs/USER_GUIDE.md`, and `CHANGELOG.md`.

## Windows layout baseline and cross-platform generator wrapping (proposed 2026-11-27)

**Status:** proposed; P1 quality/release track. **Release:** unassigned;
candidate for a 0.11.2 patch after the layout fixes pass on Windows.
**Depends on:** none. **Blocks:** a green README `tests` badge on `main`.
**Decision:** follow-up to ADR-0056; update that ADR with the deterministic
test baseline and the single-column wrapping rule. No new numerical, solver,
domain, schema, or report decision.

**Motivation:** The README `tests` badge points at `ci.yml` on `main` and has
been red since the 0.11.0 publication. The latest run
[#46053347823](https://github.com/fsclavo/antenna-desk/actions/runs/46053347823)
on commit `d342027` fails two of twelve jobs:

- `Tests (windows-latest, Python 3.13)`: 22 failed, 1,181 passed.
- `Tests (windows-latest, Python 3.12)`: the same 22 failures, then the pytest
  batch stalls until the 10-minute step timeout (exit code 124).

Every other job passes, including all three `Tests (ubuntu-latest, Python
3.11/3.12/3.13)` jobs, where the same 1,203 tests pass. The failures are
layout assertions, not domain or solver failures:

| File | Tests | Example failure |
|---|---:|---|
| `tests/ui/test_dialog_layout.py` | 4 | `loaded_dipole`, `scv`, `stacked_yagi`, `endfed` in Spanish: "a scroll area needs a horizontal scrollbar" |
| `tests/ui/test_dialog_layout_ux54.py` | 12 | `endfed`, `vertical`, `phased_vertical`, `quad_beam`, `trap_dipole`, `basic_antenna` at the 691/972 px target heights (560–620 px dialog widths): horizontal bar maxima 4–184 px |
| `tests/ui/test_dialog_layout_wave1.py` | 1 | `loaded_dipole-es`: 32 px |
| `tests/ui/test_dialog_layout_wave2.py` | 1 | `scv-es`: 8 px |
| `tests/ui/test_flower_pot_dialog.py` | 1 | Large Spanish: 324 px |
| `tests/ui/test_yagi_dialog_layout.py` | 3 | default-height vertical scroll 86/142 px; Large Spanish form width 1058 px vs 884 px viewport |

The same Windows UI batch fails in the 0.11.0 and 0.11.1 release runs and in
the main runs since 2026-11-27. CI was green at 0.10.1 on 2026-11-25. The
layout tests and the shared scaffold landed on 2026-11-26 (`229ae79`,
`fa8a019`, `ad93e10`, `68dbea7`), and the Flower Pot dialog was added the same
day (`40436ad`), after the last green Windows run.

**Working hypothesis:** the Windows offscreen platform is reporting wider
font/layout metrics than Linux. A read-only local simulation with the Qt
`Windows` style shows:

- at 1.0–1.5× the intended base font, the 920×640 guard passes for all 26
  registry dialogs;
- at 2×, the six UX54 dialogs overflow by values in the same range as CI, and
  `WrapLongRows` removes the horizontal scrollbar in five of the six;
- Basic Antenna still needs a control-width fix after wrapping.

The exact DPI, font, and style must be confirmed on the runner (UX58) before
pinning a baseline. The track must not turn an environment artefact into a
blanket Windows skip.

**Code gaps already identified:**

- `SectionedForm` sets `QFormLayout.RowWrapPolicy.WrapLongRows` only when
  `column_count == 2`; single-column generator forms have no wrapping, even
  though ADR-0056 says they do.
- Several family forms use plain `QFormLayout` instances without the policy:
  `EndFedForm` (including its nested group forms), `FlowerPotForm`,
  `VerticalForm`, `PhasedVerticalForm`, `QuadBeamForm`, `TrapDipoleForm`,
  `StackedYagiForm`, and `DipoleForm` (Basic Antenna).
- `YagiForm` sets `QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents` on
  the element table in the wide layout, which can let table content drive the
  form width.
- `FormDialogFrame` uses fixed initial widths and does not grow to the form's
  minimum size hint, so a wider platform font can open a dialog with a
  horizontal scrollbar.
- The Windows 3.12 stall is a separate symptom. It must be isolated so it
  cannot hide the layout result; it is not evidence that the layout tests are
  invalid.

**Goals:**

- Make the Windows and Linux layout tests evaluate the same documented 9–10 pt
  / 100% baseline.
- Keep every generator dialog free of horizontal scrolling at 920 px in
  English and Spanish, including `FontSize.LARGE`, with vertical scrolling
  allowed only as ADR-0056 already permits.
- Keep the action box outside the scroll and visible at every tested size.
- Leave a fast, bounded CI signal that cannot hide a 10-minute teardown stall.

**Non-goals:** no solver, domain-model, schema, project-container, report,
help-copy, or numerical-reference change; no forced two-column layout; no
change to the narrow main-window sidebar; no new dependency; no `skip`,
`xfail`, or Windows exclusion to make the badge green.

### UX58 — Deterministic Windows UI layout baseline and batch isolation

**Status:** implemented locally 2026-11-27; Windows CI verification pending.
**Depends on:** none. **Blocks:** UX59–UX61 verification on Windows.
**Effort:** S (0.5–1 day).

**Scope:**

1. Add a diagnostic that records, in the Windows UI job:
   - `QFontInfo(QApplication.font()).family()`, `pointSizeF()`, and
     `pixelSize()`;
   - `QFontMetrics(QApplication.font()).height()` and the advance of a fixed
     mixed-width string such as `"Frecuencia (MHz)"`;
   - `QGuiApplication.primaryScreen().logicalDotsPerInch()`,
     `devicePixelRatio()`, and `availableGeometry()`;
   - `QApplication.style().name()`.
   Put it in a small test (for example `tests/ui/test_qt_layout_baseline.py`)
   that prints the resolved baseline values, then asserts the pinned font is in
   the documented 9–10 pt range and that DPI, device pixel ratio, and metrics
   are finite and positive. Keep it in the suite so the next environment
   change is visible.
2. Decide and document the baseline. Prefer pinning the UI test environment
   before `QApplication` is created (`QT_FONT_DPI=96`, `QT_SCALE_FACTOR=1`)
   and adding a session or autouse fixture that normalizes the base font to
   9–10 pt and restores the original font, palette, and style. Do not pin the
   production application font or change `scaled_dialog_size()`.
3. Split the layout files into their own pytest batch in
   `.github/workflows/ci.yml`: `test_dialog_layout*.py`,
   `test_yagi_dialog_layout.py`, and `test_flower_pot_dialog.py`, with
   `timeout 180s`. Keep the existing Windows 3.12/3.13 UI jobs; do not exclude
   the batch.
4. Re-run the 22 failing tests on Windows. Classify any remaining failure as
   a production layout defect for UX59/UX60, not as a reason to relax an
   assertion.

**Acceptance:**

- The diagnostic is visible in the Windows log and records the actual font,
  DPI, device pixel ratio, style, and key font metrics.
- At the pinned baseline, the layout batch runs to completion in under 180 s
  on Windows 3.12 and 3.13 and reports the same pass/fail set as Linux.
- If the 22 failures disappear only because of the baseline pin, the track
  records that explicitly and still completes UX59/UX60 against a simulated
  2× font.
- No production behavior, schema, solver, or report change.

**Implementation (2026-11-27):**

- `tests/conftest.py` sets the offscreen platform and the 96 DPI / 1× test
  baseline before `QApplication` is created.
- `tests/ui/conftest.py` normalizes the shared test font to 9–10 pt and restores
  the original font, palette, style, and S/M/L scale after every UI test.
- `tests/ui/test_qt_layout_baseline.py` prints and asserts the resolved family,
  point/pixel size, DPI, device pixel ratio, style, font metrics, and screen.
- `.github/workflows/ci.yml` sets the baseline at job level and runs the dense
  layout files in a separate `-s` batch with a 180 s timeout; the general UI
  batch excludes them.
- Local verification: `182 passed` for the isolated layout batch; the baseline
  prints `Noto Sans 9.00pt / 96 DPI / DPR 1.00 / fusion / 17 px height`.
- Pending: the Windows 3.12/3.13 run must classify any remaining failure for
  UX59/UX60 instead of relaxing an assertion.

### UX59 — Wrap long form rows across generator dialogs

**Status:** proposed; P1. **Depends on:** UX58. **Effort:** M (2–4 days).

**Scope:**

1. Add one shared helper, for example `configure_form_layout()` in
   `sectioned_form.py` or a small `form_layout.py`, that sets
   `WrapLongRows`, `AllNonFixedFieldsGrow`, zero content margins, and explicit
   horizontal/vertical spacing. Use it from `SectionedForm` for both
   single-column and two-column modes so Windows, Fusion, and Windows 11
   styles do not silently change the width contract.
2. Apply the helper to every `QFormLayout` in the family forms that can
   overflow: EndFed (main form and the loading-coil, design-network, and
   nested network forms), FlowerPot, Vertical (main, coil, top-hat),
   PhasedVertical, QuadBeam, TrapDipole, StackedYagi, DipoleForm (Basic
   Antenna), Yagi, and the two-column LoadedDipole/SCV forms where a long
   label or combo still exceeds the viewport.
3. Audit long labels and notes for `setWordWrap(True)`. Keep the existing
   `FormLabels` binding and help application; do not rename label keys or
   change field order.
4. Add a regression test with a synthetic single-column form containing a
   very long English and Spanish label: at 560 px and 920 px it must not
   produce a horizontal scrollbar.
5. Extend `tests/ui/test_flower_pot_dialog.py` (or the new baseline test) to
   cover the Large Spanish case at the dialog's initial 600 px width.

**Acceptance:**

- At the UX58 baseline, every registry dialog at 920×640 and at its initial
  560–620 px width has no horizontal scrollbar in English or Spanish.
- At `FontSize.LARGE`, 920 px still has no horizontal scrollbar; vertical
  scrolling is allowed, and the action box remains visible.
- The existing UX54 primary-control checks and the UX52/UX53 budget tests
  pass without weakening their horizontal assertions.
- Parameter round-trips, tab order, help labels, and help coverage are
  unchanged.
- `ruff`, both `mypy` passes, and the full pytest gate are green.

### UX60 — Layout-based dialog sizing and Yagi table width

**Status:** proposed; P1. **Depends on:** UX59. **Effort:** S–M (1–3 days).

**Scope:**

1. In `FormDialogFrame`, choose the initial width from the requested size and
   the form's minimum size hint, capped by the existing
   `scaled_dialog_size()` screen cap. The 920 px target and the 560–940 px
   per-dialog defaults remain the first choice; the frame only grows when the
   content cannot otherwise fit. Re-check the resize/show path so a late
   layout does not immediately add a horizontal bar.
2. In `YagiForm`, remove `AdjustToContents` from the wide element table or
   constrain its minimum width. Keep the 140 px minimum height, stretch the
   four columns, and let the table scroll internally if a cell cannot shrink.
   Verify that the table still grows when extra height is available.
3. In Basic Antenna/DipoleForm, give the template/family control an explicit
   compact policy or elide its text so the 560 px dialog and Large font do not
   force a horizontal bar.
4. If a two-column form still cannot fit at 920 px with Large font, choose one
   of the documented options in ADR-0056: collapse to one column for that
   dialog or use the 1000 px width allowance. Record the decision in the ADR;
   do not add a silent per-platform exception.

**Acceptance:**

- All 26 registry dialogs at 920×640, English and Spanish, baseline and Large
  font: no horizontal scrollbar; action box visible; primary control visible
  at the initial narrow sizes covered by UX54/UX55.
- Yagi opens at its default size without a vertical scrollbar at the baseline
  font; at Large font only vertical scrolling is allowed.
- The Yagi table grows with extra height, headers remain readable, and no
  horizontal form scrollbar appears.
- The Windows 3.12/3.13 layout batch is green.
- No change to solver specs, schema, reports, or parameter defaults.

### UX61 — Large-font layout guard, Windows closure, and docs

**Status:** proposed; P1. **Depends on:** UX58–UX60. **Effort:** S–M
(1–2 days).

**Scope:**

1. Extend the layout guard with a compact Medium/Large matrix:
   - all 26 dialogs, English and Spanish;
   - 920×640 and the documented initial narrow sizes;
   - assert no horizontal scrollbar at Medium and Large;
   - assert the action box is visible and outside the scroll at both;
   - allow a vertical scrollbar only at Large, as ADR-0056 states.
   Reuse the existing registry and keep the runtime bounded; do not add a
   full light/dark × size × language Cartesian product to the fast batch.
2. Add the Large-font case to `test_yagi_dialog_layout.py` and the Flower Pot
   dialog test. Remove a now-redundant special-case exception only when the
   assertion is genuinely covered.
3. Update `docs/ADR/0056-antenna-dialog-layout.md` with the deterministic
   test baseline, the single-column and nested `WrapLongRows` rule, the
   layout-based initial width, and the final width decision for Yagi/Large.
4. Update `docs/STATUS.md` and `CHANGELOG.md` with the user-visible fix and
   the CI outcome. Add a short QA record under `docs/archive/qa/` for the
   manual light/dark and 125%/150% check.
5. Run the full gate on Linux and the real Windows CI. Confirm the README
   `tests` badge is green on `main` after merge.

**Acceptance:**

- Windows 3.12/3.13 and Linux 3.11–3.13 are green; the layout batch finishes
  under its timeout; no `skip`, `xfail`, or platform exclusion was added.
- The guard fails if a future change reintroduces a horizontal scrollbar at
  920 px or hides the action box.
- The manual QA record covers English/Spanish, light/dark, Medium/Large, and
  125%/150% scaling on at least one Windows and one Linux desktop.
- ADR-0056, STATUS, CHANGELOG, and the QA record are consistent with the code
  and with the actual CI run.

**Track order:** UX58 → UX59 → UX60 → UX61. UX58 must land first so the
Windows signal is trustworthy. UX59 and UX60 may share a change set if the
diff stays small, but their acceptance stays separate. UX61 closes the track
only after the real Windows run is green. Do not start with a Windows skip or
a test-only width increase: both hide the user-facing issue.

**Cross-cutting acceptance:**

- The full gate passes: `ruff check`, `ruff format --check`, both `mypy`
  passes, and the complete `NEC2C=... uv run pytest`.
- No solver, domain, schema, project-container, report, or numerical
  reference changes.
- No new dependency and no `pickle`.
- The action box remains outside the form scroll at every tested size.
- Light/dark and font-scaling QA is recorded; offscreen tests are not a
  substitute for the manual check.
- No commit or push unless explicitly requested.

**Risks and mitigation:**

- **Pinning DPI hides a real high-DPI defect.** Mitigate with the simulated
  2× guard, the real Windows runner, and the manual 125%/150% check. Keep the
  production font and `scaled_dialog_size()` unchanged.
- **Wrapping increases form height.** Mitigate with the existing form scroll
  and by asserting that the primary control and action box stay visible;
  vertical scrolling at Large is already allowed by ADR-0056.
- **A two-column collapse changes field order or tab order.** Mitigate by
  keeping sections atomic, preserving the documented reading order, and
  testing tab order in both modes.
- **CI runtime or a repeated teardown stall.** Mitigate with the dedicated
  180 s layout batch. If the stall persists after the failures are fixed,
  capture the last test and the Qt teardown state and open a separate blocker;
  do not let it mask the layout result.
- **Cross-platform style drift.** Mitigate with explicit margins and spacing
  in the shared helper instead of relying on style defaults.

**Effort and likely files:** UX58 S, UX59 M, UX60 S–M, UX61 S–M; total roughly
1–2 weeks including Windows iterations and manual QA. Likely files:
`.github/workflows/ci.yml`, `tests/conftest.py`, `tests/ui/conftest.py`, a new
`tests/ui/test_qt_layout_baseline.py`,
`src/antennadesk/ui/widgets/sectioned_form.py`,
`src/antennadesk/ui/widgets/form_dialog.py`,
`src/antennadesk/ui/widgets/yagi_form.py`,
`src/antennadesk/ui/widgets/dipole_form.py`,
`src/antennadesk/ui/widgets/endfed_form.py`,
`src/antennadesk/ui/widgets/flower_pot_form.py`,
`src/antennadesk/ui/widgets/vertical_form.py`,
`src/antennadesk/ui/widgets/phased_vertical_form.py`,
`src/antennadesk/ui/widgets/quad_beam_form.py`,
`src/antennadesk/ui/widgets/trap_dipole_form.py`,
`src/antennadesk/ui/widgets/stacked_yagi_form.py`,
`src/antennadesk/ui/dialogs/yagi_dialog.py`,
`tests/ui/test_dialog_layout.py`,
`tests/ui/test_dialog_layout_ux54.py`,
`tests/ui/test_dialog_layout_wave1.py`,
`tests/ui/test_dialog_layout_wave2.py`,
`tests/ui/test_dialog_layout_ux55.py`,
`tests/ui/test_yagi_dialog_layout.py`,
`tests/ui/test_flower_pot_dialog.py`,
`docs/ADR/0056-antenna-dialog-layout.md`, `docs/STATUS.md`, and
`CHANGELOG.md`.

## Adaptive length display units (implemented 2026-11-18; QA closed 2026-11-24)

**Status:** U0–U6 are complete. The manual desktop light/dark and font-scaling
checklist was completed on 2026-11-24 with no blocking findings. The release
plan decides whether the track lands in 0.10.0 or a later release.
**Decision:** [ADR-0044](ADR/0044-adaptive-length-display-units.md).
**Normative spec:** [`DISPLAY_UNITS_SPEC.md`](DISPLAY_UNITS_SPEC.md).

The current metric display uses meters for every length and millimeters for
wire diameters. That is readable for HF but poor for VHF/UHF construction: a
435 MHz Moxon gap shows `0.007 m`, and its 24.8 cm width rounds to `0.25 m`.
Imperial has the same problem with `0.023 ft`. The fix is a presentation-only
automatic policy, never a frequency-based or global-centimeter switch.

The policy is:

- Metric auto: mm below 1 cm, cm from 1 cm to below 1 m, m at 1 m and above.
- Imperial auto: in below 1 ft, ft at 1 ft and above.
- Scalar fields and dimension labels choose by value; editable and report
  tables choose one unit per table from the largest value and show it in the
  header.
- mm/cm use two decimals, m/ft use three, inches use two. Labels trim trailing
  zeros. Spin boxes keep fixed decimals.
- A field or table unit is frozen while editing and re-evaluated on model,
  preset, optimizer, undo/redo, or preference reload.
- Human-readable construction sheets and reports follow the policy. CSV stays
  canonical meters/mm. DXF stays canonical meters with `$INSUNITS=6` and
  meter dimension text.
- The Units preference keeps an escape hatch: metric auto (default), metric
  fixed in meters, imperial auto (default), and imperial fixed in feet.

Non-goals: per-project units, decimal-separator changes, inch fractions,
automatic radius/diameter units, DXF scaling, and any solver, domain, or schema
change.

### U1 acceptance

- `DisplayUnits`/`LengthPolicy` is a pure, Qt-free formatter with automatic and
  fixed metric/imperial policies, boundary tests, zero/negative handling,
  trimming, and table-unit selection.
- The Units preference stores the system and policy, maps existing
  `metric`/`imperial` values to automatic, and has EN/ES help.
- No scene, form, or report changes yet; the full existing gate stays green.

### U2 acceptance

- `build_scene` and `_Factory` accept `DisplayUnits`; dimension labels,
  summaries, scale bar, and insets use it.
- 28.5/144/435 MHz Moxon, 20 m dipole, and 435 MHz hexbeam scenes cover the
  automatic examples in the spec.
- The scale bar uses unit-aware candidate steps; the minimum-size layout and
  hidden-dimension strip still work; the small-dimension anchor tolerance is
  tightened.
- Existing fixed-unit tests and goldens remain stable; new auto tests are
  focused rather than regenerating every golden.

### U3 acceptance

- Every antenna-family editor uses `LengthFieldSpec` for range, step, decimals,
  suffix, and optional scale hint; no small feature inherits the global
  `0.1 m` minimum.
- Editable tables use one unit per table with the unit in the header; radius
  columns stay mm/in.
- Moxon height no longer inherits Qt's `99.99` maximum; 435 MHz hexbeam
  tip/feed gaps and element separation can be represented.
- Metric/imperial and auto/fixed switches preserve every physical value; field
  suffixes do not change mid-edit.

### U4 acceptance

- Optimization, family optimization, synthesis, parameter sweep, robustness,
  tolerance, design-from-frequency, feed-line, and related dialogs use the same
  policy.
- Every `length_bounds` caller is audited; per-field ranges replace global
  small-feature minimums.
- Plot axes, budgets, and table headers remain legible; EN/ES help covers the
  new unit presentation.

### U5 acceptance

- Construction-sheet design summary, wire schedule, BOM, feed/matching rows,
  and report tables use `DisplayUnits`; the title block states
  `Metric auto (mm/cm/m)` or the selected fixed/imperial policy.
- SVG/PNG/PDF figures follow the UI; CSV remains canonical meters/mm; DXF
  remains canonical meters with `$INSUNITS=6` and meter dimension text.
- HTML, native PDF, package, and CSV/DXF tests cover both automatic and fixed
  policies.

### U6 acceptance

- User guide and `CHANGELOG.md` describe the automatic policy, the fixed
  escape hatch, and the CSV/DXF canonical exception.
- EN/ES help coverage includes the Units preference and unit-bearing table
  headers.
- Light/dark and font-scaling QA covers the sketch, forms, and construction
  sheet; the full gate is green.

### Dependencies and order

U1 is the foundation. U2 and U3 may proceed in parallel after U1. U4 depends on
U3 because it shares the form helpers. U5 depends on U2 and U3 because it
embeds scenes and report rows. U6 closes the track after U2–U5.

Do not start any slice by adding a global current-units singleton, a
`UnitSystem.CM` value, frequency-based selection, or a per-cell table unit.
Those alternatives are rejected in ADR-0044.


## Historical design notes

Completed design notes, research, and historical sequencing are archived:

- [`archive/backlog/optimizer-and-high-frequency.md`](archive/backlog/optimizer-and-high-frequency.md)
  — high-frequency optimizer bounds and shortened-EFHW optimizer notes.
- [`archive/backlog/antennas-and-feed.md`](archive/backlog/antennas-and-feed.md)
  — HexBeam follow-ups, matching-network precedence, and phased-vertical notes.
- [`archive/backlog/ux-queue-notes.md`](archive/backlog/ux-queue-notes.md)
  — UX queue and design notes.
- [`archive/backlog/workflow-and-sequencing.md`](archive/backlog/workflow-and-sequencing.md)
  — progress feedback and historical sequencing.
- [`archive/backlog/solver-and-technical-debt.md`](archive/backlog/solver-and-technical-debt.md)
  — solver runtime measurements and technical-debt notes.


## Deferred product work

The 2026-11-04 phase plan is archived. Its open items were reviewed during the
2026-11-09 consolidation. The following are intentionally not in the active
queue because they need a different model, a traceable source, or a product
decision:

| Item | Why it is not active | Tracked in |
|---|---|---|
| Near-field and RF exposure (DL4) | Canceled 2026-11-24; not relevant enough to the amateur design workflow for the required safety-claim work | [`ROADMAP.md`](ROADMAP.md) |
| Fan-dipole angle optimization and an explicit per-element feed model | Needs a different antenna model, not another scalar correction | [`ROADMAP.md`](ROADMAP.md), [`FAN_DIPOLE_CALIBRATION.md`](FAN_DIPOLE_CALIBRATION.md) |
| Measured or optimized 20/10 m fan-dipole preset | Needs a traceable source or measurement | [`ROADMAP.md`](ROADMAP.md) |
| Gamma match for the Yagi | NEC-2 is unreliable for close-spaced gamma assemblies; the beta/hairpin match is implemented | [`ROADMAP.md`](ROADMAP.md) item 6 |
| Boom-mounting correction | No universal published model. DL5 models the boom, mast, tower, and guy wires as conductors; an empirical correction factor remains deferred. | [`ROADMAP.md`](ROADMAP.md) item 14 and §DL5, [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| Report-specific metric selection for power, directivity, and realized gain | The UI selector exists; export-specific selection is optional | [`ROADMAP.md`](ROADMAP.md) |
| General radial-screen and transmission-line geometry beyond the current subset | DL7 covers the native NEC-2 radial screen and the bounded cliff/second-medium case; arbitrary radial screens and general transmission-line geometry remain deferred | [`ROADMAP.md`](ROADMAP.md), §DL7, [`founding-decisions.md`](archive/founding-decisions.md) |
| Custom/imported geometry optimization | Deliberately unavailable because arbitrary geometry has no parameterized topology | [`ADR/0026-family-optimizer-architecture.md`](ADR/0026-family-optimizer-architecture.md) |
| Physical antenna validation | Blocked on measurements; tracked as B4 in the active queue table | [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| Segmented frequency plan in one NEC deck | Closed by ADR-0042; per-band batching retained | [`MULTIBAND_PERFORMANCE.md`](MULTIBAND_PERFORMANCE.md), [ADR-0042](ADR/0042-per-band-frequency-plan.md) |
| True per-frequency simulation progress | Needs an ADR and benchmark to choose between chunked execution and incremental parsing; not justified until simulations are long enough | [`archive/backlog/workflow-and-sequencing.md`](archive/backlog/workflow-and-sequencing.md), [ADR-0042](ADR/0042-per-band-frequency-plan.md) |
| Live VNA control, additional full-wave engines, and release signing | Need hardware, an engine decision, or release credentials | D1–D3 in the active queue table, [`ROADMAP.md`](ROADMAP.md) |

## Current baseline

- Schema: **73**; container version 1.
- Full gate: **4,807 passed, 1 skipped** on 2026-11-27 after PF2 streaming
  write, the DL3 managed-value closure, and the UX58 local layout baseline.
  The 0.11.1 release covers the optimizer close/cancel lifecycle fix. Real
  `nec2c` integration: **186 passed**. The suite also covers the QA and
  technical-debt closure,
  main-window extractions, the save/load size invariant fix, PF1 container,
  lazy open/save/compact, PreparedProject, DL7 site ground, and VR1 radial
  droop (typed simulation specs, pattern presets, and
  pattern-budget planning in the application layer, plus
  catalog/template routing in `ui/catalog.py`, export dialogs/writers in
  `ui/exporters.py`, VNA/NEC/MMANA import parsing in `ui/import_actions.py`,
  project open/save workers in `ui/project_io.py`, autosave/recovery in
  `ui/recovery_actions.py`, element-optimizer dialogs in
  `ui/element_optimization_actions.py`, family/length/synthesis dialogs in
  `ui/optimization_actions.py`, and recent-list behavior in
  `ui/recent_actions.py`), with `NEC2C` auto-detected by the test
  configuration; the skip is the Windows-only console-hiding test on Linux.
  See [`archive/qa/QA_PASS_2026-11-24.md`](archive/qa/QA_PASS_2026-11-24.md)
  and the earlier
  [`archive/qa/QA_PASS_2026-11-20.md`](archive/qa/QA_PASS_2026-11-20.md).
- Main-window decomposition: **closed 2026-11-20** after the high-value
  extractions. `_build_ui`, `_build_actions`, and `retranslate` stay in the
  window deliberately; future work extracts a component only when a feature or
  defect touches it. The duplicated `QThread` lifecycles and `results_view.py`
  are likewise feature-driven, not an active standalone refactor.
- Release: **0.10.0** published on 2026-11-24 with adaptive length units
  U1–U6, live tuning (DL3), uniform radial droop (VR1), cliff site ground
  (DL7), the PF1 ZIP container, and the 1.1 station tools. The tag-triggered CI
  run [`45508172449`](https://github.com/fsclavo/antenna-desk/actions/runs/45508172449)
  completed the wheel/sdist, Linux, Windows, and publish jobs; all six published
  assets and checksums were verified. The tag CI Windows jobs did not go
  green: two failed on a Unix-only `os.geteuid()` guard in a test added by the
  U6 QA pass, and Python 3.12 was canceled after a UI stall. The Release
  workflow still built and smoke-tested the Windows artifacts; the guard was
  fixed on main and the rerun
  [`45512002095`](https://github.com/fsclavo/antenna-desk/actions/runs/45512002095)
  passed all jobs. See
  [`RELEASE_QA_0.10.0.md`](archive/releases/RELEASE_QA_0.10.0.md). **0.9.0**
  remains the previous release (2026-11-17, Touchstone/UX31/UX30). See
  [`RELEASE_QA_0.9.0.md`](archive/releases/RELEASE_QA_0.9.0.md).
- Release: **0.10.1** published on 2026-11-24 with the refreshed application
  icon and the live-tuning GUI-thread worker fix. Windows 3.11/3.12/3.13 and
  Linux CI pass; the Release workflow built and checksum-verified every
  artifact. See [`RELEASE_QA_0.10.1.md`](archive/releases/RELEASE_QA_0.10.1.md).
- Release: **0.11.1** published on 2026-11-27 with the optimizer dialog
  close/cancel lifecycle fix. Full gate: 4,790 passed, 1 skipped; real `nec2c`
  integration: 186 passed. The tag workflow
  [`46052575256`](https://github.com/fsclavo/antenna-desk/actions/runs/46052575256)
  built and published the wheel/sdist, Linux packages, Windows packages, and
  checksums. See
  [`RELEASE_QA_0.11.1.md`](archive/releases/RELEASE_QA_0.11.1.md).
- Release: **0.11.0** published on 2026-11-27 with the UX46–UX57 3D/pattern
  and dialog-layout work, the extended DL6 stacked-Yagi feed network, and FP1
  with schema 73. Full gate: 4,787 passed, 1 skipped; real `nec2c` integration:
  186 passed. The tag workflow
  [`46033456924`](https://github.com/fsclavo/antenna-desk/actions/runs/46033456924)
  built and published the wheel/sdist, AppImage, Debian package, Windows
  installer, portable zip, and all checksums. See
  [`RELEASE_QA_0.11.0.md`](archive/releases/RELEASE_QA_0.11.0.md).
- Known CI residue: Windows Python 3.11 runs acceptance, integration, and unit
  tests only. Its UI suite is excluded because PySide6/pyqtgraph can corrupt
  the native heap during view teardown; Windows 3.12/3.13 and Linux
  3.11–3.13 run the full UI suite. See
  [`ADR/0025`](ADR/0025-pyside6-version-pin.md). Do not weaken the remaining
  gates.
- Known red CI (2026-11-27): the README `tests` badge is failing on Windows
  Python 3.12/3.13 because of 22 generator-dialog layout assertions; Linux is
  green. The Windows 3.12 batch also stalls at its 10-minute timeout after the
  failures. Tracked as UX58–UX61 in §Windows layout baseline and
  cross-platform generator wrapping. Do not skip the Windows jobs or weaken
  the assertions while that track is open.
- Recent work: use `git log --oneline`; do not maintain a commit list in this document.
