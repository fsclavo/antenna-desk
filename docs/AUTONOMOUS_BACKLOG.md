# Autonomous execution backlog

**Date:** 2026-11-20
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
2026-11-24; the optional streaming write and pattern-level lazy loading are
deferred follow-ups.

Completed rows are archived in [`archive/backlog-completed-2026-11-20.md`](archive/backlog-completed-2026-11-20.md).

| ID | Task | Size | Depends on | Acceptance |
|---|---|---|---|---|
| PF1 | ZIP project container and honest size contract | L | none | **Done 2026-11-24; manual validation passed.** A project that saves always reopens; design, runs, and optimizations are separate validated ZIP entries; per-entry/total limits apply on save and load; old runs are compacted by the save flow; oversized projects can be recovered design-only. No backward compatibility. Optional follow-ups: streaming write and pattern-level lazy loading. See §PF1. |
| B4 | Fan-dipole coupling calibration | M | measurement | A coupled-fan measurement is reproduced; no scalar correction is invented |
| C7h | Optional 6 m HexBeam band | S | C7c; published 6 m row | Add the published 6 m driver/reflector/tip-spacer row and vertical offset, with the same frame-fit validation, editor option, reports, and evidence note. No performance claim. |
| C7i | HexBeam feed harness and inter-band coupling | L | traceable harness data or measurement | Model the parallel coax feed harness/jumper lengths and inter-band coupling, or keep it explicitly unavailable; no invented values. Blocked until a source or measurement exists. |
| G27 | Optional transformer, common-mode choke, and coaxial loss models | L | G25; measured transformer insertion loss/core data; common-mode current model or measurement; manufacturer coax attenuation data | **Partially delivered.** EF7b added the measured transformer-loss table (`BalunLoss`); EF8 added the bounded feedpoint common-mode choke; ADR-0039 adds frequency-dependent feed-line attenuation with source-backed RG-58A/RG-213 tables, log-frequency interpolation, endpoint clamping, and a preflight range warning. The loss-accounting audit is also done (ADR-0040): the feed-chain sum must match the transducer gain, and NEC conductor/load losses including the feedpoint choke stay in the antenna power budget. Still deferred: analytical ferrite core loss with complex permeability/core geometry/winding/load data; frequency-interpolated `Zcm(f)` and shack-end choke placement; the remaining coax/choke evidence audit. All loss fields stay optional and off/zero by default; no invented loss numbers. |
| U6 | Documentation, help audit, and visual QA | S–M | U2–U5 | **Documentation/help complete 2026-11-18; manual QA pending.** The user guide, roadmap, units spec, README, changelog, help tests, and automated font-scaling/geometry checks are updated. [`QA_PASS_2026-11-18.md`](archive/qa/QA_PASS_2026-11-18.md) records the automated gate and the remaining desktop light/dark/font-scaling checklist. The track closes after that manual QA. |
| DL3 | Live tuning preview | M–L | none | **Partially done 2026-11-20.** Primary-dimension slider, coarse single-frequency preview, debounce/cancel, stale-result guard, preview badge, and apply/full-run path. Other managed dimensions and pattern preview remain. See §DL3. |
| DL5 | Support structures | M–L | ADR | **Done as narrowed 2026-11-24.** Yagi mast conductor plus 2–4 guy wires, geometry, BOM, scene, and schema 57–58. Conductive boom, tower, attachments, and structural hardware are deferred pending ADR/spike; no further 1.1 work. See §DL5. |
| DL6 | Stacked Yagi arrays | L | DL5 (soft), ADR | **Domain prototype 2026-11-20.** StackedYagiParameters builds 2–4 levels with an ideal source progression and per-level wires. Form, schema, per-port UI, splitter/phase lines, and optimizer remain. See ADR-0049 and §DL6. |
| DL7 | Native ground screen and cliff ground | M–L | ADR, spike | **Bounded slice implemented 2026-11-24; evidence B/C.** Cliff/second-medium far-field profile, schema 60, Site Ground dialog, and `GN`/`RP 2`/`RP 3` adapter. No external site reference is available; the native radial screen stays unvalidated for SWR and is not exposed. See ADR-0051, `spikes/dl7-ground-gn-spike.md`, and §DL7. |
| DL8 | Full terrain model | XL | DL7, validated model | **Post-1.2.** Only with a validated terrain model or a second engine; otherwise explicitly unavailable. See §DL8. |
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
writing. Remaining: stream the container write instead of holding its bytes in
memory, and add pattern-level lazy loading if reports need it. See
[ADR-0050](ADR/0050-zip-project-container.md).

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
by the full history.

**Goal:** replace the single gzip JSON envelope with a versioned ZIP container
whose entries can be validated, loaded, and pruned independently; enforce one
set of limits on both save and load; never write a project the application
cannot reopen; keep one portable `.antennadesk` file and atomic saves.

**Non-goals:** no backward compatibility with the gzip/plain-JSON project
format or schema 59; no solver, antenna-model, or numerical-reference change;
no binary pattern store or sidecar database in this item. Open a separate item
if those are still needed after the container lands.

### Container format (container version 1, schema version 60)

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

- **Implemented:** immutable `PreparedProject` with `payload`,
  `compressed_bytes`, `uncompressed_bytes`, `entry_count`, and `limits`.
  `ProjectRepository.prepare_payload()` returns it; `write_payload(path,
  prepared)` writes it atomically.
- `prepare_payload()` builds every entry, sums the uncompressed bytes, and
  raises `ProjectTooLargeError` **before** the final replace if any compressed,
  expanded, entry, count, or path limit is exceeded. A successful `save()` must
  always produce a file that `load()` accepts; add a round-trip invariant test.
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
  `USER_GUIDE.md`, `STATUS.md` (schema 60), and `CHANGELOG.md`.
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
product decision. The DL6 domain prototype is started; its form, schema, and
per-port UI wait for the support-structure decision.

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

**Status:** **Partially done 2026-11-24.** A managed-dimension selector covers
the primary dimension plus family-specific length dimensions such as height,
spacing, radial length, feed height, and reflector spacing. The coarse
single-frequency preview, debounce/cancel, stale-result guard, preview badge,
and apply/full-run path are implemented. Apply keeps the dialog open, resets the
baseline to the applied design, and re-enables tuning after the full simulation
finishes. Pattern preview and non-length managed values remain follow-ups.

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

**Dependencies:** existing worker/cancellation; no solver change.

**Acceptance:**
- Dragging a length updates SWR and impedance in preview; releasing stops the
  worker.
- A stale result never overwrites a newer one.
- Commit produces a normal simulation and undo entry.
- The dialog stays open after Apply; the operator can continue tuning, and
  closing it preserves the last applied design.
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

**Domain prototype (2026-11-20):** [`ADR-0049`](ADR/0049-stacked-yagi-composed-family.md)
and `StackedYagiParameters` build 2–4 levels with an ideal source progression.
Form, schema, per-port UI, splitter/phase lines, and optimizer remain
follow-ups. See also [`spikes/dl6-stacked-yagi-spike.md`](spikes/dl6-stacked-yagi-spike.md).

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
- A 2×3 stack runs, shows per-port impedance and the combined pattern.
- Spacing/phase optimization respects the mechanical envelope.
- The report shows the stack dimensions and feed notes.
- No gain claim beyond the evidence level.

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

## Adaptive length display units (implemented 2026-11-18; manual QA pending)

**Status:** U0–U6 are complete; only the manual desktop light/dark and
font-scaling checklist remains before the release decision. The release plan
decides whether the track lands in 0.10.0 or a later release.
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

- Schema: **60**; container version 1.
- Full gate: **4,301 passed, 1 skipped** on 2026-11-24 after the full QA,
  technical-debt sweep, main-window extractions, save/load size invariant fix,
  PF1 container, lazy open/save/compact, PreparedProject, and DL7 site ground
  (typed simulation specs,
  pattern presets, and pattern-budget planning in the application layer, plus
  catalog/template routing in `ui/catalog.py`, export dialogs/writers in
  `ui/exporters.py`, VNA/NEC/MMANA import parsing in `ui/import_actions.py`,
  project open/save workers in `ui/project_io.py`, autosave/recovery in
  `ui/recovery_actions.py`, element-optimizer dialogs in
  `ui/element_optimization_actions.py`, family/length/synthesis dialogs in
  `ui/optimization_actions.py`, and recent-list behavior in
  `ui/recent_actions.py`), with `NEC2C` auto-detected by the test
  configuration; the skip is the Windows-only console-hiding test on Linux.
  See
  [`archive/qa/QA_PASS_2026-11-20.md`](archive/qa/QA_PASS_2026-11-20.md).
- Main-window decomposition: **closed 2026-11-20** after the high-value
  extractions. `_build_ui`, `_build_actions`, and `retranslate` stay in the
  window deliberately; future work extracts a component only when a feature or
  defect touches it. The duplicated `QThread` lifecycles and `results_view.py`
  are likewise feature-driven, not an active standalone refactor.
- Release: **0.9.0** published on 2026-11-17 with the Touchstone `.s1p`
  round-trip, coaxial feed schematic (UX31), per-template material defaults
  (UX30), and the chart-cursor teardown fix. The tag-triggered CI run
  [`44103244393`](https://github.com/fsclavo/antenna-desk/actions/runs/44103244393)
  completed the wheel/sdist, Linux, Windows, and publish jobs; all six published
  assets and checksums were verified. See
  [`RELEASE_QA_0.9.0.md`](archive/releases/RELEASE_QA_0.9.0.md). **0.8.2** remains the previous
  release (2026-11-16, element-table header sizing fix). See
  [`RELEASE_QA_0.8.2.md`](archive/releases/RELEASE_QA_0.8.2.md).
- Known CI residue: Windows Python 3.11 runs acceptance, integration, and unit
  tests only. Its UI suite is excluded because PySide6/pyqtgraph can corrupt
  the native heap during view teardown; Windows 3.12/3.13 and Linux
  3.11–3.13 run the full UI suite. See
  [`ADR/0025`](ADR/0025-pyside6-version-pin.md). Do not weaken the remaining
  gates.
- Recent work: use `git log --oneline`; do not maintain a commit list in this document.
