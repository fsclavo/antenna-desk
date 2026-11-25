# AntennaDesk 0.10.1 release QA

- **Version:** `0.10.1`
- **Date:** 2026-11-24
- **Tag:** `v0.10.1`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.10.1>
- **Release workflow:** <https://github.com/fsclavo/antenna-desk/actions/runs/45528295950>
- **Tag CI:** <https://github.com/fsclavo/antenna-desk/actions/runs/45528296051>
- **Status:** published with unsigned, checksum-verified artifacts
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
- Windows 3.11 non-UI, Windows 3.12, and Windows 3.13 UI jobs pass, as do all
  Linux, solver, cross-engine, benchmark, quality, and coverage jobs.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` pass.
- The tag CI matrix passes and the Release workflow builds and smoke-tests every
  artifact.
- Regression coverage asserts that live-tuning results arrive on the dialog's
  GUI thread.

## Published assets

All six artifacts have a companion `.sha256` file. Every published checksum was
verified after downloading the release assets with `sha256sum -c`.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.10.1-py3-none-any.whl` | 1.2 M | `8a189d747abfa4cc4999f5b36ae57ca06e6778dbe05c805d4be4eaec5e4f3d0c` |
| `antennadesk-0.10.1.tar.gz` | 1.9 M | `82fafcd4c9c69936479e0261c296b662ef23e09463d9a958fd2e8d4e86a09a7a` |
| `AntennaDesk-0.10.1-x86_64.AppImage` | 130 M | `c7794e33da26628a211add21532486d85a9afed543fed1a9c29422a439565a01` |
| `antennadesk_0.10.1_amd64.deb` | 110 M | `a1a05f8feabd24e0041c42d5ef235397503f821e2973e7a2b79e860a153c06c9` |
| `AntennaDesk-0.10.1-windows-x86_64.zip` | 104 M | `69b1a2c5c2a6d5a1a797cdc48a5247a511b3f93065f0f9bba3f8d0fcf74c83c2` |
| `AntennaDesk-0.10.1-windows-x86_64-setup.exe` | 71 M | `bbe5f7108c7e014598aea0003b17675c4245bfc58a13e518c0bc5b48ae61f6fd` |

## Known limitations

- Native packages are unsigned; verify the published checksums.
- No live VNA/hardware control.
- Experimental and heuristic templates keep their documented evidence levels.
- PF2, PF3, and UX45 remain optional maintenance items.
