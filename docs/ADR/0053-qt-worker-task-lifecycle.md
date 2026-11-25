# ADR-0053 — One lifecycle owner for Qt worker tasks

- **Status:** accepted 2026-11-24; implemented in the UX45 maintenance track
- **Date:** 2026-11-24
- **Related:** UX45, `docs/AUTONOMOUS_BACKLOG.md` §UX45,
  `docs/archive/qa/QA_PASS_2026-11-24.md`

## Context

The UI had fourteen copies of the same `QThread` setup. Ten dialogs, three
main-window workers, and the modal project-I/O helper each created a thread,
moved a worker into it, connected the terminal signals, quit the thread, and
deleted the objects in a slightly different way.

The copies had already diverged:

- close-time waits ranged from `0` to `5_000` ms, and the modal wrappers used
  an unbounded `wait()`;
- some sites deleted the worker through `thread.finished`, others through a
  dialog `_cleanup` slot, and some kept only local references;
- double-start protection and cancellation text lived in each dialog;
- only `LiveTuningDialog` guarded stale results with a request generation.

The live-tuning cross-thread defect fixed in 0.10.1 was one instance of the
missing lifecycle contract. A future fix would not propagate to the other
copies.

## Decision

Introduce one controller, `antennadesk.ui.workers.task_runner.TaskRunner`, that
owns the `QThread`, the worker, and the single cleanup path for one task at a
time. Keep the existing worker classes; the controller coordinates lifecycle
only.

### Public contract

- `start(worker, *, success_signal="finished", cancel=None) -> bool`
  - refuses to start while a task is active, emits `rejected(reason)`, and
    returns `False`;
  - moves the worker to a new `QThread` and emits `started`;
  - the worker must expose a one-object success signal (default `finished`) and
    a one-object `failed` signal; the controller does not reinterpret either.
- `is_running` is `True` only between `start` and the terminal transition.
- `cancel()` forwards to the task's cancel handle. It does not stop the thread;
  the worker decides how to finish, so partial results stay available.
- `close(timeout_ms=None) -> bool` cancels, quits, and waits at most the
  configured timeout (default 2 s). It returns `True` when the thread stopped,
  or `False` when it was detached. A detached thread keeps running, deletes its
  worker and itself when it finishes, and never reaches the controller again.
  `close()` emits `cancelled` and `finished` after teardown; it does not emit a
  worker result.
- Terminal signals: `succeeded(object)`, `failed(object)`, `cancelled()`, and
  `finished()`. `is_running` is already `False` when they are emitted, so a
  handler may start the next task. The controller joins the thread for up to
  1 s after `QThread.finished`; if that join expires, it detaches the task and
  reports `cancelled` instead of handing a result to the GUI.
- Every worker-to-controller signal is delivered through a queued connection
  to the GUI thread. A per-task generation makes a late result from an
  abandoned task harmless.

### Semantics

| Situation | Thread | Worker | Controller |
| --- | --- | --- | --- |
| success | quit, deleted | `deleteLater` in its thread | `succeeded`, `finished` |
| failure | quit, deleted | `deleteLater` in its thread | `failed`, `finished` |
| cancel | worker finishes and quits | `deleteLater` in its thread | worker result, then `finished` |
| double start | untouched | untouched | `rejected`, no overlap |
| close within timeout | stopped and deleted | `deleteLater` in its thread | `cancelled`, `finished` |
| close timeout | detached, self-deletes | self-deletes | `cancelled`, `finished`, `False` |

### Blocking adapter

`project_io` and the end-fed convergence check must stay modal. They use
`run_worker_blocking()`, which is built on `TaskRunner` and a `QEventLoop`; it
does not create a second thread lifecycle. It returns the worker result,
re-raises a `BaseException` sent through `failed`, and raises `ValueError` for
a string failure.

### Migration and guard

- Migrate one site per change set, easiest first.
- Add an architecture guard that forbids `QThread(` and `moveToThread(`
  outside `ui/workers/task_runner.py`. During the migration the guard carries a
  shrinking allowlist; each migrated site is removed from it.
- Do not change solver, progress semantics, dialog layouts, or user-visible
  text in this track.

## Consequences

Positive:

- One place defines thread ownership, queued delivery, generation checks,
  bounded close, and deletion.
- The Windows teardown class of defects has one code path to fix.
- New UI surfaces cannot copy a divergent thread lifecycle without failing the
  architecture guard.

Costs:

- A small indirection between the dialog and the worker.
- `close()` may detach a stuck solver instead of blocking the GUI thread. The
  work can outlive the dialog; this is deliberate and bounded.
- The modal adapter still runs a nested event loop, because project I/O must
  remain modal.

Out of scope: a thread pool, a scheduler, async/await, worker rewrites, solver
changes, and any schema or project-format change.
