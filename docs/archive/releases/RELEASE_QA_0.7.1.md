# AntennaDesk 0.7.1 release QA

- **Version:** `0.7.1`
- **Date:** 2026-11-16
- **Tag:** `v0.7.1` at `cbe2957`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.7.1>
- **Status:** published with unsigned, checksum-verified artifacts
- **Schema:** 51 (unchanged from 0.7.0)
- **Previous release:** `0.7.0` (2026-11-16)

## Scope

This is a UI-only patch release for the Yagi generator:

- the element table now stretches its columns to the full section width;
- the table keeps a minimum height of 140 px so four rows are visible instead
  of two clipped rows;
- no antenna model, schema, solver, optimizer, persistence, or numerical result
  changes.

The fix is covered by a UI regression test in `tests/ui/test_yagi_dialog.py`.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv pip check` | all installed packages compatible |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 749 files |
| `uv run mypy` | pass, 198 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 147 UI files |
| `uv run pytest -q -W error` | **3,116 passed, 1 skipped** |

The one skip is the Windows-only console-hiding check on Linux.

## Local candidate artifacts

Artifacts were built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.7.1`. Native builds ran the bundle
license audit and passed the local smoke tests below. The published CI
artifacts were rebuilt independently.

## Published assets

Every asset has a companion `.sha256` file. All six published checksums were
verified with `sha256sum -c` after downloading the release assets.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.7.1-py3-none-any.whl` | 990 K | `40c8017ac7e5759d0603cdd3fceef62ed69ed8af882751eb06f7229647dd8c74` |
| `antennadesk-0.7.1.tar.gz` | 1.4 M | `9cc72ba49cbf35fe020e4ecd7e8f97ba8602108369acd3f288abef9ddd491922` |
| `AntennaDesk-0.7.1-x86_64.AppImage` | 129 M | `7a0071d439e2e53dc0663414710c7bf5edd032ed35876804130fcd58a16ce517` |
| `antennadesk_0.7.1_amd64.deb` | 110 M | `3484ba597b56625076910a6ef9574c18eadda6ffdd0df6ac55046af977993be0` |
| `AntennaDesk-0.7.1-windows-x86_64.zip` | 103 M | `7df941f3a63eca34c3bb9850c53a155d7beb06cb5594dc265350c6f150fc19dd` |
| `AntennaDesk-0.7.1-windows-x86_64-setup.exe` | 71 M | `a86a0e8496b5bd1fa17ef57134e895724b13ef7cb883370ebc8b323e072318d4` |

### Wheel and sdist

| Check | Result |
|---|---|
| Clean Python 3.11 venv install | pass |
| `import antennadesk; print(__version__)` | `0.7.1` |
| `python -m antennadesk.ui.app --version` | `0.7.1` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel built from the sdist | pass |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.7.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --extract` | pass |
| `--version` after extraction | `0.7.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer were built in GitHub Actions on
`windows-latest`. The workflow ran the frozen executable version/solver checks,
installed the NSIS package silently, checked the desktop shortcut and installed
executable, and completed the silent uninstall. See CI run
[`43874584598`](https://github.com/fsclavo/antenna-desk/actions/runs/43874584598).

## Known limitations

- This patch changes only the Yagi table layout.
- The manual QA in `QA_PASS_2026-11-15.md` remains valid for the underlying
  features.
- G27, signing, physical validation, and the other limitations from 0.7.0 are
  unchanged.

## Release decision

Published as `v0.7.1` on 2026-11-16. The tag-triggered CI run
[`43874584598`](https://github.com/fsclavo/antenna-desk/actions/runs/43874584598)
completed the wheel/sdist, Linux, Windows, and publish jobs successfully. All
six published assets and their companion `.sha256` files were downloaded and
verified after publication.
