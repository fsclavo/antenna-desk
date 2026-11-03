# ADR-0021 — Lossless compressed project files

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none
- **Updates:** [ADR-0020](0020-higher-pattern-storage-budget.md)

## Context

ADR-0020 raised the project limits to accommodate more pattern data, but the
user asked whether compression could be applied on the fly without removing
data. Project files are JSON with many repeated keys and numeric arrays. They
compress extremely well:

| Run | JSON | gzip level 6 |
|---|---:|---:|
| G5RV, 200 points, 13 snapshots at 5° | 12.0 MB | 1.8 MB |
| G5RV, 200 points, 5 snapshots at 2° | 21.7 MB | 3.3 MB |
| G5RV, 200 points, 9 snapshots at 2° | 35.5 MB | 5.6 MB |
| G5RV, 200 points, 9 snapshots at 1° | 127 MB | 19.9 MB |

The same data can therefore be stored in a much smaller file without dropping
fields.

## Decision

1. Serialize native project documents as **compact JSON** (no indentation).
2. Compress the UTF-8 bytes with **gzip level 6** before writing the
   `.antennadesk` file. Use `mtime=0` for deterministic output.
3. Decompress transparently on load. If the file does not start with the gzip
   magic bytes, parse it as plain JSON so projects written by older versions
   still open.
4. Apply the **32 MiB hard limit** and **20 MiB warning** to the compressed
   on-disk size, not the uncompressed JSON size.
5. Estimate the planner budget against the compressed size using a
   conservative **6.0×** compression ratio. The 24 MiB budget therefore
   corresponds to roughly 144 MB of JSON.
6. Keep all fields. Compression is lossless and does not change the schema or
   the in-memory model.

## Consequences

Positive:

- A 200-point G5RV with 13 band snapshots at 2° is about 8 MB instead of
  ~52 MB uncompressed.
- Nine band snapshots at 1° fit in about 20 MB compressed; the 3D lobe gets
  32,851 points per pattern.
- Existing plain-JSON projects continue to load.
- The save/load path remains a single file operation.

Limitations:

- Save and load spend CPU on gzip. The user explicitly accepts slower runs for
  more data; typical projects compress or decompress in well under a second.
- The `.antennadesk` file is no longer directly readable as text. Standard
  `gzip` tools can decompress it.
- The 6.0× planner ratio is conservative but not a guarantee for every model.
  The actual save still enforces the hard limit.
- The solver output limit remains 50 MB. Nine 1° snapshots are near that limit
  for a large model; denser patterns or more snapshots can still exceed it.

## Follow-ups

- Add a compression-level or "smallest file" preference.
- Exclude or truncate raw solver output for very large runs.
- Store currents only at pattern snapshots for dense sweeps.
- Revisit the planner ratio if the persisted schema changes substantially.
