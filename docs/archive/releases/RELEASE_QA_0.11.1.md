# AntennaDesk 0.11.1 release QA

- **Version:** `0.11.1`
- **Date:** 2026-11-27
- **Tag:** `v0.11.1`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.11.1>
- **Status:** published 2026-11-27
- **Schema:** 73 (unchanged from 0.11.0)
- **Previous release:** `0.11.0` (2026-11-27)

## Scope

This patch release fixes the optimizer dialog close/cancel lifecycle that could
crash the application after a manual trapped-Yagi optimization:

- the family, length, synthesis, and element optimization dialogs now call
  `TaskRunner.start()` before updating their controls;
- **Cancel** is enabled and **Close** is disabled while a run is active;
- the Close button and Esc route through cancellation while the worker is
  running instead of hiding the dialog;
- a close request no longer destroys a running `QThread`, removing
  `QThread: Destroyed while thread is still running` on Linux and Windows.

Regression tests cover the trapped-Yagi family optimizer and the element
optimizer, including Cancel, Close state, Esc/reject behavior, and clean worker
teardown.

No solver, electromagnetic model, schema, or project-format change is included.

## Validation

- **Full gate:** **4,790 passed, 1 skipped** (Windows-only console check skipped
  on Linux).
- `uv run ruff check .` — pass.
- `uv run ruff format --check .` — pass.
- `uv run mypy` — pass.
- `uv run mypy --config-file mypy_ui.ini` — pass.
- `NEC2C=spikes/phase0/build/nec2c uv run pytest tests/integration/simulation`
  — **186 passed**.
- `tests/ui/test_family_optimization_dialog.py` — trapped-Yagi lifecycle
  regression passes.
- `tests/ui/test_element_optimization_dialog.py` — element lifecycle regression
  passes.
- `tests/ui/test_optimization_dialog.py` and `tests/ui/test_synthesis_dialog.py`
  — pass.

## Packaging

- `uv build --out-dir …` produced `antennadesk-0.11.1-py3-none-any.whl` and
  `antennadesk-0.11.1.tar.gz`.
- Wheel metadata and the application `--version` report `0.11.1`.
- The tag workflow remains the publication step for the native packages and
  checksums.

## Publication verification (2026-11-27)

- Tag workflow
  [`46052575256`](https://github.com/fsclavo/antenna-desk/actions/runs/46052575256)
  completed successfully and published 12 assets.
- All six published binary checksums verify with `sha256sum -c`.
- Wheel, sdist, and AppImage report `0.11.1`; the Debian package reports
  `0.11.1`.
- The Debian package and Windows portable zip contain the bundled `nec2c`.

## Known limitations

- The 0.11.0 features and limitations remain unchanged. See
  [`RELEASE_QA_0.11.0.md`](RELEASE_QA_0.11.0.md).
- Native packages are unsigned; verify the published checksums.
- The closed crash was a dialog lifecycle bug; it did not affect solver
  results, saved projects, or the schema.
