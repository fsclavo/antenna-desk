# ADR-0020 — Higher project storage budget for pattern-rich runs

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none
- **Updates:** [ADR-0017](0017-simulation-storage-budget.md),
  [ADR-0019](0019-pattern-snapshots.md)
- **Updated by:** [ADR-0021](0021-compressed-project-files.md)

## Context

ADR-0019 decoupled the far-field pattern from the impedance sweep and added
band-aware snapshots plus 5/9/13 frequency choices. The project budget was still
9.5 MB, so a 200-point G5RV with 13 snapshots had to drop to a 10° pattern.
The user asked for more frequencies and better angular resolution even when the
run takes longer. The limiting factor is persisted project size, not solver
time: the 13-snapshot 5° run takes about 12 MB and still completes in a few
seconds.

## Decision

Raise the storage limits:

- pattern/run budget: **24 MiB** compressed;
- save warning: **20 MiB** compressed;
- hard project limit: **32 MiB** compressed.

ADR-0021 adds lossless gzip compression, so the effective JSON capacity is
roughly six times larger than these numbers.

Keep the solver output limit at 50 MB. Spend the extra space on pattern data
rather than on more projected sweep points:

- with gzip, a 200-point G5RV with 13 snapshots uses a 2° pattern and about
  8 MB compressed;
- 17 snapshots use 2° and about 10 MB; 21 snapshots use 2° and about 13 MB;
- nine band snapshots use 1° and about 20 MB compressed;
- five snapshots also use 1° and about 13 MB compressed;
- nine snapshots at 2° would be about 35 MB, above the new limit, so the budget
  still coarsens to 5°.

The save warning remains a confirmation, not a block. The hard limit still
prevents unbounded project files.

## Consequences

Positive:

- Selecting 13 pattern frequencies no longer forces a 10° pattern; 5° fits.
- Five snapshots can use a 2° pattern for detailed lobe inspection.
- Band-aware snapshots remain the default, so multiband antennas show their
  bands without sacrificing angular detail.
- The solver output limit is unchanged; the extra storage is mostly normalized
  far-field data.

Limitations:

- Project JSON files can now reach 32 MiB. Saving and opening them is slower
  than the old 10 MB limit.
- Thirteen snapshots at 2° (about 50 MB) still do not fit.
- Raw solver output and currents at every sweep frequency remain stored. They
  are the next candidates for compression or selective storage.
- The user must still trade frequency count against angular resolution through
  the **Pattern frequencies** control.

## Follow-ups

- Compress far-field records or store only the fields needed for the 3D lobe.
- Store currents only at pattern snapshots for very dense sweeps.
- Exclude or truncate raw solver output for large runs.
- Make the storage budget configurable in preferences.
