# AntennaDesk 0.6.0 release-candidate QA

- **Version:** `0.6.0`
- **Date:** 2026-11-12
- **Tag:** none yet; candidate on `release/0.6.0-qa` ready to tag
- **Status:** local static checks, Linux/Python artifact smoke tests, offscreen
  visual QA, and CI Windows bundle/installer QA passed; ready to tag

## Scope

This candidate covers the accumulated work since `v0.5.0` and moves the project
schema from 44 to 45. The release-facing changes are:

- a source-backed materials reference for wire, coax, ferrite, and insulators,
  with citations, notes, and visible limitations (UX18);
- a shared 16-cable coax catalog with a feed-line **Catalog** selector that fills
  impedance, velocity factor, and matched loss while keeping the length editable
  (UX23);
- portable `.antennadesk-bundle` ZIP files that move a project and its referenced
  images with validated import (UX19);
- manual project-level BOM costs with currency labels, line totals, and a BOM
  total, shown in the construction sheet, native PDF, package, and conductor BOM
  CSV (UX20, schema 45);
- Moxon and Yagi starting frequencies retuned to **28.500 MHz** and
  **145.000 MHz** with coherent scaled starting geometry (UX24).

The materials, bundle, cost, and starting-frequency work does not change the
solver, gain definitions, or the electromagnetic model. Cost records and image
references are project metadata. The coax catalog keeps the existing scalar
matched-loss model. The Moxon and Yagi defaults use scaled reference geometry and
are labeled as heuristic starting points.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 723 files |
| `uv run mypy` | pass, 193 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 145 UI files |
| `uv run pytest` | **2,932 passed, 1 skipped** |
| Help coverage manifest | pass in the pytest suite |

The full suite runs with the local `spikes/phase0/build/nec2c` solver. The one
skip is the Windows-only console-hiding check, which does not run on Linux.

## Visual QA

Offscreen screenshots were inspected for:

- the materials reference in light and dark themes and with large text, across
  all four tabs;
- the BOM costs dialog in light and dark themes and with large text;
- the Moxon and Yagi dialogs at their new default frequencies in light and dark
  themes.

The tables, cost fields, source links, evidence text, and starting geometry were
legible and did not overlap. This is offscreen QA only; a real-display pass with
platform scaling and all supported font sizes remains manual.

## Artifact smoke tests

Artifacts are built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.6.0`. The native builds run the bundle
license audit.

### Wheel and sdist

| Check | Result |
|---|---|
| `import antennadesk; print(__version__)` in a clean Python 3.12 venv | `0.6.0` |
| `python -m antennadesk.ui.app --version` | `0.6.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel installation | pass |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.6.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --info` | `Version: 0.6.0`, `amd64` |
| Package contents | launcher symlink, `AntennaDesk`, `nec2c`, desktop entry, copyright |
| `--version` after extraction | `0.6.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Local artifacts

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.6.0-py3-none-any.whl` | 952 K | `855635cd94446ffdcb7fa75635bc64043e734babc48f8cf50ad7b2e04db34303` |
| `antennadesk-0.6.0.tar.gz` | 1.3 M | `95a8eba7e903d4865bec88e7ffc05fa41ae8cee24d2f346c4aa61c325a80e9eb` |
| `AntennaDesk-0.6.0-x86_64.AppImage` | 120 M | `56da9fd082e71c752e18e32d2877a72c72316e3b20f37c08aea2f72bb0964ee2` |
| `antennadesk_0.6.0_amd64.deb` | 103 M | `4333b51cefc6f64062de4d600f299f62a9462e0c577b20c7ec2be889dd0574bc` |

These are local candidate artifacts. They are unsigned and are not the published
release assets.

### Windows

Windows QA runs in GitHub Actions because `makensis` is not available locally.
GitHub Actions run
[`43348235272`](https://github.com/fsclavo/antenna-desk/actions/runs/43348235272)
on `release/0.6.0-qa` completed all build jobs successfully:

| Check | Result |
|---|---|
| Wheel and sdist job | pass |
| Windows bundle, `nec2c.exe`, and NSIS installer | pass |
| Frozen `AntennaDesk.exe --version` / `--check-solver` | pass |
| Installer install, desktop shortcut, and uninstaller | pass |
| Installed `AntennaDesk.exe --version` / `--check-solver` | pass |
| Silent uninstall | pass |
| Linux AppImage and `.deb` jobs | pass |
| Publish GitHub release | skipped, because the run was not a tag |

## Signing

Signing remains deferred. No GPG key or Windows Authenticode certificate is
configured for this candidate. The artifacts are unsigned and verified only by
SHA-256.

## Known limitations

- Windows bundle and installer QA runs in CI rather than locally.
- Visual QA is offscreen only.
- BOM costs are manual; there is no price catalog, currency conversion, tax,
  shipping, labor, or quote history.
- Project bundles are local ZIP files; they do not provide cloud storage or
  synchronization.
- The coax simulation keeps a constant matched loss at the displayed datasheet
  frequency; it does not interpolate attenuation by frequency.
- The Moxon 28.500 MHz and Yagi 145.000 MHz defaults are scaled from references
  at 14.17 MHz and 50.1 MHz and are heuristic starting points.
- Antenna-model and evidence limitations are unchanged; see
  `docs/VALIDATION_PLAN.md`.

## Release decision

The 0.6.0 candidate is ready to tag and publish. The code and documentation
passed the static gate, local Linux/Python smoke tests, and the CI Windows
bundle and installer QA. Tag `v0.6.0` on this candidate and push the tag; the
tag-triggered workflow will rebuild, sign if configured, and publish the
checksum-verified artifacts.
