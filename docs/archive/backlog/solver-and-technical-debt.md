# Historical backlog — solver and technical debt

> **Historical design notes, captured 2026-11-20.** Not current
> guidance. Current status: [`../../STATUS.md`](../../STATUS.md); active
> queue: [`../../AUTONOMOUS_BACKLOG.md`](../../AUTONOMOUS_BACKLOG.md).

## Solver runtime notes (2026-11-08)

The 60 s default was measured against a four-element phased vertical array,
31-point sweep, five pattern snapshots, finite ground:

| Case | Wires | Segments | Wall time |
|---|---:|---:|---:|
| 4 verticals × 4 radials | 20 | 122 | 0.46 s |
| 4 verticals × 36 radials | 148 | 890 | 25.3 s |

The 36-radial case also returned `partial` with negative input resistance and
an absorbing-source warning. Raising the timeout is not a fix for that
numerical result; E4 must diagnose it separately.

E4 found that the quarter-wave radial screens overlap: the 4×36 case had 267
wire crossings. Halving the radial length, or using 2 m radials, removed the
crossings and completed. Doubling the spacing without changing the radial
length also removed crossings, but some frequencies still showed a negative
primary resistance because ideal phase sources can exchange power between
ports. The phased-vertical editor now warns about overlapping screens; the
ideal-source behavior is documented and exposed through the **Sources**
results.

Engineering conclusions:

- **Timeout:** 60 s leaves only about 2.4× headroom over the 890-segment case;
  180 s is a more reasonable default (~7×). Expose an override rather than
  making every simulation wait three minutes when a geometry is actually stuck.
- **Single solve:** do not split a phased array by element. The elements are
  mutually coupled and NEC2C solves one joint matrix. Frequency and pattern
  points inside one deck should not be split initially either; that duplicates
  geometry, matrix setup, and memory.
- **Parallelism:** only independent jobs are candidates: optimizer candidate
  evaluations first, band analysis second. A bounded pool of threads launching
  separate `nec2c` subprocesses is simpler than process-level model
  serialization.
- **Limits:** every worker has its own NEC matrix. Cap workers by both CPU and
  memory, terminate all processes on cancellation, keep result ordering
  deterministic, and use a per-worker timeout.


## Technical debt pass (2026-11-08)

- The UI mypy pass now rejects unused ignores, redundant casts, and
  unreachable code. Four obsolete pyqtgraph suppressions were removed, two
  dead feed-wire checks were deleted, and one incorrect PySide6 stub was
  handled with an explicit cast.
- `optimizer_availability` uses `assert_never`, so a new parameter type fails
  type checking instead of silently falling through to an unsupported result.
- Fixed band-analysis cancellation during a solver run: the next unprocessed
  band is recorded as cancelled, so a truncated sequential or parallel batch is
  reported as partial rather than completed.
- Added batch-engine fallback and cancellation tests, plus cancellation
  coverage for sequential and parallel band analysis.
- Added direct tests for the Qt worker adapters (100% coverage), the polar
  pattern paint paths (45% to 98%), and the solver locator fallbacks (69% to
  98%).
- Covered the six remaining element-optimizer entry points (`moxon`, `loop`,
  `vertical`, `inverted_v`, `ringo`, and `zs6bkw`) and the public save/open
  lifecycle: current-path save, Save As suffix/cancel, no-project errors,
  open/cancel/error, and the three unsaved-changes answers.
- Covered the data exports (CSV, sources CSV, pattern CSV, HTML, PDF, pattern
  PNG), the four geometry formats (PNG, SVG, PDF, DXF), and solver discovery
  success/error.
- At the end of that pass, `main_window.py` coverage was **76%** (from 69%)
  and the full suite was **88% total** with 346 fewer missed statements.

