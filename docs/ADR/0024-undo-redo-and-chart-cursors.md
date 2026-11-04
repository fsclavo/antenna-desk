# ADR-0024 — Project Undo/Redo and chart cursors

- **Status:** Accepted
- **Date:** 2026-11-01
- **Supersedes:** none

## Context

The project model is immutable, which makes document-level Undo/Redo
straightforward. However, the main window also owns forms, selection state,
simulation caches, and persisted simulation runs. The results charts had no
retained series data, so a nearest-point cursor could not be implemented
without restructuring part of `ResultsView`.

## Decision

1. Use Qt's `QUndoStack` for Undo/Redo.
2. Store `ProjectSnapshot` values containing the editable project and selected
   design; compare snapshots without timestamps, selection, or simulation runs.
3. Push one command per successful user action through a `history_action`
   decorator and a centralized `_record_history` method.
4. Keep completed simulation runs outside the undoable snapshot. On restore,
   merge the current runs for designs that still exist. Running a simulation or
   compacting its history is therefore not undone by Ctrl+Z.
5. Track a clean project signature and clean run identifiers so save/undo/redo
   dirty state remains correct.
6. Reconcile form state explicitly: project undo prompts before discarding
   unapplied form changes; focused text editors keep their native undo.
7. Implement a reusable `ChartCursor` for pyqtgraph charts. It owns a vertical
   line, nearest-point markers, and a floating readout, uses a rate-limited
   scene mouse signal, ignores bounds for auto-range, and clears when series
   are replaced.
8. Retain chart series in `ResultsView` after every render so the cursor can
   query the current data. Angular charts support 0–360 wrap; currents use
   segment index; measurements can show measured and simulated points.

## Consequences

Positive:

- Undo/Redo covers all user-visible document edits consistently.
- Completed simulation history survives design undo/redo.
- Cursors are shared across all result charts and testable independently.
- No new dependency is required.

Limitations:

- Simulation execution and history compaction are not undoable.
- Undo command labels are captured at action time; they are not dynamically
  retranslated for historical commands.
- Very large project histories are bounded by the undo limit.
