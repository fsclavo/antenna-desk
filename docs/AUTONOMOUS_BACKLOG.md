# Autonomous execution backlog

**Date:** 2026-11-25
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

VR1 is a vertical-geometry enhancement implemented ahead of the remaining 1.1/1.2
items. It is bounded to one uniform droop, physical radial length, schema 61, and
family-optimizer coverage; the phased vertical is not included.

UX46–UX49 are a proposed presentation-only track for 3D pattern orientation.
Implement the three layers in the order UX46 → UX48 → UX49; UX47 is an
additional orientation aid after UX46 and must not block the overlay or the
camera link. UX47 is the plan mini-map, UX48 includes the large-array outline
mode, and the shared antenna color/feed marker is introduced in UX46 and reused
by UX47/UX48. They do not change the solver, domain model, project schema,
pattern storage, or report format, and add no 3D engine or dependency. See §3D
pattern orientation and comparison.

Completed rows are archived in [`archive/backlog-completed-2026-11-20.md`](archive/backlog-completed-2026-11-20.md).

| ID | Task | Size | Depends on | Acceptance |
|---|---|---|---|---|
| PF1 | ZIP project container and honest size contract | L | none | **Done 2026-11-24; manual validation passed.** A project that saves always reopens; design, runs, and optimizations are separate validated ZIP entries; per-entry/total limits apply on save and load; old runs are compacted by the save flow; oversized projects can be recovered design-only. No backward compatibility. Optional follow-ups are tracked as PF2 (streaming write) and PF3 (pattern-level lazy loading). See §PF1. |
| PF2 | Streaming container write | M | PF1 (closed) | **Proposed; optional.** Write and compact a container one entry at a time to the atomic destination or a bounded spool; stream copied runs from the source ZIP instead of materializing them. Preserve deterministic bytes, manifest hashes, limits, and the save/load invariant. See §PF2. |
| PF3 | Pattern-level lazy loading | L | PF1 (closed); pattern-entry ADR; PF2 soft | **Proposed; optional.** Split far-field patterns into validated per-run entries and load them only for the Pattern/3D/report consumers. Distinguish "not loaded/available" from "no pattern"; prune patterns independently. See §PF3. |
| B4 | Fan-dipole coupling calibration | M | measurement | A coupled-fan measurement is reproduced; no scalar correction is invented |
| C7h | Optional 6 m HexBeam band | S | C7c; published 6 m row | Add the published 6 m driver/reflector/tip-spacer row and vertical offset, with the same frame-fit validation, editor option, reports, and evidence note. No performance claim. |
| C7i | HexBeam feed harness and inter-band coupling | L | traceable harness data or measurement | Model the parallel coax feed harness/jumper lengths and inter-band coupling, or keep it explicitly unavailable; no invented values. Blocked until a source or measurement exists. |
| G27 | Optional transformer, common-mode choke, and coaxial loss models | L | G25; measured transformer insertion loss/core data; common-mode current model or measurement; manufacturer coax attenuation data | **Partially delivered.** EF7b added the measured transformer-loss table (`BalunLoss`); EF8 added the bounded feedpoint common-mode choke; ADR-0039 adds frequency-dependent feed-line attenuation with source-backed RG-58A/RG-213 tables, log-frequency interpolation, endpoint clamping, and a preflight range warning. The loss-accounting audit is also done (ADR-0040): the feed-chain sum must match the transducer gain, and NEC conductor/load losses including the feedpoint choke stay in the antenna power budget. Still deferred: analytical ferrite core loss with complex permeability/core geometry/winding/load data; frequency-interpolated `Zcm(f)` and shack-end choke placement; the remaining coax/choke evidence audit. All loss fields stay optional and off/zero by default; no invented loss numbers. |
| U6 | Documentation, help audit, and visual QA | S–M | U2–U5 | **Done 2026-11-24.** The user guide, roadmap, units spec, README, changelog, help tests, automated font-scaling/geometry checks, and the manual desktop light/dark/font-scaling checklist are complete. [`QA_PASS_2026-11-18.md`](archive/qa/QA_PASS_2026-11-18.md) and [`QA_PASS_2026-11-24.md`](archive/qa/QA_PASS_2026-11-24.md) record the gate and closure. |
| DL3 | Live tuning preview | M–L | none | **Partially done 2026-11-20.** Primary-dimension slider, coarse single-frequency preview, debounce/cancel, stale-result guard, preview badge, and apply/full-run path. Other managed dimensions and pattern preview remain. See §DL3. |
| DL5 | Support structures | M–L | ADR | **Done as narrowed 2026-11-24.** Yagi mast conductor plus 2–4 guy wires, geometry, BOM, scene, and schema 57–58. Conductive boom, tower, attachments, and structural hardware are deferred pending ADR/spike; no further 1.1 work. See §DL5. |
| DL6 | Stacked Yagi arrays | L | DL5 (soft), ADR | **First slice implemented 2026-11-25.** 2–4 identical Yagis, schema 69, form and catalog routes, per-port **Sources**, front elevation scene, reports/BOM, a real nec2c two-port test, splitter + phase-line specification, a co-simulated lossless TL network, and a bounded spacing/phase optimizer inside the maximum top-height envelope. A matched line loss plus a per-port mismatch correction is applied to realized gain, one shared mast/guy set is modeled across every level, and a beta/hairpin match is built at every driven element. A pure-Python N-port feed-network solver, antenna Y-matrix extraction, a user-facing Wilkinson divider mode, and per-level L/Pi/T matching networks are implemented. A folded driven element is copied to every level as geometry-only, with optional ideal per-level transformer ratios, matched branch loss, and a deterministic tolerance corner check in Wilkinson mode; a frequency-dependent non-ideal splitter/isolation model remains explicitly unavailable. Network mode includes the reference line. Evidence C; no gain claim. See ADR-0049 and §DL6. |
| DL7 | Native ground screen and cliff ground | M–L | ADR, spike | **Bounded slice implemented 2026-11-24; evidence B/C.** Cliff/second-medium far-field profile, schema 60, Site Ground dialog, and `GN`/`RP 2`/`RP 3` adapter. No external site reference is available; the native radial screen stays unvalidated for SWR and is not exposed. See ADR-0051, `spikes/dl7-ground-gn-spike.md`, and §DL7. |
| DL8 | Full terrain model | XL | DL7, validated model | **Post-1.2.** Only with a validated terrain model or a second engine; otherwise explicitly unavailable. See §DL8. |
| VR1 | Sloped vertical radials with uniform droop | M | ADR; next schema bump; vertical family | **Implemented 2026-11-24.** One uniform downward droop with physical radial length, ground-tip validation, schema 61, EN/ES editor/help, scene/report/live-tuning coverage, and a locked optimizer variable with a hard tip-clearance constraint. No per-radial angles, no performance claim, and the phased vertical is excluded. See §VR1 and ADR-0052. |
| UX45 | Shared Qt worker lifecycle | M–L | short lifecycle ADR; no active feature slice | **Done 2026-11-25.** All 14 `QThread` sites use `ui/workers/task_runner.TaskRunner`: one controller owns start, queued GUI delivery, generation/stale-result rejection, cancellation, completion, failure, bounded close, and detached teardown. Modal project I/O and end-fed use the same controller. An architecture guard forbids `QThread(` and `moveToThread(` outside the controller. See §UX45 and ADR-0053. |
| UX46 | 3D lobe orientation indicators | S | none | **Proposed 2026-11-25.** First layer. Max-gain ray, same-elevation back ray with F/B, antenna azimuth line/arrow, azimuth-ring labels, and Front/Back only for families with an explicit forward axis. Shared antenna color and feed marker. No solver, domain, schema, or report change. See §UX46. |
| UX47 | Plan mini-map in the 3D lobe | S | UX46 | **Proposed 2026-11-25.** Top-view inset with the canonical footprint, feed, antenna azimuth, and max-gain azimuth; theme-aware and hidden at minimum size. No synthetic family shape and no new engine. See §UX47. |
| UX48 | Schematic antenna overlay in the 3D lobe | M | UX46 | **Proposed 2026-11-25.** Opt-in "Show antenna"; feed-centered, uniform-scale canonical wireframe with a not-to-scale note; front/back only for explicit families; Auto/Full/Outline for large arrays; same color and feed marker as UX46. No solver, domain, schema, or report change; no new engine. See §UX48. |
| UX49 | Linked geometry/pattern 3D cameras | S | UX46; UX48 | **Proposed 2026-11-25.** Opt-in link syncs yaw/pitch only; zoom and pan stay independent; reset and model-change propagation; exact projection tests; Construction mode handled explicitly. No solver, domain, schema, or report change; no new engine. See §UX49. |
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
writing. The optional follow-ups are tracked as PF2 (streaming write) and PF3
(pattern-level lazy loading); PF1's container and save/load contract stay
unchanged. See [ADR-0050](ADR/0050-zip-project-container.md).

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

**Status:** proposed 2026-11-24; optional; not started. **Priority:** P3
memory and save-time performance. **Trigger:** the PF1 benchmark shows the
copy-entry save path at 174 MB peak RSS and the materialized path at 1,614 MB
for the generated four-run project; `PreparedProject.payload` still holds the
whole container in memory.

**Current cost:** `prepare_payload()` builds every entry, `_build_container()`
calls `_zip_bytes(entries)` once to learn compressed sizes and a second time
with the manifest to produce the final bytes, and `write_payload()` validates
those bytes through `io.BytesIO` before `_atomic_write()` writes them. Peak
memory therefore includes all entry payloads plus the intermediate and final
containers. Copied run entries are read into `bytes` by `copy_entries()` even
though they are not parsed.

**Goal:** write and compact a container directly to the atomic destination (or
to a bounded temporary spool) one entry at a time, so peak memory scales with
the largest entry and I/O buffers rather than the whole history. The saved file
must remain byte-identical to the current deterministic writer and satisfy the
same limits, manifest hashes, and save/load invariant.

**Recommended design:**

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
2. Add a container writer that accepts entries as streams/chunks, not only
   `bytes`. Copied run entries should stream from the source ZIP to the spool
   or final ZIP while the existing manifest CRC/SHA is verified, without
   materializing the full entry.
3. Replace the `PreparedProject.payload: bytes` contract with a prepared spool
   handle that exposes `compressed_bytes`, `expanded_bytes`, `entry_count`,
   `limits`, `write_to(path)`, and a cleanup path. If a compatibility slice is
   preferred, keep the in-memory path behind a documented size threshold and
   use the spool above it; do not maintain two different output formats.
4. Enforce per-entry, entry-count, expanded, and container limits while
   streaming. If the compressed container exceeds `MAX_CONTAINER_BYTES`,
   abort, unlink the temporary file, and raise `ProjectTooLargeError` without
   touching the previous project. Derive the exact save/load invariant test
   from this path.
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
PF3 benefits from this path but does not require it.

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

**Likely files:** `persistence/container.py`, `application/project_payload.py`
(prepared-spool contract), `application/ports/project_repository.py`,
`ui/project_io.py`/save workers if the prepared type changes,
`scripts/benchmark_project_io.py`, and the persistence/container tests.

## PF3 — Pattern-level lazy loading

**Status:** proposed 2026-11-24; optional; not started. **Priority:** P3 memory
on open/select and report responsiveness. **Trigger:** PF1 lazy loading is per
run, not per pattern. The benchmark shows a selected 2° run with five patterns
at about 682 MB peak RSS (roughly 400 MB of domain objects), while impedance,
SWR, and currents are much smaller and are usually needed first.

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
**Release:** unassigned; optional maintenance after PF2 or after the current
1.2 work if open/select memory becomes a release blocker.

**Likely files:** `persistence/container.py`, `persistence/schema.py` (run and
pattern payloads), `application/project_session.py`,
`application/ports/project_repository.py`, `ui/main_window.py`,
`ui/widgets/results_view.py`, pattern/3D views, `reporting/`, and the
persistence, session, UI, reporting, and benchmark tests.

**Recommended sequence (PF2/PF3):**

1. Keep PF2 and PF3 in separate change sets; do not bundle either one with an
   antenna or UI feature.
2. PF2 can start first: it is a self-contained writer change with a
   byte-identical oracle, and it reduces save memory before PF3 adds more
   entries.
3. PF3 must not start before its pattern-entry ADR is accepted. PF2 is a soft
   dependency, so PF3 may run first only if open/select memory becomes the
   release blocker.
4. Migrate PF3 consumers one at a time (Pattern tab, 3D view, comparison,
   reports, pattern-bearing CSV) and keep the fully materialized path as a
   parity oracle until the last consumer migrates.
5. Benchmark both items with `scripts/benchmark_project_io.py`; record peak
   RSS and wall time for open, select one run, materialized save, copy-entry
   save, compact, and design-only save.
6. Do not change PF1's container version, entry order, compression level, or
   deterministic output in either item without an explicit ADR; keep the
   save/load invariant test green.

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
product decision. The DL6 first slice is implemented (form, schema 63, catalog,
per-port Sources, scene, reports, the splitter/phase-line feed specification,
one shared mast/guy set, and the bounded spacing/phase optimizer); per-level
matching remains.

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
optional coarse elevation-cut pattern preview, and apply/full-run path are
implemented. The selector also covers managed angles, counts, and
transformer/feed ratios. **Apply and simulate** closes the dialog and starts the
full simulation.

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
domain model, schema 69, both catalog routes, the embedded Yagi/stack form,
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
per-level transformer ratios, matched branch loss, and a deterministic
tolerance corner check in Wilkinson mode. A frequency-dependent non-ideal
splitter/isolation model remains a follow-up. Evidence is C and no
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
  validated; the Wilkinson divider mode exposes them in schema 69, the editor,
  reports, and the construction-sheet feed-network table, with a
  reconstructed pattern, optional per-level L/Pi/T matching networks, optional
  ideal transformer ratios, matched branch loss, and a deterministic tolerance
  corner check; the conductor BOM remains conductor-only.
- The optimizer searches level spacing and either the ideal phase step or the
  line increment inside the maximum top-height envelope; the level count, base
  Yagi, and amplitude ratio stay context. In Wilkinson mode it rebuilds the
  feed-network spec for each candidate, including the per-level networks.

**Remaining work:** a frequency-dependent splitter S-parameter/isolation model. The [feed-network spike](spikes/dl6-feed-network-spike.md) rejects
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

## 3D pattern orientation and comparison (proposed 2026-11-25)

**Status:** proposed presentation-only track. Implement the three layers in the
order **UX46 → UX48 → UX49**; do not start UX48 or UX49 before UX46 is green.
UX47 is an independent orientation aid after UX46 and is not a prerequisite for
UX48/UX49. Each slice must leave the full gate green. **Priority:** P2 UX, after
the current DL6/DL3 slice closes. **Release:** unassigned; candidate for the 1.2
visualization track.

**Motivation:** The 3D lobe answers "how strong" but not "where relative to the
antenna". The 2D azimuth polar already draws an antenna line; the 3D view has
only axes, an optional ground ring, and a maximum-gain marker. The user needs a
clear visual front/back and lobe takeoff direction without a numerical-precision
claim. The geometry 3D view and the pattern 3D view already share a right-handed,
Z-up frame and the same orthographic projection; their default camera angles
differ (42°/24° vs 38°/26°). This track makes that relationship legible.

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
  "Back".
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

**Scope:** opt-in camera synchronization between the geometry 3D view and the
3D lobe.

- Add a "Link 3D views" checkable action in the geometry controls row (or a
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
- **Export decision.** `GeometryView.three_d_image()` currently uses the live
  camera. Decide and document whether the construction sheet uses the live
  linked camera or a fixed camera. If fixed, add a regression test; do not change
  exported report output silently.

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

- Schema: **69**; container version 1.
- Full gate: **4,325 passed, 1 skipped** on 2026-11-24 after the QA and
  technical-debt closure, main-window extractions, save/load size invariant
  fix, PF1 container, lazy open/save/compact, PreparedProject, DL7 site ground,
  and VR1 radial droop (typed simulation specs, pattern presets, and
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
- Known CI residue: Windows Python 3.11 runs acceptance, integration, and unit
  tests only. Its UI suite is excluded because PySide6/pyqtgraph can corrupt
  the native heap during view teardown; Windows 3.12/3.13 and Linux
  3.11–3.13 run the full UI suite. See
  [`ADR/0025`](ADR/0025-pyside6-version-pin.md). Do not weaken the remaining
  gates.
- Recent work: use `git log --oneline`; do not maintain a commit list in this document.
