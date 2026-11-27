# ADR-0057 — Streaming project-container write

- **Status:** accepted 2026-11-27; implemented
- **Date:** 2026-11-27
- **Supersedes:** none
- **Related:** ADR-0050, `docs/AUTONOMOUS_BACKLOG.md` §PF2

## Context

ADR-0050 introduced the deterministic ZIP project container. The manifest is
written first and lists each entry's compressed size, CRC32, and SHA-256, so the
writer must know every entry's compressed size before it can write the manifest.

The first implementation materialized every entry, compressed the entry set once
to learn the sizes, and compressed it a second time with the manifest. It then
held the final container in `PreparedProject.payload` until the atomic write.
For the generated four-run benchmark project, the copy-entry save path peaked at
174 MB RSS and the materialized path at 1,614 MB. Copied run entries were also
read completely into `bytes` even though they were only being moved from one
container to another.

The save path must keep one portable file, deterministic bytes, the existing
limits, manifest hashes, and atomic replacement. A format change is not
justified for a memory optimization.

## Decision

Use a two-phase writer with a bounded temporary spool.

1. **Phase 1 — stage.** Write each entry, in manifest order, to a temporary ZIP
   in a private temporary directory. For in-memory entries, write the bytes and
   compute CRC32/SHA-256. For copied runs, stream the source entry in bounded
   chunks, enforce the per-entry and total limits while reading, and compute the
   same hashes. Close the stage and read each entry's `compress_size`.
2. **Phase 2 — finalize.** Build `manifest.json` from the staged metadata, then
   write a fresh deterministic ZIP with the manifest first and the entries in
   sorted path order. Entries are streamed from the stage, so peak memory is the
   largest entry plus one copy buffer, not the whole history.
3. **Prepared payload.** `PreparedProject` carries a `PreparedSpool` pointing at
   the finalized temporary file. Its `compressed_bytes` is the exact file size,
   and `copy_to()` streams the file into the destination's temporary file before
   `os.replace()`. The in-memory `payload` field remains only as a compatibility
   path for small callers and test doubles; it produces the same ZIP format.
4. **Limits and failures.** Per-entry, entry-count, path, expanded, manifest,
   and container limits are checked while staging or finalizing. Any failure
   removes the spool and leaves the previous project untouched. The destination
   is only replaced after a complete fsync and ZIP validation.
5. **Run conversion.** Project metadata and designs are converted once; each
   simulation run is converted and serialized separately instead of building a
   second full `ProjectPayload` with every run.

The manifest-first, sorted-entry, fixed-timestamp, ZIP-deflate level 6 format is
unchanged. A byte-for-byte test rebuilds the container with the old
`writestr` sequence and compares it with the streamed output.

## Alternatives considered

- **Write the manifest last in one pass.** Simpler, but changes the ZIP byte
  order and the deterministic writer contract. It would require a format
  decision and golden-byte churn for no user-visible benefit. Rejected.
- **Copy raw deflate streams from the stage into the final ZIP.** Avoids the
  second compression pass, but requires constructing local file headers and the
  central directory by hand. The resulting bytes would be harder to audit and
  more fragile than the standard library writer. Rejected.
- **Keep the whole container in memory below a threshold.** Allowed only if it
  does not create a second output format. The production path always uses the
  spool; the in-memory path is retained for callers that already hold bytes.
- **Split patterns into separate entries.** That is PF3 and changes the
  container schema; it is not part of this decision.

## Consequences

Positive:

- Copy-entry save and compaction no longer scale with the full run history.
- The final container is still byte-identical, deterministic, and validated by
  the same reader.
- Exact compressed and expanded sizes remain available to the save dialog.
- Copied runs are verified against the source manifest while streaming.

Costs and limitations:

- A save uses temporary disk space for the stage and the finalized container,
  plus the destination copy.
- The materialized save path still pays for `ProjectSession.materialize()` and
  the domain run objects; the writer is no longer the dominant cost there.
- Temporary spool cleanup is an explicit lifecycle concern. Callers close the
  prepared payload after writing; the temporary-directory owner also cleans up
  on garbage collection.

## Implementation status

Implemented 2026-11-27 in `persistence/container_writer.py`,
`persistence/container.py`, and `application/project_payload.py`. Tests cover
byte-identical output (including a stream larger than the copy chunk), copied
runs without materialization, exact sizes, spool cleanup, limit failures, and
the atomic-replace invariant. The benchmark recorded 45 MB peak RSS for the
copy-entry save and compact paths, down from 174 MB and 84 MB.
