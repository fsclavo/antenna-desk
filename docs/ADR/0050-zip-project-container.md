# ADR-0050 — ZIP project container and honest size contract

- **Status:** accepted 2026-11-20; slice 1 implemented 2026-11-20 (PF1)
- **Date:** 2026-11-20
- **Supersedes:** [ADR-0021](0021-compressed-project-files.md)
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
4. Slice 2 will make `prepare_payload()` return an immutable `PreparedProject`
   with payload, compressed bytes, expanded bytes, entry count, and limits. A
   successful save must always produce a file `load()` accepts. Slice 1 keeps
   the existing bytes API and already enforces the limits.
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

Remaining for slice 2: lazy run loading/`ProjectSession`, design-only recovery,
save-design-only UI, and physical compaction through entry removal.
