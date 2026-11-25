# AntennaDesk 0.10.1 release QA

- **Version:** `0.10.1`
- **Date:** 2026-11-24
- **Tag:** `v0.10.1`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.10.1>
- **Status:** release candidate; CI publication pending
- **Schema:** 61 (unchanged from 0.10.0)
- **Previous release:** `0.10.0` (2026-11-24)

## Scope

This patch release publishes the refreshed application icon and fixes the
live-tuning preview worker handoff:

- preview results are delivered through queued dialog slots on the GUI thread;
- closing the dialog detaches a still-running `QThread` instead of destroying
  it, removing the unsafe cross-thread widget updates;
- the Windows UI suite splits geometry, journal, and live-tuning batches with
  per-batch timeouts, and the recovery permission test skips Windows correctly;
- the SVG master, 256 px PNG, and multi-resolution Windows ICO use the new Yagi
  emblem.

No schema, solver, electromagnetic model, or project-format change is included.
The 0.10.0 compatibility statement still applies: 0.9.0 gzip/plain-JSON project
files are not readable.

## Validation

- **Full gate:** **4,326 passed, 1 skipped** with `NEC2C`; the skip is the Windows-only console-hiding test on Linux.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` must pass.
- The Windows 3.11/3.12/3.13 CI jobs and the Linux matrix must pass after the
  live-tuning fix; the tag workflow builds and smoke-tests every artifact.
- Regression coverage asserts that live-tuning results arrive on the dialog's
  GUI thread.

## Known limitations

- Native packages are unsigned; verify the published checksums.
- No live VNA/hardware control.
- Experimental and heuristic templates keep their documented evidence levels.
- PF2, PF3, and UX45 remain optional maintenance items.
