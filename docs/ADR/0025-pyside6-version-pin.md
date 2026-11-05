# ADR-0025 — PySide6 version pin and Qt upgrade policy

- **Status:** Accepted
- **Date:** 2026-11-05
- **Deciders:** Fernando Sclavo, development
- **Phase:** UI platform maintenance

## Context

AntennaDesk uses PySide6 for the desktop UI and pyqtgraph for charts. The
project deliberately pinned `pyside6-essentials` below 6.10 because 6.12
triggered a shutdown refcount crash with pyqtgraph in the test environment.
Dependabot now keeps PySide6 in its own group, but a Qt minor upgrade still
needs a deliberate evaluation: a routine grouped dependency merge is not
enough for the UI platform.

PySide6 6.11.3 became the next available minor. It needed the full test matrix
and a shutdown stress that the regular test suite does not cover, because the
original failure happened during interpreter finalization.

## Decision

- Allow `pyside6-essentials` 6.11.x: `>=6.9.2,<6.12`.
- Keep 6.12 excluded until it receives the same evaluation.
- Keep PySide6 in its own Dependabot group so Qt upgrades do not ride along
  with routine Python dependency updates.
- Require the following before allowing a new Qt minor:
  - the full CI matrix (Linux and Windows, Python 3.11–3.13, solver,
    coverage, and cross-engine jobs);
  - the UI suite under the offscreen platform;
  - repeated shutdown runs of the real `MainWindow` with pyqtgraph views,
    covering close/delete/quit variants on offscreen and Xvfb;
  - repeated runs of the real application entry point with a timed event loop;
  - `uv lock --check` and `pip-audit`.

## Evaluation of 6.11.3 (2026-11-05)

- The full CI matrix passed on the Dependabot pull request.
- Local UI suite: 423 passed.
- Local full suite with `nec2c`: 1235 passed, 2 skipped (PyNEC and the
  gitignored MMANA corpus).
- Shutdown stress on 6.11.3:
  - 90 `MainWindow` runs with pyqtgraph views: 60 offscreen and 30 Xvfb;
  - 30 application-entry runs: 20 offscreen and 10 Xvfb;
  - every run exited with code 0 and no fatal Python message.
- `pip-audit` found no known vulnerabilities and `uv lock --check` passed.
- PySide6 6.12.0 also survived the local stress runs, but the original crash
  was not reproduced. That is not enough evidence to remove the exclusion.

## Consequences

### Positive

- The UI gets the Qt 6.11 fixes and the latest available patch release.
- The pin now excludes only the known-bad 6.12 minor instead of blocking all
  versions from 6.10 onward.
- The evaluation procedure is explicit and repeatable.

### Negative

- A Qt minor upgrade costs a deliberate test session; it is not a routine
  Dependabot merge.
- The original 6.12 crash has no minimal reproducer in this repository, so the
  exclusion rests on the documented observation and caution.

### Neutral

- Patch releases inside 6.11.x may still arrive through Dependabot and use the
  normal CI gate; a new minor requires this procedure.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Stay below 6.10 | Blocks the 6.11 fixes without a current failure |
| Allow 6.12 too | The documented crash has not been explained or reproduced |
| Remove the Dependabot ignore | A future 6.12 pull request would return; the exclusion is still needed |
| Merge the grouped Python update | It mixed PySide6 with pydantic and hid the Qt decision |

## Follow-up

1. Re-evaluate 6.12 only when a minimal shutdown reproducer is available or a
   newer pyqtgraph release is confirmed to address it.
2. Keep this ADR and `AGENTS.md` in sync if the pin changes.
