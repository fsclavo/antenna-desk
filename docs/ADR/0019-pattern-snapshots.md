# ADR-0019 — Far-field pattern snapshots decoupled from the impedance sweep

- **Status:** Accepted
- **Date:** 2026-11-03
- **Supersedes:** none
- **Updated by:** [ADR-0020](0020-higher-pattern-storage-budget.md)

## Context

ADR-0017 introduced a project-size budget that coarsens the far-field pattern
when a run would be too large. It listed a follow-up: split a wideband
impedance/SWR run from a separate pattern run at selected frequencies.

That follow-up became necessary when a G5RV sweep with 200 frequencies and an
Auto pattern resolution was reduced to a 30° pattern. The 3D lobe then had only
52 sample points per frequency and looked like a polyhedron, while the same
antenna with a five-point sweep used a 5° pattern and looked smooth. The
impedance sweep density was forcing the pattern resolution down even though the
user only views one pattern at a time.

The run still has to fit the project storage limit, and the raw NEC output is
part of the saved project. Computing a 5° pattern at all 200 frequencies would
produce tens of megabytes of far-field data.

## Decision

1. Add `pattern_frequencies_hz` to `SimulationSpec`. It is a tuple of snapshot
   frequencies snapped to the frequency-plan grid. An empty tuple preserves the
   previous behavior: one pattern per sweep frequency.
2. When the main window builds a spec for a plan with more than
   `DEFAULT_PATTERN_SNAPSHOT_COUNT` points, it selects a small set of snapshot
   frequencies:
   - **Auto (bands)** picks one frequency per amateur band inside the plan
     (160 m through 6 m), using the design frequency when it falls inside a
     band.
   - A narrow single-band plan is filled with evenly spaced snapshots so it
     still gets at least five pattern cuts.
   - The custom panel also offers fixed **5**, **9**, **13**, **17**, and
     **21** snapshot counts; the budget chooses the finest angular step that
     fits that count.
   Plans with five or fewer points keep a pattern at every frequency.
3. Write one NEC deck with two kinds of frequency blocks:
   - the full `FR` sweep followed by `XQ`, which computes impedance and
     currents at every sweep point without a pattern;
   - one single-frequency `FR` block with `EX` and `RP` per snapshot.
   This keeps one solver invocation and one raw output.
4. Normalize by merging the snapshot blocks into the sweep results. The
   resulting `SimulationResult` has one `FrequencyResult` per sweep frequency.
   Only snapshot frequencies carry `far_field`; the rest keep impedance,
   SWR, and currents.
5. Populate the pattern tab from frequencies that actually have a pattern.
   The currents tab continues to list every sweep frequency. Pattern CSV and
   HTML/PDF reports use the snapshot frequencies.
6. Estimate the persisted project size from two separate terms:
   - the impedance/current sweep: `frequency_count`;
   - the pattern snapshots: `pattern_frequency_count`.
   The budget may choose the finest pattern step that fits this combined
   estimate, but it never reduces the impedance sweep to make room for a
   pattern.
7. Keep the existing behavior when the pattern does not fit even at the
   coarsest step: disable the far-field request and keep the sweep.
8. Apply the policy centrally in the main window's simulation-spec fit, not in
   individual family builders. Every current and future family inherits the
   same snapshot selection, resolution budget, compression, and 3D LOD.

## Consequences

Positive:

- A 200-point G5RV sweep now uses one snapshot per HF band (nine snapshots)
  at 5° instead of a 30° pattern at every frequency. The user can choose 13
  snapshots at 5° or five snapshots at 2°. ADR-0020 raised the storage budget
  to make these combinations fit.
- The 3D lobe keeps the same visual resolution regardless of impedance sweep
  density.
- The measured project for the 200-point G5RV case is about 7.4 MB, below the
  10 MB hard limit and below the 8 MB warning threshold.
- Shorter sweeps also benefit: a 31-point design can use 5° patterns at five
  snapshots instead of a coarser pattern at every point.

Limitations:

- Directivity, realized gain, and maximum-gain summaries are computed only at
  snapshot frequencies. A narrow lobe between snapshots is not represented.
- The pattern tab lists snapshot frequencies, not every impedance frequency.
- More snapshots can force a coarser angular step under the same storage
  budget. The status line shows both the chosen step and the snapshot count.
- Currents remain stored at every sweep frequency. This is the dominant cost
  for very dense sweeps.
- Optimization and synthesis dialogs build their own specs. They must opt into
  snapshots explicitly; the main window policy is not global.
- The raw solver output still contains all frequency blocks. Excluding or
  compressing it remains a future optimization.

## Follow-ups

- Allow the user to choose the pattern snapshot frequencies or count.
- Store currents only at snapshot frequencies when the sweep is very dense.
- Compress or omit raw solver output for large projects.
- Add band-aware snapshot selection instead of evenly spaced frequencies.
