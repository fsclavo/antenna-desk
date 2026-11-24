# ADR-0050 — ZIP project container and honest size contract

- **Status:** accepted 2026-11-20; implemented and closed 2026-11-24 (PF1)
- **Schema note:** original container used schema 59; ADR-0051 adds schema 60
  with the optional project-level `site_ground` field; ADR-0052 adds schema 61
  with the optional vertical `radial_droop_deg` field.
- **Date:** 2026-11-20
- **Supersedes:** [ADR-0021](0021-compressed-project-files.md)
- **Follow-ups:** [`AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md) §PF2
  (streaming container write) and §PF3 (pattern-level lazy loading)
- **Related:** `docs/AUTONOMOUS_BACKLOG.md` §PF1

## Context

On 2026-11-20 a 56.9 MB gzip project expanded to 409.1 MB. It was written
successfully but could not be reopened: save checked only the 64 MiB
compressed limit, while load also enforced the 256 MiB expanded limit. The
project held six large runs; the design itself was a few kilobytes.

The gzip envelope has three structural problems:

1. The compressed size is not a safe proxy for the expanded size. At the
   observed 7.19:1 ratio the effective compressed limit was about 35.6 MB.
2. Opening materializes every run, even when the user only needs one design.
3. There is no per-entry boundary, so one oversized run can make the whole
   project unopenable.

The application has not shipped to users yet, so no legacy project files need
to be supported.

## Decision

1. Replace the single gzip JSON envelope with a **versioned ZIP container**
   (container version 1, schema version 59). Keep one portable
   `.antennadesk` file and atomic saves.
2. Separate `manifest.json`, `project.json`, `designs/<id>.json`,
   `runs/<id>.json`, optional raw solver entries, and
   `optimizations/<id>.json`. Validate every entry independently.
3. Enforce one set of limits on save and load: container bytes, total
   expanded bytes, manifest bytes, per-entry bytes, entry count, and path
   bytes. Do not trust manifest-declared sizes; read bounded streams and
   verify CRC32/SHA-256.
4. `prepare_payload()` returns an immutable `PreparedProject` with payload,
   compressed bytes, expanded bytes, entry count, and limits. A successful save
   must always produce a file `load()` accepts.
5. Load the project, the selected design, and the latest retained run at open
   time. Load older runs and optimizations on demand through an application
   `ProjectSession`/`ProjectResultStore`; keep the domain `Project` immutable.
6. Offer **Compact history and save** and **Save design only** when a save
   exceeds a limit. Never write an unopenable file. Opening an oversized
   project offers design-only recovery without overwriting the original.
7. Drop gzip/plain-JSON input and schema 58 migration support. Reject them
   with a clear `ProjectFormatError`.
8. Reuse `Project._retained_simulation_runs()` as the retention policy:
   latest single run per design plus all runs of the latest batch.

## Consequences

Positive:

- The save/load contract becomes enforceable per entry and on both sides.
- Large histories no longer need to be materialized to open a design.
- Compaction removes physical entries and reduces both compressed and
  expanded size.
- A zip-bomb, traversal, duplicate-entry, symlink, or CRC mismatch is rejected
  before the domain model is built.

Limitations and costs:

- This is a breaking format change; there is no legacy reader.
- `ProjectRepository`, `SaveProject`, `ProjectIO`, bundle export/import,
  recovery, and the save UI must change together.
- The existing gzip tests and migration registry are removed or replaced.
- The example project and every committed fixture must be regenerated in
  schema 59.
- Lazy loading adds a session/cache layer above the immutable domain model.

## Implementation status (2026-11-20)

Slice 1 is implemented:

- deterministic ZIP container v1 with `manifest.json`, `project.json`,
  `designs/`, `runs/`, optional raw text entries, and `optimizations/`;
- schema 59, no gzip/plain-JSON reader, no migrations;
- container, total, manifest, per-entry, entry-count, and path limits on save
  and load;
- bounded entry reads with manifest size, CRC32, and SHA-256 verification;
- path, duplicate, case-collision, symlink, encryption, and compression
  validation;
- atomic writes and a save/load invariant test;
- structured `ProjectPayloadTooLargeError` so the save flow offers compaction
  and retry;
- example project regenerated in the current container.

Slice 2 has started: opening uses a manifest-indexed `ProjectSession`; only
the selected design's latest run or batch is materialized, a failed oversized
open offers design-only recovery, and **File → Save Design Only...** writes
metadata and designs without runs or optimization summaries. `PreparedProject`
is now the repository return type and carries the payload, compressed and
expanded sizes, entry count, and limits. Saving and compaction copy unchanged
run entries from the source container, serialize only new runs, and reopen the
session after writing. The remaining optimization is streaming the container
write instead of holding its bytes in memory, plus any pattern-level lazy
loading needed by reports or visualization.
